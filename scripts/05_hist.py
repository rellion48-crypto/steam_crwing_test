# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 없이 파일로만 그리도록 matplotlib 백엔드를 Agg로 정하기 위해 불러온다
import matplotlib
# 창을 띄우지 않는 Agg 백엔드를 쓴다
matplotlib.use("Agg")
# 그림을 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# 구간별 개수를 세기 위해 numpy를 불러온다
import numpy as np
# 표를 다루기 위해 pandas를 불러온다
import pandas as pd

# 프로젝트 폴더: 이 스크립트 위치의 한 단계 위(mini3-project)
BASE = Path(__file__).resolve().parent.parent
# 읽을 파일(읽기만 한다)
CLEAN_PATH = BASE / "data" / "clean.csv"
# 저장할 그림 파일
OUT_PATH = BASE / "charts" / "hist.png"
# 고정 구간 경계(원화 가격 2250~29100에 맞춰 5000원 간격)
EDGES = [0, 5000, 10000, 15000, 20000, 25000, 30000]

# clean.csv를 pandas로 읽는다
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig")
# clean 행 수를 구한다
n = len(df)
# price 열을 숫자로 바꾼다("무료" 글씨는 NaN이 된다)
price = pd.to_numeric(df["price"], errors="coerce")
# 숫자인 가격만 남긴다
values = price.dropna()

# 구간별 개수를 센다(왼쪽 포함·오른쪽 미포함, 마지막 구간만 오른쪽 끝 포함 = numpy 규칙)
counts, _ = np.histogram(values, bins=EDGES)

# 구간별 빈도 표 머리줄을 출력한다
print("| 구간 | 개수 |")
# 표 구분줄을 출력한다
print("|---|---|")
# 구간마다 한 줄씩 출력한다
for i, c in enumerate(counts):
    # 마지막 구간이면 오른쪽 괄호를 ]로, 아니면 )로 쓴다
    right = "]" if i == len(counts) - 1 else ")"
    # 구간과 개수를 출력한다
    print(f"| [{EDGES[i]}, {EDGES[i + 1]}{right} | {c} |")
# 빈도 합을 구한다
total = int(counts.sum())
# 합계 줄을 출력한다
print(f"| 합계 | {total} |")

# 한 줄 띄운다
print()
# 빈도 합과 clean 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"빈도 합 {total} / clean 행 수 {n} → {'같음' if total == n else '다름'}")
# 구간 왼쪽 끝보다 작은 숫자 가격 개수를 출력한다
print(f"구간 밖(< {EDGES[0]}):", int((values < EDGES[0]).sum()))
# 구간 오른쪽 끝보다 큰 숫자 가격 개수를 출력한다
print(f"구간 밖(> {EDGES[-1]}):", int((values > EDGES[-1]).sum()))
# 숫자가 아니어서 빠진 price 값과 개수를 출력한다
print("숫자가 아니어서 빠진 값:", df.loc[price.isna(), "price"].value_counts(dropna=False).to_dict())

# 그림과 축을 만든다
fig, ax = plt.subplots(figsize=(8, 5))
# 구간 너비를 구한다
widths = np.diff(EDGES)
# 구간 왼쪽 끝에 맞춰 막대를 그린다(막대 사이 흰 틈 2px 정도)
bars = ax.bar(EDGES[:-1], counts, width=widths, align="edge", color="#2a78d6", edgecolor="white", linewidth=2)
# 막대마다 위에 개수를 적는다
for bar, c in zip(bars, counts):
    # 막대 가운데 위쪽에 개수 글자를 놓는다
    ax.text(bar.get_x() + bar.get_width() / 2, c, str(c), ha="center", va="bottom", color="#0b0b0b")
# 가로축 눈금을 구간 경계로 둔다
ax.set_xticks(EDGES)
# 가로축 이름을 적는다
ax.set_xlabel("Price")
# 세로축 이름을 적는다
ax.set_ylabel("Number of game")
# 제목과 n = clean 행 수를 적는다
ax.set_title(f"Game to Scrape, pages 1-3 (n = {n})")
# 개수가 모두 0이어도 축이 보이도록 세로축 최소 범위를 둔다
ax.set_ylim(0, max(1, counts.max()) * 1.15)
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
