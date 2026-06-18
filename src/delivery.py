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


def _safe_link(url: str, text: str) -> str:
    """Return a Slack-safe linked label, falling back to plain text if URL looks broken."""
    # Strip anything after a pipe or space that could break Slack's <url|text> syntax
    url = url.strip().split(" ")[0]
    # Truncate very long headlines to avoid Slack rendering bugs
    text = text.replace("|", "-").replace("<", "").replace(">", "").strip()
    if url:
        return "<{}|{}>".format(url, text)
    return text


def send_slack_daily(stories: list):
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        log.warning("No SLACK_WEBHOOK_URL set — skipping daily Slack update")
        return

    kept = [s for s in stories if s.get("keep")]
    kept.sort(key=lambda s: sum(s.get("scores", {}).values()), reverse=True)
    skipped = [s for s in stories if not s.get("keep")]

    # Build top stories block
    top_lines = [
        "*:newspaper: Nooks daily intake — {}*".format(datetime.date.today()),
        "Scored {} stories · {} keepers · {} skipped".format(len(stories), len(kept), len(skipped)),
        "",
        "*Top stories:*",
    ]
    for i, s in enumerate(kept[:50], 1):
        top_lines.append("{}. {}".format(i, _safe_link(s.get("link", ""), s.get("headline", ""))))

    # Build also-scraped block
    skip_lines = ["", "*Also scraped:*"]
    for s in skipped[:20]:
        skip_lines.append("• {}".format(_safe_link(s.get("link", ""), s.get("headline", ""))))

    def post(text):
        resp = requests.post(webhook, json={"text": text}, timeout=10)
        resp.raise_for_status()

    # Send top stories (chunked if huge)
    top_text = "\n".join(top_lines)
    for chunk in [top_text[i:i+3800] for i in range(0, len(top_text), 3800)]:
        post(chunk)

    # Send also-scraped as second message
    post("\n".join(skip_lines))

    log.info("Daily Slack summary sent (%d keepers)", len(kept))


def deliver(digest: dict):
    try:
        send_slack_all_variants(digest)
    except Exception as e:
        log.error("Slack delivery failed: %s", e)


def maybe_send_keepalive_reminder(stories: list):
    """Every 6 weeks, remind in Slack to keep the GitHub Actions workflow alive."""
    import datetime
    today = datetime.date.today()
    # Week 1 and week 7 of the year, roughly every 6 weeks
    if today.isocalendar()[1] % 6 == 0 and today.weekday() == 0:
        webhook = __import__("os").environ.get("SLACK_WEBHOOK_URL", "")
        if webhook:
            __import__("requests").post(webhook, json={"text": ":warning: *Heads up:* GitHub disables scheduled Actions after 60 days of repo inactivity. If the bot stops posting, go to github.com/taliakusmirek/NooksGrowthBot/actions and re-enable the workflow."}, timeout=10)
