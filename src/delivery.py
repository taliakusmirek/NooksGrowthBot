"""
Delivery layer -- Slack webhook or Gmail.
"""

import base64
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests

log = logging.getLogger(__name__)


def send_slack(digest, variant="safe"):
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    bot_token = os.environ.get("SLACK_BOT_TOKEN", "")
    channel = os.environ.get("SLACK_CHANNEL", "#general")
    text = digest.get(variant, "")
    if not text:
        log.warning("No text for variant %s", variant)
        return
    week = digest.get("week_of", "")
    header = f"*:nooks: The Week, According to Nooks -- {week}*\n_(variant: {variant})_\n\n"
    payload_text = header + text
    if webhook:
        resp = requests.post(webhook, json={"text": payload_text}, timeout=10)
        resp.raise_for_status()
        log.info("Slack webhook delivered (%s)", variant)
    elif bot_token:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {bot_token}"},
            json={"channel": channel, "text": payload_text},
            timeout=10,
        )
        resp.raise_for_status()
        log.info("Slack bot delivered (%s) to %s", variant, channel)
    else:
        log.error("No Slack credentials configured")


def send_slack_all_variants(digest):
    for variant in ("safe", "funny", "spicy"):
        send_slack(digest, variant)


def _get_gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds_path = os.environ.get("GMAIL_CREDENTIALS_JSON", "credentials.json")
    token_path = os.environ.get("GMAIL_TOKEN_JSON", "token.json")
    creds = None
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(token_path).write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _build_email(digest):
    to_addr = os.environ["GMAIL_TO"]
    week = digest.get("week_of", "")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"The Week, According to Nooks -- {week}"
    msg["To"] = to_addr
    plain_body = "\n\n".join([
        f"=== SAFE ===\n\n{digest.get('safe', '')}",
        f"=== FUNNY ===\n\n{digest.get('funny', '')}",
        f"=== SPICY ===\n\n{digest.get('spicy', '')}",
    ])
    def variant_html(label, text, color):
        bullets = ""
        for line in text.split("\n"):
            if line.strip().startswith(">"):
                bullet = line.strip().lstrip("> ").strip()
                bullets += f"<li>{bullet}</li>\n"
            elif line.strip():
                bullets += f"<p style='margin:4px 0;color:#555;font-size:13px;'>{line.strip()}</p>\n"
        return f"""<div style="margin-bottom:32px;border-left:4px solid {color};padding-left:16px;">
            <h3 style="color:{color};margin:0 0 12px;">{label}</h3>
            <ul style="list-style:none;padding:0;margin:0;font-family:Georgia,serif;font-size:15px;line-height:1.7;">{bullets}</ul></div>"""
    html_body = f"""<html><body style="font-family:sans-serif;max-width:680px;margin:auto;padding:24px;">
        <h2 style="color:#5B2D8E;">The Week, According to Nooks 💜</h2>
        <p style="color:#888;font-size:13px;">Week of {week} · {digest.get('story_count',0)} stories reviewed</p>
        {variant_html("SAFE", digest.get("safe",""), "#5B2D8E")}
        {variant_html("FUNNY", digest.get("funny",""), "#E67E22")}
        {variant_html("SPICY", digest.get("spicy",""), "#C0392B")}
    </body></html>"""
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def send_gmail(digest):
    service = _get_gmail_service()
    msg = _build_email(digest)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    log.info("Gmail digest sent to %s", os.environ.get("GMAIL_TO", "?"))


def send_slack_daily(stories: list):
    import datetime
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        log.warning("No SLACK_WEBHOOK_URL set — skipping daily Slack update")
        return
    kept = [s for s in stories if s.get("keep")]
    lines = [f"*:newspaper: Nooks daily intake — {datetime.date.today()}*",
             f"Scored {len(stories)} stories · {len(kept)} keepers", ""]
    for s in kept[:8]:
        lines.append(f"• *{s['source']}* — {s['headline'][:80]}")
    try:
        resp = requests.post(webhook, json={"text": "
".join(lines)}, timeout=10)
        resp.raise_for_status()
        log.info("Daily Slack summary sent (%d keepers)", len(kept))
    except Exception as e:
        log.error("Daily Slack send failed: %s", e)


def deliver(digest):
    method = os.environ.get("DELIVERY_METHOD", "slack").lower()
    if method in ("slack", "both"):
        try:
            send_slack_all_variants(digest)
        except Exception as e:
            log.error("Slack delivery failed: %s", e)
    if method in ("gmail", "both"):
        try:
            send_gmail(digest)
        except Exception as e:
            log.error("Gmail delivery failed: %s", e)
