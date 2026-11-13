#!/usr/bin/env python3
"""Publish the first queued journal post: ~/.ipe/queue/patchland/*.md (filename order).

Moves it to content/journal/YYYY-MM-DD-<slug>.md in the publish clone with front matter `date:` set to
today (KST), builds, runs scripts/check.sh, then commit "journal: <slug>" -> pull --rebase -> push.
Clone: ~/ipe/patchland-publish (cloned from origin if missing; dirty tree -> SKIP, exit 1).
Empty queue -> log + ALERT file, exit 1. Queue <= 2 posts after publishing -> ALERT file too.
"""
import os, re, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
QUEUE = Path(os.environ.get("PATCHLAND_QUEUE", Path.home() / ".ipe/queue/patchland"))
CLONE = Path(os.environ.get("PATCHLAND_CLONE", Path.home() / "ipe/patchland-publish"))
REMOTE = os.environ.get("PATCHLAND_REMOTE", "https://github.com/blessu76/patchland-rest.git")
LOW_WATER = 2


def log(msg):
    print(datetime.now(KST).strftime("%F %T KST"), msg, flush=True)


def queued():
    return sorted(p for p in QUEUE.glob("*.md") if p.is_file())


def alert(msg):
    QUEUE.mkdir(parents=True, exist_ok=True)
    (QUEUE / "ALERT").write_text("%s %s\n" % (datetime.now(KST).strftime("%F %T KST"), msg))
    log("ALERT: " + msg)


def slugify(name):
    s = Path(name).stem
    s = re.sub(r"^(\d{4}-\d{2}-\d{2}-|\d+[-_])", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "post"


def set_date(text, date):
    """Set/insert `date:` in the YAML front matter (adds a front matter block if none)."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return "---\ndate: %s\n---\n%s" % (date, text)
    fm = m.group(1)
    if re.search(r"^date:.*$", fm, re.M):
        fm = re.sub(r"^date:.*$", "date: %s" % date, fm, flags=re.M)
    else:
        fm += "\ndate: %s" % date
    return "---\n%s\n---\n%s" % (fm, text[m.end():])


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(CLONE), *a], check=check, capture_output=True, text=True)


def main():
    posts = queued()
    if not posts:
        alert("queue is empty — nothing to publish")
        return 1
    if not (CLONE / ".git").is_dir():
        CLONE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--quiet", REMOTE, str(CLONE)], check=True)
    if git("status", "--porcelain").stdout.strip():
        log("SKIP: publish clone has uncommitted changes")
        return 1
    git("pull", "--rebase", "--quiet")
    src = posts[0]
    today = datetime.now(KST).strftime("%Y-%m-%d")
    slug = slugify(src.name)
    dest = CLONE / "content/journal" / ("%s-%s.md" % (today, slug))
    dest.parent.mkdir(parents=True, exist_ok=True)

    def rollback():
        git("reset", "--hard", "--quiet", "HEAD")
        git("clean", "-fdq", "content", "en", "ko", "ja", "zh", "es", "pt", "id", "ru", "vi", "fr", "de", "journal", "sitemap.xml", "llms.txt", check=False)

    dest.write_text(set_date(src.read_text(), today))
    for cmd in (["python3", "scripts/build_site.py"], ["bash", "scripts/check.sh"]):
        r = subprocess.run(cmd, cwd=CLONE, capture_output=True, text=True)
        if r.returncode:
            log("FAIL %s:\n%s" % (" ".join(cmd), (r.stdout + r.stderr)[-1500:]))
            rollback()
            return 1
    try:
        git("add", "-A")
        git("commit", "-q", "-m", "journal: %s" % slug)
        git("pull", "--rebase", "--quiet")
        git("push", "--quiet")
    except subprocess.CalledProcessError as e:
        log("FAIL git: %s" % (e.stderr or e))
        return 1
    src.unlink()  # only after the push succeeded: a failure leaves the post queued for retry
    log("published %s" % dest.name)
    left = len(queued())
    if left <= LOW_WATER:
        alert("queue low: %d post(s) left" % left)
    return 0


if __name__ == "__main__":
    sys.exit(main())
