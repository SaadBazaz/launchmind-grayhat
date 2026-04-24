import os
import requests


def post_launch_message(tagline: str, description: str, pr_url: str) -> None:
    payload = {
        "channel": os.environ.get("SLACK_CHANNEL", "#launches"),
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"New Launch: {tagline}"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": description},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*GitHub PR:* <{pr_url}|View PR>"},
                    {"type": "mrkdwn", "text": "*Status:* Ready for review"},
                ],
            },
        ],
    }
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"},
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack error: {data.get('error')}")


def post_ceo_summary(summary: str, pr_url: str) -> None:
    payload = {
        "channel": os.environ.get("SLACK_CHANNEL", "#launches"),
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "CEO Launch Summary"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*PR:* <{pr_url}|View Pull Request>"},
                    {"type": "mrkdwn", "text": "*Pipeline:* Complete"},
                ],
            },
        ],
    }
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"},
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack error: {data.get('error')}")
