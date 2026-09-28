# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# 수집 시각을 기록하기 위해 datetime을 불러온다
from datetime import datetime
# 페이지 사이에 쉬기 위해 time을 불러온다
import time
# 상대 주소를 전체 주소로 바꾸기 위해 urljoin을 불러온다
from urllib.parse import urljoin

# 웹 페이지 요청을 위해 requests를 불러온다
import requests
# HTML 해석을 위해 BeautifulSoup을 불러온다
from bs4 import BeautifulSoup
# 표를 만들고 CSV로 저장하기 위해 pandas를 불러온다
import pandas as pd

# 목록 주소 꼴(page 자리에 페이지 번호가 들어간다)
URL_TEMPLATE = "https://store.steampowered.com/search/?sort_by=Released_DESC&os=win&page={page}"
# 01과 같이 화면과 같은 한국어 글자로 받기 위해 스팀 언어 쿠키를 한국어로 지정한다
COOKIES = {"Steam_Language": "koreana"}
# 최대 페이지 수
MAX_PAGES = 3
# 이 행 수 이상 모이면 멈춘다
MAX_ROWS = 50
# 저장 위치: 이 스크립트 파일 위치 기준 ../data/raw.csv
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw.csv"
# CSV 열 이름과 순서(01과 같다)
COLUMNS = ["name", "price_raw", "discount_raw", "rating_raw",
           "release_date_raw", "category_raw", "detail_url", "scraped_at"]


# 선택자로 찾은 요소의 글자를 앞뒤 공백만 정리해 돌려주고, 없으면 빈 문자열을 돌려준다(01과 같다)
def text_of(parent, selector):
    # 부모 요소 안에서 선택자에 맞는 첫 요소를 찾는다
    el = parent.select_one(selector) if parent else None
    # 요소가 있으면 글자를, 없으면 빈 문자열을 돌려준다
    return el.get_text(" ", strip=True) if el else ""


# 모든 페이지의 행을 담을 리스트를 준비한다
all_rows = []
# 1페이지부터 최대 페이지까지 차례로 돈다
for page in range(1, MAX_PAGES + 1):
    # 첫 페이지가 아니면 요청 전에 1초 쉰다
    if page > 1:
        # 1초 쉰다
        time.sleep(1)
    # 이번 페이지 주소를 만든다
    url = URL_TEMPLATE.format(page=page)
    # 페이지를 한 번 요청한다(10초 안에 응답이 없으면 중단)
    response = requests.get(url, cookies=COOKIES, timeout=10)
    # 글자가 깨지지 않게 서버가 알려준 인코딩을 쓰고, 없으면 utf-8을 쓴다(01과 같다)
    response.encoding = response.encoding or "utf-8"
    # 이번 페이지에서 뽑은 행을 담을 리스트를 준비한다
    rows = []
    # 상태 코드가 200일 때만 HTML을 해석한다
    if response.status_code == 200:
        # 응답 HTML을 BeautifulSoup으로 해석한다
        soup = BeautifulSoup(response.text, "html.parser")
        # 이 페이지를 수집한 시각을 기록한다
        scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 검색 결과 목록의 칸(게임 하나)마다 돈다
        for item in soup.select("#search_resultsRows > a.search_result_row"):
            # 평가 아이콘 요소를 찾는다(평가가 없으면 None)
            review = item.select_one(".search_reviewscore .search_review_summary")
            # 한 행을 딕셔너리로 만들어 리스트에 넣는다
            rows.append({
                # 게임명
                "name": text_of(item, ".search_name .title"),
                # 현재 가격(할인가 또는 정가, 숫자로 바꾸지 않은 화면 글자)
                "price_raw": text_of(item, ".discount_final_price"),
                # 현재 할인율(할인이 없으면 빈 칸)
                "discount_raw": text_of(item, ".discount_pct"),
                # 별점(목록에서는 아이콘에 마우스를 올리면 뜨는 글자, 없으면 빈 칸)
                "rating_raw": review.get("data-tooltip-html", "") if review else "",
                # 출시일
                "release_date_raw": text_of(item, ".search_released"),
                # 게임 카테고리(목록 칸에는 장르 글자가 없어 빈 칸)
                "category_raw": "",
                # 상세 URL(이 페이지 주소 기준 전체 주소)
                "detail_url": urljoin(response.url, item.get("href", "")),
                # 수집한 시각
                "scraped_at": scraped_at,
            })
    # 실제로 연 주소, 응답 상태, 그 페이지 행 수를 한 줄로 출력한다
    print(f"{page}페이지 | 주소: {response.url} | 상태: {response.status_code} | 행 수: {len(rows)}")
    # 200이 아니거나 0행이면 여기서 멈춘다
    if response.status_code != 200 or len(rows) == 0:
        # 몇 페이지에서 멈췄는지 출력한다
        print(f"{page}페이지에서 멈춤 (200이 아니거나 0행)")
        # 반복을 끝낸다
        break
    # 이번 페이지 행을 전체 목록에 더한다
    all_rows.extend(rows)
    # 합계가 기준 행 수 이상이면 멈춘다
    if len(all_rows) >= MAX_ROWS:
        # 행 수 기준으로 멈췄다고 출력한다
        print(f"합계 {len(all_rows)}행으로 {MAX_ROWS}행 이상이 되어 {page}페이지에서 멈춤")
        # 반복을 끝낸다
        break

# 모은 행들로 정해진 열 순서의 표를 만든다
df = pd.DataFrame(all_rows, columns=COLUMNS)
# 합계 행 수를 출력한다
print("합계 행 수:", len(df))
# 서로 다른 detail_url 개수를 출력한다
print("서로 다른 detail_url 개수:", df["detail_url"].nunique())

# 1행 이상일 때만 저장하고 표본을 출력한다
if len(df) > 0:
    # data 폴더가 없으면 만든다
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 인덱스 없이 엑셀에서도 한글이 보이는 utf-8-sig로 저장한다
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    # 저장한 위치를 출력한다
    print("저장:", OUT_PATH)
    # 표본 행 번호: 첫 행, 가운데 행(행 수를 2로 나눈 몫), 마지막 행
    for i in [0, len(df) // 2, len(df) - 1]:
        # 행 번호를 출력한다
        print(f"--- 행 번호 {i} ---")
        # 그 행의 모든 열을 잘리지 않게 출력한다
        print(df.iloc[i].to_string())
# 행이 하나도 없으면 저장하지 않는다
else:
    # CSV를 만들지 않았다고 출력한다
    print("CSV를 만들지 않음 (0행)")
