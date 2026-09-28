# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 표를 다루기 위해 pandas를 불러온다
import pandas as pd

# 읽을 파일: 이 스크립트 위치 기준 ../data/clean.csv (읽기만 한다)
CLEAN_PATH = Path(__file__).resolve().parent.parent / "data" / "clean.csv"

# clean.csv를 pandas로 읽는다
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig")
# price 열을 숫자로 바꾼다("무료" 같은 글씨는 0으로 채우지 않고 NaN이 된다)
price = pd.to_numeric(df["price"], errors="coerce")
# 숫자로 바뀌지 않은 원문 값과 그 개수를 센다(원래 빈칸은 제외)
non_numeric = df.loc[price.isna() & df["price"].notna(), "price"].value_counts()

# "무료"만 0으로 환산한 비교용 price를 따로 만든다(원래 빈칸은 그대로 NaN)
price_zero = price.where(df["price"] != "무료", 0)
# 0 환산 기준 개수를 구한다
count_z = int(price_zero.count())
# 0 환산 기준 최댓값이 처음 나오는 행 번호를 구한다
max_z_i = price_zero.idxmax()
# 0 환산 기준 평균을 소수 둘째 자리까지 맞춘 글자로 만든다
mean_z_text = f"{price_zero.mean():.2f}"
# 0 환산 기준 중앙값을 계산된 그대로 구한다
median_z = price_zero.median()

# 숫자 price 개수를 구한다
count = int(price.count())
# 최솟값이 처음 나오는 행 번호를 구한다
min_i = price.idxmin()
# 최댓값이 처음 나오는 행 번호를 구한다
max_i = price.idxmax()
# 평균을 소수 둘째 자리까지 맞춘 글자로 만든다
mean_text = f"{price.mean():.2f}"
# 중앙값을 계산된 그대로 구한다
median = price.median()

# 마크다운 표 머리줄을 출력한다
print("| 항목 | 값 |")
# 마크다운 표 구분줄을 출력한다
print("|---|---|")
# 개수 줄을 출력한다(괄호 안은 무료를 0으로 환산한 값)
print(f"| 개수 | {count} ({count_z}) |")
# 최소 줄을 그 행의 name, price와 함께 출력한다(0 환산 값은 붙이지 않는다)
print(f"| 최소 | {price[min_i]:g} (name: {df.loc[min_i, 'name']}, price: {df.loc[min_i, 'price']}) |")
# 최대 줄을 그 행의 name, price와 함께 출력한다(괄호 안은 0 환산 값)
print(f"| 최대 | {price[max_i]:g} (name: {df.loc[max_i, 'name']}, price: {df.loc[max_i, 'price']}) ({price_zero[max_z_i]:g}) |")
# 평균 줄을 출력한다(괄호 안은 0 환산 값)
print(f"| 평균 | {mean_text} ({mean_z_text}) |")
# 중앙값 줄을 계산된 그대로 출력한다(괄호 안은 0 환산 값)
print(f"| 중앙값 | {median} ({median_z}) |")

# 범주 열: rating_raw의 <br> 앞 글자를 범주로 보고, 빈칸은 "(빈칸)"으로 둔다
category = df["rating_raw"].map(lambda v: v.split("<br>")[0].strip() if isinstance(v, str) else "(빈칸)")
# 범주 값별 행 수를 센다(많은 순)
cat_counts = category.value_counts()
# 범주 값마다 한 줄씩 출력한다
for cat, n in cat_counts.items():
    # 범주 이름과 행 수를 표 줄로 출력한다
    print(f"| 범주 {cat} | {n}행 |")
# 빈칸을 뺀 실제 범주들만 고른다
real_counts = cat_counts.drop("(빈칸)", errors="ignore")
# 실제 범주가 있으면 가장 적은 행 수와 그 범주들을 출력한다
if len(real_counts) > 0:
    # 가장 적은 행 수를 구한다
    fewest = int(real_counts.min())
    # 그 행 수를 가진 범주 이름들을 모은다
    fewest_names = ", ".join(real_counts[real_counts == fewest].index)
    # 가장 적은 범주 줄을 출력한다
    print(f"| 가장 적은 범주 | {fewest}행 ({fewest_names}) |")

# 한 줄 띄운다
print()
# 최솟값과 같은 값을 가진 행 수를 출력한다(동점 확인)
print("최솟값과 같은 행 수:", int((price == price[min_i]).sum()))
# 최댓값과 같은 값을 가진 행 수를 출력한다(동점 확인)
print("최댓값과 같은 행 수:", int((price == price[max_i]).sum()))
# 숫자로 바뀌지 않아 통계에서 빠진 값을 출력한다
print("통계에서 빠진 값:", non_numeric.to_dict())
# 개수와 전체 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"price 개수 {count} / clean.csv 전체 행 수 {len(df)} → {'같음' if count == len(df) else '다름'}")
