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
            self.assertTrue("12:00" <= s["time"] <= "17:59")
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


class Publish(unittest.TestCase):
    def test_set_date_and_slug(self):
        import journal_publish as j
        self.assertEqual(j.set_date("---\ntitle: a\ndate: x\n---\nbody", "2026-11-13"), "---\ntitle: a\ndate: 2026-11-13\n---\nbody")
        self.assertEqual(j.set_date("---\ntitle: a\n---\nb", "D"), "---\ntitle: a\ndate: D\n---\nb")
        self.assertTrue(j.set_date("plain", "D").startswith("---\ndate: D\n---\n"))
        self.assertEqual(j.slugify("03-Why_Mint & Sky.md"), "why-mint-sky")
        self.assertEqual(j.set_date("---\ncopy_review: iris 2026-11-14\ndate: x\n---\nb", "D"), "---\ncopy_review: iris 2026-11-14\ndate: D\n---\nb")

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


if __name__ == "__main__":
    unittest.main()
