#!/bin/bash
# Green gate for patchland-rest — run before every commit. Exit 0 = green.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== 0/4 kit"; python3 scripts/kit_lock.py check
echo "== 1/5 sources"; python3 scripts/build_site.py --check
echo "== 2/5 unit tests"; python3 -m unittest discover -s tests -q
echo "== 3/5 build is up to date"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
rsync -a --exclude='.git' ./ "$tmp/"
python3 scripts/build_site.py --root "$tmp" >/dev/null
for f in index.html 404.html sitemap.xml robots.txt llms.txt; do
  cmp -s "$f" "$tmp/$f" || { echo "$f is stale — run: python3 scripts/build_site.py"; exit 1; }
done
for d in privacy support terms releases ko ja zh es pt id ru vi fr de; do
  diff -r -q "$d" "$tmp/$d" >/dev/null 2>&1 || { echo "$d/ is stale — run: python3 scripts/build_site.py"; exit 1; }
done
echo "== 4/5 sitemap"; python3 scripts/check_sitemap.py
echo "== 5/5 release notes (kit lint)"; python3 vendor/ipe_web_kit/releases.py check content/releases.json --all --require-langs ko,en --site-langs ko,en,ja,zh,es,pt,id,ru,vi,fr,de >/dev/null
echo "GREEN"
