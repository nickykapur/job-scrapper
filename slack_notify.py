"""
Slack notifications for JobHunt admin monitoring.
Set SLACK_WEBHOOK_URL env var to your Slack Incoming Webhook URL.

_send_sync   — plain requests.post, used in a background thread
_send_async  — awaitable wrapper (runs _send_sync in a thread pool)
notify_*     — sync helpers called from non-async contexts (login/register)
notify_*_async — async helpers called from async contexts (job applied)
"""

import os
import logging
import threading
import asyncio
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")


def _send_sync(payload: dict) -> None:
    """Blocking HTTP POST to Slack. Never raises."""
    url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not url:
        logger.warning("SLACK_WEBHOOK_URL not set — skipping Slack notification")
        return
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code != 200:
            logger.warning("Slack returned %s: %s", resp.status_code, resp.text[:200])
        else:
            logger.info("Slack notification sent OK")
    except Exception as exc:
        logger.warning("Slack notification failed: %s", exc)


def _send_in_thread(payload: dict) -> None:
    """Fire-and-forget: runs _send_sync in a daemon thread so it never blocks callers."""
    t = threading.Thread(target=_send_sync, args=(payload,), daemon=True)
    t.start()


async def _send_async(payload: dict) -> None:
    """Awaitable wrapper — runs _send_sync in the default thread-pool executor."""
    await asyncio.get_event_loop().run_in_executor(None, _send_sync, payload)


# ── Sync helpers (login / register — called from sync context) ───────────────

def notify_login(username: str, display_name: str = "") -> None:
    name = display_name or username
    _send_in_thread({
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"👋  *{name}* just logged in"},
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"🕐  {_now_str()}  ·  `{username}`"}],
            },
            {"type": "divider"},
        ]
    })


def notify_register(username: str, email: str, display_name: str = "") -> None:
    name = display_name or username
    _send_in_thread({
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
                "elements": [{"type": "mrkdwn", "text": f"🕐  {_now_str()}"}],
            },
            {"type": "divider"},
        ]
    })


# ── Async helper (job applied — called from async context) ───────────────────

async def notify_job_applied_async(
    username: str,
    display_name: str,
    job_title: str,
    company: str,
    country: str,
) -> None:
    name = display_name or username
    await _send_async({
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"✅  *{name}* applied to a job!"},
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
                "elements": [{"type": "mrkdwn", "text": f"🕐  {_now_str()}  ·  `{username}`"}],
            },
            {"type": "divider"},
        ]
    })
