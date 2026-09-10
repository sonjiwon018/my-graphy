import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("1년치 일별 박스오피스 데이터를 이용해 영화의 관객 변화를 살펴봅니다.")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자 열을 숫자형으로 변환
    numeric_columns = [
        "순위",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.error(f"오류 내용: {e}")
    st.stop()


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------

st.success(f"데이터를 불러왔습니다. 총 {len(df):,}개의 기록입니다.")

with st.expander("📋 원본 데이터 확인"):
    st.dataframe(
        df,
        use_container_width=True
    )


# ==================================================
# 그래프 1. 영화별 일관객 변화
# ==================================================

st.divider()
st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 날짜에 따른 일관객 수의 변화를 확인할 수 있습니다."
)


# 영화 목록
movie_list = sorted(
    df["영화명"].dropna().unique().tolist()
)

selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_list
)


# 선택한 영화 데이터
movie_df = df[df["영화명"] == selected_movie].copy()

# 날짜순 정렬
movie_df = movie_df.sort_values("날짜")


# 선 그래프
fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,.0f"
    }
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,.0f}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "「오디세이」의 일관객 수는 날짜에 따라 크게 변하며, 특히 주말이나 특정 시기에 관객 수가 크게 증가하는 경향을 보인다."
)


# ==================================================
# 앞으로 추가할 그래프 구역
# ==================================================

st.divider()
st.header("📊 그래프 2")
st.info("앞으로 새로운 그래프를 추가할 공간입니다.")


st.divider()
st.header("📊 그래프 3")
st.info("앞으로 새로운 그래프를 추가할 공간입니다.")


st.divider()
st.header("📊 그래프 4")
st.info("앞으로 새로운 그래프를 추가할 공간입니다.")
