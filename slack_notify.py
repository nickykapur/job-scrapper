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


def _send_sync(payload: dict, label: str = "") -> None:
    """Blocking HTTP POST to Slack. Never raises."""
    url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not url:
        logger.warning("SLACK_WEBHOOK_URL not set — skipping %s notification", label or "Slack")
        return
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code != 200:
            logger.warning("Slack %s returned %s: %s", label, resp.status_code, resp.text[:300])
        else:
            logger.warning("Slack %s notification sent OK", label)
    except Exception as exc:
        logger.warning("Slack %s notification failed: %s", label, exc)


def _send_in_thread(payload: dict, label: str = "") -> None:
    """Fire-and-forget: runs _send_sync in a daemon thread so it never blocks callers."""
    t = threading.Thread(target=_send_sync, args=(payload, label), daemon=True)
    t.start()


async def _send_async(payload: dict, label: str = "") -> None:
    """Awaitable wrapper — runs _send_sync in the default thread-pool executor."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send_sync, payload, label)


# ── Sync helpers (login / register — called from sync context) ───────────────

def notify_login(username: str, display_name: str = "") -> None:
    name = display_name or username
    _send_in_thread({
        "text": f"👋 *{name}* just logged in  ·  `{username}`  ·  {_now_str()}",
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
    }, label="login")


def notify_register(username: str, email: str, display_name: str = "") -> None:
    name = display_name or username
    _send_in_thread({
        "text": f"🎉 New user registered: *{name}* (`{username}`)  ·  {email}  ·  {_now_str()}",
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
    }, label="register")


async def notify_login_async(username: str, display_name: str = "") -> None:
    name = display_name or username
    await _send_async({
        "text": f"👋 *{name}* just logged in  ·  `{username}`  ·  {_now_str()}",
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
    }, label="login")


# ── Sync helpers (job applied/rejected — called from background tasks) ────────

def notify_job_applied(
    username: str,
    display_name: str,
    job_title: str,
    company: str,
    country: str,
) -> None:
    name = display_name or username
    _send_in_thread({
        "text": f"✅ *{name}* applied to *{job_title}* at {company} ({country})  ·  {_now_str()}",
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
    }, label="job-applied")


def notify_job_rejected(
    username: str,
    display_name: str,
    job_title: str,
    company: str,
) -> None:
    name = display_name or username
    _send_in_thread({
        "text": f"❌ *{name}* rejected *{job_title}* at {company}  ·  {_now_str()}",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"❌  *{name}* skipped a job"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Role*\n{job_title}"},
                    {"type": "mrkdwn", "text": f"*Company*\n{company}"},
                ],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"🕐  {_now_str()}  ·  `{username}`"}],
            },
            {"type": "divider"},
        ]
    }, label="job-rejected")


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
        "text": f"✅ *{name}* applied to *{job_title}* at {company} ({country})  ·  {_now_str()}",
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
    }, label="job-applied")


async def notify_job_rejected_async(
    username: str,
    display_name: str,
    job_title: str,
    company: str,
) -> None:
    name = display_name or username
    await _send_async({
        "text": f"❌ *{name}* rejected *{job_title}* at {company}  ·  {_now_str()}",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"❌  *{name}* skipped a job"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Role*\n{job_title}"},
                    {"type": "mrkdwn", "text": f"*Company*\n{company}"},
                ],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"🕐  {_now_str()}  ·  `{username}`"}],
            },
            {"type": "divider"},
        ]
    }, label="job-rejected")


async def notify_cv_upload_async(
    username: str,
    display_name: str,
    filename: str,
    file_size_kb: float,
    skills_count: int,
) -> None:
    name = display_name or username
    await _send_async({
        "text": f"📄 *{name}* uploaded a CV: {filename} ({file_size_kb:.1f} KB, {skills_count} skills) — `{username}`  ·  {_now_str()}",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📄  CV uploaded"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*User*\n{name} (`{username}`)"},
                    {"type": "mrkdwn", "text": f"*File*\n{filename}"},
                    {"type": "mrkdwn", "text": f"*Size*\n{file_size_kb:.1f} KB"},
                    {"type": "mrkdwn", "text": f"*Skills matched*\n{skills_count}"},
                ],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"🕐  {_now_str()}"}],
            },
            {"type": "divider"},
        ]
    }, label="cv-upload")
