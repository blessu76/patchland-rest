---
title: 같은 규칙, 다른 판
title_en: Same Rules, Different Boards
summary: 규칙이 같아도 시작 보드가 다르면 판의 결과가 크게 갈렸습니다. 그래서 난이도와 목표치를 숫자 하나로 묶지 않기로 했습니다.
summary_en: With the same rules, the starting board could decide the whole round. So we stopped tying difficulty and targets to a single number.
date: 2026-11-14
copy_review: iris 2026-11-14
---
## 같은 규칙, 다른 판

번지기 규칙으로 AI끼리 판을 여러 번 돌려 보았습니다. 규칙은 같아도 처음 놓이는 자리가 달라지면 결과가 크게 갈렸습니다. 씨앗 하나가 판의 흐름을 거의 정해 버리는 경우가 많았습니다.

## 가장 어려운 상대의 벽

가장 어려운 영주 AI는 평범한 방식으로는 거의 이길 수 없었습니다. 겨뤄 볼 만한 상대가 아니라 벽에 가까웠습니다. 그래서 가장 어려운 단계의 난이도를 다시 맞추었습니다.

## 숫자 하나로 묶지 않기

긋기만 봐도 판의 종류에 따라 기본 확률이 달랐습니다. 그래서 목표치를 하나의 기준으로 묶지 않고, 판 종류마다 따로 보기로 했습니다.

## 한두 판으로 결정하지 않기

판마다 결과가 달라서, 한두 판만 보고 결정하면 틀리기 쉽습니다. 같은 보드를 여러 번 돌리고 시작 씨앗을 바꿔 가며 결과가 얼마나 흩어지는지 봅니다. 흩어짐이 평균보다 더 많은 것을 알려 주기 때문입니다.

## 아직 모르는 것

지금 수치는 AI끼리 돌린 결과입니다. 실제 사람이 두는 판의 균형은 아직 검증되지 않았습니다. 숫자보다 플레이테스트 기록을 더 믿기로 한 이유입니다.

## EN

## Same rules, different boards

We ran the spread rules through many simulated rounds. Even with identical rules, the result swung widely when the first patches landed in different places. Often a single starting seed nearly decided the direction of the round.

## The hardest lord was a wall

The hardest lord AI was close to unbeatable under ordinary play. It felt less like a rival and more like a wall. So we retuned the difficulty of the hardest level.

## Not one number for everything

Even tracing alone had different baseline odds depending on the kind of round. So we stopped treating targets as a single benchmark and now look at each round type on its own.

## Not deciding from one or two rounds

Results vary from round to round, so judging from one or two rounds is easy to get wrong. We run the same board many times and change the starting seed to see how far results scatter. The scatter tells us more than the average does.

## What we still do not know

These figures come from AI-only runs. The balance for real players has not been verified yet. That is why we trust playtest records more than the numbers.
