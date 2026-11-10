import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# 페이지 설정
st.set_page_config(
    page_title="기온 데이터 분석 및 미래 예측", page_icon="🌡️", layout="wide"
)

st.title("🌡️ 연도별 월 평균 기온 분석 및 머신러닝 예측")
st.markdown(
    "업로드된 기온 데이터(`temperature.csv`)를 바탕으로 특정 월의 과거 변화 추이를 살펴보고, 세 가지 대표 예측 알고리즘으로 미래 기온을 예측·비교합니다."
)


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  # 인코딩 오류 방지를 위해 cp949 시도 후 utf-8 시도
  try:
    df = pd.read_csv("temperature.csv", encoding="cp949")
  except:
    df = pd.read_csv("temperature.csv", encoding="utf-8")
  return df


try:
  df = load_data()
except Exception as e:
  st.error(
    f"데이터 파일을 불러오는 중 오류가 발생했습니다. 'temperature.csv' 파일이 같은 폴더에 있는지 확인해주세요. (오류: {e})"
  )
  st.stop()


# 데이터 전처리
# '일시' 컬럼 예: 'Oct-07' -> 월과 연도로 분리
# 07은 1907년인지 2007년인지 확인 필요 (일반적으로 1907~2025이므로 00~25는 2000년대, 07~99는 1900년대 혹은 데이터 범위에 맞게 조정)
def parse_date_str(val):
  try:
    parts = val.split("-")
    if len(parts) != 2:
      return None, None
    m_str, y_str = parts[0], int(parts[1])
    # 연도 변환 규칙 (00~25는 2000년대, 07~99는 1900년대 또는 데이터 구조에 맞춤)
    if y_str <= 26:
      year = 2000 + y_str
    else:
      year = 1900 + y_str

    # 월 영문 매핑
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
    month = month_map.get(m_str, None)
    return year, month
  except:
    return None, None


years = []
months = []
for idx, row in df.iterrows():
  y, m = parse_date_str(str(row["일시"]))
  years.append(y)
  months.append(m)

df["Year"] = years
df["Month"] = months

# 결측치 제거 및 연도 범위 필터링 (1907 ~ 2025)
df_clean = df.dropna(subset=["Year", "Month", "평균기온(℃)"])
df_clean = df_clean[
    (df_clean["Year"] >= 1907) & (df_clean["Year"] <= 2025)
].copy()

# 사이드바 설정: 사용자 입력
st.sidebar.header("⚙️ 분석 설정")

# 2. 사용자가 월을 선택
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
    "조회할 월을 선택하세요",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x],
    index=6,  # 기본값 7월
)

# 3. 사용자가 예측 연도 입력
max_year_in_data = int(df_clean["Year"].max())
target_prediction_year = st.sidebar.number_input(
    "미래 예측 연도 입력",
    min_value=max_year_in_data + 1,
    max_value=2100,
    value=2050,
    step=1,
)

# 선택된 월 데이터 필터링
df_month = (
    df_clean[df_clean["Month"] == selected_month_num]
    .sort_values("Year")
    .reset_index(drop=True)
)

st.subheader(
    f"📊 1907 ~ 2025년 {month_names[selected_month_num]} 평균기온 추이"
)

import plotly.express as px

fig_hist = px.line(
    df_month,
    x="Year",
    y="평균기온(℃)",
    title=f"{month_names[selected_month_num]} 과거 기온 변화 (1907~2025)",
    markers=True,
)
st.plotly_chart(fig_hist, use_container_width=True)

# 4 & 5. 3가지 예측 알고리즘 적용 및 비교
st.markdown("---")
st.subheader(
    f"🤖 3가지 대표 머신러닝 알고리즘을 이용한 {target_prediction_year}년 기온 예측 비교"
)

X = df_month[["Year"]].values
y = df_month["평균기온(℃)"].values

# 미래 예측용 연도 범위 생성 (과거 데이터 연도 + 예측 연도)
future_years = np.arange(int(X.min()), target_prediction_year + 1).reshape(
    -1, 1
)

# 1) 선형 회귀 (Linear Regression)
lin_reg = LinearRegression()
lin_reg.fit(X, y)
pred_lin = lin_reg.predict(future_years)

# 2) 다항 회귀 (Polynomial Regression, 차수=2)
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)
future_X_poly = poly.transform(future_years)
poly_reg = LinearRegression()
poly_reg.fit(X_poly, y)
pred_poly = poly_reg.predict(future_X_poly)

# 3) 랜덤 포레스트 (Random Forest Regressor)
rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg.fit(X, y)
pred_rf = rf_reg.predict(future_years)

# 결과를 데이터프레임으로 통합하여 Plotly로 시각화
df_pred_all = pd.DataFrame(
    {
        "Year": np.tile(future_years.flatten(), 3),
        "Temperature": np.concatenate([pred_lin, pred_poly, pred_rf]),
        "Algorithm": (
            ["Linear Regression"] * len(future_years)
            + ["Polynomial Regression (Deg 2)"] * len(future_years)
            + ["Random Forest"] * len(future_years)
        ),
    }
)

import plotly.graph_objects as go

fig_pred = go.Figure()

# 실제 데이터 산점도/선
fig_pred.add_trace(
    go.Scatter(
        x=df_month["Year"],
        y=y,
        mode="markers",
        name="실제 기온 (1907~2025)",
        marker=dict(color="black", size=6),
    )
)

# 알고리즘별 예측선 추가
colors = {
    "Linear Regression": "blue",
    "Polynomial Regression (Deg 2)": "orange",
    "Random Forest": "green",
}
for algo in df_pred_all["Algorithm"].unique():
  subset = df_pred_all[df_pred_all["Algorithm"] == algo]
  fig_pred.add_trace(
      go.Scatter(
          x=subset["Year"],
          y=subset["Temperature"],
          mode="lines",
          name=algo,
          line=dict(color=colors.get(algo, "gray"), width=2),
      )
  )

fig_pred.update_layout(
    title=f"알고리즘별 {month_names[selected_month_num]} 기온 예측 비교 그래프",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
)

st.plotly_chart(fig_pred, use_container_width=True)

# 5. 알고리즘 작동 원리 및 특징 설명
st.markdown("### 📝 알고리즘별 작동 방식 및 그래프 해석 가이드")

st.markdown("""
- **1. 선형 회귀 (Linear Regression, 파란색 선)**
  - **작동 방식:** 과거 데이터의 전체적인 흐름을 하나의 '직선'으로 표현합니다. 최소제곱법을 이용해 오차가 가장 적은 직선의 기울기와 절편을 찾습니다.
  - **그래프 해석:** 과거부터 현재까지 기온이 일정한 비율(기울기)로 꾸준히 상승 또는 하강한다고 가정할 때 유용합니다. 단순하고 직관적이지만, 미래에 기온 상승 속도가 가속화되는 비선형적 변화를 담아내기엔 한계가 있습니다.

- **2. 다항 회귀 (Polynomial Regression, 주황색 곡선)**
  - **작동 방식:** 선형 회귀를 확장하여, 연도 데이터에 제곱($X^2$) 등의 다항식 항을 추가해 '곡선' 형태로 트렌드를 학습합니다.
  - **그래프 해석:** 기온 변화가 시간이 흐를수록 더 가파르게 변하는(가속화되는) 장기적인 기후 변화 경향을 곡선 형태로 유연하게 반영할 수 있습니다. 다만, 예측 연도가 너무 멀어지면 곡선이 급격하게 꺾이는 과적합(Overfitting) 현상이 발생할 수 있습니다.

- **3. 랜덤 포레스트 (Random Forest, 초록색 계단식/구간별 선)**
  - **작동 방식:** 여러 개의 의사결정 나무(Decision Tree)를 숲처럼 묶어 이들의 예측 평균을 사용하는 앙상블 학습법입니다. 데이터의 비선형 패턴과 임계점 효과를 잘 포착합니다.
  - **그래프 해석:** 학습 데이터 범위 내에서는 복잡하고 세밀한 변동을 잘 잡아내지만, **학습한 최대 연도(2025년)를 벗어난 미래 구간에서는 더 이상 온도가 오르지 않고 마지막 학습된 값이나 최근 평균 수준에서 일직선(수평)으로 고정**되는 특성이 있습니다. (트리 기반 모델은 범위 밖의 값을 외삽(Extrapolation)하지 못하기 때문입니다.)
""")

# 최종 예측값 비교 표 제공
st.markdown("---")
st.subheader(f"📌 {target_prediction_year}년도 알고리즘별 예측 기온 요약")
latest_preds = df_pred_all[df_pred_all["Year"] == target_prediction_year]
st.dataframe(
    latest_preds[["Algorithm", "Temperature"]].rename(
        columns={"Algorithm": "예측 알고리즘", "Temperature": "예측 평균기온(℃)"}
    ),
    use_container_width=True,
)
