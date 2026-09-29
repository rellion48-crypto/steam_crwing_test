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

확인표 (별점 조건 없음 · 무료 제외 안 함, data.json 49개에서 가격(무료=0) ≤ 예산인 개수)
| 예산 | data.json 로 센 개수 | 화면 개수 | 같나 |
|---|---|---|---|
| (빈칸) | 49 | 49 | 같음 |
| 20000 | 48 | 48 | 같음 |
| 15000 | 48 | 48 | 같음 |
| 10000 | 43 | 43 | 같음 |
| 2 · 20 · 200 · 2000 (20000 입력 중) | 24 | 24 | 같음 |

## M11 배포본 v1

https://steamcrwingtest.vercel.app/
짝 : 잘보인다고 함
### 더 해보기 : 새로운 주소
https://stmcrwt.vercel.app
( Redirect old domain to new )

## M12 AI 기능 명세와 열쇠
올라갈 목록에 .env 없음 - .gitignore 에 .env 한 줄 확인

| 칸 | 무엇을 적나 |
|---|---|
| 같은 조건이면 같은 추천이 나와야 하나 | 예 — 같은 조건 · 같은 후보 2개에 누를 때마다 답이 바뀌면 「확인 방법」(data.json 과 대 보기)을 다시 해도 같은 결과가 안 나와 점검할 수 없음 |
| → 프롬프트에 더 적을 것 | 고르는 기준을 순서까지 못박음: ① price(무료=0) 낮은 쪽 ② 같으면 입력 순서 앞쪽, 이유 문장도 이 기준만 쓰게 함 (호출 설정은 temperature 0) |

## M13 AI 추천 동작본

배포 주소 (Domains) : https://stmcrwt.vercel.app
환경변수 GEMINI_API_KEY - Secret · Production · Redeploy 완료

두 조건의 추천이 서로 다른가 : [아니오]
소스 보기에서 GEMINI · 열쇠 앞 네 글자 : 안 찾아짐

이유 각 줄 40자 안쪽 (프롬프트 수정 154264d 배포 뒤, 예산 10000 · 별점 조건 없음으로 두 번)
| 누름 | 추천 | 이유 1 | 이유 2 | 40자 안쪽 |
|---|---|---|---|---|
| 1번째 | MECCHA OCTOPUS Demo | 37자 | 29자 | 예 |
| 2번째 | MECCHA OCTOPUS Demo | 17자 | 28자 | 예 |

**get_recommendation · result_status 값** : success · unverified · error · rate_limited · no_candidates — "추천을 눌렀는데 실패 안내만 뜬 사람" = 기간 안에 unverified · error · rate_limited 가 있고 success 는 한 번도 없는 사용자 수

- success ↔ "AI 추천: (게임 이름)" + 이유 두 줄 (서버 ok 이고, 이름이 화면 후보 앞 5개 안에 있을 때)
- 실패 1 · unverified ↔ "추천을 확인하지 못했습니다" (서버 unverified, 또는 서버는 ok 인데 이름이 화면 후보 앞 5개 밖일 때)
- 실패 2 · error ↔ "잠시 뒤 다시 눌러 주세요" (열쇠 없음 · Gemini 응답 실패(429 제외) · 네트워크 오류 · 20초 초과 · 답 JSON 못 읽음 · 화면의 fetch 실패)
- 실패 3 · rate_limited ↔ "잠시 뒤 다시 눌러 주세요" (Gemini 429 한도 초과, 화면 문장은 error 와 같음)
- no_candidates ↔ 새 문장 없음 (결과 자리를 비우고, 목록 자리의 빈 목록 안내만 남음)


## M14 AI 추천 검증

| 경우 | 조건 | 후보 수 | AI 불렀나 | 추천 이름 | 이유 속 숫자 | data.json 값 | 같나 | 후보 안? | 지어낸 말 |
|---|---|---|---|---|---|---|---|---|---|
| 정상 | 예산 15000 · 무료 제외 | 24 (넘긴 것 5) | 예 | The Hidden Camp - B-Duke & Dance Music | 2250원 · 2026.09.27 | 2250 · 2026.09.27 | 같음 | 예 | 없음 |
| 후보 최소 (4개) | 예산 2250 · 무료 제외 | 4 (넘긴 것 4) | 예 | The Hidden Camp - B-Duke & Dance Music | 2250원 · 2026.09.27 | 2250 · 2026.09.27 | 같음 | 예 | 없음 |
| 후보 없음 | 예산 2000 · 무료 제외 | 0 | 아니오 (안내 문장만) | — | — | — | — | — | — |

- 후보 1개는 만들 수 없음: 무료 제외 시 가장 싼 2250원이 4개 동점이라 예산만으로는 최소 4개
- 확인 주소: https://stmcrwt.vercel.app/ (커밋 197334d 배포본)

## M15 정말 쓰는지 알려면 무엇을 재는지

| 이름 | 언제 | 매개변수 | 왜 재나 | 분류 | 중복 방지 | 빼는 값 |
| --- | --- | --- | --- | --- | --- | --- |
| `filter_game_list`<br>단추 이름 "적용"이 아니라 한 일(목록 거르기)을 동사 filter로 앞에 두었고, 소문자와 밑줄만 쓴 16자라 규칙을 지킴 | 목록 화면에서 조건 칸(예산(원) · 최소 별점 · 무료 제외)에 값을 넣고 **[적용]** 을 누르거나 칸 값이 바뀌어 목록이 다시 그려진 순간 (`applyFilter`) | budget : 20 · min_rating : 4 · exclude_free : false · result_count : (그 조건에서 그려진 카드 수) | result_count가 0인 조건이 자주 나오면 수집 범위(지금 1~3페이지, 49개)를 넓힐지, 빈 목록 안내 문장을 바꿀지 정한다. 예산과 별점 중 어느 칸을 더 많이 쓰는지 보고 칸의 순서를 정한다 | 맞춤 이벤트 | 예산 칸은 한 글자 칠 때마다 적용되므로 "20"을 치면 "2"와 "20"에서 두 번 불린다. 입력이 멈춘 뒤 한 번만 보내고, 바로 전에 보낸 조건 세 개와 같으면 보내지 않는다 | 빈 목록 안내 문장(`emptyMessage`, 게임 이름이 들어감) |
| `get_recommendation`<br>단추 이름 "이 조건으로 추천받기"가 아니라 한 일(추천 받기)을 동사 get으로 앞에 두었고, 소문자와 밑줄만 쓴 18자이며 `ga_` · `google_` · `firebase_` 로 시작하지 않음 | **[이 조건으로 추천받기]** 를 누른 뒤 결과 자리(`aiResult`)가 바뀐 순간. 추천 이름이 뜨거나, "추천을 확인하지 못했습니다"나 "잠시 뒤 다시 눌러 주세요"가 뜨거나, 후보가 없어 비워진 경우를 모두 포함 | recommend_status : ok · budget : 20 · min_rating : 4 · exclude_free : false · candidate_count : (가격 낮은 순 앞 5개 중 실제 후보 수)<br>recommend_status 값: ok(추천 표시) / unverified(추천을 확인하지 못함, 서버가 ok를 줬지만 화면 후보 5개 밖인 경우 포함) / unavailable(잠시 뒤 다시) / empty · no_candidates(후보 0개) | unavailable 비율로 제한 시간(20초) · 모델 · 한도를 바꿀지 정한다. unverified 비율로 시스템 지시나 답 형식(schema)을 고칠지 정한다 | 맞춤 이벤트 | 기다리는 동안 단추가 막혀 있어 두 번 누를 수 없다. 조건이 바뀌어 옛 답이 버려질 때(`token !== aiToken`)는 보내지 않고, 번호 검사를 통과한 뒤 한 번만 보낸다 | 추천 이유 두 줄(`reasons`), `GEMINI_API_KEY` |
| `select_item` | 카드의 **"원래 화면 보기"** 링크를 누른 순간 (새 창으로 `detail_url`이 열림) | item_list_name : ai_pick ("AI 추천" 표시가 붙은 카드) / game_list (그 밖의 카드) · items : [item_name : (카드 제목 글자)] | ai_pick과 game_list의 클릭 수를 비교해 AI 추천 단추와 표시를 계속 둘지 정한다 | GA4 추천 이벤트 | 누를 때마다 한 번씩 센다. `detail_url`이 다른 도메인이면 GA4 향상된 측정의 외부 링크 클릭(`click`)에도 같이 잡히므로, 보고서에서는 한쪽만 센다 | `detail_url`, 추천 이유 문장 |
