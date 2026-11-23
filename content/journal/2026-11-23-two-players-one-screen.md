---
title: 한 기기에서 둘이 겨루는 판
title_en: Two Players, One Screen
summary: 패치랜드의 2인 대전은 기기 한 대를 두 사람이 나눠 씁니다. 화면을 어떻게 나누고 차례를 어떻게 알릴지 고민한 과정을 정리했습니다.
summary_en: Patchland's two-player mode has two people share one device. This note describes how we split the screen and how we show whose turn it is.
date: 2026-11-23
copy_review: iris 2026-11-19
published_at: 2026-11-23T16:30:04+09:00
---
## 한 기기를 넘겨 가며 하는 판

한 기기에서 두 사람이 번갈아 두는 판은 생각보다 까다롭습니다. 한 사람이 수를 두면 가림막이 판을 덮고, 다음 사람이 가림막을 눌러야 판이 다시 보입니다. 그래서 2인 대전을 만들 때 규칙보다 먼저 차례를 어떻게 넘길지 생각했습니다. 패치랜드에서 한 기기로 하는 2인 대전은 놓기(육각 판)와 번지기 두 게임에 있습니다. 땅 하키에는 2인 판이 없습니다. 2인 판은 개인 기록과 도장에 남지 않습니다.

## 차례는 색과 글자로 함께

누구 차례인지를 색 하나로만 알리지 않기로 했습니다. 색을 구분하기 어려운 사람에게는 그 정보가 전달되지 않을 수 있기 때문입니다. 차례 표시는 색 칩과 '플레이어 1·2' 글자를 함께 씁니다.

## 넘겨받는 사이의 실수

기기를 넘겨받는 사이에 상대의 판을 보거나 실수로 누르기 쉽습니다. 그래서 가림막이 떠 있는 동안에는 판의 입력을 받지 않습니다.

## 아직 정하지 않은 것

한 기기 대전이 편한지는 실제로 둘이 앉아 해 봐야 알 수 있습니다. 기기 크기와 손 크기에 따라 결과가 달라질 것입니다. 이 글은 설계의 중간 기록입니다. 플레이테스트에서 나온 의견으로 화면 구성을 다시 조정할 예정입니다.

## EN

## Passing one device back and forth

Taking turns on one device is harder than it sounds. When one player makes a move, a cover screen hides the board, and the board appears again only after the next player taps the cover. So when we built two-player mode, we thought about how to hand off the turn before we thought about rules. On one device, two-player matches exist in two games: Place (the hex board) and Spread. Turf Hockey has no two-player match. Two-player matches are not saved to personal records or stamps.

## Show the turn with color and a label

We decided not to show whose turn it is with color alone. For someone who finds colors hard to tell apart, that information might never arrive. The turn marker pairs a color chip with the label “Player 1” or “Player 2”.

## Mistakes during the hand-off

While the device changes hands, it is easy to see the other player's board or tap it by mistake. So while the cover screen is up, the board does not accept input.

## What we have not decided yet

Whether a shared-device match feels good can only be learned by two people sitting down and playing. It will depend on the screen size and on hand size. This note is a midway record of the design. We will adjust the screen layout again based on what playtesters tell us.
