"""
Entry point. Usage:
  python main.py --daily        collect + score + send to Slack
  python main.py --schedule     run as 24/7 scheduler (default)
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import schedule

from collector import collect_all
from scorer import score_stories
from delivery import send_slack_daily

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s -- %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / "logs" / "bot.log"),
    ],
)
log = logging.getLogger("main")


def daily_job():
    log.info("=== Daily collection + scoring ===")
    try:
        stories = collect_all()
        log.info("Collected %d new stories", len(stories))
        scored = score_stories(stories)
        log.info("Scored %d stories", len(scored))
        send_slack_daily(scored)
        log.info("Daily job complete")
    except Exception as e:
        log.exception("Daily job failed: %s", e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", action="store_true")
    parser.add_argument("--schedule", action="store_true")
    args = parser.parse_args()

    if args.daily:
        daily_job()
    if not any([args.daily, args.schedule]):
        args.schedule = True
    if args.schedule:
        schedule.every().monday.at("16:00").do(daily_job)
        schedule.every().tuesday.at("16:00").do(daily_job)
        schedule.every().wednesday.at("16:00").do(daily_job)
        schedule.every().thursday.at("16:00").do(daily_job)
        schedule.every().friday.at("16:00").do(daily_job)
        log.info("Scheduler running: daily Mon-Fri 16:00 UTC (8am PST)")
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()
