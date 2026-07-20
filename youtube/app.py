import re
import os
from collections import Counter
from datetime import datetime, timezone, timedelta

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from wordcloud import WordCloud

# ──────────────────────────────────────────────────────────────
# 기본 설정
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="유튜브 댓글 분석기", page_icon="📊", layout="wide")

KST = timezone(timedelta(hours=9))               # 한국 표준시
FONT_PATH = "NanumGothic.ttf"                     # 깃허브 루트에 업로드한 폰트

# 한글 형태소 분석기 (kiwipiepy) 로드
try:
    from kiwipiepy import Kiwi
    _kiwi = Kiwi()
except Exception:
    _kiwi = None

# 워드클라우드에서 제외할 한 글자성 불용어(형태소 명사 위주라 많이 필요 없음)
STOPWORDS = {
    "영상", "댓글", "진짜", "정말", "그냥", "생각", "사람", "이거", "저거",
    "우리", "너무", "완전", "다들", "하나", "때문", "이번", "요즘", "이런",
}


# ──────────────────────────────────────────────────────────────
# 유틸 함수
# ──────────────────────────────────────────────────────────────
def extract_video_id(url: str):
    """다양한 형태의 유튜브 URL에서 영상 ID를 추출한다."""
    if not url:
        return None
    url = url.strip()
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",   # ID만 붙여넣은 경우
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


@st.cache_resource
def get_youtube_client():
    """secrets에 저장된 API 키로 유튜브 클라이언트를 만든다."""
    api_key = st.secrets.get("YOUTUBE_API_KEY")
    if not api_key:
        return None
    return build("youtube", "v3", developerKey=api_key)


@st.cache_data(show_spinner=False)
def get_video_info(_yt, video_id: str):
    res = _yt.videos().list(part="snippet,statistics", id=video_id).execute()
    items = res.get("items", [])
    if not items:
        return None
    it = items[0]
    sn, stt = it["snippet"], it.get("statistics", {})
    return {
        "title": sn["title"],
        "channel": sn["channelTitle"],
        "published": sn["publishedAt"],
        "views": int(stt.get("viewCount", 0)),
        "likes": int(stt.get("likeCount", 0)),
        "comments": int(stt.get("commentCount", 0)),
    }


@st.cache_data(show_spinner=False)
def get_comments(_yt, video_id: str, max_count: int):
    """댓글(대댓글 제외 최상위 댓글)을 max_count개까지 수집한다."""
    rows, token = [], None
    while len(rows) < max_count:
        req = _yt.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=token,
            textFormat="plainText",
            order="time",
        )
        res = req.execute()
        for item in res.get("items", []):
            c = item["snippet"]["topLevelComment"]["snippet"]
            # UTC → KST 변환
            dt = datetime.fromisoformat(
                c["publishedAt"].replace("Z", "+00:00")
            ).astimezone(KST)
            rows.append({
                "author": c["authorDisplayName"],
                "text": c["textDisplay"],
                "likes": c.get("likeCount", 0),
                "published": dt,
            })
            if len(rows) >= max_count:
                break
        token = res.get("nextPageToken")
        if not token:
            break
    return pd.DataFrame(rows)


def extract_nouns(texts):
    """댓글 전체에서 한글 명사만 뽑아 빈도를 센다."""
    counter = Counter()
    joined = "\n".join(texts)
    if _kiwi is not None:
        for tok in _kiwi.tokenize(joined):
            if tok.tag in ("NNG", "NNP") and len(tok.form) > 1:
                if tok.form not in STOPWORDS:
                    counter[tok.form] += 1
    else:
        # kiwi 로드 실패 시: 2글자 이상 한글 덩어리로 대체
        for w in re.findall(r"[가-힣]{2,}", joined):
            if w not in STOPWORDS:
                counter[w] += 1
    return counter


# ──────────────────────────────────────────────────────────────
# 화면 구성
# ──────────────────────────────────────────────────────────────
st.title("📊 유튜브 댓글 분석기")
st.caption("영상 링크를 넣으면 시간대별 추이 · 반응도 · 한글 워드클라우드를 만들어줍니다.")

yt = get_youtube_client()
if yt is None:
    st.error("⚠️ API 키가 없습니다. 앱 설정(Settings → Secrets)에 "
             "`YOUTUBE_API_KEY = \"발급받은키\"` 를 추가하세요.")
    st.stop()

if not os.path.exists(FONT_PATH):
    st.warning(f"⚠️ 폰트 파일 `{FONT_PATH}` 을 찾을 수 없어 워드클라우드가 깨질 수 있어요. "
               "깃허브 저장소 최상위에 나눔고딕 파일을 올렸는지 확인하세요.")

col_url, col_num = st.columns([3, 1])
with col_url:
    url = st.text_input("유튜브 영상 링크", placeholder="https://www.youtube.com/watch?v=...")
with col_num:
    max_count = st.number_input("분석할 댓글 수", min_value=10, max_value=1000,
                                value=200, step=10)

run = st.button("🔍 분석 시작", type="primary", use_container_width=True)

if run:
    vid = extract_video_id(url)
    if not vid:
        st.error("올바른 유튜브 링크가 아니에요. 다시 확인해 주세요.")
        st.stop()

    try:
        info = get_video_info(yt, vid)
        if info is None:
            st.error("영상을 찾을 수 없어요. 링크를 확인해 주세요.")
            st.stop()

        # 1) 영상 + 기본 정보
        left, right = st.columns([1, 1])
        with left:
            st.video(f"https://www.youtube.com/watch?v={vid}")
        with right:
            st.subheader(info["title"])
            st.write(f"**채널:** {info['channel']}")
            m1, m2, m3 = st.columns(3)
            m1.metric("조회수", f"{info['views']:,}")
            m2.metric("좋아요", f"{info['likes']:,}")
            m3.metric("전체 댓글", f"{info['comments']:,}")

        # 2) 댓글 수집
        with st.spinner("댓글을 불러오는 중..."):
            df = get_comments(yt, vid, int(max_count))

        if df.empty:
            st.warning("댓글이 없거나 댓글이 사용 중지된 영상이에요.")
            st.stop()

        st.success(f"댓글 {len(df):,}개를 분석했어요.")
        st.divider()

        # 3) 시간대별 댓글 작성 추이
        st.header("⏱️ 시간대별 댓글 작성 추이")
        tab_hour, tab_date = st.tabs(["시간대(0~23시)", "날짜별"])

        with tab_hour:
            hour_counts = (df["published"].dt.hour
                           .value_counts()
                           .reindex(range(24), fill_value=0)
                           .sort_index())
            hour_counts.index.name = "시(KST)"
            st.bar_chart(hour_counts)
            peak = int(hour_counts.idxmax())
            st.caption(f"가장 활발한 시간대: **{peak}시** ({int(hour_counts.max())}개)")

        with tab_date:
            date_counts = (df["published"].dt.date
                           .value_counts()
                           .sort_index())
            date_counts.index = pd.to_datetime(date_counts.index)
            st.line_chart(date_counts)

        st.divider()

        # 4) 댓글 반응도
        st.header("👍 댓글 반응도")
        c1, c2, c3 = st.columns(3)
        c1.metric("평균 좋아요", f"{df['likes'].mean():.1f}")
        c2.metric("최다 좋아요", f"{df['likes'].max():,}")
        zero_ratio = (df["likes"] == 0).mean() * 100
        c3.metric("좋아요 0개 비율", f"{zero_ratio:.0f}%")

        st.markdown("**🏆 좋아요 많은 댓글 TOP 5**")
        top5 = df.sort_values("likes", ascending=False).head(5)[["author", "likes", "text"]]
        top5.columns = ["작성자", "좋아요", "댓글"]
        st.dataframe(top5, use_container_width=True, hide_index=True)

        st.divider()

        # 5) 한글 워드클라우드
        st.header("☁️ 댓글 워드클라우드")
        counter = extract_nouns(df["text"].tolist())
        if not counter:
            st.info("워드클라우드로 만들 한글 단어가 부족해요.")
        else:
            wc = WordCloud(
                font_path=FONT_PATH if os.path.exists(FONT_PATH) else None,
                background_color="white",
                width=1000, height=500,
                max_words=100,
                colormap="tab10",
            ).generate_from_frequencies(counter)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

            st.markdown("**자주 나온 단어 TOP 10**")
            top_words = pd.DataFrame(counter.most_common(10), columns=["단어", "빈도"])
            st.dataframe(top_words, use_container_width=True, hide_index=True)

    except HttpError as e:
        st.error(f"유튜브 API 오류가 발생했어요: {e}")
    except Exception as e:
        st.error(f"처리 중 문제가 발생했어요: {e}")
