import json, random, tempfile, unittest
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import journal_gate as g


def at(d, hm):
    return datetime.fromisoformat("%sT%s:00+09:00" % (d, hm))


class Gate(unittest.TestCase):
    def setUp(self):
        self.p = Path(tempfile.mkdtemp()) / "slot.json"
        self.calls = 0

    def pub(self, ok=True):
        def f():
            self.calls += 1
            return ok
        return f

    def st(self):
        return json.loads(self.p.read_text())

    def test_never_same_hour_as_yesterday(self):
        for seed in range(300):
            prev = "%02d:%02d" % (12 + seed % 6, seed % 60)
            self.p.write_text(json.dumps({"date": "2026-11-12", "time": prev, "published": True}))
            g.tick(self.p, lambda: at("2026-11-13", "00:01"), random.Random(seed), self.pub(), lambda m: None)
            s = self.st()
            self.assertNotEqual(s["time"][:2], prev[:2])
            self.assertTrue("12:00" <= s["time"] <= "17:45")
            self.assertEqual((s["prev_date"], s["prev_time"], s["published"]), ("2026-11-12", prev, False))

    def test_first_run_creates_slot(self):
        g.tick(self.p, lambda: at("2026-11-13", "09:00"), random.Random(1), self.pub(), lambda m: None)
        s = self.st()
        self.assertEqual(s["date"], "2026-11-13")
        self.assertIsNone(s["prev_time"])

    def test_before_time_no_publish(self):
        self.p.write_text(json.dumps({"date": "2026-11-13", "time": "15:30", "published": False}))
        r = g.tick(self.p, lambda: at("2026-11-13", "15:29"), None, self.pub(), lambda m: None)
        self.assertEqual((r, self.calls), ("not-yet", 0))

    def test_publish_at_time_then_ignored(self):
        self.p.write_text(json.dumps({"date": "2026-11-13", "time": "15:30", "published": False}))
        r = g.tick(self.p, lambda: at("2026-11-13", "15:30"), None, self.pub(), lambda m: None)
        self.assertEqual((r, self.calls, self.st()["published"]), ("published", 1, True))
        r = g.tick(self.p, lambda: at("2026-11-13", "16:00"), None, self.pub(), lambda m: None)
        self.assertEqual((r, self.calls), ("already-published", 1))

    def test_failure_keeps_unpublished(self):
        self.p.write_text(json.dumps({"date": "2026-11-13", "time": "13:00", "published": False}))
        r = g.tick(self.p, lambda: at("2026-11-13", "14:00"), None, self.pub(False), lambda m: None)
        self.assertEqual((r, self.st()["published"]), ("failed", False))

        def boom():
            raise RuntimeError("x")
        r = g.tick(self.p, lambda: at("2026-11-13", "14:15"), None, boom, lambda m: None)
        self.assertEqual((r, self.st()["published"]), ("failed", False))

    def test_failure_at_1745_retried_at_1759_publishes(self):
        self.p.write_text(json.dumps({"date": "2026-11-13", "time": "17:30", "published": False}))
        r = g.tick(self.p, lambda: at("2026-11-13", "17:45"), None, self.pub(False), lambda m: None)
        self.assertEqual((r, self.calls, self.st()["published"]), ("failed", 1, False))
        r = g.tick(self.p, lambda: at("2026-11-13", "17:59"), None, self.pub(True), lambda m: None)
        self.assertEqual((r, self.calls, self.st()["published"]), ("published", 2, True))

    def test_closed_at_1800_and_1845_without_calling_publisher(self):
        for hm in ("18:00", "18:45"):
            self.p.write_text(json.dumps({"date": "2026-11-13", "time": "17:30", "published": False}))
            r = g.tick(self.p, lambda: at("2026-11-13", hm), None, self.pub(True), lambda m: None)
            self.assertEqual((r, self.calls, self.st()["published"]), ("closed", 0, False), hm)

    def test_failure_then_1800_is_closed_not_retried(self):
        self.p.write_text(json.dumps({"date": "2026-11-13", "time": "17:30", "published": False}))
        g.tick(self.p, lambda: at("2026-11-13", "17:59"), None, self.pub(False), lambda m: None)
        r = g.tick(self.p, lambda: at("2026-11-13", "18:00"), None, self.pub(True), lambda m: None)
        self.assertEqual((r, self.calls, self.st()["published"]), ("closed", 1, False))

    def test_next_day_opens_a_new_slot_after_closed(self):
        self.p.write_text(json.dumps({"date": "2026-11-13", "time": "17:30", "published": False}))
        g.tick(self.p, lambda: at("2026-11-13", "18:45"), None, self.pub(True), lambda m: None)
        r = g.tick(self.p, lambda: at("2026-11-14", "12:00"), random.Random(3), self.pub(True), lambda m: None)
        s = self.st()
        self.assertEqual((s["date"], s["prev_date"], s["published"]), ("2026-11-14", "2026-11-13", False))
        self.assertTrue("12:00" <= s["time"] <= "17:45")
        self.assertEqual(r, "not-yet" if s["time"] > "12:00" else "published")
        self.assertEqual(self.calls, 1 if r == "published" else 0)

    def test_plist_ticks_end_at_1745_and_none_after_close(self):
        import plistlib
        with open(Path(__file__).parent / "com.ipe.patchland.journal.plist", "rb") as f:
            ticks = ["%02d:%02d" % (d["Hour"], d["Minute"]) for d in plistlib.load(f)["StartCalendarInterval"]]
        self.assertEqual(max(ticks), "17:45")
        self.assertTrue(all(t < g.CLOSE for t in ticks))
        self.assertEqual(sorted(ticks), ticks)


class Publish(unittest.TestCase):
    def test_set_date_and_slug(self):
        import journal_publish as j
        self.assertEqual(j.set_date("---\ntitle: a\ndate: x\n---\nbody", "2026-11-13"), "---\ntitle: a\ndate: 2026-11-13\n---\nbody")
        self.assertEqual(j.set_date("---\ntitle: a\n---\nb", "D"), "---\ntitle: a\ndate: D\n---\nb")
        self.assertTrue(j.set_date("plain", "D").startswith("---\ndate: D\n---\n"))
        self.assertEqual(j.slugify("03-Why_Mint & Sky.md"), "why-mint-sky")
        self.assertEqual(j.set_date("---\ncopy_review: iris 2026-11-14\ndate: x\n---\nb", "D"), "---\ncopy_review: iris 2026-11-14\ndate: D\n---\nb")

    def test_publish_stamps_published_at_with_kst_offset(self):
        import journal_publish as j
        stamp = j.published_stamp()
        self.assertRegex(stamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00$")
        out = j.set_key("---\ntitle: a\ndate: 2026-11-19\n---\nb", "published_at", "2026-11-19T19:24:57+09:00")
        self.assertEqual(out, "---\ntitle: a\ndate: 2026-11-19\npublished_at: 2026-11-19T19:24:57+09:00\n---\nb")
        again = j.set_key(out, "published_at", "2026-11-20T08:00:00+09:00")
        self.assertEqual(again.count("published_at:"), 1)
        self.assertIn("published_at: 2026-11-20T08:00:00+09:00", again)

    def test_copy_review_format(self):
        import journal_publish as j
        ok = "---\ntitle: a\ncopy_review: iris 2026-11-14\n---\nb"
        self.assertTrue(j.copy_reviewed(ok))
        self.assertTrue(j.copy_reviewed('---\ncopy_review: "iris 2026-11-14"\n---\nb'))
        for bad in ("copy_review: iris 2026-1-14", "copy_review: Iris 2026-11-14", "copy_review: iris", "copy_review: iris 2026-11-14 x",
                    "copy_review: 2026-11-14", "title: a"):
            self.assertFalse(j.copy_reviewed("---\n%s\n---\nb" % bad), bad)
        self.assertFalse(j.copy_reviewed("no front matter, copy_review: iris 2026-11-14"))

    def test_queued_skips_unreviewed_and_keeps_order(self):
        import journal_publish as j
        from unittest import mock
        q = Path(tempfile.mkdtemp())
        (q / "00-draft.md").write_text("---\ntitle: a\n---\nb")
        (q / "01-ok.md").write_text("---\ncopy_review: iris 2026-11-14\n---\nb")
        (q / "02-ok.md").write_text("---\ncopy_review: iris 2026-11-15\n---\nb")
        j.QUEUE = q
        with mock.patch.object(j, "log") as log:
            self.assertEqual([p.name for p in j.queued()], ["01-ok.md", "02-ok.md"])
        log.assert_called_once_with("SKIP unreviewed: 00-draft.md")

    def test_all_unreviewed_alerts(self):
        import journal_publish as j
        q = Path(tempfile.mkdtemp())
        (q / "00-draft.md").write_text("---\ntitle: a\n---\nb")
        j.QUEUE = q
        self.assertEqual(j.main(), 1)
        self.assertIn("no copy-reviewed post in queue", (q / "ALERT").read_text())


class PublishFlow(unittest.TestCase):
    """End to end against a throwaway origin: build output (sitemap, feed) must land in the journal commit."""

    def sh(self, cwd, *a):
        import subprocess
        return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout

    def origin(self, t, extra=None):
        origin, seed = t / "origin.git", t / "seed"
        self.sh(t, "git", "init", "-q", "--bare", "-b", "main", str(origin))
        seed.mkdir()
        (seed / "scripts").mkdir()
        (seed / "scripts/build_site.py").write_text(
            "import pathlib\n"
            "posts = sorted(p.stem for p in pathlib.Path('content/journal').glob('*.md'))\n"
            "pathlib.Path('sitemap.xml').write_text(''.join('/journal/%s/\\n' % x for x in posts))\n"
            "pathlib.Path('journal').mkdir(exist_ok=True)\n"
            "pathlib.Path('journal/feed.xml').write_text(''.join('<entry>%s</entry>' % x for x in posts))\n")
        (seed / "scripts/check.sh").write_text("exit 0\n")
        (seed / "sitemap.xml").write_text("")
        for name, text in (extra or {}).items():
            (seed / name).parent.mkdir(parents=True, exist_ok=True)
            (seed / name).write_text(text)
        for c in (("init", "-q", "-b", "main"), ("add", "-A"), ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"),
                  ("remote", "add", "origin", str(origin)), ("push", "-q", "origin", "main")):
            self.sh(seed, "git", *c)
        return origin

    def test_sitemap_and_feed_are_committed(self):
        import journal_publish as j
        t = Path(tempfile.mkdtemp())
        origin = self.origin(t)
        q = t / "queue"
        q.mkdir()
        (q / "00-draft.md").write_text("---\ntitle: Draft\n---\nbody\n")
        (q / "01-hello-world.md").write_text("---\ntitle: Hi\ncopy_review: iris 2026-11-14\n---\nbody\n")
        j.QUEUE, j.CLONE, j.REMOTE = q, t / "clone", str(origin)
        self.assertEqual(j.main(), 0)
        changed = self.sh(origin, "git", "show", "--name-only", "--format=%s", "main").split("\n")
        self.assertEqual(changed[0].strip(), "journal: hello-world")
        slug = [f for f in changed if f.startswith("content/journal/")][0]
        self.assertTrue(slug.endswith("-hello-world.md"))
        self.assertIn("copy_review: iris 2026-11-14", self.sh(origin, "git", "show", "main:" + slug))
        self.assertIn("sitemap.xml", changed)
        self.assertIn("journal/feed.xml", changed)
        self.assertFalse((q / "01-hello-world.md").exists())
        self.assertTrue((q / "00-draft.md").exists())
        self.assertTrue((q / "ALERT").exists())  # 0 reviewed left <= 2

    def test_reviewed_translations_move_with_the_post(self):
        import journal_publish as j
        from datetime import datetime
        t = Path(tempfile.mkdtemp())
        reviewed = "---\ntitle: Hallo\ndate: TBD\ncopy_review: iris 2026-11-14\n---\nbody\n"
        origin = self.origin(t, {
            "content/journal_i18n/de/01-hello-world.md": reviewed,
            "content/journal_i18n/fr/01-hello-world.md": "---\ntitle: Bonjour\ndate: TBD\n---\nbody\n",
        })
        q = t / "queue"
        q.mkdir()
        (q / "01-hello-world.md").write_text("---\ntitle: Hi\ncopy_review: iris 2026-11-14\n---\nbody\n")
        j.QUEUE, j.CLONE, j.REMOTE = q, t / "clone", str(origin)
        self.assertEqual(j.main(), 0)
        today = datetime.now(j.KST).strftime("%Y-%m-%d")
        files = self.sh(origin, "git", "ls-tree", "-r", "--name-only", "main").split("\n")
        self.assertIn("content/journal_i18n/de/%s-hello-world.md" % today, files)
        self.assertNotIn("content/journal_i18n/de/01-hello-world.md", files)
        self.assertIn("content/journal_i18n/fr/01-hello-world.md", files)
        self.assertNotIn("content/journal_i18n/fr/%s-hello-world.md" % today, files)
        moved = self.sh(origin, "git", "show", "main:content/journal_i18n/de/%s-hello-world.md" % today)
        self.assertIn("date: %s" % today, moved)
        self.assertIn("copy_review: iris 2026-11-14", moved)


class DryRun(unittest.TestCase):
    """--dry-run: the whole publish runs in a throwaway clone; origin, queue, real clone and ALERT stay untouched."""
    sh = PublishFlow.sh

    def test_dry_run_changes_nothing_real(self):
        import journal_publish as j
        t = Path(tempfile.mkdtemp())
        origin = PublishFlow.origin(self, t)
        real = t / "clone"
        self.sh(t, "git", "clone", "-q", str(origin), str(real))
        q = t / "queue"
        q.mkdir()
        (q / "01-hello-world.md").write_text("---\ntitle: Hi\ncopy_review: iris 2026-11-14\n---\nbody\n")
        j.QUEUE, j.CLONE, j.REMOTE = q, real, str(origin)
        before = self.sh(origin, "git", "rev-parse", "main").strip()
        self.assertEqual(j.main(dry_run=True), 0)
        self.assertEqual(self.sh(origin, "git", "rev-parse", "main").strip(), before)
        self.assertTrue((q / "01-hello-world.md").exists())
        self.assertFalse((q / "ALERT").exists())
        self.assertEqual(self.sh(real, "git", "status", "--porcelain").strip(), "")
        self.assertEqual(list((real / "content/journal").glob("*.md")), [])
        self.assertEqual(j.CLONE, real)  # restored after the dry run
        self.assertFalse(j.DRY_RUN)


if __name__ == "__main__":
    unittest.main()
