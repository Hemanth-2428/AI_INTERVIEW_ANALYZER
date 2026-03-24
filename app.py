import streamlit as st

# Import modules
from src.speech_to_text import record_audio
from src.sentiment_analysis import analyze_sentiment
from src.communication_analysis import analyze_communication
from src.confidence_analysis import analyze_confidence
from src.explainability import generate_explanation


# Page title
st.title("AI Interview Analyzer with Explainable AI")

st.write("Click the button and answer the interview question.")


# Button to start recording
if st.button("Start Recording"):

    st.write("Recording... Speak now")

    # Record audio and convert to text
    text = record_audio()

    st.subheader("Your Answer:")
    st.write(text)


    # -----------------------------
    # Confidence Analysis (FIXED)
    # -----------------------------
    confidence_score, confidence_feedback = analyze_confidence(text)

    st.subheader("Confidence Analysis")
    st.write("Confidence Score:", confidence_score, "%")
    st.write("Feedback:", confidence_feedback)


    # -----------------------------
    # Sentiment Analysis
    # -----------------------------
    sentiment, polarity, sentiment_feedback = analyze_sentiment(text)

    st.subheader("Sentiment Analysis")
    st.write("Sentiment:", sentiment)
    st.write("Sentiment Polarity:", round(polarity, 2))
    st.write("Feedback:", sentiment_feedback)


    # -----------------------------
    # Communication Analysis
    # -----------------------------
    communication_score, communication_feedback = analyze_communication(text)

    st.subheader("Communication Analysis")
    st.write("Communication Score:", communication_score, "%")
    st.write("Feedback:", communication_feedback)


    # -----------------------------
    # Overall Score
    # -----------------------------
    overall_score = round(
        (confidence_score + communication_score) / 2, 2
    )

    st.subheader("Overall Interview Score")
    st.write("Overall Score:", overall_score, "%")

    if overall_score > 75:
        st.success("Excellent interview performance!")

    elif overall_score > 50:
        st.warning("Good performance, but room for improvement.")

    else:
        st.error("Needs improvement. Practice more.")


    # -----------------------------
    # Explainable AI Section
    # -----------------------------
    st.subheader("Explainable AI Analysis")

    explanation, feature_names, features = generate_explanation(
        confidence_score, communication_score
    )

    st.write("Score Contributions:")

    st.write(
        "Confidence Contribution:",
        explanation["Confidence Score Contribution"]
    )

    st.write(
        "Communication Contribution:",
        explanation["Communication Score Contribution"]
    )


    # Bar chart visualization
    chart_data = {
        "Confidence Score": confidence_score,
        "Communication Score": communication_score
    }

    st.bar_chart(chart_data)
