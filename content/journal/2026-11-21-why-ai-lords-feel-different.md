---
title: AI 영주의 성격이 판마다 다르게 느껴지는 이유
title_en: Why Each AI Lord Feels Different from Round to Round
summary: 패치랜드의 AI 영주는 같은 규칙 안에서 움직이지만, 영주마다 다른 사람을 상대하는 듯한 느낌이 들도록 만들고 있습니다. 그 느낌을 만드는 디자인 선택을 정리했습니다.
summary_en: Patchland's AI lords play under the same rules, yet we are shaping each one to feel like a different person. This note describes the design choices behind that feeling.
date: 2026-11-21
copy_review: iris 2026-11-17
published_at: 2026-11-21T17:00:06+09:00
---
## 규칙은 같고, 손버릇이 다르다

패치랜드의 규칙은 모든 영주에게 똑같이 적용됩니다. 긋고, 놓고, 번지는 세 가지 동작도 누구에게나 같습니다. 그래도 영주마다 다른 사람과 겨루는 것처럼 느껴지도록 만들고 싶었습니다. 차이는 규칙이 아니라 손버릇에서 나온다고 보았습니다. 어떤 영주는 가장자리부터 조각을 넓히고, 어떤 영주는 한가운데를 먼저 잡습니다. 같은 동작이라도 어디서 시작하느냐에 따라 판의 흐름이 달라집니다.

## 망설임을 보여 주기

사람이 상대일 때는 망설이는 시간이 곧 성격으로 읽힙니다. 상대가 잠깐 생각하다가 자리를 고르는 모습에서 우리는 그 사람의 기질을 짐작합니다. AI에게는 그 시간이 기본으로 없습니다. 그래서 영주마다 판단을 내리기 전에 머무는 길이와 방식을 따로 두었습니다. 화면에서 바로 답하지 않고 한 박자 쉬는 것만으로도 상대가 생각하고 있다는 느낌이 생깁니다. 다만 너무 오래 기다리게 하면 답답함만 남기 때문에 짧은 망설임을 기준으로 맞추었습니다.

## 실수의 방향을 정하기

완벽한 영주는 오히려 재미가 덜하다고 보았습니다. 실수가 전혀 없으면 플레이어는 이길 방법을 찾기보다 벽을 확인하는 데 시간을 쓰게 됩니다. 그래서 영주마다 자주 하는 실수의 방향을 정했습니다. 욕심이 많은 영주는 너무 멀리 뻗다가 조각이 끊기고, 조심스러운 영주는 기회를 한 번 놓칩니다. 플레이어는 그 실수를 보고 이 영주가 어떤 사람인지 짐작합니다. 실수가 곧 개성이 되는 셈입니다. 다만 실수는 판을 뒤집을 만큼 크면 안 됩니다. 작은 어긋남으로 머물러야 플레이어가 그 영주를 읽을 수 있습니다.

## 같은 판을 다시 열어 보기

같은 보드에서도 영주의 성격이 드러나도록 하는 것을 목표로 했습니다. 같은 자리에서 다른 영주가 어떻게 움직이는지 비교할 수 있으면 차이가 더 분명해집니다. 이 비교가 가능한 구성이 성격에 대한 기억을 오래 남깁니다. 한 번만 보면 지나치기 쉬운 차이도 같은 보드에서 나란히 놓이면 눈에 들어옵니다. 다음 날 같은 보드에 다른 영주가 앉아 있다면 플레이어는 자연스럽게 비교를 시작합니다. 그 비교가 곧 다시 찾아오는 이유가 됩니다.

## 이기는 것보다 계속 두는 것

영주가 항상 이기면 플레이어는 금방 지치기 쉽습니다. 그래서 영주가 이기려고만 하지 않도록 목표를 나누었습니다. 어떤 영주는 넓은 땅을 원하고, 어떤 영주는 작은 땅이라도 지키기를 원합니다. 목표가 다르면 같은 상황에서도 선택이 달라집니다. 플레이어는 그 선택을 보며 영주가 무엇을 아끼는지 알게 됩니다. 이기고 지는 결과보다 그 과정에서 드러나는 취향이 기억에 남는다고 보았습니다.

## 아직 다듬는 것

지금의 차이가 충분한지는 아직 확인하지 못했습니다. 어떤 플레이어는 영주 사이의 차이를 금방 알아보고, 어떤 플레이어는 규칙만 보입니다. 이 차이를 어떻게 전할지도 정해야 합니다. 플레이테스트 기록을 모아 어떤 손버릇이 실제로 기억되는지 살펴볼 계획입니다. 이 글도 결론이 아니라 중간 기록입니다.

## EN

## Same rules, different habits

Patchland's rules apply to every lord in the same way. The three actions of tracing, placing and spreading are the same for all of them. Yet we want each lord to feel like a different person to face. We think the difference comes from habits rather than rules. One lord widens its patches from the edges, while another takes the center first. Even the same action leads to a different flow depending on where it starts.

## Showing hesitation

When the opponent is a person, the time spent hesitating reads as character. Watching someone pause and then choose a spot tells us something about their temperament. An AI has no such time by default, so each lord was given its own length and manner of pausing before a decision. Simply not answering on the very next frame makes the opponent seem to be thinking. The pause is kept short, though, because a long wait only creates frustration.

## Deciding the direction of mistakes

We thought a perfect lord would be less fun. When a lord never errs, players spend their time testing a wall instead of looking for a way through. So we chose the direction each lord tends to err in. A greedy lord stretches too far and its patches break apart. A cautious lord misses one opening. Players see the mistake and guess what kind of person the lord is. The mistake becomes part of the character. It has to stay small, though, so that the lord stays readable. A mistake big enough to flip the board would leave nothing to read.

## Reopening the same board

We aimed for each lord's character to show even on the same board. When different lords can be compared in the same place, the differences become clearer, and that comparison helps the characters stay in memory. A gap that is easy to miss when seen once becomes visible when the lords are placed side by side on one board. If a different lord sits at the same board the next day, players naturally start comparing, and that comparison becomes a reason to come back.

## Playing to keep, not only to win

If a lord always wins, players tend to tire quickly. So we split the goals so that a lord does not play only to win. One lord wants a wide territory, while another would rather hold a small patch. When the goals differ, the choices differ even in the same situation. Players watch those choices and learn what each lord cares about. We think the taste revealed in the process stays in memory more than the win or the loss.

## What we are still refining

We have not yet confirmed whether the current differences are enough. Some players notice the gap between lords quickly, while others see only the rules. We also need to decide how to convey these differences. We plan to gather playtest records and check which habits are actually remembered. This note is also a midpoint record, not a conclusion.
