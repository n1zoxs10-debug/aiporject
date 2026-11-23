
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Dessert Data Lab",
    page_icon="🍰",
    layout="wide"
)

# -------------------------
# 페이지 디자인
# -------------------------
st.markdown("""
<style>
    .main {
        background-color: #fffaf5;
    }
    .title {
        text-align: center;
        color: #795548;
        font-size: 42px;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: #9e8275;
        font-size: 17px;
    }
    div[data-testid="stMetric"] {
        background-color: #fff1e6;
        padding: 18px;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">Dessert Data Lab</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '디저트의 영양 정보를 데이터로 알아보는 공간'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

# -------------------------
# 데이터 불러오기
# -------------------------
@st.cache_data
def load_data(file):
    encodings = ["cp949", "utf-8-sig", "euc-kr"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file,
                encoding=encoding,
                low_memory=False
            )
            return data
        except UnicodeDecodeError:
            continue

    return pd.read_csv(file, encoding="cp949")


# 저장소에 CSV 파일이 있으면 자동으로 불러오기
file_path = "전국통합식품영양성분정보표준데이터.csv"

if os.path.exists(file_path):
    df = load_data(file_path)
    st.success("식품 영양 데이터가 준비되었습니다.")

else:
    uploaded_file = st.file_uploader(
        "식품 영양 데이터 CSV 파일을 업로드하세요.",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "CSV 파일을 업로드하면 디저트 검색을 시작할 수 있어요."
        )
        st.stop()

    df = load_data(uploaded_file)


# -------------------------
# 데이터 정리
# -------------------------
required_columns = [
    "식품명",
    "에너지(kcal)",
    "탄수화물(g)",
    "단백질(g)",
    "지방(g)",
    "당류(g)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("데이터에 필요한 영양 정보 열이 없습니다.")
    st.write("누락된 항목:", missing_columns)
    st.stop()

df["식품명"] = df["식품명"].fillna("").astype(str)

nutrition_columns = [
    "에너지(kcal)",
    "탄수화물(g)",
    "단백질(g)",
    "지방(g)",
    "당류(g)"
]

for col in nutrition_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# -------------------------
# 디저트 검색
# -------------------------
st.markdown("## 디저트 검색")

dessert = st.text_input(
    "어떤 디저트가 궁금한가요?",
    placeholder="예: 마카롱, 케이크, 크루아상"
)

if dessert.strip():

    search_data = df[
        df["식품명"].str.contains(
            dessert.strip(),
            case=False,
            na=False,
            regex=False
        )
    ].copy()

    if search_data.empty:
        st.warning(
            "검색 결과가 없습니다. "
            "다른 디저트 이름을 입력해 보세요."
        )

    else:
        st.success(
            f"'{dessert}' 검색 결과 "
            f"{len(search_data)}개를 찾았습니다."
        )

        # 검색 결과 선택
        selected_name = st.selectbox(
            "확인하고 싶은 디저트를 선택하세요.",
            search_data["식품명"].drop_duplicates().tolist()
        )

        selected = search_data[
            search_data["식품명"] == selected_name
        ].iloc[0]

        st.markdown("---")
        st.markdown(f"## {selected_name}")

        # 영양 성분 표시
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "에너지",
                f"{selected['에너지(kcal)']} kcal"
                if pd.notna(selected["에너지(kcal)"])
                else "정보 없음"
            )

        with col2:
            st.metric(
                "탄수화물",
                f"{selected['탄수화물(g)']} g"
                if pd.notna(selected["탄수화물(g)"])
                else "정보 없음"
            )

        with col3:
            st.metric(
                "단백질",
                f"{selected['단백질(g)']} g"
                if pd.notna(selected["단백질(g)"])
                else "정보 없음"
            )

        col4, col5 = st.columns(2)

        with col4:
            st.metric(
                "지방",
                f"{selected['지방(g)']} g"
                if pd.notna(selected["지방(g)"])
                else "정보 없음"
            )

        with col5:
            st.metric(
                "당류",
                f"{selected['당류(g)']} g"
                if pd.notna(selected["당류(g)"])
                else "정보 없음"
            )

        # 기준량 표시
        if "영양성분함량기준량" in df.columns:
            standard = selected["영양성분함량기준량"]
            st.caption(f"영양 성분 기준량: {standard}")

        st.markdown("---")

        # 상세 영양 정보
        st.markdown("### 영양 성분 상세 정보")

        detail = pd.DataFrame({
            "영양 성분": [
                "에너지",
                "탄수화물",
                "단백질",
                "지방",
                "당류"
            ],
            "함량": [
                selected["에너지(kcal)"],
                selected["탄수화물(g)"],
                selected["단백질(g)"],
                selected["지방(g)"],
                selected["당류(g)"]
            ],
            "단위": [
                "kcal",
                "g",
                "g",
                "g",
                "g"
            ]
        })

        st.dataframe(
            detail,
            use_container_width=True,
            hide_index=True
        )

        # 검색 결과 전체
        with st.expander("검색된 디저트 목록 보기"):
            st.dataframe(
                search_data[
                    [
                        "식품명",
                        "에너지(kcal)",
                        "탄수화물(g)",
                        "단백질(g)",
                        "지방(g)",
                        "당류(g)"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

else:
    st.markdown("### 오늘의 디저트 탐색")

    st.write(
        "검색창에 디저트 이름을 입력하면 "
        "해당 디저트의 영양 정보를 확인할 수 있습니다."
    )

    st.info(
        "예시 검색어: 마카롱 · 케이크 · 베이글 · "
        "크루아상 · 쿠키 · 식빵"
    )

st.markdown("---")

st.caption(
    "본 웹페이지는 전국통합식품영양성분정보표준데이터를 "
    "활용하여 제작되었습니다. "
    "식품별 영양 성분은 제품과 제조 방법에 따라 달라질 수 있습니다."
)

