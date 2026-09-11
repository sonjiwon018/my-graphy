import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write(
    "일별 박스오피스 데이터를 이용해 영화의 관객 변화를 "
    "다양한 그래프로 살펴봅니다."
)


# ============================================================
# 데이터 불러오기
# ============================================================
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/"
    "data/kobis_daily.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str).str.strip(),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형으로 변환
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


st.success(
    f"데이터를 불러왔습니다. 총 {len(df):,}개의 기록입니다."
)


# ============================================================
# 그래프 1
# 영화별 일관객 변화
# ============================================================
st.divider()

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 그 영화가 박스오피스 10위권에 있었던 "
    "날짜의 일관객 수 변화를 확인할 수 있습니다."
)


# 영화별 기록 개수
movie_counts = (
    df.groupby("영화명")
    .size()
    .sort_values(ascending=False)
)

movie_list = movie_counts.index.tolist()


# 영화 선택
selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_list,
    format_func=lambda movie: (
        f"{movie} ({movie_counts[movie]}일)"
    )
)


# 선택한 영화 데이터
movie_df = (
    df[df["영화명"] == selected_movie]
    .copy()
    .sort_values("날짜")
)

record_count = len(movie_df)

st.caption(
    f"선택한 영화의 기록: {record_count}일"
)


if record_count == 1:
    st.warning(
        "⚠️ 이 영화는 10위권에 기록된 날짜가 1일뿐이라 "
        "그래프에 점 하나만 표시됩니다."
    )


# 그래프 1
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


# 노란색 선
fig1.update_traces(
    line=dict(
        color="#F4B400",
        width=3
    ),
    marker=dict(
        color="#F4B400",
        size=7
    ),
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>관객수: %{y:,.0f}명"
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


# 그래프 1 설명
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


# ============================================================
# 그래프 2
# 인기 영화 TOP 5 일관객 변화
# ============================================================
st.divider()

st.header("📊 그래프 2. 인기 영화 TOP 5 일관객 변화")

st.write(
    "전체 기간 동안의 일관객 합계를 기준으로 가장 인기 있었던 "
    "영화 5편의 날짜별 일관객 변화를 비교합니다."
)


# 영화별 전체 일관객 합계
movie_total = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
)

top5_movies = movie_total.head(5).index.tolist()


# TOP 5 표시
st.write("**전체 기간 일관객 합계 TOP 5**")

for i, movie in enumerate(top5_movies, start=1):

    total = movie_total[movie]

    st.write(
        f"{i}위. **{movie}** — "
        f"{total:,.0f}명"
    )


# 전체 날짜 범위
all_dates = pd.date_range(
    start=df["날짜"].min(),
    end=df["날짜"].max(),
    freq="D"
)


# TOP 5 데이터 생성
top5_graph_list = []


for movie in top5_movies:

    temp = (
        df[df["영화명"] == movie]
        .groupby("날짜")["일관객"]
        .sum()
        .reindex(all_dates)
    )

    temp = temp.rename("일관객").reset_index()

    temp = temp.rename(
        columns={"index": "날짜"}
    )

    temp["영화명"] = movie

    top5_graph_list.append(temp)


top5_graph_df = pd.concat(
    top5_graph_list,
    ignore_index=True
)


# 그래프 2
fig2 = px.line(
    top5_graph_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="전체 기간 일관객 합계 TOP 5 영화의 날짜별 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    },
    color_discrete_sequence=[
        "#F4B400",
        "#FFD54F",
        "#FFCA28",
        "#FFA000",
        "#FFE082"
    ]
)


fig2.update_traces(
    connectgaps=False,
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>관객수: %{y:,.0f}명"
        "<br>영화: %{fullData.name}"
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
    hovermode="x unified",
    legend_title_text="영화"
)


# 범례 클릭 기능
fig2.update_layout(
    legend=dict(
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)


st.plotly_chart(
    fig2,
    use_container_width=True
)


# 그래프 2 설명
st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 그래프를 통해 전체 기간 동안 일관객 합계가 많았던 "
        "TOP 5 영화의 날짜별 관객 변화를 서로 비교할 수 있습니다."
    ),
    height=100,
    key="graph2_explanation"
)


# ============================================================
# 그래프 3
# 날짜별 전체 일관객 합계
# ============================================================
st.divider()

st.header("📅 그래프 3. 날짜별 전체 일관객 합계")

st.write(
    "각 날짜에 박스오피스 10위권 영화들이 기록한 "
    "일관객을 모두 합산하여 보여줍니다."
)


# 날짜별 일관객 합계
daily_total = (
    df.groupby(
        "날짜",
        as_index=False
    )["일관객"]
    .sum()
    .sort_values("날짜")
)


# 관객이 가장 많았던 TOP 3 날짜
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)


# 그래프 3
fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 전체 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "전체 일관객 합계"
    }
)


# 노란색 영역
fig3.update_traces(
    line=dict(
        color="#F4B400",
        width=3
    ),
    fillcolor="rgba(244, 180, 0, 0.25)",
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}"
        "<br>전체 관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)


# TOP 3 날짜 표시
for _, row in top3_days.iterrows():

    date_text = row["날짜"].strftime(
        "%Y년 %m월 %d일"
    )

    audience = row["일관객"]

    fig3.add_annotation(
        x=row["날짜"],
        y=audience,
        text=(
            f"{date_text}"
            f"<br>{audience:,.0f}명"
        ),
        showarrow=True,
        arrowhead=2,
        yshift=10
    )


fig3.update_xaxes(
    tickformat="%Y-%m-%d",
    title_text="날짜"
)

fig3.update_yaxes(
    title_text="전체 일관객 합계(명)",
    tickformat=","
)


fig3.update_layout(
    height=600,
    hovermode="x",
    margin=dict(
        t=80,
        b=60,
        l=70,
        r=40
    )
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


# TOP 3 날짜
st.markdown("#### 🏆 관객이 가장 많았던 날짜 TOP 3")


for rank, (_, row) in enumerate(
    top3_days.sort_values(
        "일관객",
        ascending=False
    ).iterrows(),
    start=1
):

    date_text = row["날짜"].strftime(
        "%Y년 %m월 %d일"
    )

    st.write(
        f"**{rank}위 — {date_text}** "
        f": {row['일관객']:,.0f}명"
    )


# 그래프 3 설명
st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 그래프를 통해 날짜별로 전체 박스오피스 관객 규모가 "
        "어떻게 변했는지 알 수 있으며, 관객이 특히 많았던 "
        "날짜도 확인할 수 있습니다."
    ),
    height=100,
    key="graph3_explanation"
)


# ============================================================
# 그래프 4
# 영화별 기간 전체 일관객 합계 TOP 10
# ============================================================
st.divider()

st.header("🏆 그래프 4. 영화별 기간 전체 일관객 합계 TOP 10")

st.write(
    "전체 기간 동안 각 영화의 일관객을 모두 합산하여 "
    "관객수가 가장 많았던 영화 10편을 비교합니다."
)


# 영화별 전체 일관객 합계 + 기록일수
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


# 높은 값이 위로 오도록 정렬
top10_plot_df = (
    top10_df
    .sort_values(
        "총일관객",
        ascending=True
    )
)


# 그래프 4
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


# 노란색 막대
fig4.update_traces(
    marker_color="#F4B400",
    hovertemplate=(
        "영화: %{y}"
        "<br>기간 전체 일관객: %{x:,.0f}명"
        "<br>10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    )
)


fig4.update_xaxes(
    title_text="기간 전체 일관객 합계",
    tickformat=","
)

fig4.update_yaxes(
    title_text="영화"
)


fig4.update_layout(
    height=600
)


st.plotly_chart(
    fig4,
    use_container_width=True
)


# 그래프 4 설명
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


# ============================================================
# 그래프 5
# 월 × 요일별 일관객 합계 히트맵
# ============================================================
st.divider()

st.header("🔥 그래프 5. 월 × 요일별 일관객 합계 히트맵")

st.write(
    "날짜에서 월과 요일을 추출하여 각 월·요일 조합에서 "
    "발생한 일관객의 합계를 히트맵으로 보여줍니다. "
    "색이 진할수록 해당 월·요일의 총 관객수가 많습니다."
)


# 데이터 복사
heatmap_df = df.copy()


# 날짜에서 월 추출
heatmap_df["월"] = (
    heatmap_df["날짜"].dt.month
)


# 요일 순서
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]


# 날짜에서 요일 추출
# 월요일 = 0
# 일요일 = 6
heatmap_df["요일"] = (
    heatmap_df["날짜"]
    .dt.weekday
    .map(
        dict(
            enumerate(weekday_order)
        )
    )
)


# 월 × 요일별 일관객 합계
heatmap_data = (
    heatmap_df
    .pivot_table(
        index="월",
        columns="요일",
        values="일관객",
        aggfunc="sum",
        fill_value=0
    )
)


# 월요일 → 일요일 순서
heatmap_data = heatmap_data.reindex(
    columns=weekday_order
)


# 1월 → 12월 순서
heatmap_data = heatmap_data.reindex(
    range(1, 13),
    fill_value=0
)


# ============================================================
# 노란색 히트맵
# ============================================================
fig5 = px.imshow(
    heatmap_data,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_order,
    y=[
        f"{month}월"
        for month in heatmap_data.index
    ],
    aspect="auto",

    # 연한 노랑 → 진한 노랑
    color_continuous_scale=[
        "#FFFDE7",
        "#FFF9C4",
        "#FFF176",
        "#FFD54F",
        "#FFCA28",
        "#F4B400",
        "#FF8F00"
    ]
)


# 마우스를 올렸을 때
fig5.update_traces(
    hovertemplate=(
        "월: %{y}"
        "<br>요일: %{x}"
        "<br>일관객 합계: %{z:,.0f}명"
        "<extra></extra>"
    )
)


fig5.update_layout(
    title="월 × 요일별 일관객 합계",
    height=600,
    xaxis_title="요일",
    yaxis_title="월",
    coloraxis_colorbar_title="일관객"
)


st.plotly_chart(
    fig5,
    use_container_width=True
)


# 그래프 5 설명
st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 입력하세요.",
    value=(
        "이 히트맵을 통해 월과 요일에 따라 일관객 합계가 "
        "어떻게 다른지 한눈에 비교할 수 있습니다. "
        "색이 진할수록 해당 월·요일에 많은 관객이 "
        "발생했다는 것을 의미합니다."
    ),
    height=100,
    key="graph5_explanation"
)


# ============================================================
# 마무리
# ============================================================
st.divider()

st.caption(
    "🎬 영화 데이터 그래프 도감 1 - 시간"
)
