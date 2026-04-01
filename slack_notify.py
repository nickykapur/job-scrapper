"""
Slack notifications for JobHunt admin monitoring.
Set SLACK_WEBHOOK_URL env var to your Slack Incoming Webhook URL.
"""

import os
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")


def _send(payload: dict) -> None:
    """Post payload to Slack webhook synchronously. Errors are logged, never raised."""
    url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not url:
        logger.warning("SLACK_WEBHOOK_URL not set — skipping notification")
        return
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            logger.warning("Slack returned %s: %s", response.status_code, response.text)
    except Exception as exc:
        logger.warning("Slack notification failed: %s", exc)


def notify_login(username: str, display_name: str = "") -> None:
    name = display_name or username
    _send({
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
    _send({
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


def notify_job_applied(
    username: str,
    display_name: str,
    job_title: str,
    company: str,
    country: str,
) -> None:
    name = display_name or username
    _send({
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
