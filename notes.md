# 미니3: [게임 비교 도우미]

## 다시 실행하는 순서

1. 수집 스크립트(01_collect_p1.py · 02_collect.py)는 다시 돌리지 않는다 (사이트 목록이 바뀌어 raw.csv 가 달라짐)
2. mini3-project 폴더에서 python scripts/03_clean.py → 04_stats.py → 05_hist.py → 06_hist_half.py 순서로 실행
3. 이어서 python scripts/06_by_category.py → 07_by_category_median.py → 07_export_json.py 순서로 실행
4. 결과: data/clean.csv · data/data.json · charts/*.png 가 다시 만들어지고, data/raw.csv 는 그대로

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