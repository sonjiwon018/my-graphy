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

    # 숫자 열 변환
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


# ==================================================
# 데이터 불러오기
# ==================================================

try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.error(str(e))
    st.stop()


st.success(
    f"데이터를 불러왔습니다. 총 {len(df):,}개의 기록입니다."
)


# ==================================================
# 그래프 1. 영화별 일관객 변화
# ==================================================

st.divider()

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 그 영화가 박스오피스 10위권에 있었던 "
    "날짜의 일관객 수 변화를 확인할 수 있습니다."
)


movie_counts = (
    df.groupby("영화명")
    .size()
    .sort_values(ascending=False)
)

movie_list = movie_counts.index.tolist()


selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_list,
    format_func=lambda movie:
        f"{movie} ({movie_counts[movie]}일)"
)


movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


record_count = len(movie_df)

st.caption(
    f"선택한 영화의 기록: {record_count}일"
)


if record_count == 1:
    st.warning(
        "⚠️ 이 영화는 10위권에 기록된 날짜가 1일뿐이라 "
        "그래프에 점 하나만 표시됩니다."
    )


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
    title_text="날짜"
)

fig1.update_yaxes(
    title_text="일관객 수(명)",
    tickformat=","
)

fig1.update_layout(
    height=550,
    hovermode="closest"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


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


movie_total = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
)

top5_movies = movie_total.head(5).index.tolist()


st.markdown("#### 🏆 이 기간의 일관객 합계 TOP 5")

for rank, movie in enumerate(top5_movies, start=1):
    st.write(
        f"**{rank}위. {movie}** — "
        f"{movie_total[movie]:,.0f}명"
    )


all_dates = pd.date_range(
    start=df["날짜"].min(),
    end=df["날짜"].max(),
    freq="D"
)

top5_data = []

for movie in top5_movies:

    temp = df[
        df["영화명"] == movie
    ][["날짜", "일관객"]].copy()

    temp = (
        temp.groupby("날짜", as_index=False)["일관객"]
        .sum()
    )

    temp = (
        temp.set_index("날짜")
        .reindex(all_dates)
        .rename_axis("날짜")
        .reset_index()
    )

    temp["영화명"] = movie

    top5_data.append(temp)


top5_df = pd.concat(
    top5_data,
    ignore_index=True
)


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

fig2.update_xaxes(
    tickformat="%Y-%m-%d",
    title_text="날짜"
)

fig2.update_yaxes(
    title_text="일관객 수(명)",
    tickformat=","
)

fig2.update_layout(
    height=600,
    hovermode="closest",
    legend=dict(
        title="영화",
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


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
# 그래프 3. 날짜별 10위권 일관객 합계
# ==================================================

st.divider()

st.header("📊 그래프 3. 날짜별 10위권 일관객 합계")

st.write(
    "각 날짜의 박스오피스 10위권 영화의 일관객을 모두 합산하여 "
    "날짜별 전체 관객 규모의 변화를 보여 줍니다."
)


daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)


top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)


fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>"
        "10위권 일관객 합계: %{y:,.0f}명"
        "<extra></extra>"
    )
)


for _, row in top3_days.iterrows():

    date = row["날짜"]
    total = row["일관객"]

    fig3.add_annotation(
        x=date,
        y=total,
        text=(
            f"{date.strftime('%Y년 %m월 %d일')}"
            f"<br>{total:,.0f}명"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-60,
        font=dict(size=13),
        bgcolor="white",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )


fig3.update_xaxes(
    tickformat="%Y-%m-%d",
    title_text="날짜"
)

fig3.update_yaxes(
    title_text="10위권 일관객 합계(명)",
    tickformat=","
)

fig3.update_layout(
    height=600,
    hovermode="x",
    margin=dict(
        l=80,
        r=40,
        t=100,
        b=70
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


st.markdown("### 🏆 일관객 합계가 가장 컸던 날 TOP 3")

top3_ranked = top3_days.sort_values(
    "일관객",
    ascending=False
)

for rank, (_, row) in enumerate(
    top3_ranked.iterrows(),
    start=1
):

    st.write(
        f"**{rank}위 — "
        f"{row['날짜'].strftime('%Y년 %m월 %d일')}** : "
        f"{row['일관객']:,.0f}명"
    )


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 그래프를 통해 날짜별 박스오피스 10위권 전체의 "
        "관객 규모가 어떻게 변했는지 알 수 있습니다."
    ),
    height=100,
    key="graph3_explanation"
)


# ==================================================
# 그래프 4. 일관객 합계 TOP 10
# ==================================================

st.divider()

st.header("📊 그래프 4. 영화별 일관객 합계 TOP 10")

st.write(
    "이 기간 동안 각 영화의 일관객을 모두 더하여 "
    "관객 합계가 가장 큰 영화 10편을 비교합니다."
)


# --------------------------------------------------
# 영화별 총 일관객 + 10위권 기록 일수 계산
# --------------------------------------------------

top10_df = (
    df.groupby("영화명")
    .agg(
        총일관객=("일관객", "sum"),
        기록일수=("날짜", "nunique")
    )
    .sort_values(
        "총일관객",
        ascending=False
    )
    .head(10)
    .reset_index()
)


# --------------------------------------------------
# 그래프용 순서
# --------------------------------------------------
# 가로 막대그래프에서는 아래쪽 데이터가 위에 표시되므로
# 관객이 많은 영화가 위에 오도록 역순으로 정렬

top10_plot_df = top10_df.sort_values(
    "총일관객",
    ascending=True
)


# --------------------------------------------------
# 가로 막대그래프
# --------------------------------------------------

fig4 = px.bar(
    top10_plot_df,
    x="총일관객",
    y="영화명",
    orientation="h",
    title="영화별 기간 전체 일관객 합계 TOP 10",
    labels={
        "총일관객": "기간 전체 일관객 합계",
        "영화명": "영화"
    },
    custom_data=["기록일수"]
)


# --------------------------------------------------
# 마우스를 올렸을 때
# --------------------------------------------------

fig4.update_traces(
    hovertemplate=(
        "영화: %{y}"
        "<br>"
        "기간 전체 일관객: %{x:,.0f}명"
        "<br>"
        "10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    )
)


# --------------------------------------------------
# X축
# --------------------------------------------------

fig4.update_xaxes(
    title_text="기간 전체 일관객 합계(명)",
    tickformat=","
)


# --------------------------------------------------
# Y축
# --------------------------------------------------

fig4.update_yaxes(
    title_text="영화"
)


# --------------------------------------------------
# 그래프 설정
# --------------------------------------------------

fig4.update_layout(
    height=650,
    hovermode="closest",
    margin=dict(
        l=100,
        r=40,
        t=80,
        b=70
    )
)


st.plotly_chart(
    fig4,
    use_container_width=True
)


# --------------------------------------------------
# TOP 10 순위도 표시
# --------------------------------------------------

st.markdown("### 🏆 일관객 합계 TOP 10")

for rank, (_, row) in enumerate(
    top10_df.iterrows(),
    start=1
):

    st.write(
        f"**{rank}위 — {row['영화명']}** : "
        f"{row['총일관객']:,.0f}명 "
        f"({row['기록일수']}일)"
    )


# ==================================================
# 그래프 4 - 직접 작성
# ==================================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 그래프를 통해 이 기간 동안 일관객 합계가 가장 큰 "
        "영화 10편과 각 영화가 10위권에 든 날수를 비교할 수 있습니다."
    ),
    height=100,
    key="graph4_explanation"
)


# ==================================================
# 그래프 5
# ==================================================

st.divider()

st.header("📊 그래프 5")

st.info(
    "앞으로 새로운 그래프를 추가할 공간입니다."
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value="여기에 그래프 5를 통해 알 수 있는 내용을 작성합니다.",
    height=100,
    key="graph5_explanation"
)
