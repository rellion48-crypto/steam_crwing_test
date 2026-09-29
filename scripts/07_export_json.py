# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# JSON 파일을 쓰고 읽기 위해 json을 불러온다
import json

# 표를 다루기 위해 pandas를 불러온다
import pandas as pd

# 프로젝트 폴더: 이 스크립트 위치의 한 단계 위(mini3-project)
BASE = Path(__file__).resolve().parent.parent
# 읽을 파일(고치지 않는다)
CLEAN_PATH = BASE / "data" / "clean.csv"
# 저장할 JSON 파일
JSON_PATH = BASE / "data" / "data.json"
# 고를 열과 순서
COLS = ["name", "price", "release_date", "scraped_at", "detail_url"]

# clean.csv를 값 그대로(글자로, 빈 칸도 빈 문자열로) 읽는다
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", dtype=str, keep_default_na=False)
# 필요한 네 열만 고른다
out = df[COLS].copy()
# price가 숫자 글자면 정수로, "무료" 같은 글씨는 그대로 둔다
out["price"] = out["price"].map(lambda v: int(v) if v.isdigit() else v)
# 한 행을 한 묶음(사전)으로 하는 목록으로 바꾼다
records = out.to_dict(orient="records")

# data.json을 utf-8로 연다
with open(JSON_PATH, "w", encoding="utf-8") as f:
    # 한글을 그대로 두고(ensure_ascii=False) 2칸 들여쓰기로 저장한다
    json.dump(records, f, ensure_ascii=False, indent=2)

# 저장한 data.json을 utf-8로 다시 연다
with open(JSON_PATH, encoding="utf-8") as f:
    # JSON을 목록으로 읽는다
    loaded = json.load(f)

# 항목 수와 clean.csv 행 수가 같은지 구한다
same = len(loaded) == len(df)
# 항목 수와 clean.csv 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"data.json 항목 수 {len(loaded)} / clean.csv 행 수 {len(df)} → {'같음' if same else '다름'}")
# 한 줄 띄운다
print()
# 비교 표 머리줄을 출력한다
print("| 열 | data.json 첫 항목 | clean.csv 첫 줄 |")
# 비교 표 구분줄을 출력한다
print("|---|---|---|")
# 네 열마다 두 값을 나란히 출력한다
for c in COLS:
    # JSON 값(형 포함)과 CSV 글자를 repr로 보여 준다
    print(f"| {c} | {loaded[0][c]!r} | {df.loc[0, c]!r} |")
# 저장한 위치를 출력한다
print()
# 저장 위치를 출력한다
print("저장:", JSON_PATH)
