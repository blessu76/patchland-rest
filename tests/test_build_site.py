import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_site as bs  # noqa: E402
from ipe_web_kit import journal, redirects  # noqa: E402

PAIRED = "paper-patch-three-verbs"
PAIRED_HTML = "journal/" + PAIRED + "/index.html"
POST_BASE = "---\ntitle: a\ntitle_en: a\nsummary: s\nsummary_en: s\ndate: 2026-11-14\n%s---\nk\n\n## EN\n\ne\n"
TRANS_BASE = "---\ntitle: t\nsummary: s\ndate: 2026-11-14\n%s---\n번역 본문\n"


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bs.Ctx(str(ROOT))
        cls.files = bs.build_all(cls.ctx) if not cls.ctx.errs else {}

    def page(self, lang, rest):
        return self.files[(lang + "/" if lang != "en" else "") + rest]

    def test_sources_valid(self):
        self.assertEqual(self.ctx.errs, [])

    def test_journal_requires_copy_review(self):
        root = Path(tempfile.mkdtemp())
        write(root, "content/journal/2026-11-14-x.md", POST_BASE % "")
        self.assertTrue(any("copy_review" in e for e in bs.Ctx(str(root)).errs))
        for bad in ("copy_review: iris 2026-1-14\n", "copy_review: Iris 2026-11-14\n", "copy_review: iris\n"):
            write(root, "content/journal/2026-11-14-x.md", POST_BASE % bad)
            self.assertTrue(any("copy_review" in e for e in bs.Ctx(str(root)).errs), bad)
        write(root, "content/journal/2026-11-14-x.md", POST_BASE % "copy_review: iris 2026-11-14\n")
        self.assertEqual(bs.Ctx(str(root)).errs, [])

    def test_translation_without_copy_review_is_excluded_with_warning(self):
        root = Path(tempfile.mkdtemp())
        write(root, "content/journal/2026-11-14-x.md", POST_BASE % "copy_review: iris 2026-11-14\n")
        write(root, "content/journal_i18n/ja/2026-11-14-x.md", TRANS_BASE % "")
        write(root, "content/journal_i18n/ja/2026-11-14-y.md", TRANS_BASE % "copy_review: iris 2026-11-14\n")
        ctx = bs.Ctx(str(root))
        self.assertEqual(ctx.errs, [])
        self.assertTrue(any("2026-11-14-x.md" in w and "copy_review" in w for w in ctx.warnings))
        self.assertEqual(ctx.journal[0]["body"].keys(), {"ko", "en"})

    def test_orphan_translation_is_excluded_with_warning(self):
        root = Path(tempfile.mkdtemp())
        write(root, "content/journal_i18n/ja/2026-11-14-z.md", TRANS_BASE % "copy_review: iris 2026-11-14\n")
        ctx = bs.Ctx(str(root))
        self.assertEqual(ctx.journal, [])
        self.assertTrue(any("no ko/en source" in w for w in ctx.warnings))

    def test_orphan_translations_in_repo_are_warned_not_built(self):
        orphans = [w for w in self.ctx.warnings if "no ko/en source" in w]
        self.assertTrue(orphans)
        self.assertNotIn("journal/02-same-rules-different-boards/index.html", "\n".join(self.files))

    def test_all_languages(self):
        self.assertEqual(sorted(self.ctx.langs), sorted(bs.languages.SUPPORTED))
        self.assertEqual(len(bs.languages.SUPPORTED), 12)

    def test_every_page_exists(self):
        for l in bs.languages.SUPPORTED:
            self.assertIn(("index.html" if l == "en" else l + "/index.html"), self.files)
            for s in bs.PAGE_SLUGS + (bs.JOURNAL,):
                self.assertIn(bs.path_page(l, s).strip("/") + "/index.html", self.files)
            self.assertIn(bs.path_article(l, PAIRED).strip("/") + "/index.html", self.files)

    def test_translations_have_ai_notice_and_hreflang(self):
        for l in bs.languages.SUPPORTED:
            h = self.files["index.html" if l == "en" else l + "/index.html"]
            self.assertEqual("ai-note" in h, l not in bs.ORIGINALS, l)
            self.assertIn('hreflang="x-default"', h)
            self.assertEqual(h.count('rel="alternate" hreflang="'), 13, l)

    def test_article_inlanguage_and_hreflang(self):
        for l in bs.languages.SUPPORTED:
            h = self.page(l, PAIRED_HTML)
            self.assertIn('"@type":"BlogPosting"', h, l)
            self.assertIn('"inLanguage":"%s"' % bs.languages.hreflang(l), h, l)
            self.assertEqual(h.count('rel="alternate" hreflang="'), 13, l)
            self.assertEqual(h.count('<html lang="%s"' % l), 1, l)

    def test_paired_post_passes_kit_publish_gate(self):
        post = next(a for a in self.ctx.journal if a["slug"] == "paper-patch-three-verbs")
        editions = {l: {"url": bs.url(bs.path_article(l, post["slug"])), "copy_review": "iris", "copy_review_date": "2026-11-14"}
                    for l in bs.article_langs(post)}
        self.assertEqual(journal.check_post(editions), [])

    def test_no_forbidden_claims(self):
        for f, t in self.files.items():
            if f.endswith(".html"):
                self.assertIsNone(re.search(r"\$\s?\d|★", t), f)
                self.assertNotIn("UA-", t)
                self.assertNotIn("googletagmanager", t)

    def test_asset_cache_busting(self):
        self.assertIn("?v=" + bs.ASSET_V, self.files["index.html"])
        self.assertIn("assets/ipe-lang.js", self.files)

    def all_page_paths(self, l):
        paths = [bs.path_home(l), bs.path_journal(l)]
        paths += [bs.path_page(l, s) for s in bs.PAGE_SLUGS]
        paths += [bs.path_article(l, a["slug"]) for a in self.ctx.journal if l in bs.article_langs(a)]
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

    def test_exactly_one_language_select_per_page(self):
        for l in bs.languages.SUPPORTED:
            for f in self.all_page_paths(l):
                h = self.files[f]
                self.assertEqual(h.count("<select "), 1, f)
                head = re.search(r'<header class="site-header".*?</header>', h, re.S).group(0)
                opts = re.findall(r'<option value="([^"]+)"[^>]*?( selected)?>', head)
                self.assertEqual(len(opts), 12, f)
                self.assertEqual(len([v for v, s in opts if s]), 1, f)
                foot = re.search(r'<footer class="site-footer".*?</footer>', h, re.S).group(0)
                self.assertNotIn("<select", foot, f)
                self.assertNotIn("lang-pick", h, f)
                self.assertNotIn("langsel", h, f)

    def test_language_select_points_to_same_page_in_each_language(self):
        ko = re.search(r'<header class="site-header".*?</header>', self.files["ko/index.html"], re.S).group(0)
        self.assertIn('<option value="/ko/" lang="ko" selected>', ko)
        self.assertIn('<option value="/" lang="en">', ko)
        self.assertIn('<option value="/ja/" lang="ja">', ko)
        privacy = re.search(r'<header class="site-header".*?</header>', self.files["ko/privacy/index.html"], re.S).group(0)
        self.assertIn('<option value="/ko/privacy/" lang="ko" selected>', privacy)
        self.assertIn('<option value="/privacy/" lang="en">', privacy)

    def test_ipe_lang_script_on_root_only(self):
        self.assertIn('<script src="/assets/ipe-lang.js?v=%s" data-redirect defer></script>' % bs.langswitch.asset_version(), self.files["index.html"])
        for f in self.files:
            if f.endswith(".html") and f != "index.html":
                self.assertNotIn("ipe-lang.js", self.files[f], f)

    def test_kit_langswitch_css_in_site_stylesheet(self):
        css = (ROOT / "assets" / "patchland.css").read_text(encoding="utf-8")
        self.assertIn(".ipe-lang__select", css)
        self.assertNotIn(".lang-select", css)
        self.assertFalse((ROOT / "assets" / "langpick.js").exists())

    def test_retired_languages_redirect_via_kit(self):
        self.assertIn("https://patchland.ipe.rest/pt-BR/", self.files["pt/index.html"])
        self.assertIn("https://patchland.ipe.rest/zh-Hant/", self.files["zh/index.html"])
        self.assertIn("https://patchland.ipe.rest/", self.files["ru/index.html"])
        self.assertIn("https://patchland.ipe.rest/", self.files["ar/index.html"])
        self.assertIn("https://patchland.ipe.rest/", self.files["hi/index.html"])
        self.assertIn("https://patchland.ipe.rest/pt-BR/privacy/", self.files["pt/privacy/index.html"])
        self.assertIn("https://patchland.ipe.rest/journal/%s/" % PAIRED, self.files["ru/journal/%s/index.html" % PAIRED])
        self.assertIn('noindex,follow', self.files["pt/index.html"])

    def test_no_legacy_urls_in_sitemap(self):
        self.assertEqual(redirects.sitemap_leaks(self.files["sitemap.xml"]), [])

    def test_sitemap_urls(self):
        self.assertEqual(self.files["sitemap.xml"].count("<url>"), 12 * 7)

    def test_redirect_pages_are_generated_for_retired_langs(self):
        for lang in redirects.LEGACY_REDIRECTS:
            self.assertIn(lang + "/index.html", self.files)


if __name__ == "__main__":
    unittest.main()
