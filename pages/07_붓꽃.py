
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------
st.set_page_config(
    page_title="Iris Flower Classifier",
    page_icon="🌸",
    layout="wide"
)

# ----------------------------------
# 2. 디자인
# ----------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #fff8fb;
}
h1 {
    color: #d85b91;
}
h2, h3 {
    color: #bd5c88;
}
div[data-testid="stMetric"] {
    background-color: #fff0f6;
    padding: 18px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌸 Iris Flower Classifier")
st.subheader("꽃잎의 크기로 붓꽃 품종을 예측해 보세요!")

st.write(
    "꽃잎길이와 꽃잎너비를 입력하면 "
    "KNN 알고리즘이 가장 가까운 데이터를 비교하여 "
    "붓꽃의 품종을 예측합니다."
)

# ----------------------------------
# 3. 아이리스 데이터 불러오기
# ----------------------------------
iris = load_iris()

X = iris.data[:, [2, 3]]

species_names = {
    "setosa": "세토사 (Setosa)",
    "versicolor": "버시컬러 (Versicolor)",
    "virginica": "버지니카 (Virginica)"
}

y = np.array([
    species_names[iris.target_names[i]]
    for i in iris.target
])

df = pd.DataFrame(
    X,
    columns=["꽃잎길이", "꽃잎너비"]
)

df["품종"] = y

# ----------------------------------
# 4. KNN 모델 생성
# ----------------------------------
model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# ----------------------------------
# 5. 사용자 입력
# ----------------------------------
st.markdown("---")
st.header("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎길이 (cm)",
        min_value=0.1,
        max_value=7.0,
        value=1.5,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "꽃잎너비 (cm)",
        min_value=0.1,
        max_value=3.0,
        value=0.3,
        step=0.1
    )

# ----------------------------------
# 6. 품종 예측
# ----------------------------------
input_data = np.array([
    [petal_length, petal_width]
])

prediction = model.predict(input_data)[0]
probabilities = model.predict_proba(input_data)[0]

class_names = model.named_steps["knn"].classes_

confidence = probabilities[
    list(class_names).index(prediction)
] * 100

st.markdown("---")
st.header("🔍 품종 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.metric(
        label="예측된 붓꽃 품종",
        value=prediction
    )

with result_col2:
    st.metric(
        label="가까운 5개 데이터 중 해당 품종 비율",
        value=f"{confidence:.0f}%"
    )

st.success(
    f"입력한 꽃잎 크기는 **{prediction}**으로 분류되었습니다!"
)

# ----------------------------------
# 7. 가장 가까운 데이터 5개 찾기
# ----------------------------------
scaler = model.named_steps["scaler"]
knn = model.named_steps["knn"]

scaled_input = scaler.transform(input_data)

distances, indices = knn.kneighbors(
    scaled_input,
    n_neighbors=5
)

neighbors = df.iloc[indices[0]].copy()

neighbors["거리"] = distances[0].round(3)

# ----------------------------------
# 8. 시각화 영역 생성
# ----------------------------------
st.markdown("---")
st.header("📊 붓꽃 품종 분류 시각화")

st.write(
    "그래프의 배경색은 KNN 모델이 예측한 품종별 영역입니다. "
    "핑크색 하트는 사용자가 입력한 위치이며, "
    "테두리가 있는 원은 가장 가까운 5개의 데이터입니다."
)

# 그래프 범위
x_min = max(0, X[:, 0].min() - 0.5)
x_max = X[:, 0].max() + 0.5

y_min = max(0, X[:, 1].min() - 0.3)
y_max = X[:, 1].max() + 0.3

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 180),
    np.linspace(y_min, y_max, 180)
)

grid = np.c_[xx.ravel(), yy.ravel()]

Z = model.predict(grid)

# 품종별 숫자 변환
class_to_num = {
    name: i for i, name in enumerate(class_names)
}

Z_num = np.array([
    class_to_num[name] for name in Z
]).reshape(xx.shape)

# 품종별 색상
colors = {
    "세토사 (Setosa)": "#8ecae6",
    "버시컬러 (Versicolor)": "#a8d5a2",
    "버지니카 (Virginica)": "#f6c58c"
}

fig = go.Figure()

# ----------------------------------
# 9. 품종별 예측 영역
# ----------------------------------
colorscale = [
    [0.0, "#d9efff"],
    [1/3 - 0.001, "#d9efff"],
    [1/3, "#e0f2dc"],
    [2/3 - 0.001, "#e0f2dc"],
    [2/3, "#ffebd5"],
    [1.0, "#ffebd5"]
]

fig.add_trace(go.Heatmap(
    x=np.linspace(x_min, x_max, 180),
    y=np.linspace(y_min, y_max, 180),
    z=Z_num,
    colorscale=colorscale,
    zmin=-0.5,
    zmax=2.5,
    showscale=False,
    opacity=0.65,
    hoverinfo="skip"
))

# ----------------------------------
# 10. 실제 붓꽃 데이터 표시
# ----------------------------------
for species, color in colors.items():

    subset = df[df["품종"] == species]

    fig.add_trace(go.Scatter(
        x=subset["꽃잎길이"],
        y=subset["꽃잎너비"],
        mode="markers",
        name=species,
        marker=dict(
            color=color,
            size=8,
            line=dict(color="white", width=1)
        ),
        hovertemplate=(
            "꽃잎길이: %{x:.1f}cm<br>"
            "꽃잎너비: %{y:.1f}cm<br>"
            f"품종: {species}<extra></extra>"
        )
    ))

# ----------------------------------
# 11. 가장 가까운 5개 데이터 강조
# ----------------------------------
fig.add_trace(go.Scatter(
    x=neighbors["꽃잎길이"],
    y=neighbors["꽃잎너비"],
    mode="markers",
    name="가장 가까운 5개 데이터",
    marker=dict(
        symbol="circle-open",
        size=19,
        color="#5b3b83",
        line=dict(width=2)
    ),
    hovertemplate=(
        "꽃잎길이: %{x:.1f}cm<br>"
        "꽃잎너비: %{y:.1f}cm"
        "<extra>가까운 데이터</extra>"
    )
))

# ----------------------------------
# 12. 사용자 입력값 하트 표시
# ----------------------------------
fig.add_trace(go.Scatter(
    x=[petal_length],
    y=[petal_width],
    mode="markers",
    name="내가 입력한 값 ♥",
    marker=dict(
        symbol="heart",
        size=25,
        color="#ff1493",
        line=dict(color="#ffffff", width=2)
    ),
    hovertemplate=(
        "내가 입력한 값 ♥<br>"
        "꽃잎길이: %{x:.1f}cm<br>"
        "꽃잎너비: %{y:.1f}cm"
        "<extra></extra>"
    )
))

# ----------------------------------
# 13. 그래프 디자인
# ----------------------------------
fig.update_layout(
    title="Iris Flower Classification Map",
    xaxis_title="꽃잎길이 (cm)",
    yaxis_title="꽃잎너비 (cm)",
    height=650,
    template="plotly_white",
    font=dict(
        family="Arial",
        size=13
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=30, r=30, t=100, b=40)
)

fig.update_xaxes(range=[x_min, x_max])
fig.update_yaxes(range=[y_min, y_max])

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------
# 14. 분류 이유 설명
# ----------------------------------
st.markdown("---")
st.header("💡 왜 이 품종으로 분류되었을까요?")

st.write(
    "KNN 알고리즘은 입력한 데이터와 기존 붓꽃 데이터 사이의 "
    "거리를 계산합니다. 그중 가장 가까운 5개의 데이터를 찾아 "
    "가장 많이 등장한 품종으로 분류합니다."
)

st.subheader("가장 가까운 5개 데이터")

display_neighbors = neighbors.rename(columns={
    "꽃잎길이": "꽃잎길이 (cm)",
    "꽃잎너비": "꽃잎너비 (cm)",
    "품종": "실제 품종",
    "거리": "거리 (표준화)"
})

st.dataframe(
    display_neighbors,
    use_container_width=True,
    hide_index=True
)

# 품종별 투표 결과
vote_counts = pd.Series(
    y[indices[0]]
).value_counts()

st.subheader("품종별 투표 결과")

vote_df = pd.DataFrame({
    "품종": class_names,
    "투표 수": [
        int(vote_counts.get(name, 0))
        for name in class_names
    ]
})

st.bar_chart(
    vote_df.set_index("품종"),
    color="#ed83b1"
)

st.info(
    f"가장 가까운 5개 데이터 중 "
    f"**{prediction}**이(가) "
    f"{int(vote_counts.get(prediction, 0))}표를 얻어 "
    "최종 품종으로 예측되었습니다."
)

# ----------------------------------
# 15. 알고리즘 설명
# ----------------------------------
with st.expander("📚 KNN 알고리즘 알아보기"):

    st.write("""
    **KNN (K-Nearest Neighbors)**

    KNN은 새로운 데이터와 기존 데이터 사이의 거리를
    비교하여 가장 가까운 K개의 이웃을 찾는 분류 알고리즘입니다.

    이 프로그램에서는 다음과 같이 작동합니다.

    1. 사용자가 꽃잎길이와 꽃잎너비를 입력합니다.
    2. 기존 붓꽃 데이터와 입력값의 거리를 계산합니다.
    3. 가장 가까운 5개의 데이터를 선택합니다.
    4. 5개 데이터의 품종을 비교합니다.
    5. 가장 많이 등장한 품종을 최종 결과로 출력합니다.

    또한 두 측정값의 단위와 범위 차이를 고려하기 위해
    StandardScaler로 데이터를 표준화합니다.
    """)

st.markdown("---")
st.caption("Iris Flower Classifier | KNN Machine Learning Project")
