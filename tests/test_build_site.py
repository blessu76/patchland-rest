import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_site as bs  # noqa: E402


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bs.Ctx(str(ROOT))
        cls.files = bs.build_all(cls.ctx) if not cls.ctx.errs else {}

    def test_sources_valid(self):
        self.assertEqual(self.ctx.errs, [])

    def test_all_languages(self):
        self.assertEqual(sorted(self.ctx.langs), sorted(bs.LANGS))
        self.assertEqual(len(bs.LANGS), 11)

    def test_every_page_exists(self):
        for l in bs.LANGS:
            self.assertIn(("index.html" if l == "en" else l + "/index.html"), self.files)
            for s in bs.PAGE_SLUGS + (bs.RELEASES,):
                self.assertIn(bs.path_page(l, s).strip("/") + "/index.html", self.files)

    def test_releases_linked_from_every_home_and_complete(self):
        self.assertGreaterEqual(len(self.ctx.releases), 6)
        for l in bs.LANGS:
            home = self.files["index.html" if l == "en" else l + "/index.html"]
            self.assertIn('href="%s"' % bs.path_releases(l), home, l)
            page = self.files[bs.path_releases(l).strip("/") + "/index.html"]
            for e in self.ctx.releases:
                self.assertIn('id="%s"' % e["id"], page, l)

    def test_translations_have_ai_notice_and_hreflang(self):
        for l in bs.LANGS:
            h = self.files["index.html" if l == "en" else l + "/index.html"]
            self.assertEqual("ai-note" in h, l not in bs.ORIGINALS, l)
            self.assertIn('hreflang="x-default"', h)
            self.assertEqual(h.count('rel="alternate" hreflang="'), 12, l)

    def test_no_forbidden_claims(self):
        for f, t in self.files.items():
            if f.endswith(".html"):
                self.assertIsNone(re.search(r"\$\s?\d|★", t), f)
                self.assertNotIn("UA-", t)
                self.assertNotIn("googletagmanager", t)

    def test_asset_cache_busting(self):
        self.assertIn("?v=" + bs.ASSET_V, self.files["index.html"])

    def test_sitemap_urls(self):
        self.assertEqual(self.files["sitemap.xml"].count("<url>"), 11 * 5)


if __name__ == "__main__":
    unittest.main()
