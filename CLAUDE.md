# CLAUDE.md

정적 사이트(빌드 없음). 규칙: 그라데이션 금지, 출시·가격 단정 금지, 분석/광고 스크립트 추가 금지, UI 변경 후 375/320/768/1280 렌더 확인, CSS 수정 시 `?v=` 갱신. 기획 문서는 `_ipe/foundry/F-023_landgrab/web/` 에.

## 저널 작성 절차
1. 글 작성 (front matter: title, title_en, summary, summary_en; 본문은 한국어 → `## EN` → 영어).
2. Iris 카피 검수 — 문장·톤·사실·과장·브랜드 용어, KO·EN 둘 다.
3. 고친 글의 front matter 에 `copy_review: iris YYYY-MM-DD` 기록 (검수 날짜).
4. `~/.ipe/queue/patchland/` 에 `NN-slug.md` 로 넣는다.
검수 기록이 없거나 형식이 틀린 글은 발행되지 않는다 (`ops/journal_publish.py` 가 SKIP, `build_site.py` 는 빌드 에러).

### 번역 → Iris 검수 → 발행 (상시 규칙)
- 번역본은 `content/journal_i18n/<lang>/<같은-파일명>.md` 에 둔다. 원문(ko/en)이 먼저 검수를 통과해야 한다.
- 번역은 반드시 Iris 가 해당 언어까지 검수하고, 그 번역 front matter 에 `copy_review: iris YYYY-MM-DD` 를 기록한 뒤에만 발행한다.
- 검수 기록이 없는 번역은 빌드에서 제외되고 경고가 남는다. 원문 없이 번역만 있는 파일도 제외된다.
- 원문을 고치면 해당 번역도 다시 검수한다.
