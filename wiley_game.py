import streamlit as st
import random
import time
from streamlit_extras.audio import st_audio
from questions import question_bank
from sheets import save_score_to_sheet, load_scores_from_sheet
from datetime import datetime

# Page setup
st.set_page_config(page_title="Wiley’s Wild What?!", layout="wide")

# Config
GAME_TITLE = "Wiley's Wild What?!"
SLOGAN = "Ready, Set… WHAT?!"
ROUND_TIME_LIMIT = 60
QUESTION_LIMIT = 3

CORRECT_SOUND = "assets/correct.wav"
WRONG_SOUND = "assets/wrong.wav"
TIMEOUT_SOUND = "assets/timeout.wav"

# Custom Styles
st.markdown("""
<style>
    .main {background-color: #f5faff;}
    .big-title {color: white; text-align: center; font-size: 3rem; margin-bottom: 0;}
    .subtitle {color: #f9ff4e; text-align: center; font-size: 1.8rem; font-weight: bold;}
    .question-box {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #008cff;
        box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.1);
    }
    .timer {font-size: 1.3rem; color: #ff2e2e; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.selected_category = None
    st.session_state.questions = []
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.round_start_time = 0
    st.session_state.answered = False
    st.session_state.player_name = ""
    st.session_state.wheel_spin = False

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/WWWLogo1.png", use_column_width=True)
    st.markdown(f'<div class="big-title">{GAME_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">🎤 {SLOGAN}</div>', unsafe_allow_html=True)

# Sidebar Leaderboard
st.sidebar.title("🎛️ Game Controls")
st.sidebar.markdown("### 🏆 Leaderboard")
scores = load_scores_from_sheet()
for i, s in enumerate(scores[:10], 1):
    st.sidebar.markdown(f"**{i}.** {s['user']} – {s['score']} pts ({s['category']})")

# Start Screen
if not st.session_state.started:
    st.session_state.player_name = st.text_input("Enter your name to start 👤")

    categories = list(question_bank.keys())
    st.markdown("### 🎡 Spin the Wheel or Pick a Category")

    col_a, col_b = st.columns(2)
    with col_a:
        selected_manual = st.selectbox("Choose manually", categories + ["Random"])

    with col_b:
        if st.button("🎯 SPIN THE WHEEL!"):
            with st.spinner("Spinning..."):
                for _ in range(20):
                    pick = random.choice(categories)
                    st.markdown(f"🌀 **{pick}**")
                    time.sleep(0.1)
            selected_manual = pick
            st.success(f"🎉 Your category is: **{pick}**")

    if st.button("Start Game!") and st.session_state.player_name:
        st.session_state.selected_category = selected_manual
        st.session_state.started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.round_start_time = time.time()

        if selected_manual == "Random":
            all_questions = sum(question_bank.values(), [])
            st.session_state.questions = random.sample(all_questions, QUESTION_LIMIT)
        else:
            st.session_state.questions = random.sample(question_bank[selected_manual], QUESTION_LIMIT)

        st.experimental_rerun()

# Game In Progress
elif st.session_state.q_index < QUESTION_LIMIT:
    elapsed = time.time() - st.session_state.round_start_time
    remaining = ROUND_TIME_LIMIT - int(elapsed)

    if remaining <= 0:
        st.warning("⏰ Time's up for the round!")
        st_audio(TIMEOUT_SOUND, autoplay=True)
        st.session_state.q_index = QUESTION_LIMIT
        st.experimental_rerun()

    with st.container():
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"🕒 <span class='timer'>Time Remaining: {remaining} seconds</span>", unsafe_allow_html=True)
        q = st.session_state.questions[st.session_state.q_index]
        st.markdown(f"**Question {st.session_state.q_index + 1}:** {q['question']}")

        if not st.session_state.answered:
            selected = st.radio("Choose one:", q["options"], index=None, key=f"q{st.session_state.q_index}")
            if selected:
                if selected == q["answer"]:
                    st.success("🎯 Correct! You nailed it!")
                    st.session_state.score += 1
                    st_audio(CORRECT_SOUND, autoplay=True)
                else:
                    st.error("🚫 Nope! That’s not right.")
                    st_audio(WRONG_SOUND, autoplay=True)
                st.session_state.answered = True

        if st.session_state.answered:
            if st.button("Next"):
                st.session_state.q_index += 1
                st.session_state.answered = False
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Game Over
else:
    st.success(f"🎉 You scored {st.session_state.score} out of {QUESTION_LIMIT}!")
    if st.session_state.player_name:
        save_score_to_sheet(st.session_state.player_name, st.session_state.score, st.session_state.selected_category)

    if st.button("Play Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
