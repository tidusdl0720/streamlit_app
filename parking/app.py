import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ----------------------------
# 기본 설정
# ----------------------------
st.set_page_config(page_title="서울시 공영주차장 지도", page_icon="🅿️", layout="wide")

DATA_PATH = "data/seoul_parking.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    # 무료 여부
    df["무료여부"] = df["유무료구분명"].apply(lambda x: "무료" if x == "무료" else "유료")

    # 주말 운영 여부 (시작/종료 시각이 모두 0이면 휴무로 간주)
    def weekend_status(row):
        s, e = row["주말 운영 시작시각(HHMM)"], row["주말 운영 종료시각(HHMM)"]
        if pd.isna(s) or pd.isna(e):
            return "정보없음"
        if s == 0 and e == 0:
            return "휴무"
        return "운영"

    df["주말운영여부"] = df.apply(weekend_status, axis=1)

    def fmt_time(v):
        if pd.isna(v):
            return "-"
        v = int(v)
        h, m = divmod(v, 100)
        if v == 2400:
            h, m = 24, 0
        return f"{h:02d}:{m:02d}"

    df["주말운영시간"] = df.apply(
        lambda r: f"{fmt_time(r['주말 운영 시작시각(HHMM)'])}~{fmt_time(r['주말 운영 종료시각(HHMM)'])}"
        if r["주말운영여부"] == "운영" else r["주말운영여부"],
        axis=1,
    )

    # 요금 텍스트 & 분당 요금(비교용)
    def fee_text_and_rate(row):
        if row["무료여부"] == "무료":
            return "무료", 0.0
        base_fee = row["기본 주차 요금"]
        base_min = row["기본 주차 시간(분 단위)"]
        add_fee = row["추가 단위 요금"]
        add_min = row["추가 단위 시간(분 단위)"]
        day_max = row["일 최대 요금"]

        if pd.isna(base_fee) or pd.isna(base_min) or base_min == 0:
            return "정보없음", None

        text = f"기본 {int(base_min)}분 {int(base_fee):,}원"
        if not pd.isna(add_fee) and not pd.isna(add_min) and add_min > 0:
            text += f" / 추가 {int(add_min)}분당 {int(add_fee):,}원"
        if not pd.isna(day_max) and day_max > 0:
            text += f" / 일 최대 {int(day_max):,}원"

        rate = base_fee / base_min  # 분당 요금 (비교 기준)
        return text, rate

    fee_info = df.apply(fee_text_and_rate, axis=1)
    df["요금정보"] = fee_info.apply(lambda x: x[0])
    df["분당요금"] = fee_info.apply(lambda x: x[1])

    return df


df = load_data()
df_geo = df.dropna(subset=["위도", "경도"]).copy()

# ----------------------------
# 사이드바 - 필터
# ----------------------------
st.sidebar.header("🔍 필터")

gu_list = ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
selected_gu = st.sidebar.selectbox("자치구 선택", gu_list)

free_only = st.sidebar.checkbox("무료 주차장만 보기")
weekend_only = st.sidebar.checkbox("주말 운영 주차장만 보기")

filtered = df_geo.copy()
if selected_gu != "전체":
    filtered = filtered[filtered["자치구"] == selected_gu]
if free_only:
    filtered = filtered[filtered["무료여부"] == "무료"]
if weekend_only:
    filtered = filtered[filtered["주말운영여부"] == "운영"]

# ----------------------------
# 메인 화면
# ----------------------------
st.title("🅿️ 서울시 공영주차장 안내 지도")
st.caption("자치구를 선택하면 지도 마커와 요금 비교 결과가 함께 업데이트됩니다. 마커에 마우스를 올리면 상세 정보가 보여요.")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"📍 지도 ({len(filtered)}곳 표시 중)")

    if len(filtered) == 0:
        st.warning("조건에 맞는 주차장이 없습니다.")
    else:
        center_lat = filtered["위도"].mean()
        center_lon = filtered["경도"].mean()
        zoom = 12 if selected_gu != "전체" else 11

        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
        cluster = MarkerCluster().add_to(m)

        for _, row in filtered.iterrows():
            color = "green" if row["무료여부"] == "무료" else "blue"
            tooltip_html = (
                f"<b>{row['주차장명']}</b><br>"
                f"주소: {row['주소']}<br>"
                f"요금: {row['요금정보']}<br>"
                f"주말운영: {row['주말운영시간']}"
            )
            popup_html = (
                f"<b>{row['주차장명']}</b><br>"
                f"주소: {row['주소']}<br>"
                f"구분: {row['무료여부']} ({row['운영구분명']})<br>"
                f"요금: {row['요금정보']}<br>"
                f"주말운영: {row['주말운영시간']}<br>"
                f"총 주차면: {int(row['총 주차면']) if not pd.isna(row['총 주차면']) else '-'}면<br>"
                f"야간개방: {row['야간무료개방여부명']}"
            )
            folium.Marker(
                location=[row["위도"], row["경도"]],
                tooltip=tooltip_html,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon="car", prefix="fa"),
            ).add_to(cluster)

        st_folium(m, width=None, height=560, returned_objects=[])

    st.caption("🟢 무료 주차장 · 🔵 유료 주차장  |  ⚠️ 좌표 정보가 없는 일부 주차장은 지도에 표시되지 않아요.")

with col_right:
    st.subheader("💰 최저가 주차장 찾기")

    target_df = df[df["자치구"] == selected_gu] if selected_gu != "전체" else df

    free_count = (target_df["무료여부"] == "무료").sum()
    if free_count > 0:
        st.success(f"✅ {selected_gu if selected_gu != '전체' else '서울시 전체'}에 **무료 주차장 {free_count}곳**이 있어요!")
        st.dataframe(
            target_df[target_df["무료여부"] == "무료"][["주차장명", "주소"]].reset_index(drop=True),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("무료 주차장이 없어요. 유료 중 가장 저렴한 곳을 알려드릴게요.")

    st.markdown("**유료 주차장 중 분당 요금이 낮은 순 TOP 5**")
    paid_ranked = (
        target_df[(target_df["무료여부"] == "유료") & target_df["분당요금"].notna()]
        .sort_values("분당요금")
        .head(5)[["주차장명", "주소", "요금정보", "주말운영시간"]]
        .reset_index(drop=True)
    )
    if len(paid_ranked) > 0:
        st.dataframe(paid_ranked, use_container_width=True, hide_index=True)
    else:
        st.warning("요금 정보가 있는 유료 주차장이 없어요.")

st.divider()
st.subheader("📋 전체 목록")
show_cols = ["주차장명", "주소", "자치구", "무료여부", "요금정보", "주말운영시간", "야간무료개방여부명", "총 주차면"]
st.dataframe(filtered[show_cols] if len(filtered) else df[show_cols].head(0), use_container_width=True, hide_index=True)

st.caption("데이터 출처: 서울시 공영주차장 안내 정보 (사용자 업로드 CSV)")
