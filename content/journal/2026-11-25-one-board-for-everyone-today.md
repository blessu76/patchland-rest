---
title: 모두 같은 판을 받는 오늘의 땅
title_en: Daily Patch: One Board for Everyone
summary: 오늘의 땅은 하루에 한 번 바뀌고, 같은 날에는 누구나 같은 판을 받습니다. 판을 날짜로 정하는 방법과 풀 수 있는 판인지 먼저 확인하는 과정을 정리했습니다.
summary_en: Daily Patch changes once a day, and everyone gets the same board on the same day. This note describes how the date sets the board and how we check that each board can be solved.
date: 2026-11-25
copy_review: iris 2026-11-20
published_at: 2026-11-25T16:15:04+09:00
---
## 날짜로 정해지는 판

오늘의 땅은 하루에 한 판씩 바뀌는, 혼자 푸는 번지기 판입니다. 판은 날짜로 정해집니다. 기기의 달력 날짜를 연·월·일 숫자로 만들어 판의 씨앗으로 씁니다. 그래서 같은 날에는 누구나 같은 판을 받습니다. 판을 서버에서 내려받지 않으니 인터넷이 없어도 오늘의 판을 열 수 있습니다. 다만 날짜는 기기의 달력을 따르므로, 시간대가 다르면 같은 순간에 서로 다른 날의 판을 볼 수 있습니다.

## 정해진 수 안에 채우기

판은 12×12 칸, 다섯 가지 색입니다. 왼쪽 위 칸에서 시작해 색을 하나 고르면, 내 땅에 닿아 있는 같은 색 칸이 모두 내 땅이 됩니다. 22수 안에 판 전체를 내 땅으로 채우면 그날의 판을 푼 것입니다. 색을 골라 땅을 넓히는 방식은 영주와 겨루는 번지기와 같지만, 상대 없이 수의 제한과 겨룬다는 점이 다릅니다.

## 풀 수 있는 판인지 먼저 확인

날짜 씨앗이 어떤 판을 내놓을지는 미리 알 수 없습니다. 운이 나쁘면 22수로는 채우기 어려운 판이 나올 수 있습니다. 그래서 판을 만들 때 단순한 방식으로 한 번 풀어 봅니다. 매 수마다 지금 가장 많이 넓어지는 색을 고르는 방식입니다. 이 방식으로 세 수 이상 남기고 채워지지 않으면 판을 다시 그립니다. 판은 최대 60번까지 그려 보고, 그래도 맞는 판이 나오지 않으면 마지막 판을 씁니다.

## 연속일수를 세는 법

판을 다 채워야 그날이 완료로 남습니다. 수를 다 써서 못 채웠다면 같은 날 다시 도전할 수 있습니다. 연속일수는 오늘 또는 어제까지 끊기지 않고 이어진 날 수입니다. 어제까지 이어 왔다면, 오늘 판을 아직 풀지 않았어도 연속일수가 그대로 보입니다. 하루가 시작되자마자 기록이 끊긴 것처럼 보이지 않게 하려는 것입니다.

## 허브의 「오늘」 줄

허브 위쪽의 「오늘」 줄에는 오늘의 땅과 컬러코드가 한 줄씩 놓입니다. 오늘 끝냈는지는 색만이 아니라 체크 표시 모양으로도 구분하고, 연속일수는 글자로 붙입니다.

## 아직 정하지 않은 것

세 수의 여유가 알맞은지는 아직 모릅니다. 단순한 풀이를 기준으로 정한 여유라서, 사람이 실제로 느끼는 난이도와는 다를 수 있습니다. 플레이테스트에서 나온 의견을 보고 다시 맞출 예정입니다.

## EN

## A board set by the date

Daily Patch is a solo Spread board that changes once a day. The date sets the board. We turn the device's calendar date into a year-month-day number and use it as the board's seed. So everyone gets the same board on the same day. The board is not downloaded from a server, so today's board opens even without an internet connection. Because the date follows the device's calendar, though, people in different time zones may see different days' boards at the same moment.

## Fill it in the moves given

The board is 12×12 squares in five colors. You start from the top-left square, and when you pick a color, every square of that color touching your land becomes yours. Fill the whole board with your land within 22 moves, and the day's board is solved. Picking colors to spread works the same way as in Spread against a lord, but here you play against the move limit instead of a rival.

## Checking that a board can be solved

There is no telling in advance what board a date's seed will produce. With bad luck, it could be a board that is hard to fill in 22 moves. So when the board is made, we solve it once in a simple way: each move picks the color that grows the land most right now. If that does not fill the board with three or more moves to spare, the board is drawn again. We try up to 60 boards, and if none of them passes, the last one is used.

## How the streak is counted

A day counts as done only when the board is filled. If you run out of moves, you can try again the same day. The streak is the number of days in a row, ending today or yesterday. If your streak ran through yesterday, it still shows even before you solve today's board. We did not want the streak to look broken the moment a new day begins.

## The "Today" row on the hub

The "Today" row near the top of the hub lists Daily Patch and Color Code, one line each. Whether you have finished today is shown by the shape of a check mark, not by color alone, and the streak is written out as text.

## What we have not decided yet

We do not yet know whether a three-move margin is right. It is based on a simple solver, so it may differ from how hard a board feels to a person. We will adjust it based on what playtesters tell us.
