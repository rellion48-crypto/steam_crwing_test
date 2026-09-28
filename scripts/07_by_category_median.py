# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 없이 파일로만 그리도록 matplotlib 백엔드를 Agg로 정하기 위해 불러온다
import matplotlib
# 창을 띄우지 않는 Agg 백엔드를 쓴다
matplotlib.use("Agg")
# 그림을 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# 표를 다루기 위해 pandas를 불러온다
import pandas as pd

# 프로젝트 폴더: 이 스크립트 위치의 한 단계 위(mini3-project)
BASE = Path(__file__).resolve().parent.parent
# 읽을 파일(읽기만 한다)
CLEAN_PATH = BASE / "data" / "clean.csv"
# 저장할 그림 파일(by_category.png와 다른 이름)
OUT_PATH = BASE / "charts" / "by_category_median.png"

# clean.csv를 pandas로 읽는다
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig")
# clean 행 수를 구한다
n = len(df)
# price 열을 숫자로 바꾼다("무료" 글씨는 0으로 채우지 않고 NaN이 된다)
df["price_num"] = pd.to_numeric(df["price"], errors="coerce")
# 범주 열의 빈칸은 "(빈칸)"으로 둔다(06_by_category.py와 같은 그룹)
df["category"] = df["release_date"].fillna("(빈칸)")
# 범주를 파일에 처음 나온 순서 그대로 모은다
order = list(dict.fromkeys(df["category"]))
# 범주별 숫자 가격 개수와 중앙값을 구하고 처음 나온 순서로 맞춘다
g = df.groupby("category", sort=False)["price_num"].agg(["count", "median"]).reindex(order)

# 그룹별 표 머리줄을 출력한다
print("| 범주 | 개수 | 중앙값 |")
# 표 구분줄을 출력한다
print("|---|---|---|")
# 범주마다 한 줄씩 출력한다
for cat, r in g.iterrows():
    # 숫자 가격이 없으면 "자료 없음", 있으면 소수 둘째 자리까지 적는다
    med = "자료 없음" if r["count"] == 0 else f"{r['median']:.2f}"
    # 범주·개수·중앙값 줄을 출력한다
    print(f"| {cat} | {int(r['count'])} | {med} |")
# 한 줄 띄운다
print()
# 개수 합과 clean 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"개수 합 {int(g['count'].sum())} / clean 행 수 {n} → {'같음' if int(g['count'].sum()) == n else '다름'}")
# 숫자 가격이 가장 큰 행 번호를 구한다
max_i = df["price_num"].idxmax()
# 가장 큰 값과 그 행의 이름·그룹을 출력한다
print(f"가장 큰 price: {df.loc[max_i, 'price_num']:g} (name: {df.loc[max_i, 'name']}, 그룹: {df.loc[max_i, 'category']})")

# 그림과 축을 만든다
fig, ax = plt.subplots(figsize=(8, 5))
# 가로축 자리 번호를 범주 순서대로 만든다
xs = list(range(len(order)))
# 범주마다 막대를 그린다
for x, cat in zip(xs, order):
    # 이 범주의 개수를 꺼낸다
    cnt = int(g.loc[cat, "count"])
    # 자료가 없으면 막대를 그리지 않는다
    if cnt == 0:
        # 다음 범주로 넘어간다
        continue
    # 이 범주의 중앙값을 꺼낸다
    med = g.loc[cat, "median"]
    # 중앙값 높이의 막대를 그린다
    ax.bar(x, med, width=0.6, color="#2a78d6")
    # 막대 위에 중앙값과 n을 두 줄로 적는다
    ax.text(x, med, f"{med:.2f}\nn = {cnt}", ha="center", va="bottom", color="#0b0b0b")
# 가로축 눈금 자리를 범주 순서대로 둔다
ax.set_xticks(xs)
# 가로축 눈금 글자를 범주 이름으로 적는다
ax.set_xticklabels(order)
# 가로축 이름을 적는다(06_by_category.py와 같은 글자)
ax.set_xlabel("Relesase_date")
# 세로축 이름을 적는다
ax.set_ylabel("Median price")
# 제목과 n = clean 행 수를 적는다(06_by_category.py 제목에서 Average만 Median으로)
ax.set_title(f"Median price by rating, n = {n}")
# 막대 위 두 줄 글자가 들어가도록 세로축 위쪽을 넉넉히 둔다
ax.set_ylim(0, g["median"].max() * 1.25)
# 위쪽·오른쪽 테두리를 지워 축을 가볍게 한다
ax.spines[["top", "right"]].set_visible(False)
# charts 폴더가 없으면 만든다
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
# 그림을 파일로 저장한다(plt.show는 쓰지 않는다)
fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
# 그림을 닫아 메모리를 비운다
plt.close(fig)
# 저장한 위치를 출력한다
print("저장:", OUT_PATH)
