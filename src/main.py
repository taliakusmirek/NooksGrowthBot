"""
Entry point. Usage:
  python main.py --daily        collect + score
  python main.py --friday       build + deliver digest
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
from scorer import run_daily_scoring
from digest import run_friday_digest
from delivery import deliver

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
        run_daily_scoring()
        log.info("Daily job complete")
    except Exception as e:
        log.exception("Daily job failed: %s", e)


def friday_job():
    log.info("=== Friday digest build + delivery ===")
    try:
        digest = run_friday_digest()
        deliver(digest)
        log.info("Friday digest delivered")
    except Exception as e:
        log.exception("Friday job failed: %s", e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", action="store_true")
    parser.add_argument("--friday", action="store_true")
    parser.add_argument("--schedule", action="store_true")
    args = parser.parse_args()

    if args.daily:
        daily_job()
    if args.friday:
        friday_job()
    if not any([args.daily, args.friday, args.schedule]):
        args.schedule = True
    if args.schedule:
        schedule.every().day.at("08:00").do(daily_job)
        schedule.every().friday.at("14:00").do(friday_job)
        log.info("Scheduler running: daily 08:00 UTC, Friday digest 14:00 UTC")
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()
