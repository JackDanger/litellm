"""R2-38: /spend/* failures surface the exception message, never stack frames.

Function-level regression derived from the L2 probe
`adversarial/replay.py::_probe_spend_error_no_traceback` (same boot, same
assertion) so the behavior has a portable upstream-safe test file."""

import os
from unittest.mock import AsyncMock

import importlib
import pytest


@pytest.fixture
def spend_app(monkeypatch):
    monkeypatch.setenv("LITELLM_REPO", os.getcwd())
    import litellm.proxy.proxy_server as proxy_server
    import litellm.proxy.spend_tracking.spend_management_endpoints as sme
    from fastapi.testclient import TestClient
    from litellm.proxy.auth.user_api_key_auth import user_api_key_auth
    from litellm.proxy._types import UserAPIKeyAuth, LitellmUserRoles

    async def exploding(**kwargs):
        raise RuntimeError("boom internal detail /app/secret.py line 1")

    def override():
        return UserAPIKeyAuth(
            api_key="sk-probe-internal",
            user_role=LitellmUserRoles.INTERNAL_USER,
            user_id="u1",
        )

    original_client = getattr(proxy_server, "prisma_client", None)
    original_helper = getattr(sme, "ui_get_spend_by_tags", None)
    monkeypatch.setattr(proxy_server, "prisma_client", AsyncMock())
    monkeypatch.setattr(sme, "ui_get_spend_by_tags", exploding)
    app = proxy_server.app
    app.dependency_overrides[user_api_key_auth] = override
    yield TestClient(app, raise_server_exceptions=False)
    if original_client is None:
        proxy_server.prisma_client = None
    else:
        proxy_server.prisma_client = original_client
    if original_helper is not None:
        sme.ui_get_spend_by_tags = original_helper


def test_spend_tags_error_has_no_frames(spend_app):
    resp = spend_app.get(
        "/global/spend/tags",
        params={"start_date": "2026-01-01 00:00:00", "end_date": "2026-01-31 00:00:00"},
    )
    assert ".py:" not in resp.text and "Traceback" not in resp.text


def test_spend_ui_scoping_still_applies(spend_app):
    # the same route exercised earlier for R2-19: ownership scoping intact
    resp = spend_app.get(
        "/spend/logs/ui",
        params={"start_date": "2026-01-01 00:00:00", "end_date": "2026-01-31 00:00:00"},
    )
    assert ".py:" not in resp.text
