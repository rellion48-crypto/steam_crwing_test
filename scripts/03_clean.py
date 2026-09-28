# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# 글자 모양을 찾기 위해 정규식 re를 불러온다
import re

# 표를 다루기 위해 pandas를 불러온다
import pandas as pd
# NaN 값을 쓰기 위해 numpy를 불러온다
import numpy as np

# 프로젝트 폴더: 이 스크립트 위치의 한 단계 위(mini3-project)
BASE = Path(__file__).resolve().parent.parent
# 읽을 파일(고치지 않는다)
RAW_PATH = BASE / "data" / "raw.csv"
# 저장할 파일
CLEAN_PATH = BASE / "data" / "clean.csv"

# raw.csv를 pandas 기본 방식으로 읽는다(빈 칸은 NaN이 된다)
raw = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
# 원본을 건드리지 않도록 복사본에서 작업한다
df = raw.copy()


# 가격 글자를 원화 숫자로 바꾼다: 무료는 "무료" 그대로, ₩가 아니거나 못 읽으면 NaN
def clean_price(v):
    # 빈 칸이면 NaN을 돌려준다
    if pd.isna(v):
        # 바꿀 값이 없다
        return np.nan
    # 앞뒤 공백을 정리한다
    s = str(v).strip()
    # 무료는 글씨 그대로 둔다
    if s == "무료":
        # "무료"를 돌려준다
        return "무료"
    # "₩ 13,600" 꼴(원화 기호 + 숫자와 쉼표)인지 확인한다
    m = re.fullmatch(r"₩\s*([0-9][0-9,]*)", s)
    # 원화 꼴이면 기호와 쉼표를 떼고 정수로 바꾼다
    if m:
        # 쉼표를 뺀 숫자를 정수로 돌려준다
        return int(m.group(1).replace(",", ""))
    # 다른 통화나 알 수 없는 꼴은 환율을 모르므로 NaN으로 둔다
    return np.nan


# 할인 글자를 비율 숫자로 바꾼다: "-15%" → 0.15, 못 읽으면 NaN
def clean_discount(v):
    # 빈 칸이면 NaN을 돌려준다
    if pd.isna(v):
        # 바꿀 값이 없다
        return np.nan
    # "-15%" 꼴에서 숫자만 찾는다
    m = re.fullmatch(r"-?\s*([0-9]+(?:\.[0-9]+)?)\s*%", str(v).strip())
    # 꼴이 맞으면 100으로 나눈 비율을 돌려준다
    if m:
        # 소수 둘째 자리까지 반올림한 비율을 돌려준다
        return round(float(m.group(1)) / 100, 4)
    # 꼴이 다르면 NaN으로 둔다
    return np.nan


# 출시일 글자를 "0000.00.00" 꼴로 바꾼다: "2026년 9월 27일" → "2026.09.27", 못 읽으면 NaN
def clean_date(v):
    # 빈 칸이면 NaN을 돌려준다
    if pd.isna(v):
        # 바꿀 값이 없다
        return np.nan
    # "0000년 0월 0일" 꼴에서 연·월·일을 찾는다
    m = re.fullmatch(r"([0-9]{4})년\s*([0-9]{1,2})월\s*([0-9]{1,2})일", str(v).strip())
    # 꼴이 맞으면 월·일을 두 자리로 맞춰 이어 붙인다
    if m:
        # "연.월.일" 글자를 돌려준다
        return f"{m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}"
    # 꼴이 다르면 NaN으로 둔다
    return np.nan


# 규칙 4: name 앞뒤 공백을 정리한다(빈 칸은 그대로 NaN)
df["name"] = df["name"].map(lambda v: v.strip() if isinstance(v, str) else v)
# 공백만 있던 이름은 빈 칸(NaN)으로 본다
df["name"] = df["name"].replace("", np.nan)

# 규칙 1~3: 새 열 이름과 바꾸는 함수를 짝지어 둔다
RULES = {"price_raw": ("price", clean_price),
         "discount_raw": ("discount", clean_discount),
         "release_date_raw": ("release_date", clean_date)}
# 원본 열마다 새 열을 만든다
for raw_col, (new_col, func) in RULES.items():
    # 함수를 적용해 새 열 값을 만든다
    values = df[raw_col].map(func)
    # _raw 열 바로 옆 자리에 새 열을 끼워 넣는다
    df.insert(df.columns.get_loc(raw_col) + 1, new_col, values)

# 못 바꾼 값(원문은 있는데 새 값이 NaN)의 원문 목록을 출력한다
print("=== 못 바꾼 값 (NaN으로 둠) ===")
# 원본 열마다 확인한다
for raw_col, (new_col, _) in RULES.items():
    # 원문은 비어 있지 않은데 새 값이 NaN인 행을 고른다
    failed = df[df[raw_col].notna() & df[new_col].isna()]
    # 열 이름과 개수를 출력한다
    print(f"{raw_col} → {new_col}: {len(failed)}개")
    # 행 번호와 원문을 한 줄씩 출력한다
    for i, v in failed[raw_col].items():
        # 행 번호와 원문을 출력한다
        print(f"  행 {i}: {v!r}")

# 빼기 전 표를 따로 남겨 둔다(전후 비교용)
before = df.copy()

# 뺄 행과 사유를 담을 사전을 준비한다(행 번호 → 사유 목록)
reasons = {}
# name · price · detail_url 중 빈칸인 행을 찾는다
for col in ["name", "price", "detail_url"]:
    # 이 열이 빈칸인 행 번호마다
    for i in df.index[df[col].isna()]:
        # 사유를 붙인다
        reasons.setdefault(i, []).append(f"{col} 빈칸")
# detail_url이 앞 행과 겹치는 행을 찾는다(처음 한 행만 남긴다)
for i in df.index[df["detail_url"].notna() & df["detail_url"].duplicated(keep="first")]:
    # 사유를 붙인다
    reasons.setdefault(i, []).append("detail_url 중복")

# 뺄 행을 사유와 함께 먼저 출력한다
print()
# 제목과 개수를 출력한다
print(f"=== 뺄 행 {len(reasons)}개 ===")
# 행 번호 순서대로
for i in sorted(reasons):
    # 행 번호, 사유, 이름, 가격 원문, 주소를 출력한다
    print(f"  행 {i}: {', '.join(reasons[i])} | name={df.loc[i, 'name']!r} | price_raw={df.loc[i, 'price_raw']!r} | detail_url={df.loc[i, 'detail_url']}")

# 사유가 있는 행을 빼고 행 번호를 새로 매긴다
clean = df.drop(index=list(reasons)).reset_index(drop=True)
# clean.csv로 저장한다(인덱스 없이 utf-8-sig)
clean.to_csv(CLEAN_PATH, index=False, encoding="utf-8-sig")


# 표 하나의 요약(열별 데이터형과 빈칸 수)을 만든다
def summary(t):
    # 데이터형과 빈칸 수를 열로 가진 표를 돌려준다
    return pd.DataFrame({"데이터형": t.dtypes.astype(str), "빈칸": t.isna().sum()})


# 처리 전(raw.csv 그대로)과 처리 후(clean.csv)의 요약을 열 이름 기준으로 나란히 붙인다
side = summary(raw).join(summary(clean), how="outer", lsuffix="_전", rsuffix="_후")
# clean 열 순서대로 정렬한다
side = side.reindex(clean.columns)
# 빈칸 수는 정수로, 표에 없던 칸은 "-"로 보이게 한다
for col in side.columns:
    # 칸마다 NaN이면 "-", 빈칸 수 열이면 정수로 바꾼다
    side[col] = side[col].map(lambda x: "-" if pd.isna(x) else (int(x) if col.startswith("빈칸") else x))

# 전후 비교를 출력한다
print()
# 제목을 출력한다
print("=== 처리 전후 비교 ===")
# 행 수를 나란히 출력한다
print(f"행 수: 전 {len(raw)} → 후 {len(clean)}")
# detail_url 중복 수를 나란히 출력한다
print(f"detail_url 중복 수: 전 {raw['detail_url'].duplicated().sum()} → 후 {clean['detail_url'].duplicated().sum()}")
# 열별 데이터형과 빈칸 수를 나란히 출력한다
print(side.to_string())
# 저장한 위치를 출력한다
print()
# 저장 위치를 출력한다
print("저장:", CLEAN_PATH)
