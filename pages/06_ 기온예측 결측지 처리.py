import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# 페이지 설정
st.set_page_config(
    page_title="기온 데이터 분석 및 예측 비교", page_icon="🌡️", layout="wide"
)

st.title("🌡️ 결측치 처리 방식 & 머신러닝 알고리즘별 기온 예측 비교")
st.markdown(
    "사이드바에서 **결측치 처리 방식**과 **조회할 월**, **미래 예측 연도**를 선택하여 예측 결과의 변화를 확인해보세요."
)


# 데이터 로드 함수
@st.cache_data
def load_data():
  try:
    df = pd.read_csv("temperature.csv", encoding="cp949")
  except:
    df = pd.read_csv("temperature.csv", encoding="utf-8")
  return df


try:
  df = load_data()
except Exception as e:
  st.error(f"데이터 파일을 불러오는 중 오류가 발생했습니다: {e}")
  st.stop()


# 날짜 파싱 함수 ('Oct-07' 형태 변환)
def parse_date_str(val):
  try:
    parts = str(val).split("-")
    if len(parts) != 2:
      return None, None
    m_str, y_str = parts[0], int(parts[1])
    year = 2000 + y_str if y_str <= 26 else 1900 + y_str

    month_map = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
    return year, month_map.get(m_str, None)
  except:
    return None, None


years, months = [], []
for idx, row in df.iterrows():
  y, m = parse_date_str(row["일시"])
  years.append(y)
  months.append(m)

df["Year"] = years
df["Month"] = months

# 1907 ~ 2025년 범위만 필터링
df_filtered = df[(df["Year"] >= 1907) & (df["Year"] <= 2025)].copy()

# ==========================================
# 사이드바: 사용자 설정
# ==========================================
st.sidebar.header("⚙️ 분석 설정 옵션")

# 1. 월 선택
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월",
}
selected_month_num = st.sidebar.selectbox(
    "조회할 월 선택",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x],
    index=6,  # 기본값 7월
)

# 2. 결측치 처리 방식 선택
impute_method = st.sidebar.selectbox(
    "결측치 처리 방식 선택",
    options=["1. 제거 (Drop)", "2. 중앙값 대체 (Median)", "3. 선형보간법 (Interpolation)"],
    index=2,  # 기본값 선형보간법
)

# 3. 미래 예측 연도 입력
target_prediction_year = st.sidebar.number_input(
    "미래 예측 연도 입력", min_value=2026, max_value=2100, value=2050, step=1
)

# ==========================================
# 데이터 가공 및 결측치 처리 적용
# ==========================================
# 특정 월 데이터만 추출
df_month = (
    df_filtered[df_filtered["Month"] == selected_month_num]
    .sort_values("Year")
    .reset_index(drop=True)
)

# 연도가 빠짐없이 존재하도록 전체 연도(1907~2025) 인덱스 생성 후 병합 (보간법을 위해 필요)
all_years_df = pd.DataFrame(
    {"Year": range(int(df_month["Year"].min()), int(df_month["Year"].max()) + 1)}
)
df_month = pd.merge(all_years_df, df_month, on="Year", how="left")
df_month["Month"] = selected_month_num

# 결측치 처리 로직 수행
missing_count_before = df_month["평균기온(℃)"].isnull().sum()

if "1. 제거" in impute_method:
  df_processed = df_month.dropna(subset=["평균기온(℃)"]).copy()
  impute_desc = "결측치가 있는 연도를 데이터셋에서 완전히 제거했습니다."
elif "2. 중앙값" in impute_method:
  df_processed = df_month.copy()
  median_val = df_processed["평균기온(℃)"].median()
  df_processed["평균기온(℃)"] = df_processed["평균기온(℃)"].fillna(median_val)
  impute_desc = f"결측치를 전체 기간 중앙값({median_val:.2f}℃)으로 대체했습니다."
else:  # 선형보간법
  df_processed = df_month.copy()
  df_processed["평균기온(℃)"] = df_processed["평균기온(℃)"].interpolate(
      method="linear"
  )
  # 앞뒤 남은 결측치는 전/후 값으로 채우기
  df_processed["평균기온(℃)"] = (
      df_processed["평균기온(℃)"].bfill().ffill()
  )
  impute_desc = (
      "결측치 앞뒤의 값을 연결하는 선형보간법(Interpolation)을 적용했습니다."
  )

st.info(
    f"🔍 **선택한 결측치 처리 결과**: 총 {missing_count_before개의 누락된 기온 데이터가 존재했으며, {impute_desc}"
)

# ==========================================
# 시각화 1: 선택한 월의 과거 기온 변화
# ==========================================
st.subheader(
    f"📊 1907 ~ 2025년 {month_names[selected_month_num]} 평균기온 추이"
)

fig_hist = px.line(
    df_processed,
    x="Year",
    y="평균기온(℃)",
    title=f"{month_names[selected_month_num]} 기온 변화 추이 (결측치 처리 적용됨)",
    markers=True,
)
st.plotly_chart(fig_hist, use_container_width=True)

# ==========================================
# 머신러닝 예측 모델 학습 (3가지 알고리즘)
# ==========================================
X = df_processed[["Year"]].values
y = df_processed["평균기온(℃)"].values

future_years = np.arange(int(X.min()), target_prediction_year + 1).reshape(
    -1, 1
)

# 1) 선형 회귀
lin_reg = LinearRegression()
lin_reg.fit(X, y)
pred_lin = lin_reg.predict(future_years)

# 2) 다항 회귀 (2차)
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)
future_X_poly = poly.transform(future_years)
poly_reg = LinearRegression()
poly_reg.fit(X_poly, y)
pred_poly = poly_reg.predict(future_X_poly)

# 3) 랜덤 포레스트
rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg.fit(X, y)
pred_rf = rf_reg.predict(future_years)

# 결과 통합 데이터프레임
df_pred_all = pd.DataFrame(
    {
        "Year": np.tile(future_years.flatten(), 3),
        "Temperature": np.concatenate([pred_lin, pred_poly, pred_rf]),
        "Algorithm": (
            ["선형 회귀 (Linear Regression)"] * len(future_years)
            + ["다항 회귀 (Polynomial Reg, 2차)"] * len(future_years)
            + ["랜덤 포레스트 (Random Forest)"] * len(future_years)
        ),
    }
)

# ==========================================
# 시각화 2: 3가지 알고리즘 예측 비교 그래프
# ==========================================
st.markdown("---")
st.subheader(
    f"🤖 3가지 머신러닝 알고리즘별 {target_prediction_year}년 기온 예측 비교"
)

fig_pred = go.Figure()

# 실제 기온 데이터 포인트
fig_pred.add_trace(
    go.Scatter(
        x=df_processed["Year"],
        y=y,
        mode="markers",
        name="처리된 실제 기온",
        marker=dict(color="black", size=5),
    )
)

colors = {
    "선형 회귀 (Linear Regression)": "blue",
    "다항 회귀 (Polynomial Reg, 2차)": "orange",
    "랜덤 포레스트 (Random Forest)": "green",
}

for algo in df_pred_all["Algorithm"].unique():
  subset = df_pred_all[df_pred_all["Algorithm"] == algo]
  fig_pred.add_trace(
      go.Scatter(
          x=subset["Year"],
          y=subset["Temperature"],
          mode="lines",
          name=algo,
          line=dict(color=colors.get(algo, "gray"), width=2.5),
      )
  )

fig_pred.update_layout(
    title=f"알고리즘별 예측 비교 ({month_names[selected_month_num]})",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
)

st.plotly_chart(fig_pred, use_container_width=True)

# ==========================================
# 알고리즘 작동 원리 설명 및 해석
# ==========================================
st.markdown("### 💡 그래프로 보는 알고리즘별 작동 원리 및 특징")

st.markdown("""
1. **파란색 선 (선형 회귀, Linear Regression)**
   * **작동 원리**: 전체 데이터를 가장 잘 대변하는 **하나의 곧은 직선**을 찾습니다. 과거부터 현재까지 일정한 증가/감소 추세가 이어질 것이라는 가정하에 작동합니다.
   * **그래프 특징**: 미래로 갈수록 일정한 기울기로 온도가 계속해서 오르거나 내려가는 정직한 직선 형태를 띱니다.

2. **주황색 곡선 (다항 회귀, Polynomial Regression)**
   * **작동 원리**: 선형 회귀를 발전시켜 데이터의 **곡선 형태(비선형 패턴)**를 학습할 수 있도록 차수를 높인 모델입니다.
   * **그래프 특징**: 최근 들어 기온 상승 폭이 가파라지는 경향을 곡선 형태로 유연하게 따라갑니다. 다만 멀고 먼 미래를 예측할 때 곡선이 급격하게 솟구칠 수 있습니다.

3. **초록색 선 (랜덤 포레스트, Random Forest)**
   * **작동 원리**: 수많은 의사결정 나무(Decision Tree)를 결합하여 데이터의 복잡한 구간별 특징을 조각조각 나누어 학습합니다.
   * **그래프 특징**: 과거 데이터 구간 내에서는 구불구불한 세부 변동을 잘 잡아내지만, **학습 데이터의 최댓값(2025년)을 벗어나는 순간 더 이상 온도가 변하지 않고 마지막 값에서 수평(일직선)**으로 멈추는 특성이 있습니다. (트리 기반 모델은 범위 밖을 외삽하지 못하기 때문입니다.)
""")

# 최종 예측값 요약 표
st.markdown("---")
st.subheader(f"📌 {target_prediction_year}년도 알고리즘별 최종 예측 기온")
latest_preds = df_pred_all[df_pred_all["Year"] == target_prediction_year]
st.dataframe(
    latest_preds[["Algorithm", "Temperature"]].rename(
        columns={"Algorithm": "예측 알고리즘", "Temperature": f"{target_prediction_year}년 예측 기온(℃)"}
    ),
    use_container_width=True,
)
