# OAuth2 introspection validation contract (fork hardening R1-L1) and the
# credential-disclosure contract (R1-L2).

import asyncio
import json
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _handler_response(active: bool | None) -> Any:
    """Build the httpx response the IdP introspection endpoint would return."""
    response = MagicMock()
    response.status_code = 200
    payload: dict[str, Any] = {"sub": "user-1", "email": "u@example.com"}
    if active is not None:
        payload["active"] = active
    response.json = lambda: payload
    return response


async def _run_check(monkeypatch, active: bool | None, captured: dict | None = None):
    from litellm.proxy.auth import oauth2_check

    import litellm.proxy.proxy_server as proxy_server_mod

    monkeypatch.setattr(proxy_server_mod, "premium_user", True)
    import os

    monkeypatch.setenv("OAUTH_TOKEN_INFO_ENDPOINT", "https://idp.example.com/introspect")
    monkeypatch.setenv("OAUTH_CLIENT_ID", "client")
    monkeypatch.setenv("OAUTH_CLIENT_SECRET", "secret")

    def fake_post(url, headers=None, data=None):
        captured["request"] = {"url": url, "data": data}
        return _handler_response(active)

    client = MagicMock()
    client.post = AsyncMock(side_effect=lambda url, headers=None, data=None: _handler_response(active))
    monkeypatch.setattr(
        oauth2_check,
        "get_async_httpx_client",
        lambda *a, **kw: client,
    )

    authenticated = await oauth2_check.Oauth2Handler.check_oauth2_token(token="sk-idp-bearer")
    captured["client"] = client
    return authenticated


def test_introspection_active_false_is_rejected(monkeypatch):
    with pytest.raises(Exception) as exc:
        asyncio.run(_run_check(monkeypatch, active=False, captured={}))
    assert (
        "active" in str(exc.value)
        and "400" in str(getattr(exc.value, "status_code", 400))
        or "400" in str(getattr(exc.value, "detail", ""))
    )


def test_introspection_missing_active_flag_is_rejected(monkeypatch):
    """RFC 7662 requires the active flag; a degraded IdP response that omits
    it must not silently validate the presented token (was default-True)."""
    with pytest.raises(Exception):
        asyncio.run(_run_check(monkeypatch, active=None, captured={}))


def test_introspection_active_true_validates(monkeypatch):
    result = asyncio.run(_run_check(monkeypatch, active=True, captured={}))
    from litellm.proxy._types import UserAPIKeyAuth

    assert isinstance(result, UserAPIKeyAuth)


def test_check_oauth2_token_does_not_log_the_bearer(monkeypatch):
    """The presented IdP bearer must not appear in debug output (R1-L2)."""
    import logging

    from litellm.proxy.auth import oauth2_check

    logged: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logged.append(record.getMessage())

    logger = logging.getLogger(oauth2_check.verbose_proxy_logger.name)
    handler = Capture()
    logger.addHandler(Capture())
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        asyncio.run(_run_check(monkeypatch, active=True, captured={}))
    finally:
        logger.removeHandler(Capture())
        logger.setLevel(old_level)

    assert all("sk-idp-bearer" not in line for line in logged)
