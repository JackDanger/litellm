# render-level test: hostile alerting_metadata must arrive escaped in the
# formatted message queued for delivery (LD fork R1-M10)

import asyncio
from unittest.mock import patch, AsyncMock

import pytest

from litellm.integrations.SlackAlerting.slack_alerting import SlackAlerting  # noqa: F401


@pytest.mark.asyncio
async def test_send_alert_escapes_hostile_metadata(monkeypatch):
    import os

    sa = SlackAlerting(default_webhook_url="https://hooks.slack.com/T/B/FAKE")
    sa.alerting = ["slack", "ms_teams"]
    sa._enqueue_ms_teams_alert = AsyncMock()
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/T/B/FAKE")

    with (
        patch.object(sa, "batch_size", 1),
        patch.object(sa, "flush_queue", AsyncMock()),
    ):
        await sa.send_alert(
            message="LLM API call failed",
            level="High",
            alert_type="llm_exceptions",
            user_info=None,
            alerting_metadata={"0xevil": "<@U999> <!here> `x`"},
        )

    queued_text = "".join(
        str(item.get("payload", {}).get("text", "")) for item in sa.log_queue
    )
    assert "<@U999>" not in queued_text
    assert "&lt;@U999&gt;" in queued_text
    assert "`x`" not in queued_text

# render-level test: hostile alerting_metadata must arrive escaped in the
# formatted message queued for delivery (LD fork R1-M10)

import asyncio
from unittest.mock import patch, AsyncMock

import pytest

from litellm.integrations.SlackAlerting.slack_alerting import SlackAlerting  # noqa: F401


@pytest.mark.asyncio
async def test_send_alert_escapes_hostile_metadata(monkeypatch):
    import os

    sa = SlackAlerting(default_webhook_url="https://hooks.slack.com/T/B/FAKE")
    sa.alerting = ["slack", "ms_teams"]
    sa._enqueue_ms_teams_alert = AsyncMock()
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/T/B/FAKE")

    with (
        patch.object(sa, "batch_size", 1),
        patch.object(sa, "flush_queue", AsyncMock()),
    ):
        await sa.send_alert(
            message="LLM API call failed",
            level="High",
            alert_type="llm_exceptions",
            user_info=None,
            alerting_metadata={"0xevil": "<@U999> <!here> `x`"},
        )

    queued_text = "".join(
        str(item.get("payload", {}).get("text", "")) for item in sa.log_queue
    )
    assert "<@U999>" not in queued_text
    assert "&lt;@U999&gt;" in queued_text
    assert "`x`" not in queued_text
