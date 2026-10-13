# Login-CSRF state enforcement for the non-PKCE Google/Microsoft SSO flows
# (LD fork R2-13): the pinned fastapi-sso 0.19.0 skips state checks entirely
# when no state is present, so a pre-minted callback signed the victim's
# browser into the attacker's account.

from fastapi import HTTPException
from unittest.mock import MagicMock

import pytest

from litellm.proxy.management_endpoints.ui_sso import (
    _bind_state_cookie_on_sso_redirect,
    _enforce_sso_browser_state,
)


def _req(*, cookies: dict, https: bool = True):
    req = MagicMock()
    req.cookies = cookies
    with (
        __import__("contextlib").suppress(Exception),
        __import__("unittest.mock").patch(
            "litellm.proxy.management_endpoints.ui_sso.IPAddressUtils.is_request_https",
            staticmethod(lambda request: https),
        ),
    ):
        pass
    return req


def test_missing_state_rejected():
    req = _req(cookies={})
    with pytest.raises(HTTPException) as exc:
        _enforce_sso_browser_state(request=req, state=None)
    assert int(getattr(exc.value, "status_code", 0)) == 400


def test_mismatched_state_rejected():
    req = _req(cookies={"litellm_oauth_state": "AAA"})
    with pytest.raises(HTTPException) as exc:
        _enforce_sso_browser_state(request=req, state="BBB")
    assert int(getattr(exc.value, "status_code", 0)) == 401


def test_matching_state_passes_and_cli_exempt():
    req = MagicMock()
    req.cookies = {"litellm_oauth_state": "AAA"}
    _enforce_sso_browser_state(request=req, state="AAA")
    _enforce_sso_browser_state(request=req, state="litellm-session-token:xyz")


def test_opt_out_flag_releases_enforcement(monkeypatch):
    import litellm.proxy.proxy_server as ps

    monkeypatch.setattr(
        ps, "general_settings", {"disable_sso_login_csrf_protection": True}
    )
    req = _req(cookies={})
    _enforce_sso_browser_state(request=req, state=None)  # no raise


def test_bind_state_cookie_mints_state_and_cookie():
    redirect = MagicMock()
    redirect.headers = {"location": "https://idp.example.com/auth"}
    redirect.set_cookie = MagicMock()
    req = _req(cookies={})

    _bind_state_cookie_on_sso_redirect(
        redirect_response=redirect, state=None, request=req
    )

    location = redirect.headers["location"]
    assert "state=" in location
    assert redirect.set_cookie.called
    cookie_kwargs = redirect.set_cookie.call_args.kwargs
    assert cookie_kwargs["key"] == "litellm_oauth_state"
    assert cookie_kwargs["httponly"] is True
    assert location.split("state=")[1] == cookie_kwargs["value"]
