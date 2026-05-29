import json
import random
import re
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Dark background on every Streamlit wrapper */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main {
    background-color: #0f1117 !important;
    color: #e8eaf0 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Dark header — keeps the sidebar-toggle arrow visible */
header[data-testid="stHeader"] {
    background-color: #0f1117 !important;
    border-bottom: 1px solid #1a2035 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b27 !important;
    border-right: 1px solid #1e2535 !important;
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
[data-testid="stSidebar"] hr { border-color: #1e2535 !important; }
[data-testid="stSidebar"] h1 {
    font-size: 1.05rem !important; font-weight: 700;
    color: #fff !important;
}
[data-testid="stSidebar"] h3 {
    font-size: 0.72rem !important; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #6b7a9a !important; margin-top: 1.1rem !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 0.4rem 0.6rem; border-radius: 7px;
    display: block; font-size: 0.88rem; transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #1e2535; }
[data-testid="stSidebar"] .stTextInput input {
    background: #0f1117 !important; border: 1px solid #1e2535 !important;
    border-radius: 8px !important; color: #e8eaf0 !important; font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stRadio > label:first-child { display: none; }

/* Remove Streamlit branding */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

/* ── Spinner animation (shown while "thinking") ── */
@keyframes spin { to { transform: rotate(360deg); } }
.ai-spinner {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.85rem 0; color: #8b96b0; font-size: 0.9rem;
}
.ai-spinner .ring {
    width: 22px; height: 22px; flex-shrink: 0;
    border: 2.5px solid #1e2a40;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
}

/* Main content area — limit width, remove excess padding */
.main .block-container {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 1rem 1.5rem 0.5rem !important;
}

/* ── Scrollable chat box ── */
#chat-box {
    height: calc(100vh - 210px);
    overflow-y: auto;
    padding: 0.5rem 0 1rem;
    scrollbar-width: thin;
    scrollbar-color: #2a3347 transparent;
}
#chat-box::-webkit-scrollbar { width: 5px; }
#chat-box::-webkit-scrollbar-track { background: transparent; }
#chat-box::-webkit-scrollbar-thumb { background: #2a3347; border-radius: 3px; }

/* ── Chat bubbles ── */
.chat-user { display: flex; justify-content: flex-end; margin: 0.55rem 0; }
.chat-user .bubble {
    background: #2563eb; color: #fff;
    padding: 0.68rem 1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%; font-size: 0.92rem;
    line-height: 1.55; white-space: pre-wrap; word-break: break-word;
}
.chat-ai { display: flex; align-items: flex-start; gap: 0.6rem; margin: 0.55rem 0; }
.chat-ai .av {
    flex-shrink: 0; width: 30px; height: 30px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 0.82rem; color: #fff;
}
.chat-ai .bubble {
    background: #1a2035; color: #e8eaf0;
    padding: 0.75rem 1.05rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 82%; font-size: 0.92rem;
    line-height: 1.72; border: 1px solid #1e2a40;
    white-space: pre-wrap; word-break: break-word;
}

/* ── Welcome screen ── */
.welcome-wrap {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100%; min-height: 300px;
    text-align: center; gap: 0.4rem; padding: 3rem 0;
}
.welcome-wrap .w-icon { font-size: 2.4rem; }
.welcome-wrap h2 { color: #fff; font-size: 1.25rem; font-weight: 700; margin: 0; }
.welcome-wrap p { color: #6b7a9a; font-size: 0.88rem; max-width: 400px; line-height: 1.6; margin: 0.25rem 0 0; }

/* ── Input bar ── */
.stTextArea textarea {
    background: #1a2035 !important; border: 1px solid #1e2a40 !important;
    border-radius: 14px !important; color: #e8eaf0 !important;
    font-size: 0.92rem !important; padding: 0.75rem 1rem !important;
    resize: none !important; box-shadow: none !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.18) !important;
}
.stTextArea textarea::placeholder { color: #3d4a63 !important; }

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; padding: 0.62rem 1.4rem !important;
    font-weight: 600 !important; font-size: 0.87rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; }
.stButton > button[kind="secondary"] {
    background: #1a2035 !important; color: #8b96b0 !important;
    border: 1px solid #1e2a40 !important; border-radius: 10px !important;
    font-size: 0.82rem !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1e2535 !important; color: #c9d1e0 !important;
}

/* ── Misc ── */
hr { border-color: #1a2035 !important; }
.stAlert { border-radius: 10px !important; font-size: 0.87rem !important; }
label[data-testid="stWidgetLabel"] { color: #c9d1e0 !important; font-size: 0.88rem !important; }
.stToggle label { color: #c9d1e0 !important; }
.streamlit-expanderHeader {
    background: #1a2035 !important; border-radius: 8px !important;
    color: #8b96b0 !important; font-size: 0.83rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar toggle: JS injection (CSS alone is unreliable across versions) ────
components.html("""
<script>
(function styleToggle() {
    var doc = window.parent.document;
    // Streamlit uses different data-testid values across versions; try all.
    var selectors = [
        '[data-testid="collapsedControl"]',
        '[data-testid="stSidebarCollapsedControl"]',
        'button[aria-label="Open sidebar"]',
        'button[title="Open sidebar"]',
    ];
    var found = false;
    selectors.forEach(function(sel) {
        var els = doc.querySelectorAll(sel);
        els.forEach(function(el) {
            el.style.cssText = [
                'display:flex!important',
                'visibility:visible!important',
                'opacity:1!important',
                'background:#1a2035!important',
                'border:1px solid #2a3a55!important',
                'border-radius:0 8px 8px 0!important',
                'color:#c9d1e0!important',
                'padding:6px 10px!important',
                'margin-top:8px!important',
                'cursor:pointer!important',
                'box-shadow:2px 2px 10px rgba(0,0,0,0.5)!important',
                'z-index:9999!important',
                'position:fixed!important',
                'left:0!important',
                'top:60px!important',
            ].join(';');
            el.onmouseenter = function(){ el.style.background='#2563eb'; el.style.color='#fff'; };
            el.onmouseleave = function(){ el.style.background='#1a2035'; el.style.color='#c9d1e0'; };
            found = true;
        });
    });
    // Retry until found (Streamlit renders async)
    if (!found) setTimeout(styleToggle, 300);
})();
</script>
""", height=0, scrolling=False)

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "precomputed_medical_demo_answers.json"

for k, v in {"use_streaming": True, "show_evaluation": False, "chat_history": [], "_clear_input": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Clear the textarea BEFORE any widget with key="input_box" is created.
if st.session_state._clear_input:
    st.session_state["input_box"] = ""
    st.session_state._clear_input = False


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


def _ai_bubble(content, cursor=False):
    """Wrap content in the AI chat bubble HTML."""
    suffix = "▌" if cursor else ""
    escaped = (content
               .replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))
    return (
        f'<div class="chat-ai">'
        f'<div class="av">🩺</div>'
        f'<div class="bubble">{escaped}{suffix}</div>'
        f'</div>'
    )


def stream_text(text, placeholder):
    # 1. Spinner phase: ~2.5 s "thinking" animation
    spinner_html = (
        '<div class="chat-ai">'
        '<div class="av">🩺</div>'
        '<div class="ai-spinner"><div class="ring"></div>Generating response…</div>'
        '</div>'
    )
    placeholder.markdown(spinner_html, unsafe_allow_html=True)
    time.sleep(2.5)

    # 2. Output phase
    if not st.session_state.use_streaming:
        placeholder.markdown(_ai_bubble(text), unsafe_allow_html=True)
        return

    printed = ""
    for char in str(text):
        printed += char
        placeholder.markdown(_ai_bubble(printed, cursor=True), unsafe_allow_html=True)
        if char in [".", "!", "?", "。", "\n", "다", "요"]:
            time.sleep(0.06)
        else:
            time.sleep(random.uniform(0.004, 0.018))
    placeholder.markdown(_ai_bubble(printed), unsafe_allow_html=True)


def bubble_html(role, content):
    escaped = (content
               .replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))
    if role == "user":
        return f'<div class="chat-user"><div class="bubble">{escaped}</div></div>'
    return (
        f'<div class="chat-ai">'
        f'<div class="av">🩺</div>'
        f'<div class="bubble">{escaped}</div>'
        f'</div>'
    )


def scroll_to_bottom():
    """Run JS inside a zero-height iframe to scroll #chat-box to bottom."""
    components.html("""
    <script>
    (function tick(n) {
        var box = window.parent.document.getElementById('chat-box');
        if (box) { box.scrollTop = box.scrollHeight; }
        if (n > 0) setTimeout(function(){ tick(n-1); }, 120);
    })(4);
    </script>
    """, height=0, scrolling=False)


# ── Sidebar ───────────────────────────────────────────────────────────────────
rows = load_data()

with st.sidebar:
    st.markdown("## 🩺 Medical AI")
    st.divider()
    st.markdown("### Model")
    backend = st.radio("backend", ["Local (Ollama)", "OpenAI API"], label_visibility="collapsed")
    if backend == "Local (Ollama)":
        model_name = st.text_input("name", value="gpt-oss:latest", label_visibility="collapsed")
    else:
        model_name = st.text_input("name", value="gpt-4o-mini", label_visibility="collapsed")

    model_rows = get_rows_for_model(rows, model_name)
    if not model_rows:
        st.warning("No data found for this model.")
    elif all(str(r.get("model", "")).strip() == "" for r in model_rows):
        st.caption("Using default dataset")

    st.divider()
    st.markdown("### Options")
    st.session_state.use_streaming  = st.toggle("Streaming output",  value=st.session_state.use_streaming)
    st.session_state.show_evaluation = st.toggle("Show evaluation",   value=st.session_state.show_evaluation)
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ── Guard ─────────────────────────────────────────────────────────────────────
if not rows:
    st.error(f"Data file not found: `{DATA_FILE.name}`. Place it next to app.py.")
    st.stop()

# ── Layout ────────────────────────────────────────────────────────────────────
#
# We define chat_area FIRST so Streamlit places it ABOVE input_area on screen,
# even though we write into input_area first in code.
#
chat_area = st.container()
input_area = st.container()

# ── Input bar (written first, renders second / bottom) ────────────────────────
with input_area:
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    col_txt, col_btn = st.columns([6, 1], vertical_alignment="bottom")
    with col_txt:
        user_prompt = st.text_area(
            "prompt",
            height=68,
            placeholder="Describe the clinical situation…",
            label_visibility="collapsed",
            key="input_box",
        )
    with col_btn:
        send = st.button("Send →", type="primary", use_container_width=True)

# ── Chat pane (written second, renders first / top) ───────────────────────────
with chat_area:

    # Build the HTML string for all committed messages
    if not st.session_state.chat_history:
        inner_html = """
        <div class="welcome-wrap">
            <div class="w-icon">🩺</div>
            <h2>Medical AI Assistant</h2>
            <p>Describe a clinical situation and the AI will provide a decision-support response.</p>
        </div>"""
    else:
        inner_html = "".join(bubble_html(m["role"], m["content"])
                             for m in st.session_state.chat_history)

    # Single scrollable div — the page itself does not grow
    st.markdown(f'<div id="chat-box">{inner_html}</div>', unsafe_allow_html=True)

    # Auto-scroll to bottom on every render
    scroll_to_bottom()

    # Evaluation panels (Streamlit widgets, rendered below the box but still in chat_area)
    if st.session_state.show_evaluation:
        for msg in st.session_state.chat_history:
            if msg["role"] == "ai" and msg.get("meta"):
                meta = msg["meta"]
                with st.expander(f"Evaluation — {meta.get('framing', 'response')}"):
                    st.markdown(f"**Reference answer:** {meta.get('correct_answer', '—')}")
                    is_correct = meta.get("is_correct")
                    if is_correct is True:
                        st.success("Appropriate response")
                    elif is_correct is False:
                        st.error("Inappropriate or overconfident response")
                    else:
                        st.info("No evaluation available")
                    st.json({"model": meta.get("model",""), "category": meta.get("category",""), "framing": meta.get("framing","")})

    # ── Handle send — stays inside chat_area so it renders above the input bar ──
    if send:
        if not user_prompt.strip():
            st.warning("Please enter a prompt before sending.")
            st.stop()

        matched = find_match(user_prompt, model_rows)
        if matched is None:
            st.error("No matching pre-computed response found. Check the prompt wording.")
            st.stop()

        # Show the new user bubble immediately (above the input bar)
        st.markdown(bubble_html("user", user_prompt), unsafe_allow_html=True)

        # ai_slot holds spinner → then streams text (stream_text handles both)
        ai_slot = st.empty()
        stream_text(matched["response"], ai_slot)

        # Commit to history, clear the input field, rerender
        st.session_state.chat_history.append({"role": "user", "content": user_prompt, "meta": None})
        st.session_state.chat_history.append({"role": "ai",   "content": matched["response"], "meta": matched})
        st.session_state._clear_input = True   # cleared at top of next run, before widget renders
        st.rerun()