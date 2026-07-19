"""
AI-Powered Sports Quiz Generation Agent

Streamlit Frontend
"""

from __future__ import annotations

import streamlit as st


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="AI-Powered Sports Quiz Generation Agent",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# Session State
# ==========================================================

if "quiz_generated" not in st.session_state:
    st.session_state.quiz_generated = False


# ==========================================================
# Header
# ==========================================================

st.title("🏆 AI-Powered Sports Quiz Generation Agent")

st.markdown(
    """
Generate AI-powered sports quizzes using **Semantic Search**, **Vector Database**,
**DuckDuckGo Search**, and **Google Gemini**.
"""
)

st.divider()


# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.header("⚙️ Quiz Settings")

    sport = st.selectbox(
        "Select Sport",
        (
            "Cricket",
            "Football",
            "Basketball",
            "Tennis",
            "Badminton",
            "Baseball",
            "Olympics",
        ),
    )

    difficulty = st.selectbox(
        "Difficulty",
        (
            "Easy",
            "Medium",
            "Hard",
        ),
    )

    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=15,
        value=5,
        step=5,
    )

    st.divider()

    generate_quiz = st.button(
        "🚀 Generate Quiz",
        use_container_width=True,
    )


# ==========================================================
# Main Content
# ==========================================================

left_col, right_col = st.columns([2, 1])

with left_col:

    st.subheader("📋 Selected Configuration")

    st.info(
        f"""
**Sport:** {sport}

**Difficulty:** {difficulty}

**Questions:** {num_questions}
"""
    )

    if generate_quiz:

        st.session_state.quiz_generated = True

        st.success("Frontend is working successfully!")

        st.balloons()


with right_col:

    st.subheader("📊 Quiz Summary")

    st.metric("Sport", sport)
    st.metric("Difficulty", difficulty)
    st.metric("Questions", num_questions)


# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(
    "AI-Powered Sports Quiz Generation Agent • Streamlit Frontend"
)