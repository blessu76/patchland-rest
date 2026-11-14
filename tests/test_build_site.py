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

    def test_journal_requires_copy_review(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        (root / "content" / "journal").mkdir(parents=True)
        base = "---\ntitle: a\ntitle_en: a\nsummary: s\nsummary_en: s\ndate: 2026-11-14\n%s---\nk\n\n## EN\n\ne\n"
        (root / "content" / "journal" / "2026-11-14-x.md").write_text(base % "")
        self.assertTrue(any("copy_review" in e for e in bs.Ctx(str(root)).errs))
        for bad in ("copy_review: iris 2026-1-14\n", "copy_review: Iris 2026-11-14\n", "copy_review: iris\n"):
            (root / "content" / "journal" / "2026-11-14-x.md").write_text(base % bad)
            self.assertTrue(any("copy_review" in e for e in bs.Ctx(str(root)).errs), bad)
        (root / "content" / "journal" / "2026-11-14-x.md").write_text(base % "copy_review: iris 2026-11-14\n")
        self.assertEqual(bs.Ctx(str(root)).errs, [])

    def test_all_languages(self):
        self.assertEqual(sorted(self.ctx.langs), sorted(bs.languages.SUPPORTED))
        self.assertEqual(len(bs.languages.SUPPORTED), 12)

    def test_every_page_exists(self):
        for l in bs.languages.SUPPORTED:
            self.assertIn(("index.html" if l == "en" else l + "/index.html"), self.files)
            for s in bs.PAGE_SLUGS + (bs.JOURNAL,):
                self.assertIn(bs.path_page(l, s).strip("/") + "/index.html", self.files)

    def test_translations_have_ai_notice_and_hreflang(self):
        for l in bs.languages.SUPPORTED:
            h = self.files["index.html" if l == "en" else l + "/index.html"]
            self.assertEqual("ai-note" in h, l not in bs.ORIGINALS, l)
            self.assertIn('hreflang="x-default"', h)
            self.assertEqual(h.count('rel="alternate" hreflang="'), 13, l)

    def test_no_forbidden_claims(self):
        for f, t in self.files.items():
            if f.endswith(".html"):
                self.assertIsNone(re.search(r"\$\s?\d|★", t), f)
                self.assertNotIn("UA-", t)
                self.assertNotIn("googletagmanager", t)

    def test_asset_cache_busting(self):
        self.assertIn("?v=" + bs.ASSET_V, self.files["index.html"])

    def all_page_paths(self, l):
        paths = [bs.path_home(l), bs.path_journal(l)]
        paths += [bs.path_page(l, s) for s in bs.PAGE_SLUGS]
        paths += [bs.path_article(l, a["slug"]) for a in self.ctx.journal]
        return [(p.strip("/") + "/index.html") if p != "/" else "index.html" for p in paths]

    def test_legal_links_in_footer_not_nav(self):
        for l in bs.languages.SUPPORTED:
            for f in self.all_page_paths(l):
                h = self.files[f]
                nav = re.search(r'<nav class="nav".*?</nav>', h, re.S).group(0)
                self.assertNotIn("/privacy/", nav, f)
                self.assertNotIn("/terms/", nav, f)
                foot = re.search(r'<footer class="site-footer".*?</footer>', h, re.S).group(0)
                self.assertIn('href="%s"' % bs.path_page(l, "privacy"), foot, f)
                self.assertIn('href="%s"' % bs.path_page(l, "terms"), foot, f)

    def test_language_select_on_every_page(self):
        for l in bs.languages.SUPPORTED:
            for f in self.all_page_paths(l):
                h = self.files[f]
                self.assertNotIn("langsw", h, f)
                self.assertEqual(h.count("<select "), 1, f)
                foot = re.search(r'<footer class="site-footer".*?</footer>', h, re.S).group(0)
                opts = re.findall(r'<option value="([^"]+)"( selected)?>', foot)
                self.assertEqual(len(opts), 12, f)
                selected = [v for v, s in opts if s]
                self.assertEqual(len(selected), 1, f)
                self.assertEqual(len(set(v for v, _ in opts)), 12, f)
                links = re.findall(r'<noscript><span class="lang-links">(.*?)</span></noscript>', foot, re.S)
                self.assertEqual(len(links), 1, f)
                self.assertEqual(links[0].count("<a "), 12, f)
                self.assertIn('hidden><label for="langsel">', foot, f)

    def test_language_select_pill_style_keeps_label_for_screen_readers(self):
        css = (ROOT / "assets" / "patchland.css").read_text(encoding="utf-8")
        self.assertIn(".lang-select{appearance:none", css)
        self.assertIn("border-radius:999px", css)
        self.assertIn(".lang-pick label{position:absolute;width:1px;height:1px;overflow:hidden", css)

    def test_language_select_points_to_same_page_in_each_language(self):
        ko = self.files["ko/index.html"]
        foot = re.search(r'<footer class="site-footer".*?</footer>', ko, re.S).group(0)
        self.assertIn('<option value="/ko/" selected>', foot)
        self.assertIn('<option value="/?lang=en">', foot)
        self.assertIn('<option value="/ja/">', foot)
        privacy = re.search(r'<footer class="site-footer".*?</footer>', self.files["ko/privacy/index.html"], re.S).group(0)
        self.assertIn('<option value="/ko/privacy/" selected>', privacy)
        self.assertIn('<option value="/privacy/?lang=en">', privacy)

    def test_hreflang_alternates_kept(self):
        for l in bs.languages.SUPPORTED:
            for f in self.all_page_paths(l):
                self.assertEqual(self.files[f].count('rel="alternate" hreflang="'), 13, f)

    def test_sitemap_urls(self):
        self.assertEqual(self.files["sitemap.xml"].count("<url>"), 12 * 6)


if __name__ == "__main__":
    unittest.main()
