---
title: 테스트 빌드에서 우리가 보는 것
title_en: What We Look for in Test Builds
summary: 빌드마다 시뮬레이터로 기기 화면을 먼저 확인하고, 그다음 사람이 처음 해 볼 때 어디서 멈추는지를 봅니다. 실제 균형은 아직 남은 질문입니다.
summary_en: Each build is checked on simulated device screens first, then on where a first-time player stops. Real balance is still an open question.
date: 2026-11-16
copy_review: iris 2026-11-14
---
## 시뮬레이터에서 먼저

빌드마다 아이폰과 아이패드를 세로와 가로로 돌려 화면을 확인합니다. 글자가 잘리거나 칸이 어긋나는 문제는 시뮬레이터에서 먼저 찾습니다. 기기마다 화면 비율이 달라서 한 가지 화면으로는 부족합니다. 화면이 비슷해도 손가락이 닿는 자리는 기기마다 달라서, 실제 기기에서 한 번 더 확인합니다.

## 사람이 해야 알 수 있는 것

화면이 맞아도 재미가 맞는지는 다른 문제입니다. 우리가 보려는 것은 처음 보는 사람이 같은 판에서 어디서 멈추는지입니다. 설명을 읽고도 첫 행동을 못 하는 순간이 있다면 그 자리를 먼저 고칩니다.

## 무엇을 기록할지

테스트에서 들은 말을 그대로 옮기면 잡음이 많습니다. 어디서 멈췄는지, 몇 번 다시 시도했는지처럼 행동으로 남는 기록을 먼저 모읍니다. 감상은 참고로 두고, 같은 자리에서 여러 사람이 멈추면 그때 고칩니다. 기록에는 빌드 번호를 함께 적어, 어떤 변경 뒤의 일인지 잃지 않게 합니다.

## 아직 남은 질문

실제 플레이어 기준의 균형은 아직 검증되지 않았습니다. 테스트 기록이 쌓이면 그때 숫자를 다시 봅니다. 그 전까지 이 글의 내용은 결론이 아니라 중간 기록입니다.

## EN

## Simulator first

For each build we check iPhone and iPad screens in portrait and landscape. We look for clipped text and misaligned cells in the simulator first. Screen ratios differ between devices, so one layout is not enough. Even on similar screens, thumb reach differs by device, so we check on real hardware once more.

## What only people can tell

A screen can look right and the fun can still be wrong. What we want to see is where a first-time player stops in the same round. If someone reads the instructions and still cannot make the first move, we fix that spot first.

## What we record

Writing down everything testers say gives us a lot of noise. We first collect records of behavior: where a player stopped, how many tries it took. Opinions stay as reference. When several people stop in the same place, that is when we fix it. Each record carries its build number so we do not lose track of which change came before it.

## Still open

Balance for real players has not been verified yet. When test records build up, we will look at the numbers again. Until then, what is written here is a midpoint record, not a conclusion.
