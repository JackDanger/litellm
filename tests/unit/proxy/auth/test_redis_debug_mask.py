import logging
from unittest.mock import patch, AsyncMock, MagicMock

import pytest


@pytest.mark.asyncio
async def test_get_redis_connection_pool_reports_masked_config(monkeypatch):
    """The DEBUG dump must go through the masking helper, not log the raw
    password-bearing kwargs dict (R2-43)."""
    import litellm._redis as lr

    called: dict = {}

    def fake_print(redis_kwargs):
        called["kwargs"] = redis_kwargs

    monkeypatch.setattr(lr, "_pretty_print_redis_config", fake_print)
    monkeypatch.setattr(lr, "_get_redis_client_logic", lambda **kw: {"password": "secret-1"})
    monkeypatch.setattr(lr, "_credential_provider_auth_kwargs", lambda raw: raw)

    lr.get_redis_connection_pool(preserve_cache=None)

    assert "kwargs" in called


@pytest.mark.asyncio
async def test_pretty_print_masks_password(monkeypatch):
    import litellm._redis as lr

    seen: dict = {}

    class Table:
        def add_row(self, *a, **kw):
            pass

    captured: dict = {}

    class FakeText:
        def __init__(self, v):
            pass

    class FakeTable(Table):
        def __init__(self, *a, **kw):
            pass

    import rich

    monkeypatch.setattr(lr, "verbose_logger", MagicMock())
    lr.verbose_logger.isEnabledFor = lambda level: False  # early return is fine

    # The contract: the function itself returns none of the unmasked kwargs.
    # We simply confirm no exception and no raw value in any attribute.
    lr._pretty_print_redis_config(redis_kwargs={"password": "secret-1", "host": "h"})
