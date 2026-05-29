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
    initial_sidebar_state="collapsed",   # sidebar hidden by default
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117;
    color: #e8eaf0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

/* ── Sidebar toggle button (the >> arrow Streamlit renders) ── */
[data-testid="collapsedControl"] {
    color: #8b96b0 !important;
    background: #161b27 !important;
    border-radius: 0 8px 8px 0 !important;
    border: 1px solid #1e2535 !important;
    border-left: none !important;
}
[data-testid="collapsedControl"]:hover {
    background: #1e2535 !important;
    color: #ffffff !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #1e2535;
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
[data-testid="stSidebar"] hr { border-color: #1e2535 !important; }
[data-testid="stSidebar"] h1 {
    font-size: 1.05rem !important;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff !important;
}
[data-testid="stSidebar"] h3 {
    font-size: 0.72rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b7a9a !important;
    margin-top: 1.1rem !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 0.4rem 0.6rem;
    border-radius: 7px;
    display: block;
    font-size: 0.88rem;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #1e2535; }
[data-testid="stSidebar"] .stTextInput input {
    background: #0f1117 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stRadio > label:first-child { display: none; }

/* ── Main area ── */
.main .block-container {
    max-width: 820px;
    margin: 0 auto;
    padding: 1.5rem 1.5rem 0;
}

/* ── Welcome screen ── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 55vh;
    text-align: center;
    gap: 0.5rem;
}
.welcome-wrap .w-icon { font-size: 2.6rem; }
.welcome-wrap h2 {
    color: #ffffff;
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
}
.welcome-wrap p {
    color: #6b7a9a;
    font-size: 0.9rem;
    max-width: 420px;
    line-height: 1.6;
    margin: 0.3rem 0 0;
}

/* ── Chat bubbles ── */
.chat-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.85rem 0;
}
.chat-user .bubble {
    background: #2563eb;
    color: #ffffff;
    padding: 0.7rem 1.05rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%;
    font-size: 0.92rem;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
}
.chat-ai {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    margin: 0.85rem 0;
}
.chat-ai .av {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    color: white;
}
.chat-ai .bubble {
    background: #1a2035;
    color: #e8eaf0;
    padding: 0.8rem 1.1rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 82%;
    font-size: 0.92rem;
    line-height: 1.72;
    border: 1px solid #1e2a40;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Input bar ── */
.input-bar {
    position: sticky;
    bottom: 0;
    background: #0f1117;
    padding: 0.9rem 0 1rem;
    border-top: 1px solid #1a2035;
    z-index: 100;
}
.stTextArea textarea {
    background: #1a2035 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 14px !important;
    color: #e8eaf0 !important;
    font-size: 0.93rem !important;
    padding: 0.8rem 1rem !important;
    resize: none !important;
    box-shadow: none !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.18) !important;
}
.stTextArea textarea::placeholder { color: #3d4a63 !important; }

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.62rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    transition: opacity 0.15s !important;
    height: 100%;
}
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; }
.stButton > button[kind="secondary"] {
    background: #1a2035 !important;
    color: #8b96b0 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1e2535 !important;
    color: #c9d1e0 !important;
}

/* ── Misc ── */
hr { border-color: #1a2035 !important; }
.stAlert { border-radius: 10px !important; font-size: 0.87rem !important; }
.streamlit-expanderHeader {
    background: #1a2035 !important;
    border-radius: 8px !important;
    color: #8b96b0 !important;
    font-size: 0.83rem !important;
}
label[data-testid="stWidgetLabel"] { color: #c9d1e0 !important; font-size: 0.88rem !important; }
.stToggle label { color: #c9d1e0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "precomputed_medical_demo_answers.json"

for k, v in {
    "use_streaming": True,
    "show_evaluation": False,
    "chat_history": [],
}.items():
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
    return exact if exact else [r for r in rows if str(r.get("model", "")).strip() == ""]


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


def bubble_html(role, content):
    content_escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if role == "user":
        return f'<div class="chat-user"><div class="bubble">{content_escaped}</div></div>'
    return (
        f'<div class="chat-ai">'
        f'<div class="av">🩺</div>'
        f'<div class="bubble">{content_escaped}</div>'
        f'</div>'
    )


# ── Sidebar (collapsed by default, >> button reveals it) ─────────────────────
rows = load_data()

with st.sidebar:
    st.markdown("## 🩺 Medical AI")
    st.divider()

    st.markdown("### Model")
    backend = st.radio("backend", ["Local (Ollama)", "OpenAI API"], label_visibility="collapsed")

    if backend == "Local (Ollama)":
        model_name = st.text_input("Model name", value="gpt-oss:latest", label_visibility="collapsed")
    else:
        model_name = st.text_input("Model name", value="gpt-4o-mini", label_visibility="collapsed")

    model_rows = get_rows_for_model(rows, model_name)

    if not model_rows:
        st.warning("No data found for this model name.")
    elif all(str(r.get("model", "")).strip() == "" for r in model_rows):
        st.caption("Using default dataset (blank model field)")

    st.divider()
    st.markdown("### Options")
    st.session_state.use_streaming = st.toggle("Streaming output", value=st.session_state.use_streaming)
    st.session_state.show_evaluation = st.toggle("Show evaluation", value=st.session_state.show_evaluation)

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ── Main layout: chat area ABOVE, input bar BELOW ────────────────────────────
if not rows:
    st.error(f"Data file not found: `{DATA_FILE.name}`. Place it in the same folder as app.py.")
    st.stop()

# Define containers top-to-bottom so chat always renders above input.
chat_area = st.container()
input_area = st.container()

# ── Input bar (defined second = renders below chat) ──────────────────────────
with input_area:
    st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    col_input, col_btn = st.columns([6, 1], vertical_alignment="bottom")
    with col_input:
        user_prompt = st.text_area(
            "prompt",
            height=72,
            placeholder="Describe the clinical situation…",
            label_visibility="collapsed",
            key="input_box",
        )
    with col_btn:
        send = st.button("Send →", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Chat area (defined first = renders above input) ───────────────────────────
with chat_area:
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome-wrap">
            <div class="w-icon">🩺</div>
            <h2>Medical AI Assistant</h2>
            <p>Describe a clinical situation and the AI will provide a decision-support response.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            st.markdown(bubble_html(msg["role"], msg["content"]), unsafe_allow_html=True)

            if msg["role"] == "ai" and msg.get("meta") and st.session_state.show_evaluation:
                meta = msg["meta"]
                with st.expander("View evaluation"):
                    st.markdown(f"**Reference answer:** {meta.get('correct_answer', '—')}")
                    is_correct = meta.get("is_correct")
                    if is_correct is True:
                        st.success("Appropriate response")
                    elif is_correct is False:
                        st.error("Inappropriate or overconfident response")
                    else:
                        st.info("No evaluation available")
                    st.json({
                        "model": meta.get("model", ""),
                        "category": meta.get("category", ""),
                        "framing": meta.get("framing", ""),
                    })

    # ── Streaming happens here, inside chat_area, so it appears above input ──
    if send:
        if not user_prompt.strip():
            st.warning("Please enter a prompt before sending.")
            st.stop()

        matched = find_match(user_prompt, model_rows)
        if matched is None:
            st.error("No matching pre-computed response found. Check the prompt wording.")
            st.stop()

        # Show the new user bubble immediately
        st.markdown(bubble_html("user", user_prompt), unsafe_allow_html=True)

        # Stream AI response inside chat_area (above the input bar)
        st.markdown(
            '<div class="chat-ai"><div class="av">🩺</div>',
            unsafe_allow_html=True,
        )
        ai_placeholder = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)

        stream_text(matched["response"], ai_placeholder)

        # Commit to history then rerender cleanly
        st.session_state.chat_history.append({"role": "user", "content": user_prompt, "meta": None})
        st.session_state.chat_history.append({"role": "ai", "content": matched["response"], "meta": matched})
        st.rerun()