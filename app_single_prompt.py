import json
import random
import re
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117;
    color: #e8eaf0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #1e2535;
    padding-top: 0.5rem;
}
[data-testid="stSidebar"] * {
    color: #c9d1e0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    display: block;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #1e2535;
}
[data-testid="stSidebar"] hr {
    border-color: #1e2535 !important;
}
[data-testid="stSidebar"] h1 {
    font-size: 1.1rem !important;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 0.78rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #6b7a9a !important;
    margin-top: 1.2rem !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Main area ── */
.main .block-container {
    max-width: 860px;
    margin: 0 auto;
    padding: 2rem 1.5rem 7rem;
}

/* ── Chat messages ── */
.chat-user {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0;
}
.chat-user .bubble {
    background: #2563eb;
    color: #ffffff;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.95rem;
    line-height: 1.55;
    white-space: pre-wrap;
}

.chat-ai {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    margin: 1rem 0;
}
.chat-ai .avatar {
    flex-shrink: 0;
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    color: white;
}
.chat-ai .bubble {
    background: #1a2035;
    color: #e8eaf0;
    padding: 0.85rem 1.2rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 80%;
    font-size: 0.95rem;
    line-height: 1.7;
    border: 1px solid #1e2a40;
    white-space: pre-wrap;
}

/* ── Page header ── */
.page-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.03em;
}
.page-header p {
    color: #6b7a9a;
    font-size: 0.9rem;
    margin-top: 0.4rem;
}

/* ── Welcome card (shown before first message) ── */
.welcome-card {
    text-align: center;
    padding: 4rem 2rem;
    color: #6b7a9a;
}
.welcome-card .icon { font-size: 2.8rem; margin-bottom: 1rem; }
.welcome-card h2 { color: #c9d1e0; font-size: 1.2rem; font-weight: 600; margin: 0 0 0.5rem; }
.welcome-card p { font-size: 0.9rem; line-height: 1.6; max-width: 480px; margin: 0 auto; }

/* ── Input area ── */
.stTextArea textarea {
    background: #1a2035 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 12px !important;
    color: #e8eaf0 !important;
    font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important;
    resize: none !important;
    box-shadow: none !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
}
.stTextArea textarea::placeholder { color: #4a5568 !important; }

/* ── Send button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.01em;
    transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: #1a2035 !important;
    color: #8b96b0 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.1rem !important;
    font-size: 0.85rem !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1e2535 !important;
    color: #c9d1e0 !important;
}

/* ── Status / alert boxes ── */
.stAlert {
    border-radius: 10px !important;
    font-size: 0.88rem !important;
}

/* ── Settings page ── */
.stSlider > div > div > div { background: #2563eb !important; }
label[data-testid="stWidgetLabel"] { color: #c9d1e0 !important; font-size: 0.9rem !important; }
.stToggle label { color: #c9d1e0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #1a2035 !important;
    border-radius: 8px !important;
    color: #8b96b0 !important;
    font-size: 0.85rem !important;
}

/* ── Divider ── */
hr { border-color: #1e2535 !important; }

/* ── Sidebar radio: hide the outer label ── */
[data-testid="stSidebar"] .stRadio > label:first-child { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "precomputed_medical_demo_answers.json"

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "use_streaming": True,
    "show_evaluation": False,
    "chat_history": [],   # list of {"role": "user"|"ai", "content": str, "meta": dict|None}
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for idx, item in enumerate(data):
        rows.append({
            "id": item.get("id", f"item_{idx}"),
            "model": str(item.get("model", "")).strip(),
            "backend": item.get("backend", ""),
            "prompt": item.get("prompt", ""),
            "response": item.get("response", ""),
            "correct_answer": item.get("correct_answer", ""),
            "is_correct": item.get("is_correct", None),
            "category": item.get("category", ""),
            "framing": item.get("framing", ""),
        })
    return rows


def normalize(text):
    text = str(text)
    for ch in ["\n", "\r", "\\n", "\\", '"', "'", "“", "”", "‘", "’"]:
        text = text.replace(ch, "")
    return re.sub(r"\s+", "", text).lower()


def get_rows_for_model(rows, model):
    model = str(model).strip()
    exact = [r for r in rows if str(r.get("model", "")).strip() == model]
    if exact:
        return exact
    return [r for r in rows if str(r.get("model", "")).strip() == ""]


def find_match(user_prompt, rows):
    cleaned = normalize(user_prompt)
    exact = [r for r in rows if normalize(r["prompt"]) == cleaned]
    if exact:
        return random.choice(exact)
    partial = [r for r in rows if cleaned in normalize(r["prompt"]) or normalize(r["prompt"]) in cleaned]
    return random.choice(partial) if partial else None


def stream_text(text, placeholder):
    if not st.session_state.use_streaming:
        placeholder.markdown(text)
        return
    printed = ""
    for char in str(text):
        printed += char
        placeholder.markdown(printed + "▌")
        if char in [".", "!", "?", "。", "\n", "다", "요"]:
            time.sleep(0.06)
        else:
            time.sleep(random.uniform(0.004, 0.018))
    placeholder.markdown(printed)


def render_message(role, content):
    if role == "user":
        st.markdown(
            f'<div class="chat-user"><div class="bubble">{content}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="chat-ai">'
            f'<div class="avatar">🩺</div>'
            f'<div class="bubble">{content}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Sidebar ───────────────────────────────────────────────────────────────────
rows = load_data()

with st.sidebar:
    st.markdown("## 🩺 Medical AI")
    st.divider()

    page = st.radio("nav", ["대화", "설정"], label_visibility="collapsed")

    st.divider()
    st.markdown("### 모델")

    backend = st.radio("backend", ["로컬 (Ollama)", "OpenAI API"], label_visibility="collapsed")

    if backend == "로컬 (Ollama)":
        model_name = st.text_input("모델 이름", value="gpt-oss:latest", label_visibility="collapsed")
    else:
        model_name = st.text_input("모델 이름", value="gpt-4o-mini", label_visibility="collapsed")

    model_rows = get_rows_for_model(rows, model_name)

    if not model_rows:
        st.warning("해당 모델의 데이터가 없습니다.")
    elif all(str(r.get("model", "")).strip() == "" for r in model_rows):
        st.caption("기본 데이터셋 사용 중")

    st.divider()

    if st.button("대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ── Pages ─────────────────────────────────────────────────────────────────────
if page == "대화":

    if not rows:
        st.error(f"데이터 파일을 찾을 수 없습니다: `{DATA_FILE.name}`")
        st.stop()

    # Chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome-card">
            <div class="icon">🩺</div>
            <h2>Medical AI Assistant</h2>
            <p>임상 상황을 설명해 주세요. AI가 의사결정을 지원하는 응답을 제공합니다.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            render_message(msg["role"], msg["content"])

            if msg["role"] == "ai" and msg.get("meta") and st.session_state.show_evaluation:
                meta = msg["meta"]
                with st.expander("평가 결과 보기"):
                    st.markdown(f"**정답 기준:** {meta.get('correct_answer', '—')}")
                    is_correct = meta.get("is_correct")
                    if is_correct is True:
                        st.success("적절한 응답")
                    elif is_correct is False:
                        st.error("부적절하거나 과도하게 단정적인 응답")
                    else:
                        st.info("평가값 없음")
                    st.json({
                        "model": meta.get("model", ""),
                        "category": meta.get("category", ""),
                        "framing": meta.get("framing", ""),
                    })

    # ── Input area ────────────────────────────────────────────────────────────
    st.divider()
    col_input, col_btn = st.columns([5, 1], vertical_alignment="bottom")

    with col_input:
        user_prompt = st.text_area(
            "message",
            height=80,
            placeholder="임상 상황을 입력하세요…",
            label_visibility="collapsed",
            key="input_box",
        )

    with col_btn:
        send = st.button("전송 →", type="primary", use_container_width=True)

    if send:
        if not user_prompt.strip():
            st.warning("질문을 입력해 주세요.")
            st.stop()

        matched = find_match(user_prompt, model_rows)
        if matched is None:
            st.error("일치하는 사전 계산 응답을 찾지 못했습니다. 프롬프트 문구를 확인해 주세요.")
            st.stop()

        st.session_state.chat_history.append({"role": "user", "content": user_prompt, "meta": None})

        # Stream into a placeholder, then freeze into history
        render_message("user", user_prompt)
        st.markdown(
            '<div class="chat-ai"><div class="avatar">🩺</div>',
            unsafe_allow_html=True,
        )
        ai_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)

        stream_text(matched["response"], ai_placeholder)

        st.session_state.chat_history.append({
            "role": "ai",
            "content": matched["response"],
            "meta": matched,
        })

        st.rerun()


elif page == "설정":

    st.markdown('<div class="page-header"><h1>설정</h1><p>응답 출력 방식을 조정합니다.</p></div>', unsafe_allow_html=True)

    st.markdown("#### 출력 방식")

    st.session_state.use_streaming = st.toggle(
        "실시간 스트리밍",
        value=bool(st.session_state.use_streaming),
        help="글자가 하나씩 출력되는 타이핑 효과를 켜거나 끕니다.",
    )

    st.session_state.show_evaluation = st.toggle(
        "정답 기준 및 평가 표시",
        value=bool(st.session_state.show_evaluation),
        help="각 응답 아래에 사전 평가 결과를 펼칠 수 있는 섹션을 표시합니다.",
    )

    st.divider()
    st.markdown("#### 파라미터 (표시 전용)")
    st.caption("이 데모는 사전 계산된 응답을 사용하므로 아래 값은 실제 출력에 영향을 주지 않습니다.")

    st.session_state.temperature = st.slider(
        "Temperature",
        0.0, 1.5, float(st.session_state.temperature), 0.1,
    )
    st.session_state.max_tokens = st.slider(
        "Max tokens",
        100, 3000, int(st.session_state.max_tokens), 100,
    )