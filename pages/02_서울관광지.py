import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정
st.set_page_config(
    page_title="외국인이 사랑하는 서울 관광지 & 1박 2일 코스",
    page_icon="🗺️",
    layout="wide"
)

# 1. 외국인 선호 서울 주요 관광지 데이터
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

df = pd.DataFrame(tourist_spots)

# 타이틀 영역
st.title("🗺️ 외국인이 가장 사랑하는 서울 주요 관광지 가이드")
st.markdown("유럽, 미주, 아시아 등 전 세계 외국인 관광객들이 꼭 방문하는 서울의 대표 명소들을 지도, 상세 설명, 그리고 추천 일정으로 만나보세요!")
st.divider()

# 2. 필터 기능 (사이드바)
st.sidebar.header("🔍 관광지 필터")
selected_category = st.sidebar.selectbox(
    "카테고리 선택",
    options=["전체 보기"] + list(df["category"].unique())
)

if selected_category != "전체 보기":
    filtered_df = df[df["category"] == selected_category]
else:
    filtered_df = df

# 3. 지도 시각화 (Folium)
st.subheader("📍 서울 관광지도")
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="CartoDB positron")

for idx, row in filtered_df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"<b>{row['name']}</b>",
        tooltip=row["name"],
        icon=folium.Icon(color="red" if "역사" in row["category"] or "랜드마크" in row["category"] else "blue", icon="info-sign")
    ).add_to(m)

st_folium(m, width=700, height=500, use_container_width=True)

st.divider()

# 4. 관광지 상세 설명 카드 섹션
st.subheader("📖 관광지 상세 설명")
st.markdown(f"총 **{len(filtered_df)}개**의 관광지가 표시되어 있습니다.")

cols = st.columns(2)
for idx, row in filtered_df.reset_index().iterrows():
    col = cols[idx % 2]
    with col:
        with st.container(border=True):
            st.markdown(f"### **{row['name']}**")
            st.caption(f"🏷️ 카테고리: {row['category']}")
            st.write(row['desc'])

st.divider()

# 5. 추가 기능: 1박 2일 추천 코스 및 식당 안내 (아침 9시 ~ 저녁 8시)
st.subheader("🗓️ 서울 주요 명소 1박 2일 추천 코스 (09:00 ~ 20:00)")
st.markdown("외국인 관광객들이 알차게 서울을 즐길 수 있도록 오전 9시부터 저녁 8시까지 동선을 맞춘 추천 일정과 맛집 정보입니다.")

itinerary_data = [
    {"day": "1일차", "time": "09:00 - 11:30", "type": "관광", "place": "경복궁 & 한복 체험", "detail": "조선 왕조의 법궁 관람 및 전통 한복을 입고 인생 사진 남기기"},
    {"day": "1일차", "time": "11:30 - 13:00", "type": "점심", "place": "토속촌 삼계탕 (경복궁 인근)", "detail": "외국인 입맛에도 잘 맞는 진하고 건강한 전통 보양식 삼계탕"},
    {"day": "1일차", "time": "13:00 - 15:00", "type": "관광", "place": "북촌한옥마을 & 삼청동", "detail": "아름다운 한옥 골목길 산책 및 전통 찻집 방문"},
    {"day": "1일차", "time": "15:00 - 17:00", "type": "관광", "place": "인사동 문화거리", "detail": "한국 전통 공예품 구경 및 쌈지길 쇼핑"},
    {"day": "1일차", "time": "17:00 - 19:00", "type": "관광", "place": "광장시장", "detail": "한국 전통 시장의 활기를 느끼고 빈대떡, 마약김밥 구경"},
    {"day": "1일차", "time": "19:00 - 20:00", "type": "저녁", "place": "부촌육회 (광장시장 내)", "detail": "신선한 육회와 빈대떡 등 다양한 시장 먹거리 체험"},
    {"day": "2일차", "time": "09:00 - 11:00", "type": "관광", "place": "N서울타워 (남산)", "detail": "케이블카를 타고 올라가 서울 전경을 한눈에 조망"},
    {"day": "2일차", "time": "11:00 - 12:30", "type": "이동", "place": "명동 거리", "detail": "명동 대성당 방문 및 거리 산책"},
    {"day": "2일차", "time": "12:30 - 14:00", "type": "점심", "place": "명동교자", "detail": "미쉐린 가이드에 오른 깊은 맛의 칼국수와 마늘 김치"},
    {"day": "2일차", "time": "14:00 - 16:30", "type": "관광", "place": "동대문디자인플라자 (DDP)", "detail": "세계적인 건축 디자인 감상 및 K-패션 쇼핑"},
    {"day": "2일차", "time": "16:30 - 19:00", "type": "관광", "place": "성수동 카페거리 & 서울숲", "detail": "힙한 팝업스토어, 감성 카페, 자연이 어우러진 핫플 탐방"},
    {"day": "2일차", "time": "19:00 - 20:00", "type": "저녁", "place": "소문난성수감자탕", "detail": "한국 직장인과 외국인 모두에게 사랑받는 진한 감자탕"},
]

df_itinerary = pd.DataFrame(itinerary_data)
st.dataframe(df_itinerary, use_container_width=True, hide_index=True)

# 푸터
st.markdown("---")
st.markdown("💡 *Streamlit Cloud에 배포하여 웹사이트 형태로 간편하게 공유해 보세요!*")
