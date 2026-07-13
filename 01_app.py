import streamlit as st
import random

st.set_page_config(
    page_title="윤리 학습 앱",
    page_icon="📚",
    layout="centered"
)

st.title("📚 윤리 학습 앱")
st.write("윤리 과목을 재미있게 공부해보세요!")

menu = st.sidebar.radio(
    "메뉴 선택",
    ["홈", "OX 퀴즈", "사상가 퀴즈"]
)

# -----------------------------
# 홈
# -----------------------------
if menu == "홈":
    st.header("환영합니다!")
    st.write("""
    ### 학습 메뉴
    - ⭕❌ OX 퀴즈
    - 👨‍🏫 사상가 퀴즈

    원하는 메뉴를 선택하여 공부해보세요.
    """)

# -----------------------------
# OX 퀴즈 데이터
# -----------------------------
ox_questions = [
    {
        "question":"공자는 인(仁)을 중요하게 생각하였다.",
        "answer":"O",
        "explanation":"맞습니다. 공자는 인을 최고의 덕목으로 보았습니다."
    },
    {
        "question":"맹자는 성악설을 주장하였다.",
        "answer":"X",
        "explanation":"맹자는 성선설을 주장했습니다."
    },
    {
        "question":"순자는 성악설을 주장하였다.",
        "answer":"O",
        "explanation":"맞습니다."
    },
    {
        "question":"칸트는 결과보다 의무를 중요하게 생각하였다.",
        "answer":"O",
        "explanation":"칸트는 의무론을 주장했습니다."
    },
    {
        "question":"공리주의는 행위자의 의도만을 중요하게 생각한다.",
        "answer":"X",
        "explanation":"공리주의는 결과를 중요하게 생각합니다."
    }
]

# -----------------------------
# OX 퀴즈
# -----------------------------
if menu == "OX 퀴즈":

    st.header("⭕❌ OX 퀴즈")

    if "ox_index" not in st.session_state:
        st.session_state.ox_index = 0
        st.session_state.ox_score = 0
        random.shuffle(ox_questions)

    if st.session_state.ox_index < len(ox_questions):

        q = ox_questions[st.session_state.ox_index]

        st.subheader(f"문제 {st.session_state.ox_index+1}")

        st.write(q["question"])

        col1,col2 = st.columns(2)

        if col1.button("⭕ O"):
            if q["answer"]=="O":
                st.success("정답!")
                st.session_state.ox_score += 1
            else:
                st.error("오답!")

            st.info(q["explanation"])
            st.session_state.ox_index += 1
            st.rerun()

        if col2.button("❌ X"):
            if q["answer"]=="X":
                st.success("정답!")
                st.session_state.ox_score += 1
            else:
                st.error("오답!")

            st.info(q["explanation"])
            st.session_state.ox_index += 1
            st.rerun()

    else:

        st.success("퀴즈 종료!")

        st.header(f"점수 : {st.session_state.ox_score} / {len(ox_questions)}")

        if st.button("다시 풀기"):
            del st.session_state["ox_index"]
            del st.session_state["ox_score"]
            st.rerun()

# -----------------------------
# 사상가 퀴즈
# -----------------------------
thinker_questions = [

    {
        "question":"'최대 다수의 최대 행복'을 주장한 사상가는?",
        "options":["칸트","벤담","공자","노자"],
        "answer":"벤담"
    },
    {
        "question":"의무론을 주장한 사상가는?",
        "options":["칸트","밀","순자","맹자"],
        "answer":"칸트"
    },
    {
        "question":"성선설을 주장한 사람은?",
        "options":["맹자","순자","한비자","장자"],
        "answer":"맹자"
    },
    {
        "question":"성악설을 주장한 사람은?",
        "options":["공자","순자","맹자","노자"],
        "answer":"순자"
    },
    {
        "question":"인(仁)을 가장 중요한 덕목으로 본 사람은?",
        "options":["공자","한비자","장자","묵자"],
        "answer":"공자"
    },
    {
        "question":"법치주의를 주장한 사상가는?",
        "options":["공자","맹자","한비자","장자"],
        "answer":"한비자"
    }
]

if menu=="사상가 퀴즈":

    st.header("👨‍🏫 사상가 퀴즈")

    if "thinker_index" not in st.session_state:
        random.shuffle(thinker_questions)
        st.session_state.thinker_index=0
        st.session_state.thinker_score=0

    if st.session_state.thinker_index < len(thinker_questions):

        q=thinker_questions[st.session_state.thinker_index]

        st.subheader(f"문제 {st.session_state.thinker_index+1}")

        answer=st.radio(
            q["question"],
            q["options"],
            key=f"radio{st.session_state.thinker_index}"
        )

        if st.button("정답 확인"):

            if answer==q["answer"]:
                st.success("정답입니다!")
                st.session_state.thinker_score+=1
            else:
                st.error(f"오답입니다. 정답은 {q['answer']} 입니다.")

            st.session_state.thinker_index+=1
            st.rerun()

    else:

        st.success("모든 문제를 풀었습니다!")

        st.header(f"점수 : {st.session_state.thinker_score} / {len(thinker_questions)}")

        if st.button("다시 시작"):
            del st.session_state["thinker_index"]
            del st.session_state["thinker_score"]
            st.rerun()
