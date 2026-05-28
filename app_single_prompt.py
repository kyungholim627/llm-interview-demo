import json
import random
import re
import time
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="LLM 응답 시연",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "precomputed_medical_demo_answers_with_runs.json"


if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 1000

if "use_streaming" not in st.session_state:
    st.session_state.use_streaming = True

# Stores which response should be shown next for each prompt/model combination.
# This is internal only and is never displayed in the UI.
if "prompt_run_counters" not in st.session_state:
    st.session_state.prompt_run_counters = {}


@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for item in data:
        rows.append({
            "model": str(item.get("model", "")).strip(),
            "prompt": item.get("prompt", ""),
            "response": item.get("response", ""),
            "run": int(item.get("run", 1)),
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


def get_rows_for_model(rows, selected_model):
    selected_model = str(selected_model).strip()

    exact_rows = [
        row for row in rows
        if str(row.get("model", "")).strip() == selected_model
    ]

    if exact_rows:
        return exact_rows

    blank_model_rows = [
        row for row in rows
        if str(row.get("model", "")).strip() == ""
    ]

    return blank_model_rows


def find_matching_rows(user_prompt, rows):
    user_prompt_clean = normalize_for_matching(user_prompt)

    exact_matches = []
    for row in rows:
        row_prompt_clean = normalize_for_matching(row["prompt"])
        if row_prompt_clean == user_prompt_clean:
            exact_matches.append(row)

    if exact_matches:
        return sorted(exact_matches, key=lambda x: x.get("run", 1))

    partial_matches = []
    for row in rows:
        row_prompt_clean = normalize_for_matching(row["prompt"])
        if user_prompt_clean in row_prompt_clean or row_prompt_clean in user_prompt_clean:
            partial_matches.append(row)

    return sorted(partial_matches, key=lambda x: x.get("run", 1))


def rows_by_run(rows):
    grouped = {}
    for row in rows:
        grouped[int(row.get("run", 1))] = row
    return grouped


def make_prompt_key(model_name, user_prompt):
    key_parts = [
        str(model_name).strip(),
        normalize_for_matching(user_prompt),
    ]
    return "||".join(key_parts)


def choose_next_run(prompt_key, available_runs):
    """
    Returns one run id per button click.
    First click -> first available run.
    Second click -> second available run.
    After the last run -> loops back to the first run.
    """
    if not available_runs:
        return None

    current_index = st.session_state.prompt_run_counters.get(prompt_key, 0)
    run_id = available_runs[current_index % len(available_runs)]
    st.session_state.prompt_run_counters[prompt_key] = current_index + 1

    return run_id


def stream_response(
    text,
    text_placeholder,
    status_placeholder,
    initial_delay=1.0,
    min_delay=0.004,
    max_delay=0.018,
    pause_after_sentence=0.06
):
    printed = ""

    status_placeholder.info("답변 생성 중입니다...")
    time.sleep(initial_delay)

    if not st.session_state.use_streaming:
        text_placeholder.markdown(str(text))
        status_placeholder.success("답변 생성이 완료되었습니다.")
        return

    for char in str(text):
        printed += char
        text_placeholder.markdown(printed)

        if char in [".", "!", "?", "。", "\n", "다", "요"]:
            time.sleep(pause_after_sentence)
        else:
            time.sleep(random.uniform(min_delay, max_delay))

    status_placeholder.success("답변 생성이 완료되었습니다.")


rows = load_data()

st.sidebar.title("메뉴")

page = st.sidebar.radio(
    "페이지 선택",
    ["시연", "설정"],
    label_visibility="collapsed"
)

st.sidebar.divider()


if page == "시연":

    st.title("LLM 응답 시연")
    st.caption("질문을 입력하면 사전 계산된 AI 답변 중 하나를 순서대로 보여줍니다.")

    if not rows:
        st.error(f"{DATA_FILE.name} 파일을 찾을 수 없습니다. app.py와 같은 폴더에 JSON 파일을 넣어주세요.")
        st.stop()

    st.sidebar.header("모델 선택")

    backend = st.sidebar.radio(
        "모델 종류",
        ["로컬 모델(Ollama)", "OpenAI API"]
    )

    if backend == "로컬 모델(Ollama)":
        model_name = st.sidebar.text_input(
            "Ollama 모델 이름",
            value="gpt-oss:latest"
        )

    else:
        model_name = st.sidebar.text_input(
            "OpenAI 모델 이름",
            value="gpt-4o-mini"
        )

    model_rows = get_rows_for_model(rows, model_name)

    if not model_rows:
        st.sidebar.warning("선택한 모델명과 일치하는 JSON 항목이 없습니다.")

    if model_rows and all(str(row.get("model", "")).strip() == "" for row in model_rows):
        st.sidebar.info("현재 JSON의 model 값이 비어 있어 blank-model 항목을 사용합니다.")

    st.markdown("### 무엇을 물어 보고 싶으세요?")

    user_prompt = st.text_area(
        "질문 입력",
        height=220,
        placeholder="질문을 입력하세요.",
        label_visibility="collapsed"
    )

    run_response = st.button("답변 생성", type="primary")

    if run_response:

        if not user_prompt.strip():
            st.warning("질문을 입력해주세요.")
            st.stop()

        matched_rows = find_matching_rows(user_prompt, model_rows)

        if not matched_rows:
            st.error("선택한 모델의 JSON에서 입력한 질문과 일치하는 프롬프트를 찾지 못했습니다.")
            st.stop()

        grouped_rows = rows_by_run(matched_rows)
        available_runs = sorted(grouped_rows.keys())

        if not available_runs:
            st.error("출력할 사전 계산 답변을 찾지 못했습니다.")
            st.stop()

        prompt_key = make_prompt_key(model_name, user_prompt)
        selected_run = choose_next_run(prompt_key, available_runs)

        if selected_run is None:
            st.error("출력할 사전 계산 답변을 찾지 못했습니다.")
            st.stop()

        st.divider()
        st.subheader("답변")

        response_text_placeholder = st.empty()
        response_status_placeholder = st.empty()

        stream_response(
            grouped_rows[selected_run]["response"],
            text_placeholder=response_text_placeholder,
            status_placeholder=response_status_placeholder,
            initial_delay=0.8,
            min_delay=0.004,
            max_delay=0.018,
            pause_after_sentence=0.06
        )

        st.divider()
        st.info(
            "답변 생성 버튼을 다시 누르면 같은 질문에 대해 다음 사전 계산 답변을 순서대로 보여줍니다."
        )


elif page == "설정":

    st.title("설정")
    st.caption("사전 계산된 답변의 출력 방식을 조정합니다.")

    st.subheader("생성 설정")

    st.session_state.temperature = st.slider(
        "창의성(Temperature)",
        min_value=0.0,
        max_value=1.5,
        value=float(st.session_state.temperature),
        step=0.1,
        help="이 데모는 사전 계산된 답변을 사용하므로 실제 출력에는 영향을 주지 않습니다."
    )

    st.session_state.max_tokens = st.slider(
        "최대 출력 길이",
        min_value=100,
        max_value=3000,
        value=int(st.session_state.max_tokens),
        step=100,
        help="이 데모는 사전 계산된 답변을 사용하므로 실제 출력에는 영향을 주지 않습니다."
    )

    st.divider()

    st.subheader("출력 방식")

    st.session_state.use_streaming = st.toggle(
        "실시간 스트리밍 사용",
        value=bool(st.session_state.use_streaming)
    )

    st.success("설정이 저장되었습니다. 왼쪽 메뉴에서 시연 페이지로 돌아가세요.")
