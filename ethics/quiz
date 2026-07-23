# -*- coding: utf-8 -*-
"""
생활과 윤리 학습앱 (Streamlit)
- OX 퀴즈 / 저자 맞히기 / 사상가 얼굴 퀴즈
- 오답노트(틀린 문제 모아서 복습)
- 맞힌 개수에 따른 사상가 레벨 부여 (싱어 → 롤스 → 칸트)

실행 방법:
    pip install streamlit
    streamlit run ethics_quiz_app.py
"""

import os
import random
import streamlit as st

# =====================================================================
# 1. 기본 설정
# =====================================================================
st.set_page_config(page_title="생활과 윤리 퀴즈", page_icon="📘", layout="centered")

IMAGE_DIR = "images"  # 사상가 사진을 넣어둘 폴더 (예: images/칸트.jpg)


# =====================================================================
# 2. 문제 데이터  (여기만 고치면 문제를 자유롭게 추가/수정할 수 있어요)
# =====================================================================

# --- OX 퀴즈 ---  answer: True=O, False=X
OX_QUESTIONS = [
    {"id": "ox1",  "q": "칸트는 행위의 결과보다 동기(의무)를 중시하는 의무론을 주장했다.", "answer": True,
     "explain": "칸트는 결과가 아니라 '선의지'와 의무에서 나온 행위를 도덕적이라고 봤어요."},
    {"id": "ox2",  "q": "벤담은 쾌락의 질적 차이를 강조한 질적 공리주의자다.", "answer": False,
     "explain": "벤담은 쾌락을 '양'으로 계산했어요. 질적 차이를 강조한 사람은 밀(J.S. Mill)이에요."},
    {"id": "ox3",  "q": "롤스는 '무지의 베일' 상태에서 정의의 원칙을 도출했다.", "answer": True,
     "explain": "자신의 처지를 모르는 원초적 입장에서 합의한 원칙이 공정하다고 봤어요."},
    {"id": "ox4",  "q": "싱어는 이익 평등 고려의 원칙에 따라 동물의 이익도 고려해야 한다고 보았다.", "answer": True,
     "explain": "싱어는 종차별주의를 비판하며 쾌고 감수 능력이 있으면 이익을 평등하게 고려해야 한다고 했어요."},
    {"id": "ox5",  "q": "아리스토텔레스는 지나침과 모자람의 중간인 '중용'을 덕의 핵심으로 보았다.", "answer": True,
     "explain": "예: 만용(지나침)과 비겁(모자람)의 중용이 '용기'예요."},
    {"id": "ox6",  "q": "요나스는 현세대만을 위한 윤리를 강조했다.", "answer": False,
     "explain": "요나스의 책임 윤리는 아직 태어나지 않은 '미래 세대'와 자연에 대한 책임을 강조해요."},
    {"id": "ox7",  "q": "칸트의 정언명령은 조건이 붙는 명령이다.", "answer": False,
     "explain": "정언명령은 '무조건적' 명령이에요. 조건(~하려면 ~하라)이 붙는 건 '가언명령'이에요."},
    {"id": "ox8",  "q": "니부어는 사회의 도덕성이 개인의 도덕성보다 낮다고 보았다.", "answer": True,
     "explain": "니부어는 개인은 도덕적이어도 집단은 이기적일 수 있어 사회 구조 개선이 필요하다고 했어요."},
    {"id": "ox9",  "q": "롤스의 차등의 원칙은 최소 수혜자에게 최대 이익이 돌아갈 때 불평등이 정당화된다고 본다.", "answer": True,
     "explain": "사회적·경제적 불평등은 가장 불리한 사람에게 이익이 될 때만 허용된다는 원칙이에요."},
    {"id": "ox10", "q": "레건은 삶의 주체인 동물은 도덕적 권리를 지닌다고 보았다.", "answer": True,
     "explain": "레건(의무론적 동물권)은 삶의 주체(subject-of-a-life)로서 동물이 내재적 가치를 지닌다고 봤어요."},
]

# --- 저자 맞히기 --- (이 책을 쓴 사람은?)
BOOK_QUESTIONS = [
    {"id": "bk1", "book": "정의론", "answer": "롤스",
     "choices": ["롤스", "노직", "싱어", "밀"]},
    {"id": "bk2", "book": "동물 해방", "answer": "싱어",
     "choices": ["레건", "싱어", "칸트", "벤담"]},
    {"id": "bk3", "book": "실천이성비판", "answer": "칸트",
     "choices": ["칸트", "헤겔", "밀", "아리스토텔레스"]},
    {"id": "bk4", "book": "공리주의", "answer": "밀",
     "choices": ["벤담", "밀", "싱어", "롤스"]},
    {"id": "bk5", "book": "니코마코스 윤리학", "answer": "아리스토텔레스",
     "choices": ["플라톤", "소크라테스", "아리스토텔레스", "칸트"]},
    {"id": "bk6", "book": "책임의 원리", "answer": "요나스",
     "choices": ["요나스", "레건", "롤스", "칸트"]},
    {"id": "bk7", "book": "도덕과 입법의 원리 서설", "answer": "벤담",
     "choices": ["밀", "벤담", "싱어", "롤스"]},
    {"id": "bk8", "book": "동물권 옹호", "answer": "레건",
     "choices": ["싱어", "레건", "요나스", "밀"]},
]

# --- 사상가 얼굴 퀴즈 --- (사진이 없으면 힌트로 대체)
FACE_QUESTIONS = [
    {"id": "fc1", "name": "칸트",
     "hint": "정언명령·의무론. 『실천이성비판』을 쓴 독일 철학자.",
     "choices": ["칸트", "밀", "롤스", "싱어"]},
    {"id": "fc2", "name": "롤스",
     "hint": "무지의 베일·정의론. 공정으로서의 정의를 주장한 미국 철학자.",
     "choices": ["롤스", "노직", "칸트", "벤담"]},
    {"id": "fc3", "name": "싱어",
     "hint": "동물 해방·이익 평등 고려의 원칙. 실천윤리학자.",
     "choices": ["레건", "싱어", "밀", "요나스"]},
    {"id": "fc4", "name": "밀",
     "hint": "질적 공리주의. '배부른 돼지보다 배고픈 소크라테스'.",
     "choices": ["벤담", "밀", "칸트", "롤스"]},
    {"id": "fc5", "name": "아리스토텔레스",
     "hint": "덕 윤리·중용. 『니코마코스 윤리학』.",
     "choices": ["플라톤", "아리스토텔레스", "소크라테스", "칸트"]},
]


# =====================================================================
# 3. 레벨(사상가) 정의  —  순서를 바꾸고 싶으면 여기만 수정하세요
# =====================================================================
LEVELS = [
    {"min": 0.0,  "name": "싱어",  "emoji": "🐾", "desc": "실천윤리 입문자 — 이제 막 윤리의 세계에 들어섰어요."},
    {"min": 0.4,  "name": "롤스",  "emoji": "⚖️", "desc": "정의론 탐구자 — 원리를 이해하기 시작했어요."},
    {"min": 0.75, "name": "칸트",  "emoji": "👑", "desc": "정언명령 마스터 — 흔들림 없는 윤리 실력자!"},
]


def get_level(correct, total):
    """정답률에 따라 레벨(사상가) 반환"""
    if total == 0:
        return LEVELS[0]
    rate = correct / total
    result = LEVELS[0]
    for lv in LEVELS:
        if rate >= lv["min"]:
            result = lv
    return result


# =====================================================================
# 4. 세션 상태 초기화
# =====================================================================
def init_state():
    defaults = {
        "correct": 0,          # 총 맞힌 개수
        "answered_ids": set(),  # 이미 채점한 문제 id (중복 채점 방지)
        "wrong_notes": [],     # 오답노트 (dict 리스트)
        "feedback": None,      # 방금 채점 결과 메시지
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def total_answered():
    return len(st.session_state.answered_ids)


def record_answer(qid, is_correct, wrong_info=None):
    """채점 기록: 처음 푸는 문제만 점수/오답에 반영"""
    if qid in st.session_state.answered_ids:
        return
    st.session_state.answered_ids.add(qid)
    if is_correct:
        st.session_state.correct += 1
    elif wrong_info:
        st.session_state.wrong_notes.append(wrong_info)


def remove_from_wrong(qid):
    """오답노트에서 복습으로 맞힌 문제 제거"""
    st.session_state.wrong_notes = [
        w for w in st.session_state.wrong_notes if w["id"] != qid
    ]


# =====================================================================
# 5. 사이드바 (메뉴 + 진행 현황 + 레벨)
# =====================================================================
with st.sidebar:
    st.title("📘 생활과 윤리")
    menu = st.radio(
        "메뉴",
        ["🏠 홈", "⭕ OX 퀴즈", "📖 저자 맞히기", "🧑‍🏫 얼굴 퀴즈", "📝 오답노트"],
    )

    st.divider()
    correct = st.session_state.correct
    total = total_answered()
    lv = get_level(correct, total)
    rate = (correct / total * 100) if total else 0

    st.metric("현재 레벨", f"{lv['emoji']} {lv['name']}")
    st.write(f"**{correct} / {total}** 문제 정답  ({rate:.0f}%)")
    st.caption(lv["desc"])
    st.progress(min(rate / 100, 1.0))
    st.caption(f"오답노트: {len(st.session_state.wrong_notes)}문제")

    st.divider()
    if st.button("🔄 처음부터 다시"):
        for key in ["correct", "answered_ids", "wrong_notes", "feedback"]:
            del st.session_state[key]
        init_state()
        st.rerun()


# =====================================================================
# 6. 화면별 함수
# =====================================================================
def show_home():
    st.title("생활과 윤리 학습앱 📘")
    st.write("퀴즈를 풀면서 사상가 레벨을 올려 보세요!")

    st.subheader("이렇게 공부해요")
    st.markdown(
        """
        1. **⭕ OX 퀴즈** — 개념이 맞는지 O/X로 판단  
        2. **📖 저자 맞히기** — 이 책을 쓴 사상가는 누구?  
        3. **🧑‍🏫 얼굴 퀴즈** — 사진(또는 힌트)으로 사상가 맞히기  
        4. **📝 오답노트** — 틀린 문제만 모아서 다시 풀기  
        """
    )

    st.subheader("레벨 (사상가)")
    st.markdown(
        """
        | 정답률 | 레벨 | 설명 |
        |---|---|---|
        | 0% 이상 | 🐾 **싱어** | 실천윤리 입문자 |
        | 40% 이상 | ⚖️ **롤스** | 정의론 탐구자 |
        | 75% 이상 | 👑 **칸트** | 정언명령 마스터 |
        """
    )
    st.info("💡 얼굴 퀴즈 사진은 `images/` 폴더에 `칸트.jpg`처럼 넣으면 자동으로 보여요. "
            "없으면 힌트로 대체돼요.")


def show_ox():
    st.title("⭕ OX 퀴즈")
    st.caption("개념 설명이 맞으면 O, 틀리면 X!")

    for item in OX_QUESTIONS:
        qid = item["id"]
        done = qid in st.session_state.answered_ids
        with st.container(border=True):
            st.markdown(f"**{item['q']}**")
            c1, c2 = st.columns(2)
            picked = None
            if c1.button("⭕ O", key=f"{qid}_O", disabled=done, use_container_width=True):
                picked = True
            if c2.button("❌ X", key=f"{qid}_X", disabled=done, use_container_width=True):
                picked = False

            if picked is not None:
                is_correct = (picked == item["answer"])
                record_answer(
                    qid, is_correct,
                    wrong_info={
                        "id": qid, "type": "OX", "q": item["q"],
                        "answer": "O" if item["answer"] else "X",
                        "explain": item["explain"],
                    },
                )
                st.rerun()

            if done:
                ans = "O" if item["answer"] else "X"
                st.success(f"정답: {ans}")
                st.caption("📌 " + item["explain"])


def show_book():
    st.title("📖 저자 맞히기")
    st.caption("이 책을 쓴 사상가는 누구일까요?")

    for item in BOOK_QUESTIONS:
        qid = item["id"]
        done = qid in st.session_state.answered_ids
        with st.container(border=True):
            st.markdown(f"### 『{item['book']}』")
            choice = st.radio(
                "저자는?", item["choices"], key=f"{qid}_radio",
                index=None, horizontal=True, disabled=done,
            )
            if st.button("제출", key=f"{qid}_submit", disabled=done):
                if choice is None:
                    st.warning("보기를 선택해 주세요.")
                else:
                    is_correct = (choice == item["answer"])
                    record_answer(
                        qid, is_correct,
                        wrong_info={
                            "id": qid, "type": "저자",
                            "q": f"『{item['book']}』의 저자는?",
                            "answer": item["answer"], "explain": "",
                        },
                    )
                    st.rerun()

            if done:
                st.success(f"정답: {item['answer']}")


def show_face():
    st.title("🧑‍🏫 사상가 얼굴 퀴즈")
    st.caption("사진(또는 힌트)을 보고 사상가를 맞혀 보세요!")

    for item in FACE_QUESTIONS:
        qid = item["id"]
        done = qid in st.session_state.answered_ids
        with st.container(border=True):
            # 이미지가 있으면 사진, 없으면 힌트 표시
            img_path = None
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                p = os.path.join(IMAGE_DIR, item["name"] + ext)
                if os.path.exists(p):
                    img_path = p
                    break

            if img_path:
                st.image(img_path, width=220)
            else:
                st.markdown("#### 🕵️ 힌트")
                st.info(item["hint"])

            choice = st.radio(
                "누구일까요?", item["choices"], key=f"{qid}_radio",
                index=None, horizontal=True, disabled=done,
            )
            if st.button("제출", key=f"{qid}_submit", disabled=done):
                if choice is None:
                    st.warning("보기를 선택해 주세요.")
                else:
                    is_correct = (choice == item["name"])
                    record_answer(
                        qid, is_correct,
                        wrong_info={
                            "id": qid, "type": "얼굴",
                            "q": f"힌트: {item['hint']}",
                            "answer": item["name"], "explain": "",
                        },
                    )
                    st.rerun()

            if done:
                st.success(f"정답: {item['name']}")


def show_review():
    st.title("📝 오답노트")
    notes = st.session_state.wrong_notes

    if not notes:
        st.success("🎉 틀린 문제가 없어요! 완벽합니다.")
        return

    st.caption(f"틀린 문제 {len(notes)}개 — 다시 풀어서 맞히면 오답노트에서 사라져요.")

    for item in list(notes):  # 순회 중 수정되므로 복사본
        qid = item["id"]
        with st.container(border=True):
            st.markdown(f"**[{item['type']}]** {item['q']}")
            if item.get("explain"):
                with st.expander("💡 해설 보기"):
                    st.write(item["explain"])

            # 복습용 재입력
            ans = st.text_input("정답을 입력해 보세요 (O/X 또는 사상가 이름)",
                                key=f"review_{qid}")
            c1, c2 = st.columns(2)
            if c1.button("확인", key=f"review_check_{qid}"):
                if ans.strip() == item["answer"]:
                    st.success("정답! 오답노트에서 제거할게요. ✅")
                    remove_from_wrong(qid)
                    st.rerun()
                else:
                    st.error(f"아직 아니에요. (정답: {item['answer']})")
            if c2.button("정답 보고 제거", key=f"review_del_{qid}"):
                remove_from_wrong(qid)
                st.rerun()


# =====================================================================
# 7. 라우팅
# =====================================================================
if menu == "🏠 홈":
    show_home()
elif menu == "⭕ OX 퀴즈":
    show_ox()
elif menu == "📖 저자 맞히기":
    show_book()
elif menu == "🧑‍🏫 얼굴 퀴즈":
    show_face()
elif menu == "📝 오답노트":
    show_review()
