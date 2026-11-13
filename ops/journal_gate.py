#!/usr/bin/env python3
"""patchland journal gate — one post a day at a random afternoon time (KST).

launchd calls this every 15 minutes (12:00-18:45 KST). State: ~/.ipe/queue/patchland/slot.json
  {"date","time","prev_date","prev_time","published"}
- new day -> draw today's time in 12:00-17:59, never the same hour as yesterday's; yesterday moves to prev_*
- now >= time and not published -> run the publisher; published=true only if it succeeds
Clock, RNG, publisher are injectable (see ops/test_journal_gate.py).
Tests: python3 -m unittest discover -s ops -p 'test_*.py' -q   (wired into scripts/check.sh)
"""
import json, os, random, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
QUEUE_DIR = Path(os.environ.get("PATCHLAND_QUEUE", Path.home() / ".ipe/queue/patchland"))
HOURS = range(12, 18)  # 12:00-17:59


def now_kst():
    return datetime.now(KST)


def draw_time(rng, prev_time=None):
    prev_hour = int(prev_time.split(":")[0]) if prev_time else None
    hours = [h for h in HOURS if h != prev_hour]
    return "%02d:%02d" % (rng.choice(hours), rng.randrange(60))


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def save(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, path)


def run_publisher():
    here = Path(__file__).resolve().parent
    return subprocess.run([sys.executable, str(here / "journal_publish.py")]).returncode == 0


def tick(state_path=None, clock=now_kst, rng=None, publisher=run_publisher, log=print):
    state_path = state_path or QUEUE_DIR / "slot.json"
    rng = rng or random.SystemRandom()
    now = clock()
    today = now.strftime("%Y-%m-%d")
    st = load(state_path)
    if st.get("date") != today:
        st = {"date": today, "time": draw_time(rng, st.get("time")),
              "prev_date": st.get("date"), "prev_time": st.get("time"), "published": False}
        save(state_path, st)
        log("new slot %s %s (prev %s %s)" % (today, st["time"], st["prev_date"], st["prev_time"]))
    if st.get("published"):
        return "already-published"
    if now.strftime("%H:%M") < st["time"]:
        return "not-yet"
    ok = False
    try:
        ok = bool(publisher())
    except Exception as e:  # publisher failure must never mark published
        log("publisher raised: %r" % e)
    if ok:
        st["published"] = True
        save(state_path, st)
        log("published %s" % today)
        return "published"
    log("publish failed — will retry next tick")
    return "failed"


if __name__ == "__main__":
    print(datetime.now(KST).strftime("%F %T KST"), tick())
