import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write(
    "1년치 일별 박스오피스 데이터를 이용해 영화의 관객 변화를 살펴봅니다."
)


# ==================================================
# 데이터 불러오기
# ==================================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str).str.strip(),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자 데이터 변환
    number_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for column in number_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 필요한 데이터가 없는 행 제거
    df = df.dropna(
        subset=["날짜", "영화명", "일관객"]
    )

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.error(str(e))
    st.stop()


# ==================================================
# 데이터 기본 정보
# ==================================================

st.success(
    f"데이터를 불러왔습니다. 총 {len(df):,}개의 기록입니다."
)


# ==================================================
# 그래프 1. 영화별 일관객 변화
# ==================================================

st.divider()

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 그 영화가 박스오피스 10위권에 있었던 날짜의 "
    "일관객 수 변화를 확인할 수 있습니다."
)


# --------------------------------------------------
# 영화별 등장 횟수
# --------------------------------------------------

movie_counts = (
    df.groupby("영화명")
    .size()
    .sort_values(ascending=False)
)

movie_list = movie_counts.index.tolist()

default_movie = movie_list[0]


# --------------------------------------------------
# 영화 선택
# --------------------------------------------------

selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_list,
    index=movie_list.index(default_movie),
    format_func=lambda movie:
        f"{movie} ({movie_counts[movie]}일)"
)


# --------------------------------------------------
# 선택한 영화 데이터
# --------------------------------------------------

movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


# ==================================================
# 기록 개수 안내
# ==================================================

record_count = len(movie_df)

st.caption(
    f"선택한 영화의 기록: {record_count}일"
)

if record_count == 1:
    st.warning(
        "⚠️ 이 영화는 10위권에 기록된 날짜가 1일뿐이라 "
        "그래프에 점 하나만 표시됩니다. "
        "다른 영화를 선택하면 날짜별 변화를 확인할 수 있습니다."
    )


# ==================================================
# 그래프 1 선 그래프
# ==================================================

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)


fig1.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>"
        "관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)


fig1.update_xaxes(
    tickformat="%Y-%m-%d",
    title_text="날짜",
    showgrid=True
)


fig1.update_yaxes(
    title_text="일관객 수(명)",
    tickformat=","
)


fig1.update_layout(
    height=550,
    hovermode="closest",
    margin=dict(
        l=70,
        r=30,
        t=80,
        b=70
    )
)


st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==================================================
# 그래프 1 - 직접 작성
# ==================================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 그래프를 통해 선택한 영화의 일관객 수가 "
        "날짜에 따라 어떻게 변했는지 알 수 있습니다."
    ),
    height=100,
    key="graph1_explanation"
)


# ==================================================
# 그래프 2. 일관객 합계 TOP 5
# ==================================================

st.divider()

st.header("📊 그래프 2. 일관객 합계가 가장 큰 영화 TOP 5")

st.write(
    "전체 기간 동안 일관객을 모두 합산하여 관객 수가 가장 큰 "
    "5편의 날짜별 일관객 변화를 비교합니다."
)


# --------------------------------------------------
# 영화별 일관객 합계 계산
# --------------------------------------------------

movie_total = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
)


# --------------------------------------------------
# 일관객 합계 TOP 5
# --------------------------------------------------

top5_movies = movie_total.head(5).index.tolist()


# --------------------------------------------------
# TOP 5 영화의 총 관객수 표시
# --------------------------------------------------

st.markdown("#### 🏆 이 기간의 일관객 합계 TOP 5")

for rank, movie in enumerate(top5_movies, start=1):
    st.write(
        f"**{rank}위. {movie}** — "
        f"{movie_total[movie]:,.0f}명"
    )


# ==================================================
# 날짜별 TOP 5 데이터 만들기
# ==================================================

# 전체 날짜 범위 만들기
all_dates = pd.date_range(
    start=df["날짜"].min(),
    end=df["날짜"].max(),
    freq="D"
)


# TOP 5 각각의 날짜별 데이터 만들기
top5_data = []

for movie in top5_movies:

    temp = df[
        df["영화명"] == movie
    ][["날짜", "일관객"]].copy()

    # 같은 영화가 같은 날짜에 여러 기록이 있을 경우 합산
    temp = (
        temp.groupby("날짜", as_index=False)["일관객"]
        .sum()
    )

    # 전체 날짜에 맞춰 데이터 생성
    temp = (
        temp.set_index("날짜")
        .reindex(all_dates)
        .rename_axis("날짜")
        .reset_index()
    )

    # 영화 이름 추가
    temp["영화명"] = movie

    top5_data.append(temp)


# 하나의 데이터프레임으로 합치기
top5_df = pd.concat(
    top5_data,
    ignore_index=True
)


# ==================================================
# 그래프 2 선 그래프
# ==================================================

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)


# --------------------------------------------------
# 결측 날짜는 선을 연결하지 않도록 설정
# --------------------------------------------------

fig2.update_traces(
    connectgaps=False,
    hovertemplate=(
        "영화: %{fullData.name}"
        "<br>"
        "날짜: %{x|%Y-%m-%d}"
        "<br>"
        "관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)


# --------------------------------------------------
# X축
# --------------------------------------------------

fig2.update_xaxes(
    tickformat="%Y-%m-%d",
    title_text="날짜",
    showgrid=True
)


# --------------------------------------------------
# Y축
# --------------------------------------------------

fig2.update_yaxes(
    title_text="일관객 수(명)",
    tickformat=","
)


# --------------------------------------------------
# 범례 클릭 기능
# --------------------------------------------------

fig2.update_layout(
    height=600,
    hovermode="closest",
    legend=dict(
        title="영화",
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    ),
    margin=dict(
        l=70,
        r=30,
        t=80,
        b=70
    )
)


# 그래프 출력
st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==================================================
# 그래프 2 - 직접 작성
# ==================================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 그래프를 통해 기간 동안 일관객 합계가 가장 큰 "
        "5편의 영화가 날짜에 따라 어떤 관객 변화를 보였는지 비교할 수 있습니다."
    ),
    height=100,
    key="graph2_explanation"
)


# ==================================================
# 그래프 3
# ==================================================

st.divider()

st.header("📊 그래프 3")

st.info(
    "앞으로 새로운 그래프를 추가할 공간입니다."
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value="여기에 그래프 3을 통해 알 수 있는 내용을 작성합니다.",
    height=100,
    key="graph3_explanation"
)
