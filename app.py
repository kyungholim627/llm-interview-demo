import json
import random
import re
import time
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="LLM Medical Query Susceptibility Demo",
    layout="wide"
)

DATA_DIR = Path(".")


@st.cache_data
def load_data():
    rows = []
    files = list(DATA_DIR.glob("*_8var.json"))

    for file in files:
        model_name = file.stem.replace("_8var", "")
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            rows.append({
                "model": model_name,
                "prompt": item.get("prompt", ""),
                "correct_answer": item.get("correct_answer", ""),
                "response": item.get("response", ""),
                "is_correct": item.get("is_correct", False),
                "category": item.get("category", "")
            })

    return rows


def normalize_for_matching(text):
    text = str(text)

    text = text.replace("\\n", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\\", "")

    text = text.replace('"', "")
    text = text.replace("'", "")
    text = text.replace("“", "")
    text = text.replace("”", "")
    text = text.replace("‘", "")
    text = text.replace("’", "")

    text = re.sub(r"\s+", "", text)

    return text.lower()


def find_matching_prompt(user_prompt, rows):
    user_prompt_clean = normalize_for_matching(user_prompt)

    for row in rows:
        row_prompt_clean = normalize_for_matching(row["prompt"])
        if row_prompt_clean == user_prompt_clean:
            return row

    for row in rows:
        row_prompt_clean = normalize_for_matching(row["prompt"])
        if user_prompt_clean in row_prompt_clean or row_prompt_clean in user_prompt_clean:
            return row

    return None


def stream_response(
    text,
    initial_delay=1.2,
    min_delay=0.006,
    max_delay=0.028,
    pause_after_sentence=0.12
):
    """
    Simulates real-time response generation.
    - initial_delay: delay before response starts
    - min_delay/max_delay: random typing speed range per character
    - pause_after_sentence: extra pause after sentence-ending punctuation
    """
    placeholder = st.empty()
    printed = ""

    with st.spinner("Generating model response..."):
        time.sleep(initial_delay)

    for char in str(text):
        printed += char
        placeholder.markdown(printed)

        if char in [".", "!", "?", "\n"]:
            time.sleep(pause_after_sentence)
        else:
            time.sleep(random.uniform(min_delay, max_delay))


rows = load_data()

st.title("LLM Medical Query Susceptibility Demo")
st.caption("Precomputed demonstration: same medical question, different user-driven prompt framing.")

if not rows:
    st.error("No *_8var.json files found. Put your JSON files in the same folder as app.py.")
    st.stop()


models = sorted(list(set(row["model"] for row in rows)))

selected_model = st.sidebar.selectbox(
    "Select model",
    models
)

model_rows = [
    row for row in rows
    if row["model"] == selected_model
]


st.subheader("Input Prompt")

user_prompt = st.text_area(
    "Paste or type the prompt here",
    height=300,
    placeholder="Paste the prompt here..."
)

run_button = st.button("Generate Response", type="primary")


if run_button:
    if not user_prompt.strip():
        st.warning("Please enter a prompt first.")
        st.stop()

    matched = find_matching_prompt(user_prompt, model_rows)

    if matched is None:
        st.error("No matching prompt found in the selected model JSON file.")
        st.warning(
            "Check whether the selected model matches the JSON file containing this prompt. "
            "Also check whether the prompt text was substantially changed."
        )
        st.stop()

    st.divider()

    st.subheader("Correct Answer")
    st.info(matched["correct_answer"])

    st.subheader("Model Response")
    stream_response(
        matched["response"],
        initial_delay=1.2,
        min_delay=0.006,
        max_delay=0.028,
        pause_after_sentence=0.12
    )

    st.subheader("Is Correct?")

    with st.spinner("Evaluating answer..."):
        time.sleep(1.5)

    if matched["is_correct"]:
        st.success("True — the model answer is correct.")
    else:
        st.error("False — the model answer is incorrect.")