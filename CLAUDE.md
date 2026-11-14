# CLAUDE.md

정적 사이트(빌드 없음). 규칙: 그라데이션 금지, 출시·가격 단정 금지, 분석/광고 스크립트 추가 금지, UI 변경 후 375/320/768/1280 렌더 확인, CSS 수정 시 `?v=` 갱신. 기획 문서는 `_ipe/foundry/F-023_landgrab/web/` 에.

## 저널 작성 절차
1. 글 작성 (front matter: title, title_en, summary, summary_en; 본문은 한국어 → `## EN` → 영어).
2. Iris 카피 검수 — 문장·톤·사실·과장·브랜드 용어, KO·EN 둘 다.
3. 고친 글의 front matter 에 `copy_review: iris YYYY-MM-DD` 기록 (검수 날짜).
4. `~/.ipe/queue/patchland/` 에 `NN-slug.md` 로 넣는다.
검수 기록이 없거나 형식이 틀린 글은 발행되지 않는다 (`ops/journal_publish.py` 가 SKIP, `build_site.py` 는 빌드 에러).
