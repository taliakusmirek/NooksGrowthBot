"""
Friday digest builder -- three tone variants via Claude.
"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic

log = logging.getLogger(__name__)

SCORED_FILE = Path(__file__).parent.parent / "data" / "scored_inbox.json"
DIGEST_FILE = Path(__file__).parent.parent / "data" / "weekly_digest.json"
ARCHIVE_FILE = Path(__file__).parent.parent / "data" / "digest_archive.json"

DIGEST_PROMPT = """\
You are the editor of "The Week, According to Nooks" -- a weekly LinkedIn / social roundup
published by Nooks (an AI-powered sales dialer / revenue intelligence startup).

Writing rules (non-negotiable):
- Every bullet: short, specific, slightly opinionated. No explanations. No corporate tone.
- BAD: "Nooks continued seeing strong AI Dialer adoption."
  GOOD: "Nooks hit record daily AI Dialer users."
- BAD: "Apple announced plans to develop camera-enabled AirPods."
  GOOD: "Apple is planning camera-equipped AirPods. Sure."
- No bullet should exceed 15 words.

Target structure (10 bullets, this order):
1. AI/startup moment
2. Nooks product milestone
3. Weird internet / culture moment
4. AI/startup product launch
5. Nooks community / customer moment
6. Nooks shipped feature
7. Sports / pop culture moment
8. Weird science / internet moment
9. GTM / startup moment
10. Nooks closer (product or customer)

Closing line (always): "and it's not even end of quarter yet 💜"

Produce all three variants labeled exactly as shown:

=== SAFE ===
Professional but warm.

=== FUNNY ===
Dry wit. Light sarcasm.

=== SPICY ===
Takes a stance. Slightly edgy. Still safe for B2B.

---
Top keeper stories this week:

{stories_json}

Pick the 10 best. Mark any slot with no good match as [PLACEHOLDER -- needs real data].

Return format:

=== SAFE ===
the week, according to Nooks:

> ...
(10 bullets)

and it's not even end of quarter yet 💜

=== FUNNY ===
the week, according to Nooks:

> ...

and it's not even end of quarter yet 💜

=== SPICY ===
the week, according to Nooks:

> ...

and it's not even end of quarter yet 💜
"""


def _week_cutoff():
    return datetime.now(timezone.utc) - timedelta(days=7)


def load_keepers():
    if not SCORED_FILE.exists():
        return []
    stories = json.loads(SCORED_FILE.read_text())
    cutoff = _week_cutoff()
    keepers = []
    for s in stories:
        if not s.get("keep"):
            continue
        try:
            pub = datetime.strptime(s["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            pub = datetime.now(timezone.utc)
        if pub >= cutoff:
            keepers.append(s)
    keepers.sort(key=lambda s: sum(s.get("scores", {}).values()), reverse=True)
    return keepers


def build_digest(keepers):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    minimal = [
        {
            "headline": s["headline"],
            "source": s["source"],
            "category": s["category"],
            "why_it_matters": s.get("why_it_matters", ""),
            "nooks_angle": s.get("nooks_angle", ""),
            "virality_signal": s.get("virality_signal", ""),
            "scores": s.get("scores", {}),
        }
        for s in keepers[:40]
    ]
    prompt = DIGEST_PROMPT.format(stories_json=json.dumps(minimal, indent=2))
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()

    def extract_variant(label):
        marker = f"=== {label} ==="
        start = raw.find(marker)
        if start == -1:
            return ""
        start += len(marker)
        next_marker = raw.find("===", start)
        chunk = raw[start:next_marker].strip() if next_marker != -1 else raw[start:].strip()
        return chunk

    return {
        "week_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "safe": extract_variant("SAFE"),
        "funny": extract_variant("FUNNY"),
        "spicy": extract_variant("SPICY"),
        "story_count": len(keepers),
    }


def save_digest(digest):
    DIGEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    DIGEST_FILE.write_text(json.dumps(digest, indent=2))
    archive = []
    if ARCHIVE_FILE.exists():
        archive = json.loads(ARCHIVE_FILE.read_text())
    archive.append(digest)
    ARCHIVE_FILE.write_text(json.dumps(archive, indent=2))
    log.info("Digest saved (week of %s)", digest["week_of"])


def run_friday_digest():
    keepers = load_keepers()
    log.info("Building digest from %d keeper stories", len(keepers))
    digest = build_digest(keepers)
    save_digest(digest)
    return digest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    d = run_friday_digest()
    print("\n=== SAFE ===\n", d["safe"])
    print("\n=== FUNNY ===\n", d["funny"])
    print("\n=== SPICY ===\n", d["spicy"])
