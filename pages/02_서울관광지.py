import streamlit as pd_alias
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정
st.set_page_config(
    page_title="외국인이 사랑하는 서울 관광지 TOP 100",
    page_icon="🗺️",
    layout="wide"
)

# 1. 외국인 선호 서울 주요 관광지 데이터 (대표 장소들로 구성된 구조화된 리스트)
tourist_spots = [
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770, "category": "역사/문화", "desc": "조선 왕조의 법궁으로, 전통 한복을 입고 관람하는 외국인 관광객들에게 가장 인기 있는 서울의 랜드마크입니다."},
    {"name": "N서울타워 (남산타워)", "lat": 37.5512, "lon": 126.9882, "category": "전망/경치", "desc": "서울의 중심 남산 정상에 위치하여 서울 전경을 360도로 조망할 수 있으며, 자물쇠 매달기 명소로 유명합니다."},
    {"name": "북촌한옥마을", "lat": 37.5826, "lon": 126.9830, "category": "역사/문화", "desc": "조선시대 양반 가옥인 전통 한옥이 고스란히 보존되어 있어 한국의 전통미를 느끼기 좋은 아름다운 마을입니다."},
    {"name": "명동", "lat": 37.5636, "lon": 126.9834, "category": "쇼핑/미식", "desc": "다양한 K-뷰티 화장품 브랜드와 길거리 음식을 즐길 수 있어 쇼핑을 좋아하는 외국인들에게 필수 코스입니다."},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.5665, "lon": 127.0091, "category": "건축/디자인", "desc": "세계적인 건축가 자하 하디드가 설계한 유려한 곡선미의 복합 문화 공간으로, 미래지향적 분위기를 자랑합니다."},
    {"name": "홍대 거리 (레드로드)", "lat": 37.5563, "lon": 126.9236, "category": "젊음/예술", "desc": "인디 음악, 버스킹, 트렌디한 카페와 클럽이 모여 있는 한국 젊은 문화의 중심지입니다."},
    {"name": "광장시장", "lat": 37.5702, "lon": 126.9991, "category": "미식/시장", "desc": "빈대떡, 마약김밥, 육회 등 한국의 전통 시장 먹거리를 생생하게 체험할 수 있는 곳입니다."},
    {"name": "국립중앙박물관", "lat": 37.5239, "lon": 126.9800, "category": "역사/문화", "desc": "한국의 선사시대부터 조선시대까지 방대한 역사 유물과 국보를 소장하고 있는 세계적인 수준의 박물관입니다."},
    {"name": "창덕궁과 후원", "lat": 37.5794, "lon": 126.9910, "category": "역사/문화", "desc": "자연 지형과 조화를 이룬 아름다운 왕실 정원(비원)으로 유네스코 세계문화유산에 등재되어 있습니다."},
    {"name": "반포한강공원 (세빛섬)", "lat": 37.5110, "lon": 126.9950, "category": "자연/휴식", "desc": "한강의 야경과 함께 달빛무지개분수를 감상하며 치킨과 맥주(치맥)를 즐길 수 있는 대표적인 힐링 명소입니다."},
    {"name": "롯데월드타워 & 서울스카이", "lat": 37.5125, "lon": 127.1025, "category": "랜드마크", "desc": "대한민국 최고 높이 빌딩으로, 초고속 전망대에서 서울 전체를 내려다보는 아찔한 스릴과 야경을 선사합니다."},
    {"name": "인사동 문화거리", "lat": 37.5743, "lon": 126.9850, "category": "전통/공예", "desc": "한국의 전통 공예품, 골동품, 전통 찻집과 쌈지길 등이 모여 있어 기념품 쇼핑에 최적화된 거리입니다."},
    {"name": "성수동 카페거리 & 서울숲", "lat": 37.5506, "lon": 127.0413, "category": "트렌드/카페", "desc": "낡은 공장과 창고가 개성 있는 카페, 팝업스토어, 부티크로 변신하여 로컬 젊은이와 외국인 모두에게 인기 있는 핫플입니다."},
    {"name": "이태원 & 용산리오단길", "lat": 37.5340, "lon": 126.9940, "category": "글로벌/다문화", "desc": "다양한 국적의 세계 각국 음식점과 이국적인 분위기를 느낄 수 있는 서울의 대표적인 다문화 거리입니다."},
    {"name": "덕수궁 돌담길", "lat": 37.5658, "lon": 126.9751, "category": "역사/산책", "desc": "고즈넉한 궁궐 담장을 따라 걸으며 아름다운 가로수와 현대적 미술관이 어우러진 풍경을 감상할 수 있는 산책로입니다."},
]

# 데이터프레임 변환 (확장성을 위해 리스트 구조 활용)
df = pd.DataFrame(tourist_spots)

# 타이틀 영역
st.title("🗺️ 외국인이 가장 사랑하는 서울 주요 관광지")
st.markdown("유럽, 미주, 아시아 등 전 세계 외국인 관광객들이 꼭 방문하는 서울의 대표 명소들을 지도와 설명으로 만나보세요!")
st.divider()

# 2. 필터 기능 (사이드바)
st.sidebar.header("🔍 관광지 필터")
selected_category = st.sidebar.selectbox(
    "카테고리 선택",
    options=["전체 보기"] + list(df["category"].unique())
)

# 필터 적용
if selected_category != "전체 보기":
    filtered_df = df[df["category"] == selected_category]
else:
    filtered_df = df

# 3. 지도 시각화 (Folium)
st.subheader("📍 서울 관광지도")
# 서울 중심부 좌표 (시청 기준)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="CartoDB positron")

# 지도에 마커 추가
for idx, row in filtered_df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"<b>{row['name']}</b>",
        tooltip=row["name"],
        icon=folium.Icon(color="red" if "역사" in row["category"] or "랜드마크" in row["category"] else "blue", icon="info-sign")
    ).add_to(m)

# Streamlit에 지도 렌더링
st_folium(m, width=700, height=500, use_container_width=True)

st.divider()

# 4. 관광지 상세 설명 카드 섹션 (하단)
st.subheader("📖 관광지 상세 설명")
st.markdown(f"총 **{len(filtered_df)}개**의 관광지가 표시되어 있습니다.")

# 2열 그리드로 깔끔하게 설명 카드 배치
cols = st.columns(2)
for idx, row in filtered_df.reset_index().iterrows():
    col = cols[idx % 2]
    with col:
        with st.container(border=True):
            st.markdown(f"### **{row['name']}**")
            st.caption(f"🏷️ 카테고리: {row['category']}")
            st.write(row['desc'])

# 푸터
st.markdown("---")
st.markdown("💡 *Streamlit Cloud에 배포하여 언제 어디서나 웹으로 공유할 수 있습니다!*")
