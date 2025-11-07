#!/usr/bin/env python3
"""
Send user analytics to Slack
Tracks: logins, jobs applied, user activity
"""

import os
import sys
import asyncio
import asyncpg
import requests
from datetime import datetime, timedelta

async def get_analytics():
    """Get user analytics from database"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not set")
        return None

    conn = await asyncpg.connect(db_url)

    try:
        # Get all users with their stats
        users = await conn.fetch("""
            SELECT
                u.id,
                u.username,
                u.email,
                u.full_name,
                u.created_at,
                u.last_login,
                up.job_types,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE) as jobs_applied,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE) as jobs_rejected,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.saved = TRUE) as jobs_saved,
                MAX(uji.updated_at) as last_interaction
            FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            GROUP BY u.id, u.username, u.email, u.full_name, u.created_at, u.last_login, up.job_types
            ORDER BY u.created_at DESC
        """)

        # Get recent activity (last 24 hours)
        recent_activity = await conn.fetch("""
            SELECT
                u.username,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE AND uji.applied_at > NOW() - INTERVAL '24 hours') as applied_24h,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE AND uji.rejected_at > NOW() - INTERVAL '24 hours') as rejected_24h
            FROM users u
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            GROUP BY u.username
            HAVING COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE AND uji.applied_at > NOW() - INTERVAL '24 hours') > 0
                OR COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE AND uji.rejected_at > NOW() - INTERVAL '24 hours') > 0
        """)

        # Get total job counts
        total_jobs = await conn.fetchrow("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE country = 'Ireland') as ireland,
                COUNT(*) FILTER (WHERE country = 'Spain') as spain,
                COUNT(*) FILTER (WHERE country = 'Panama') as panama,
                COUNT(*) FILTER (WHERE country = 'Chile') as chile,
                COUNT(*) FILTER (WHERE country = 'Netherlands') as netherlands,
                COUNT(*) FILTER (WHERE country = 'Germany') as germany,
                COUNT(*) FILTER (WHERE country = 'Sweden') as sweden,
                COUNT(*) FILTER (WHERE country = 'Belgium') as belgium,
                COUNT(*) FILTER (WHERE country = 'Denmark') as denmark,
                COUNT(*) FILTER (WHERE job_type = 'software') as software_jobs,
                COUNT(*) FILTER (WHERE job_type = 'hr') as hr_jobs,
                COUNT(*) FILTER (WHERE job_type = 'cybersecurity') as cybersecurity_jobs
            FROM jobs
        """)

        return {
            'users': users,
            'recent_activity': recent_activity,
            'total_jobs': total_jobs
        }

    finally:
        await conn.close()

def send_to_slack(analytics):
    """Send analytics to Slack"""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("[ERROR] SLACK_WEBHOOK_URL not set")
        return False

    # Build user stats
    user_stats = []
    for user in analytics['users']:
        # Determine job type display name
        job_types = user['job_types'] or []
        if 'software' in job_types:
            job_type_name = "Software"
        elif 'hr' in job_types or 'recruitment' in job_types:
            job_type_name = "HR"
        elif 'cybersecurity' in job_types or 'security' in job_types or 'soc' in job_types:
            job_type_name = "Cybersecurity"
        else:
            job_type_name = "General"

        last_login = "Never" if not user['last_login'] else f"<t:{int(user['last_login'].timestamp())}:R>"

        user_stats.append(
            f"*{user['username']}* ({job_type_name})\n"
            f"  Applied: {user['jobs_applied']} | Rejected: {user['jobs_rejected']} | Saved: {user['jobs_saved']}\n"
            f"  Last login: {last_login}"
        )

    # Build recent activity
    recent_text = []
    for activity in analytics['recent_activity']:
        if activity['applied_24h'] > 0 or activity['rejected_24h'] > 0:
            recent_text.append(
                f"• *{activity['username']}*: {activity['applied_24h']} applied, {activity['rejected_24h']} rejected"
            )

    if not recent_text:
        recent_text.append("• No activity in last 24 hours")

    # Build job database stats
    tj = analytics['total_jobs']

    # Ensure all values are not None (some might be None if no jobs exist for that type/country)
    safe_get = lambda key: tj.get(key) or 0

    message = {
        "text": "Daily User Analytics Report",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily Analytics Report"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {datetime.now().strftime('%Y-%m-%d')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*👥 User Activity*\n\n" + "\n\n".join(user_stats)
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*⚡ Recent Activity (Last 24h)*\n\n" + "\n".join(recent_text)
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💼 Job Database Stats*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Jobs:*\n{safe_get('total')}"},
                    {"type": "mrkdwn", "text": f"*Software:*\n{safe_get('software_jobs')}"},
                    {"type": "mrkdwn", "text": f"*HR:*\n{safe_get('hr_jobs')}"},
                    {"type": "mrkdwn", "text": f"*Cybersecurity:*\n{safe_get('cybersecurity_jobs')}"},
                    {"type": "mrkdwn", "text": f"*🇮🇪 Ireland:*\n{safe_get('ireland')}"},
                    {"type": "mrkdwn", "text": f"*🇪🇸 Spain:*\n{safe_get('spain')}"},
                    {"type": "mrkdwn", "text": f"*🇵🇦 Panama:*\n{safe_get('panama')}"},
                    {"type": "mrkdwn", "text": f"*🇨🇱 Chile:*\n{safe_get('chile')}"},
                    {"type": "mrkdwn", "text": f"*🇳🇱 Netherlands:*\n{safe_get('netherlands')}"},
                    {"type": "mrkdwn", "text": f"*🇩🇪 Germany:*\n{safe_get('germany')}"},
                    {"type": "mrkdwn", "text": f"*🇸🇪 Sweden:*\n{safe_get('sweden')}"},
                    {"type": "mrkdwn", "text": f"*🇧🇪 Belgium:*\n{safe_get('belgium')}"},
                    {"type": "mrkdwn", "text": f"*🇩🇰 Denmark:*\n{safe_get('denmark')}"}
                ]
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            print("[SUCCESS] Analytics sent to Slack")
            return True
        else:
            print(f"[ERROR] Slack API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error sending to Slack: {e}")
        return False

async def main():
    print("[INFO] Fetching user analytics...")
    analytics = await get_analytics()

    if not analytics:
        sys.exit(1)

    print(f"[SUCCESS] Found {len(analytics['users'])} users")
    print(f"[INFO] Recent activity: {len(analytics['recent_activity'])} active users")

    print("\n[INFO] Sending to Slack...")
    success = send_to_slack(analytics)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
