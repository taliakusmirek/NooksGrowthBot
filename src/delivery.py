"""
Delivery layer — sends digests and daily summaries via Slack webhook.
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

    # Sort keepers by total score descending
    kept = [s for s in stories if s.get("keep")]
    kept.sort(key=lambda s: sum(s.get("scores", {}).values()), reverse=True)
    skipped = [s for s in stories if not s.get("keep")]

    lines = [
        "*:newspaper: Nooks daily intake — {}*".format(datetime.date.today()),
        "Scored {} stories · {} keepers · {} skipped".format(len(stories), len(kept), len(skipped)),
        "",
        "*Top stories:*",
    ]

    for i, s in enumerate(kept[:50], 1):
        score = sum(s.get("scores", {}).values())
        link = s.get("link", "")
        headline = s.get("headline", "")
        why = s.get("why_it_matters", "")
        nooks = s.get("nooks_angle", "")
        line = "{}. <{}|{}>".format(i, link, headline) if link else "{}. {}".format(i, headline)
        if why:
            line += "\n    _{}_".format(why)
        if nooks:
            line += "\n    :nooks: {}".format(nooks)
        line += "\n    Score: {} · {}".format(score, s.get("virality_signal", ""))
        lines.append(line)
        lines.append("")

    if skipped:
        lines.append("*Also scraped (not kept):*")
        for s in skipped[:20]:
            link = s.get("link", "")
            headline = s.get("headline", "")
            src = s.get("source", "")
            if link:
                lines.append("• <{}|{}> _({})_".format(link, headline, src))
            else:
                lines.append("• {} _({})_".format(headline, src))

    # Slack has a 40k char limit — chunk into multiple messages if needed
    full_text = "\n".join(lines)
    chunks = [full_text[i:i+3800] for i in range(0, len(full_text), 3800)]
    for chunk in chunks:
        resp = requests.post(webhook, json={"text": chunk}, timeout=10)
        resp.raise_for_status()

    log.info("Daily Slack summary sent (%d keepers, %d chunks)", len(kept), len(chunks))


def deliver(digest: dict):
    try:
        send_slack_all_variants(digest)
    except Exception as e:
        log.error("Slack delivery failed: %s", e)
