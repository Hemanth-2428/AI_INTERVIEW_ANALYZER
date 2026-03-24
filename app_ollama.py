import pandas as pd
import streamlit as st

from src.database import (
    create_table,
    delete_all_interviews,
    delete_interview,
    get_all_interviews,
    save_interview,
)
from src.ollama_analysis import analyze_full_interview
from src.speech_to_text import start_recording, stop_recording


st.set_page_config(
    page_title="AI Interview Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "logged_in" not in st.session_state:
    st.switch_page("pages/login.py")

st.title("AI Interview Analyzer (LLM Powered - Ollama)")
current_role = st.session_state.role

create_table()

if st.button("🔄 Reset Interview", key="reset_interview"):
    for key in [
        "question",
        "answer",
        "history",
        "mode",
        "recording",
        "analysis_result",
        "audio_recorder",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if "question" not in st.session_state:
    st.session_state.question = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "mode" not in st.session_state:
    st.session_state.mode = None

if "recording" not in st.session_state:
    st.session_state.recording = False

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎤 Record Question", key="record_question"):
        if st.session_state.recording:
            st.warning("Stop current recording first")
        else:
            start_recording()
            st.session_state.mode = "question"
            st.session_state.recording = True
            st.success("Recording interviewer question...")

with col2:
    if st.button("🗣️ Record Answer", key="record_answer"):
        if st.session_state.recording:
            st.warning("Stop current recording first")
        else:
            start_recording()
            st.session_state.mode = "answer"
            st.session_state.recording = True
            st.success("Recording candidate answer...")

with col3:
    if st.button("⏹️ Stop Recording", key="stop_recording"):
        if not st.session_state.recording:
            st.warning("No recording in progress")
        else:
            text, duration = stop_recording()

            if text.strip() == "":
                st.warning("No audio detected")
            else:
                if st.session_state.mode == "question":
                    st.session_state.question = text
                elif st.session_state.mode == "answer":
                    st.session_state.answer = text

            st.session_state.recording = False
            st.session_state.mode = None

if st.session_state.question:
    st.subheader("Interviewer Question")
    st.write(st.session_state.question)

if st.session_state.answer:
    st.subheader("Candidate Answer")
    st.write(st.session_state.answer)

if st.button("💾 Save Round", key="save_round"):
    if st.session_state.question and st.session_state.answer:
        st.session_state.history.append(
            {
                "question": st.session_state.question,
                "answer": st.session_state.answer,
            }
        )

        st.session_state.question = ""
        st.session_state.answer = ""
        st.success("Round saved successfully")
    else:
        st.warning("Please record both question and answer")

st.markdown("---")
st.subheader("Interview History")

for i, item in enumerate(st.session_state.history, 1):
    with st.expander(f"Round {i}"):
        st.write("Question:", item["question"])
        st.write("Answer:", item["answer"])

if st.button("📊 Finalize Interview and Get Overall Score", key="finalize_interview"):
    if not st.session_state.history:
        st.error("No interview rounds saved")
    else:
        with st.spinner("Analyzing interview..."):
            st.session_state.analysis_result = analyze_full_interview(
                st.session_state.history
            )

        result = st.session_state.analysis_result

        st.markdown("---")
        st.subheader("AI Evaluation")
        st.write("Confidence Score:", result["confidence_score"], "%")
        st.write("Communication Score:", result["communication_score"], "%")
        st.write("Overall Score:", result["overall_score"], "%")

        st.subheader("Feedback")
        st.write(result["feedback"])

        st.subheader("Explanation")
        st.write(result["explanation"])

        st.markdown("---")
        st.subheader("Score Visualization")

        score_data = {
            "Metric": ["Confidence", "Communication", "Overall"],
            "Score": [
                result["confidence_score"],
                result["communication_score"],
                result["overall_score"],
            ],
        }

        df = pd.DataFrame(score_data)
        st.bar_chart(df.set_index("Metric"))

        for item in st.session_state.history:
            save_interview(
                current_role,
                item["question"],
                item["answer"],
                st.session_state.analysis_result,
            )

        st.success("Interview results saved to database")

st.markdown("---")
st.subheader("Past Interview Records")

if current_role == "admin":
    st.markdown("---")
    st.subheader("Admin Panel")
    st.write("Admin controls for managing interview data.")

    if st.button("🧹 Delete All Interview Records", key="delete_all_records"):
        delete_all_interviews(current_role)
        st.success("All records deleted.")
        st.rerun()

rows = get_all_interviews(current_role)

if not rows:
    st.info("No interview records saved yet")
else:
    for index, row in enumerate(rows, 1):
        with st.expander(f"Record {index} | {row[9]}"):
            st.write("Question:")
            st.write(row[2])

            st.write("Answer:")
            st.write(row[3])

            st.write("Confidence Score:", row[4], "%")
            st.write("Communication Score:", row[5], "%")
            st.write("Overall Score:", row[6], "%")

            st.write("Feedback:")
            st.write(row[7])

            st.write("Explanation:")
            st.write(row[8])

            if st.button(f"🗑️ Delete Record {index}", key=f"delete_record_{row[0]}"):
                delete_interview(row[0], current_role)
                st.success("Record deleted")
                st.rerun()

if st.button("🚪 Logout", key="logout"):
    st.session_state.clear()
    st.switch_page("pages/login.py")
