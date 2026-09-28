# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# 수집 시각을 기록하기 위해 datetime을 불러온다
from datetime import datetime

# 웹 페이지 요청을 위해 requests를 불러온다
import requests
# HTML 해석을 위해 BeautifulSoup을 불러온다
from bs4 import BeautifulSoup
# 표를 만들고 CSV로 저장하기 위해 pandas를 불러온다
import pandas as pd

# 수집할 페이지 주소(이 페이지 하나만 요청한다)
URL = "https://store.steampowered.com/app/4656000/BOMBANANA/"
# 화면과 같은 한국어 글자로 받기 위해 스팀 언어 쿠키를 한국어로 지정한다
COOKIES = {"Steam_Language": "koreana"}
# 저장 위치: 이 스크립트 파일 위치 기준 ../data/raw_p1.csv
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_p1.csv"
# CSV 열 이름과 순서
COLUMNS = ["name", "price_raw", "discount_raw", "rating_raw",
           "release_date_raw", "category_raw", "detail_url", "scraped_at"]


# 선택자로 찾은 요소의 글자를 앞뒤 공백만 정리해 돌려주고, 없으면 빈 문자열을 돌려준다
def text_of(parent, selector):
    # 부모 요소 안에서 선택자에 맞는 첫 요소를 찾는다
    el = parent.select_one(selector) if parent else None
    # 요소가 있으면 글자를, 없으면 빈 문자열을 돌려준다
    return el.get_text(" ", strip=True) if el else ""


# 페이지를 한 번 요청한다(10초 안에 응답이 없으면 중단)
response = requests.get(URL, cookies=COOKIES, timeout=10)
# 글자가 깨지지 않게 서버가 알려준 인코딩을 쓰고, 없으면 utf-8을 쓴다
response.encoding = response.encoding or "utf-8"
# 응답 상태 코드를 출력한다
print("상태 코드:", response.status_code)

# 수집한 행을 담을 리스트를 준비한다
rows = []
# 행마다 화면에 찍힌 이름 글자를 담을 리스트를 준비한다
screen_names = []
# 상태 코드가 200일 때만 HTML을 해석한다
if response.status_code == 200:
    # 응답 HTML을 BeautifulSoup으로 해석한다
    soup = BeautifulSoup(response.text, "html.parser")
    # 게임명 요소가 있을 때만 한 행을 만든다
    if soup.select_one("#appHubAppName"):
        # 게임명 요소를 찾는다
        name_el = soup.select_one("#appHubAppName")
        # 요소에 찍힌 글자(화면 글자)를 가져온다
        screen_name = name_el.get_text(" ", strip=True)
        # title 속성에 전체 이름이 있으면 그것을, 없으면 화면 글자를 이름으로 쓴다
        full_name = (name_el.get("title") or "").strip() or screen_name
        # 화면 글자를 비교용 리스트에 넣는다
        screen_names.append(screen_name)
        # 본편 구매 칸(첫 번째 구매 영역)을 찾는다
        buy_box = soup.select_one(".game_area_purchase_game_wrapper")
        # 할인 중이면 할인가, 아니면 정가 글자를 가져온다
        price = text_of(buy_box, ".discount_final_price") or text_of(buy_box, ".game_purchase_price")
        # 첫 번째 평가 요약 줄(화면 맨 위 평가)을 찾는다
        review = soup.select_one(".user_reviews_summary_row")
        # 평가 문구와 괄호 속 평가 수를 화면 글자 그대로 이어 붙인다
        rating = (text_of(review, ".game_review_summary") + " " + text_of(review, ".responsive_hidden")).strip()
        # 장르 링크 글자들을 화면처럼 쉼표로 이어 붙인다
        genres = ", ".join(a.get_text(strip=True) for a in soup.select("#genresAndManufacturer a[href*='/genre/']"))
        # 페이지가 알려주는 대표 주소를 가져오고, 없으면 요청 주소를 쓴다
        canonical = soup.select_one("link[rel=canonical]")
        # 한 행을 딕셔너리로 만들어 리스트에 넣는다
        rows.append({
            # 게임명
            "name": full_name,
            # 현재 가격(숫자로 바꾸지 않은 화면 글자)
            "price_raw": price,
            # 현재 할인율(할인이 없으면 빈 칸)
            "discount_raw": text_of(buy_box, ".discount_pct"),
            # 별점(평가 요약과 평가 수)
            "rating_raw": rating,
            # 출시일
            "release_date_raw": text_of(soup, ".release_date .date"),
            # 게임 카테고리(장르)
            "category_raw": genres,
            # 상세 URL
            "detail_url": canonical["href"] if canonical else URL,
            # 수집한 시각
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

# 수집한 행들로 정해진 열 순서의 표를 만든다
df = pd.DataFrame(rows, columns=COLUMNS)
# 행 수를 출력한다
print("행 수:", len(df))
# 앞 3행을 출력한다
print(df.head(3).to_string())
# 화면 글자가 name과 다르거나 말줄임표(… 또는 ...)로 끝나는 행을 센다
cut_count = sum(1 for s, n in zip(screen_names, df["name"]) if s != n or s.endswith(("…", "...")))
# 잘려 보이는 이름 수를 출력한다
print("잘려 보이는 이름:", cut_count, "개")

# 상태 코드가 200이고 1행 이상일 때만 CSV를 만든다
if response.status_code == 200 and len(df) > 0:
    # data 폴더가 없으면 만든다
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 인덱스 없이 엑셀에서도 한글이 보이는 utf-8-sig로 저장한다
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    # 저장한 위치를 출력한다
    print("저장:", OUT_PATH)
# 조건을 만족하지 못하면 CSV를 만들지 않는다
else:
    # CSV를 만들지 않았다고 출력한다
    print("CSV를 만들지 않음 (200이 아니거나 0행)")
