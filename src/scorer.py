"""
Scores raw stories using Groq (free tier, llama-3.3-70b).
"""

import json
import logging
import os
from pathlib import Path

from openai import OpenAI

log = logging.getLogger(__name__)

INBOX_FILE = Path(__file__).parent.parent / "data" / "trend_inbox.json"
SCORED_FILE = Path(__file__).parent.parent / "data" / "scored_inbox.json"

MODEL = "llama-3.3-70b-versatile"

SCORING_PROMPT = """\
You are the editor of "The Week, According to Nooks" — a weekly content roundup published
by Nooks (an AI-powered sales dialer / revenue intelligence startup).

Your job is to triage a batch of news stories and decide which are worth keeping.
The ideal mix is: AI/startup moments, Nooks product/customer wins, GTM/sales trends,
weird internet / culture moments.

Avoid: politics, tragedy, overly negative stories, anything risky for a B2B company account.

For each story below, respond with a JSON array. Each object must have exactly these fields:
- id: the story id (copy from input, do not change)
- keep: true or false
- why_it_matters: one plain sentence (omit if keep=false)
- virality_signal: one word or short phrase (omit if keep=false)
- nooks_angle: one sentence tying this to Nooks' world (omit if keep=false)
- scores: object with integer fields surprise, relevance, cultural, nooks_angle, shareability (each 1-5; omit if keep=false)

Respond with ONLY valid JSON — no markdown fences, no explanation.

STORIES:
{stories_json}
"""


def _groq_client():
    return OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
        max_retries=0,
    )


def _chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def score_stories(stories):
    if not stories:
        return []
    client = _groq_client()
    scored = []
    for batch in _chunk(stories, 20):
        minimal = [{"id": s["id"], "headline": s["headline"], "source": s["source"],
                    "category": s["category"], "summary": s["summary"]} for s in batch]
        prompt = SCORING_PROMPT.format(stories_json=json.dumps(minimal, indent=2))
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.2,
            )
            raw = resp.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            results = json.loads(raw)
        except Exception as e:
            log.error("Scoring batch failed: %s", e)
            results = []
        result_by_id = {r["id"]: r for r in results}
        for story in batch:
            enrichment = result_by_id.get(story["id"], {})
            story.update({
                "keep": enrichment.get("keep", False),
                "why_it_matters": enrichment.get("why_it_matters", ""),
                "virality_signal": enrichment.get("virality_signal", ""),
                "nooks_angle": enrichment.get("nooks_angle", ""),
                "scores": enrichment.get("scores", {}),
            })
            scored.append(story)
        log.info("Scored batch of %d", len(batch))
    return scored


def load_unscored() -> list[dict]:
    if not INBOX_FILE.exists():
        return []
    stories = json.loads(INBOX_FILE.read_text())
    already_scored = set()
    if SCORED_FILE.exists():
        already_scored = {s["id"] for s in json.loads(SCORED_FILE.read_text())}
    return [s for s in stories if s.get("keep") is None and s["id"] not in already_scored]


def save_scored(stories):
    SCORED_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if SCORED_FILE.exists():
        existing = json.loads(SCORED_FILE.read_text())
    id_set = {s["id"] for s in existing}
    new = [s for s in stories if s["id"] not in id_set]
    existing.extend(new)
    SCORED_FILE.write_text(json.dumps(existing, indent=2))
    log.info("Saved %d scored stories (total %d)", len(new), len(existing))


def run_daily_scoring():
    unscored = load_unscored()
    if not unscored:
        log.info("No new stories to score")
        return
    log.info("Scoring %d stories...", len(unscored))
    scored = score_stories(unscored)
    save_scored(scored)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_daily_scoring()
