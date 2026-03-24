import json
import re

import ollama


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "we",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
    "you",
    "your",
    "tell",
    "about",
}

INAPPROPRIATE_WORDS = {
    "idiot",
    "stupid",
    "hate",
    "damn",
    "shit",
    "fuck",
    "nonsense",
}

VAGUE_PHRASES = {
    "i do not know",
    "don't know",
    "no idea",
    "anything",
    "whatever",
    "something like that",
    "and all",
}


def safe_parse(text):
    try:
        text = text.replace("```json", "").replace("```", "")
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return None


def ensure_string(value):
    if isinstance(value, tuple):
        return str(value[0])
    return str(value)


def clamp_score(value):
    return max(0, min(100, int(round(value))))


def tokenize(text):
    return re.findall(r"[a-zA-Z]+", text.lower())


def keyword_overlap(question, answer):
    question_tokens = {t for t in tokenize(question) if t not in STOP_WORDS}
    answer_tokens = {t for t in tokenize(answer) if t not in STOP_WORDS}

    if not question_tokens:
        return 1.0

    return len(question_tokens & answer_tokens) / len(question_tokens)


def compute_filler_penalty(answer):
    answer = ensure_string(answer)

    fillers = re.findall(
        r"\b(um|uh|ah|like|you know|hmm|actually|basically|so)\b",
        answer.lower(),
    )

    penalty = min(len(fillers) * 2, 25)
    return penalty, len(fillers)


def compute_relevance_penalty(question, answer):
    overlap = keyword_overlap(question, answer)
    answer_word_count = len(tokenize(answer))

    if answer_word_count <= 3:
        return 35
    if overlap < 0.10:
        return 28
    if overlap < 0.20:
        return 18
    if overlap < 0.30:
        return 10
    return 0


def compute_clarity_penalty(answer):
    answer_lower = answer.lower().strip()
    word_count = len(tokenize(answer))
    penalty = 0

    if word_count < 6:
        penalty += 20
    elif word_count < 12:
        penalty += 10

    for phrase in VAGUE_PHRASES:
        if phrase in answer_lower:
            penalty += 12

    repeated_words = re.findall(r"\b(\w+)\s+\1\b", answer_lower)
    penalty += min(len(repeated_words) * 4, 12)

    return min(penalty, 30)


def compute_inappropriate_penalty(answer):
    answer_tokens = set(tokenize(answer))
    hits = answer_tokens & INAPPROPRIATE_WORDS
    if not hits:
        return 0
    return min(20 * len(hits), 40)


def build_prompt(full_context):
    return f"""
You are a strict AI interviewer evaluating candidate answers.

Score harshly when an answer is vague, irrelevant, incomplete, unprofessional, or not aligned with the question.
Do not give high scores unless the answer is genuinely strong.

Scoring guidance:
- 90-100: excellent, highly relevant, clear, complete, polished, professional
- 75-89: good, relevant and clear, but missing depth or polish
- 50-74: average, partially relevant, somewhat unclear, generic, or incomplete
- 25-49: weak, mostly vague, poorly structured, low clarity, or limited relevance
- 0-24: very poor, unrelated, inappropriate, evasive, or nonsensical

Evaluation rules:
- Confidence score should reflect clarity, ownership, conviction, and professionalism.
- Communication score should reflect relevance to the question, structure, grammar, specificity, and clarity.
- If the answer is not related to the question, lower both scores strongly.
- If the answer is inappropriate or offensive, score very low.
- If the answer is too short or generic, do not rate it highly.

Return ONLY valid JSON in this exact shape:
{{
  "confidence_score": integer 0-100,
  "communication_score": integer 0-100,
  "overall_score": integer 0-100,
  "feedback": "short feedback",
  "explanation": "detailed explanation focused on relevance, clarity, completeness, and professionalism"
}}

Interview:
{full_context}
"""


def build_fallback_result(
    total_filler_penalty,
    total_relevance_penalty,
    total_clarity_penalty,
    total_inappropriate_penalty,
):
    confidence_score = clamp_score(
        78 - total_filler_penalty - total_clarity_penalty - total_inappropriate_penalty
    )
    communication_score = clamp_score(
        80
        - total_filler_penalty
        - total_relevance_penalty
        - total_clarity_penalty
        - total_inappropriate_penalty
    )
    overall_score = clamp_score((confidence_score + communication_score) / 2)

    feedback_parts = []

    if total_inappropriate_penalty > 0:
        feedback_parts.append("The answer contains inappropriate language.")
    if total_relevance_penalty >= 18:
        feedback_parts.append("The answer is weakly related to the question.")
    elif total_relevance_penalty > 0:
        feedback_parts.append("The answer is only partially aligned with the question.")
    if total_clarity_penalty >= 20:
        feedback_parts.append("The response lacks clarity and detail.")
    elif total_clarity_penalty > 0:
        feedback_parts.append("The response could be clearer and more complete.")
    if total_filler_penalty >= 8:
        feedback_parts.append("Too many filler words reduced the quality of delivery.")

    if not feedback_parts:
        feedback_parts.append("The answer is relevant and reasonably clear.")

    explanation = (
        "Fallback scoring was used because Ollama is not available. "
        f"Confidence={confidence_score}, Communication={communication_score}, Overall={overall_score}. "
        "Scores were estimated using relevance, clarity, filler-word usage, and inappropriate-language penalties."
    )

    return {
        "confidence_score": confidence_score,
        "communication_score": communication_score,
        "overall_score": overall_score,
        "feedback": " ".join(feedback_parts),
        "explanation": explanation,
    }


def analyze_full_interview(interview_history):
    if not interview_history:
        return {
            "confidence_score": 0,
            "communication_score": 0,
            "overall_score": 0,
            "feedback": "No interview data found.",
            "explanation": "No questions were answered.",
        }

    full_context = ""
    total_filler_penalty = 0
    total_relevance_penalty = 0
    total_clarity_penalty = 0
    total_inappropriate_penalty = 0

    for idx, item in enumerate(interview_history, 1):
        question = ensure_string(item["question"])
        answer = ensure_string(item["answer"])

        filler_penalty, filler_count = compute_filler_penalty(answer)
        relevance_penalty = compute_relevance_penalty(question, answer)
        clarity_penalty = compute_clarity_penalty(answer)
        inappropriate_penalty = compute_inappropriate_penalty(answer)

        total_filler_penalty += filler_penalty
        total_relevance_penalty += relevance_penalty
        total_clarity_penalty += clarity_penalty
        total_inappropriate_penalty += inappropriate_penalty

        full_context += f"""
Round {idx}
Question: {question}
Answer: {answer}
Filler Words: {filler_count}
Relevance Penalty Hint: {relevance_penalty}
Clarity Penalty Hint: {clarity_penalty}
Inappropriate Penalty Hint: {inappropriate_penalty}
"""

    prompt = build_prompt(full_context)

    try:
        response = ollama.chat(
            model="mistral:7b-instruct",
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.1,
                "top_p": 0.7,
                "num_predict": 300,
            },
        )
        result = safe_parse(response["message"]["content"])
    except Exception:
        result = build_fallback_result(
            total_filler_penalty,
            total_relevance_penalty,
            total_clarity_penalty,
            total_inappropriate_penalty,
        )
        return result

    if not result:
        return build_fallback_result(
            total_filler_penalty,
            total_relevance_penalty,
            total_clarity_penalty,
            total_inappropriate_penalty,
        )

    confidence_penalty = total_filler_penalty + total_clarity_penalty + total_inappropriate_penalty
    communication_penalty = (
        total_filler_penalty
        + total_relevance_penalty
        + total_clarity_penalty
        + total_inappropriate_penalty
    )

    result["confidence_score"] = clamp_score(
        result.get("confidence_score", 0) - confidence_penalty
    )
    result["communication_score"] = clamp_score(
        result.get("communication_score", 0) - communication_penalty
    )
    result["overall_score"] = clamp_score(
        (result["confidence_score"] + result["communication_score"]) / 2
    )

    return result
