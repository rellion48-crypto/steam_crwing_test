# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 읽을 파일: 이 스크립트 파일 위치 기준 ../data/raw.csv
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "raw.csv"

# 값을 고치지 않도록 모든 열을 글자로, 빈 칸도 빈 문자열 그대로 읽는다
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", dtype=str, keep_default_na=False)
# 전체 행 수를 출력한다
print("전체 행 수:", len(df))

# 02_collect.py는 페이지마다 scraped_at을 한 번 기록하므로, 처음 나온 순서대로 페이지를 나눈다
for page, (stamp, group) in enumerate(df.groupby("scraped_at", sort=False), start=1):
    # 이 페이지의 첫 행 번호와 끝 행 번호를 구한다
    first_i, last_i = group.index[0], group.index[-1]
    # 페이지 번호, 수집 시각, 행 번호 범위, 행 수를 출력한다
    print(f"--- {page}페이지 (scraped_at {stamp}) | 행 번호 {first_i}~{last_i} | {len(group)}행")
    # 첫 이름을 출력한다
    print(f"첫 이름: {df.loc[first_i, 'name']}")
    # 끝 이름을 출력한다
    print(f"끝 이름: {df.loc[last_i, 'name']}")

# 페이지 사이에 겹친 게임이 있는지 보려고 detail_url이 두 번 이상 나온 행 수를 센다
dup_count = df["detail_url"].duplicated(keep=False).sum()
# 겹친 행 수를 출력한다
print("detail_url이 겹친 행 수:", dup_count)
