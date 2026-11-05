#!/usr/bin/env python3
"""Check sitemap.xml against the built site — stdlib only. Exit 1 on any problem.

  python3 scripts/check_sitemap.py          # offline checks
  python3 scripts/check_sitemap.py --live   # + every URL answers HTTP 200 (after deploy)
"""
import argparse
import datetime as dt
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site as bs  # noqa: E402

NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}


def check(root):
    root = Path(root)
    errs = []
    try:
        tree = ET.parse(root / "sitemap.xml")
    except (ET.ParseError, OSError) as ex:
        return ["sitemap.xml: %s" % ex], []
    urls = {}
    today = dt.date.today().isoformat()
    for u in tree.getroot().findall("s:url", NS):
        loc = (u.findtext("s:loc", namespaces=NS) or "").strip()
        urls[loc] = [(l.get("hreflang"), l.get("href")) for l in u.findall("x:link", NS)]
        lm = (u.findtext("s:lastmod", namespaces=NS) or "").strip()
        if lm > today:
            errs.append("lastmod in the future: %s %s" % (loc, lm))
    for loc, alts in urls.items():
        if not loc.startswith(bs.SITE + "/"):
            errs.append("not a %s URL: %s" % (bs.SITE, loc))
            continue
        rel = loc[len(bs.SITE):].lstrip("/")
        f = root / rel / "index.html" if (rel == "" or rel.endswith("/")) else root / rel
        if not f.is_file():
            errs.append("no file for %s" % loc)
        d = dict(alts)
        if "x-default" not in d:
            errs.append("no x-default: %s" % loc)
        if loc not in d.values():
            errs.append("hreflang list lacks itself: %s" % loc)
        for h, href in alts:
            if href not in urls:
                errs.append("hreflang target not in sitemap: %s -> %s" % (loc, href))
            elif loc not in [x for _, x in urls[href]]:
                errs.append("hreflang not reciprocal: %s <-> %s" % (loc, href))
    langs = [p.stem for p in (root / "content" / "i18n").glob("*.json")]
    for l in langs:
        for pth in [bs.path_home(l)] + [bs.path_page(l, s) for s in bs.PAGE_SLUGS + (bs.RELEASES,)]:
            if bs.url(pth) not in urls:
                errs.append("missing from sitemap: %s" % bs.url(pth))
    return errs, sorted(urls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args()
    errs, urls = check(a.root)
    if a.live and not errs:
        for u in urls:
            try:
                code = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "sitemap-check"}), timeout=20).status
            except Exception as ex:  # noqa: BLE001
                code = str(ex)
            if code != 200:
                errs.append("%s -> %s" % (u, code))
    if errs:
        print("sitemap check FAILED:\n  " + "\n  ".join(errs), file=sys.stderr)
        return 1
    print("sitemap ok: %d urls" % len(urls))
    return 0


if __name__ == "__main__":
    sys.exit(main())
