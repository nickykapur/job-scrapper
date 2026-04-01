"""
Slack notifications for JobHunt admin monitoring.

Usage: set SLACK_WEBHOOK_URL env var to your Slack Incoming Webhook URL.
All functions are fire-and-forget — errors are logged but never raised.
"""

import os
import asyncio
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")


async def _send(payload: dict) -> None:
    """Post payload to Slack webhook in a thread — does not block the event loop."""
    if not SLACK_WEBHOOK_URL:
        return
    try:
        await asyncio.to_thread(
            requests.post,
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=5,
        )
    except Exception as exc:
        logger.warning("Slack notification failed: %s", exc)


# ── Public notification functions ────────────────────────────────────────────

async def notify_login(username: str, display_name: str = "") -> None:
    """Send a login alert to Slack."""
    name = display_name or username
    await _send({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"👋  *{name}* just logged in",
                },
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"🕐  {_now_str()}  ·  `{username}`"},
                ],
            },
            {"type": "divider"},
        ]
    })


async def notify_register(username: str, email: str, display_name: str = "") -> None:
    """Send a new-user registration alert to Slack."""
    name = display_name or username
    await _send({
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🎉  New user registered!"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Name*\n{name}"},
                    {"type": "mrkdwn", "text": f"*Username*\n`{username}`"},
                    {"type": "mrkdwn", "text": f"*Email*\n{email}"},
                ],
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"🕐  {_now_str()}"},
                ],
            },
            {"type": "divider"},
        ]
    })


async def notify_job_applied(
    username: str,
    display_name: str,
    job_title: str,
    company: str,
    country: str,
) -> None:
    """Send a job-applied alert to Slack."""
    name = display_name or username
    await _send({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅  *{name}* applied to a job!",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Role*\n{job_title}"},
                    {"type": "mrkdwn", "text": f"*Company*\n{company}"},
                    {"type": "mrkdwn", "text": f"*Country*\n{country}"},
                ],
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"🕐  {_now_str()}  ·  `{username}`"},
                ],
            },
            {"type": "divider"},
        ]
    })
