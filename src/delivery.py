"""
Delivery layer — sends digests via Slack webhook.
"""

import datetime
import logging
import os

import requests

log = logging.getLogger(__name__)


def send_slack(digest: dict, variant: str = "safe"):
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        log.error("No SLACK_WEBHOOK_URL configured")
        return
    text = digest.get(variant, "")
    if not text:
        log.warning("No text for variant %s", variant)
        return
    week = digest.get("week_of", "")
    header = "*:nooks: The Week, According to Nooks — {}*\n_(variant: {})_\n\n".format(week, variant)
    resp = requests.post(webhook, json={"text": header + text}, timeout=10)
    resp.raise_for_status()
    log.info("Slack webhook delivered (%s)", variant)


def send_slack_all_variants(digest: dict):
    for variant in ("safe", "funny", "spicy"):
        send_slack(digest, variant)


def send_slack_daily(stories: list):
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        log.warning("No SLACK_WEBHOOK_URL set — skipping daily Slack update")
        return
    kept = [s for s in stories if s.get("keep")]
    lines = [
        "*:newspaper: Nooks daily intake — {}*".format(datetime.date.today()),
        "Scored {} stories · {} keepers".format(len(stories), len(kept)),
        "",
    ]
    for s in kept[:8]:
        lines.append("• *{}* — {}".format(s.get("source", ""), s.get("headline", "")[:80]))
    resp = requests.post(webhook, json={"text": "\n".join(lines)}, timeout=10)
    resp.raise_for_status()
    log.info("Daily Slack summary sent (%d keepers)", len(kept))


def deliver(digest: dict):
    try:
        send_slack_all_variants(digest)
    except Exception as e:
        log.error("Slack delivery failed: %s", e)
