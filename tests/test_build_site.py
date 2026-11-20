import html as html_module
import json
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


def jsonld_nodes(page_html):
    """All @graph nodes from every application/ld+json block of a rendered page."""
    nodes = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page_html, flags=re.S):
        nodes += json.loads(raw)["@graph"]
    return nodes


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
        # per language: home, privacy, support, terms, journal index + one page per post (auto-publish adds posts)
        posts = len(list((ROOT / "content" / "journal").glob("*.md")))
        self.assertEqual(self.files["sitemap.xml"].count("<url>"), 12 * (5 + posts))

    def test_home_has_videogame_jsonld_without_price_or_release_claims(self):
        for lang in self.ctx.langs:
            page = self.page(lang, "index.html")
            self.assertIn('"@type":"VideoGame"', page, lang)
            self.assertIn('"gamePlatform":["iOS","Android"]', page, lang)
            self.assertNotRegex(page, r'"(price|offers|datePublished|aggregateRating)"', lang)
            games = [n for n in jsonld_nodes(page) if n.get("@type") == "VideoGame"]
            self.assertEqual(len(games), 1, lang)
            self.assertNotIn("inLanguage", games[0], lang)

    def test_support_faqpage_is_in_rendered_html(self):
        # Reads the built support HTML (what crawlers see), not bs.faq_ld, so a missing extra_ld link fails here.
        for lang in self.ctx.langs:
            page = self.page(lang, "support/index.html")
            faqs = [n for n in jsonld_nodes(page) if n.get("@type") == "FAQPage"]
            self.assertEqual(len(faqs), 1, lang)
            items = faqs[0]["mainEntity"]
            self.assertGreaterEqual(len(items), 4, lang)
            for q in items:
                self.assertEqual(q["@type"], "Question", lang)
                self.assertTrue(q["acceptedAnswer"]["text"].strip(), lang)
            headings = [html_module.unescape(re.sub(r"<[^>]+>", "", h)).strip()
                        for h in re.findall(r"<h3[^>]*>(.*?)</h3>", page, flags=re.S)]
            self.assertEqual([q["name"] for q in items], headings, lang)
        self.assertIsNone(bs.faq_ld("## No questions here\n\nText.\n", "en"))

    # 「지원 언어」 FAQ 답에 들어가야 하는 12개 언어 이름(각 페이지 언어로 적힌 이름). 답이 2개 언어로 되돌아가면 실패한다.
    NATIVE12 = ["English", "한국어", "日本語", "繁體中文", "Español", "Português (Brasil)", "Français", "Deutsch",
                "Bahasa Indonesia", "ไทย", "Tiếng Việt", "Türkçe"]
    LANG12 = {
        "en": ["English", "Korean", "Japanese", "Traditional Chinese", "Spanish", "Portuguese (Brazil)", "French", "German",
               "Indonesian", "Thai", "Vietnamese", "Turkish"],
        "ko": ["영어", "한국어", "일본어", "중국어 번체", "스페인어", "포르투갈어", "프랑스어", "독일어", "인도네시아어", "태국어", "베트남어", "터키어"],
        "ja": ["英語", "韓国語", "日本語", "繁体字中国語", "スペイン語", "ポルトガル語", "フランス語", "ドイツ語", "インドネシア語", "タイ語", "ベトナム語", "トルコ語"],
        "zh-Hant": NATIVE12,
        "es": ["inglés", "coreano", "japonés", "chino tradicional", "español", "portugués", "francés", "alemán", "indonesio", "tailandés", "vietnamita", "turco"],
        "pt-BR": ["inglês", "coreano", "japonês", "chinês tradicional", "espanhol", "português", "francês", "alemão", "indonésio", "tailandês", "vietnamita", "turco"],
        "fr": ["anglais", "coréen", "japonais", "chinois traditionnel", "espagnol", "portugais", "français", "allemand", "indonésien", "thaï", "vietnamien", "turc"],
        "de": ["Englisch", "Koreanisch", "Japanisch", "Traditionelles Chinesisch", "Spanisch", "Portugiesisch", "Französisch", "Deutsch", "Indonesisch", "Thai", "Vietnamesisch", "Türkisch"],
        "id": ["Inggris", "Korea", "Jepang", "Tionghoa tradisional", "Spanyol", "Portugis", "Prancis", "Jerman", "Indonesia", "Thailand", "Vietnam", "Turki"],
        "th": NATIVE12,
        "vi": ["tiếng Anh", "tiếng Hàn", "tiếng Nhật", "tiếng Hoa phồn thể", "tiếng Tây Ban Nha", "tiếng Bồ Đào Nha", "tiếng Pháp",
               "tiếng Đức", "tiếng Indonesia", "tiếng Thái", "tiếng Việt", "tiếng Thổ Nhĩ Kỳ"],
        "tr": NATIVE12,
    }

    def test_support_language_faq_lists_all_12_languages(self):
        self.assertEqual(sorted(self.LANG12), sorted(bs.languages.SUPPORTED))
        for lang in bs.languages.SUPPORTED:
            names = self.LANG12[lang]
            self.assertEqual(len(names), 12, lang)
            page = self.files[(lang + "/" if lang != "en" else "") + "support/index.html"]
            # FAQPage JSON-LD 는 화면 문구와 같은 원천에서 나온다 — 답은 JSON-LD 와 화면 모두에 12개 언어를 담아야 한다.
            nodes = [n for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                     for n in json.loads(m).get("@graph", [])]
            answers = [e["acceptedAnswer"]["text"] for n in nodes if n.get("@type") == "FAQPage" for e in n["mainEntity"]]
            lang_answers = [a for a in answers if all(n in a for n in names)]
            self.assertEqual(len(lang_answers), 1, lang)
            self.assertIn(html_module.escape(lang_answers[0]), page, lang)

    def test_redirect_pages_are_generated_for_retired_langs(self):
        for lang in redirects.LEGACY_REDIRECTS:
            self.assertIn(lang + "/index.html", self.files)


class PublishedAtTest(unittest.TestCase):
    """JSON-LD datePublished/dateModified: the front matter time when stamped (published_at / modified_at), else the plain date."""

    @classmethod
    def setUpClass(cls):
        # Hermetic: a fixture post, not ctx.journal[0] of the real repo. The newest real post changes on every
        # publish (the journal gate adds one a day), so tying these date assertions to it made them fail on the next run.
        cls.ctx = bs.Ctx(str(ROOT))  # renders with the real i18n strings
        root = Path(tempfile.mkdtemp())
        write(root, "content/journal/2026-11-14-x.md", POST_BASE % "copy_review: iris 2026-11-14\n")
        cls.base = bs.Ctx(str(root)).journal[0]

    def ld(self, post, lang="ko"):
        html = bs.build_article(self.ctx, lang, post)
        return dict(re.findall(r'"(datePublished|dateModified)":"([^"]+)"', html))

    def post(self, **kw):
        a = dict(self.base)
        a.update(kw)
        return a

    def test_stamp_gives_datetime_with_offset(self):
        got = self.ld(self.post(published_at="2026-11-14T19:24:57+09:00"))
        self.assertEqual(got, {"datePublished": "2026-11-14T19:24:57+09:00"})

    def test_no_stamp_falls_back_to_date_only(self):
        self.assertEqual(self.ld(self.post(published_at="")), {"datePublished": "2026-11-14"})
        a = self.post()
        del a["published_at"]
        self.assertEqual(self.ld(a), {"datePublished": "2026-11-14"})

    def test_date_modified_follows_the_same_rule(self):
        got = self.ld(self.post(published_at="2026-11-14T19:24:57+09:00", modified_at="2026-11-20T08:00:00+09:00"))
        self.assertEqual(got["dateModified"], "2026-11-20T08:00:00+09:00")
        self.assertNotIn("dateModified", self.ld(self.post(published_at="", modified_at="")))

    def test_visible_date_is_unchanged(self):
        html = bs.build_article(self.ctx, "ko", self.post(published_at="2026-11-14T19:24:57+09:00"))
        self.assertIn('<time datetime="2026-11-14">2026-11-14</time>', html)

    def test_stamp_must_match_file_date_and_format(self):
        root = Path(tempfile.mkdtemp())
        head = "copy_review: iris 2026-11-14\npublished_at: %s\n"
        for ok in ("2026-11-14T10:00:00+09:00", "2026-11-14T10:00:00-05:00"):
            write(root, "content/journal/2026-11-14-x.md", POST_BASE % (head % ok))
            self.assertEqual(bs.Ctx(str(root)).errs, [], ok)
        for bad in ("2026-11-15T10:00:00+09:00", "2026-11-14 10:00:00", "2026-11-14T10:00:00", "2026-11-14T25:00:00+09:00", "2026-11-14"):
            write(root, "content/journal/2026-11-14-x.md", POST_BASE % (head % bad))
            self.assertTrue(any("published_at" in e for e in bs.Ctx(str(root)).errs), bad)

    def test_translation_inherits_source_stamp(self):
        root = Path(tempfile.mkdtemp())
        write(root, "content/journal/2026-11-14-x.md", POST_BASE % "copy_review: iris 2026-11-14\npublished_at: 2026-11-14T10:00:00+09:00\n")
        write(root, "content/journal_i18n/ja/2026-11-14-x.md", TRANS_BASE % "copy_review: iris 2026-11-14\npublished_at: 2026-11-14T10:00:00+09:00\n")
        ctx = bs.Ctx(str(root))
        self.assertEqual(ctx.errs, [])
        self.assertEqual(ctx.journal[0]["published_at"], "2026-11-14T10:00:00+09:00")


if __name__ == "__main__":
    unittest.main()
