import json
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
                "metadata": item.get("metadata", {}),
                "category": item.get("category", "")
            })

    return rows


def normalize_text(text):
    return (
        str(text)
        .replace("\\n", "\n")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace('"', "")
        .replace("“", "")
        .replace("”", "")
        .replace("’", "'")
        .strip()
    )


def compact_text(text):
    return " ".join(normalize_text(text).split())


def find_matching_prompt(user_prompt, rows):
    user_prompt_clean = compact_text(user_prompt)

    for row in rows:
        row_prompt_clean = compact_text(row["prompt"])
        if row_prompt_clean == user_prompt_clean:
            return row

    for row in rows:
        row_prompt_clean = compact_text(row["prompt"])
        if user_prompt_clean in row_prompt_clean or row_prompt_clean in user_prompt_clean:
            return row

    return None


def stream_response(text, delay=0.02):
    placeholder = st.empty()
    printed = ""

    for char in text:
        printed += char
        placeholder.markdown(printed)
        time.sleep(delay)


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


st.sidebar.divider()
st.sidebar.write(f"Loaded cases for selected model: **{len(model_rows)}**")


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
    stream_response(matched["response"], delay=0.02)

    st.subheader("Is Correct?")
    if matched["is_correct"]:
        st.success("True — the model answer is correct.")
    else:
        st.error("False — the model answer is incorrect.")

    with st.expander("Metadata"):
        st.json({
            "model": matched["model"],
            "category": matched["category"],
            "metadata": matched["metadata"]
        })