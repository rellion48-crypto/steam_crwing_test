# 미니3: [게임 비교 도우미]

## 다시 실행하는 순서

1. 수집 스크립트(01_collect_p1.py · 02_collect.py)는 다시 돌리지 않는다 (사이트 목록이 바뀌어 raw.csv 가 달라짐)
2. mini3-project 폴더에서 python scripts/03_clean.py → 04_stats.py → 05_hist.py → 06_hist_half.py 순서로 실행
3. 이어서 python scripts/06_by_category.py → 07_by_category_median.py → 07_export_json.py 순서로 실행
4. 결과: data/clean.csv · data/data.json · charts/*.png 가 다시 만들어지고, data/raw.csv 는 그대로

## M01 범위 카드 · EDA 질문 2개 · 사이트 판정표 · 모을 열 정의표

https://app.notion.com/p/M01-baeabd06af5382ea988281e3b8b2fb20?p=3e9abd06af53802382cbd056f3da33b8&pm=c

## M02 한 페이지 수집

화면에서 센 항목 8개 = 수집 1행

| 행 | 열 | CSV 값 | 원래 화면 | 같나 |
|---|---|---|---|---|
| 1 | name | BOMBANANA! | | |
| 1 | price_raw | ₩ 8,700 | | |
| 1 | rating_raw | 압도적으로 긍정적 (2,918) | | |

잘려 보이는 이름 0개

## M03 표본 3행 대조

| 표본 | 행 번호 | 이름 | 숫자 | 범주 | 확인한 곳 |
|---|---|---|---|---|---|
| 첫 행 | 0 | (RaceLineCalc) | (₩ 13,600) | () | |
| 가운데 행 | 25 | (Space Cat Digger Demo) | (무료) | () | |
| 마지막 행 | 49 | (Paint Gang Demo) | (무료) | () | |

판정: 모두 동일

## M04 정제

생김새 조사: price_raw 모양 4가지(무료 · ₩ 9,999 · ₩ 99,999 · 빈칸) · discount_raw 2가지(-99% · 빈칸) · rating_raw 3가지(빈칸 48 · 툴팁 글자 2) · release_date_raw 1가지(9999년 9월 99일) · 빈칸 price_raw 1 · discount_raw 38 · rating_raw 48 · category_raw 50 · detail_url 중복 0 · 50행

규칙
1. price_raw 의 ₩ 와 쉼표를 떼고 정수로 바꿔 price 에, 무료는 "무료" 글씨 그대로, 다른 통화는 NaN
2. discount_raw 의 -15% 를 0.15 처럼 비율로 바꿔 discount 에, 빈칸은 NaN 그대로
3. release_date_raw 의 2026년 9월 27일 을 2026.09.27 꼴로 바꿔 release_date 에
4. name 앞뒤 공백 정리
5. 못 바꾼 값은 채우지 않고 NaN -> 이번에는 0건
6. name · price · detail_url 빈칸 행과 detail_url 중복 행은 사유와 함께 뺌 -> 이번에는 1건(행 22 Solitaire Together, price 빈칸), 50행 → 49행

첫 줄 손 검산
| 원문 | 손으로 바꾼 값 | clean.csv 값 | 같나 |
|---|---|---|---|
| ₩ 13,600 | 13600 | 13600 |O|
| -15% | 0.15 | 0.15 |O|
| 2026년 9월 27일 | 2026.09.27 | 2026.09.27 |O|
| RaceLineCalc | RaceLineCalc | RaceLineCalc |O|

## M05 데이터 점검표

| 점검 항목 | 처리 전 | 처리 후 | 규칙·근거 |
|---|---|---|---|
| 수집 범위 | 목록 주소 https://store.steampowered.com/search/?sort_by=Released_DESC&os=win · 3페이지 · 60행 | - | 수집 기록서 |
| 행 수 | 50행 | 49행 | 50 - 1 = 49 (M04 생김새 조사 · 규칙 6) |
| 숫자 열 | price_raw 모양 4가지(무료 · ₩ 9,999 · ₩ 99,999 · 빈칸) · discount_raw 2가지(-99% · 빈칸) | price(정수, 무료는 글씨 그대로) · discount(비율) · 못 바꾼 값 0건 | M04 규칙 1 · 2 · 5 |
| 범주 열 | rating_raw 3가지(빈칸 48 · 툴팁 글자 2) · category_raw 빈칸 50 | 미확인 | M04 생김새 조사, 범주 열 규칙 없음 |
| 공백 | 미확인 | 미확인 | M04 규칙 4 (name 앞뒤 공백 정리) |
| 필수값 빈칸 | 1건(행 22 Solitaire Together, price 빈칸) | 미확인 | M04 규칙 6 |
| detail_url 중복 | 0건 | 미확인 | M04 생김새 조사 |
| 뺀 행 | - | 1건(행 22 Solitaire Together, price 빈칸) | M04 규칙 6 |
| 표본 3행 대조 | 3행(행 0 · 25 · 49) 판정: 모두 동일 | 첫 줄 손 검산 4개 모두 O | M03 판정 · M04 첫 줄 손 검산 |

## M06 구간 폭 바꿔 보기

가장 높은 막대: 폭 5000 은 [0, 5000) 11개, 폭 2500 은 [2500, 5000) 7개 → 0~5000원 범위 안에 그대로 있음 (그 안에서는 오른쪽 절반으로 옮겨감)

## M07 그룹별 중앙값

가장 큰 값 29100(연운 - [오동나무의 울림] 패키지)은 2026.09.27 그룹에 있음 (M05에는 최댓값 기록이 없어 04_stats.py · 07_by_category_median.py 출력 기준)

## M08 Github저장소

https://github.com/rellion48-crypto/steam_crwing_test

## M09 비교 화면 뼈대

JSON 49개 = 화면 [49]개

| 카드 | 번호 | 이름 | 숫자 | 범주 | 화면과 같나 |
|---|---|---|---|---|---|
| 첫 카드 | 0 | RaceLineCalc | 13600 | (없음) | |
| 가운데 카드 | 24 | Space Cat Digger Demo | 무료 | (없음) | |
| 마지막 카드 | 48 | Paint Gang Demo | 무료 | (없음) | |

정렬 단추(가격 낮은 순 · 높은 순): 처음 · 낮은 순 · 높은 순 모두 「총 49개」, 카드 49장으로 그대로 (무료는 정렬할 때만 0으로 봄)

## M10 바로 바뀌는 조건

[적용] 없이 칸 값이 바뀌면 바로 적용: 예산 20000 → 48개 · 15000 → 48개 · 10000 → 43개로 확인표 개수와 같음
주의: 예산을 한 글자 칠 때마다 목록이 다시 그려져(20000 입력 중 2 · 20 · 200 · 2000 에서 24개가 거쳐 감) M15 에서 「조건 적용」 시각을 첫 글자 · 마지막 글자 · 결과가 멈춘 때 중 언제로 잴지 먼저 정해야 함

## M11 배포본 v1

https://steamcrwingtest.vercel.app/
짝 : 잘보인다고 함
### 더 해보기 : 새로운 주소
stmcrwt.vercel.app
( Redirect old domain to new )

## M12 AI 기능 명세와 열쇠
올라갈 목록에 .env 없음 - .gitignore 에 .env 한 줄 확인

| 칸 | 무엇을 적나 |
|---|---|
| 같은 조건이면 같은 추천이 나와야 하나 | 예 — 같은 조건 · 같은 후보 2개에 누를 때마다 답이 바뀌면 「확인 방법」(data.json 과 대 보기)을 다시 해도 같은 결과가 안 나와 점검할 수 없음 |
| → 프롬프트에 더 적을 것 | 고르는 기준을 순서까지 못박음: ① price(무료=0) 낮은 쪽 ② 같으면 입력 순서 앞쪽, 이유 문장도 이 기준만 쓰게 함 (호출 설정은 temperature 0) |