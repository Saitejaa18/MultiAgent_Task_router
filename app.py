# -*- coding: utf-8 -*-
"""
app.py -- Streamlit UI for the Multi-Agent Task Router.
Run: streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from graph.workflow import task_router

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Task Router",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* Main container */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }

    .main-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* Agent badge */
    .agent-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    .badge-code      { background: rgba(99, 102, 241, 0.25); color: #818cf8; border: 1px solid #6366f1; }
    .badge-research  { background: rgba(59, 130, 246, 0.2);  color: #60a5fa; border: 1px solid #3b82f6; }
    .badge-summarize { background: rgba(16, 185, 129, 0.2);  color: #34d399; border: 1px solid #10b981; }
    .badge-general   { background: rgba(245, 158, 11, 0.2);  color: #fbbf24; border: 1px solid #f59e0b; }

    /* Result card */
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }

    /* Trace log */
    .trace-item {
        background: rgba(0, 0, 0, 0.3);
        border-left: 3px solid #6366f1;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem 0;
        border-radius: 0 6px 6px 0;
        font-family: monospace;
        font-size: 0.8rem;
        color: #94a3b8;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.85) !important;
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    /* Input field */
    .stTextArea textarea {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100%;
        transition: transform 0.1s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* History items */
    .history-item {
        background: rgba(255,255,255,0.04);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        color: #94a3b8;
        cursor: pointer;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "total_tasks" not in st.session_state:
    st.session_state.total_tasks = 0
if "total_retries" not in st.session_state:
    st.session_state.total_retries = 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Task Router")
    st.markdown("---")

    # Agent descriptions
    st.markdown("### 🧩 Active Agents")
    agents_info = {
        "🔵 Router":      "Groq Llama 3 8B — classifies task",
        "🟣 Code":        "Groq Llama 3 70B — writes/debugs code",
        "🔷 Research":    "Groq Llama 3 70B — answers & research",
        "🟢 Summarize":   "Groq Llama 3 70B — condenses content",
        "🟡 General":     "Groq Llama 3 70B — general queries",
        "🔴 Correction":  "Groq Llama 3 70B — self-corrects errors",
    }
    for name, desc in agents_info.items():
        st.markdown(f"**{name}**  \n<span style='color:#64748b;font-size:0.8rem'>{desc}</span>", unsafe_allow_html=True)

    st.markdown("---")

    # Session stats
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    col1.metric("Tasks Run", st.session_state.total_tasks)
    col2.metric("Retries", st.session_state.total_retries)

    st.markdown("---")

    # History
    if st.session_state.history:
        st.markdown("### 🕒 History")
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            badge = {"code": "🟣", "research": "🔷", "summarize": "🟢", "general": "🟡"}.get(item["type"], "⚪")
            short = item["task"][:35] + "..." if len(item["task"]) > 35 else item["task"]
            st.markdown(f'<div class="history-item">{badge} {short}</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.session_state.total_tasks = 0
            st.session_state.total_retries = 0
            st.rerun()


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="main-title">⚡ Multi-Agent Task Router</div>
    <div class="main-subtitle">Powered by LangGraph · Groq · Gemini · Self-Correcting Pipeline</div>
</div>
""", unsafe_allow_html=True)

# Input area
user_input = st.text_area(
    "Enter your task:",
    placeholder="e.g. Write a Python function to sort a list... / Summarize the history of AI... / What is quantum computing?",
    height=120,
    key="task_input",
    label_visibility="collapsed",
)

run_btn = st.button("🚀 Run Task", use_container_width=True)

# ── Run Pipeline ──────────────────────────────────────────────────────────────
if run_btn and user_input.strip():
    with st.spinner("⚙️ Routing through agents..."):
        initial_state = {
            "task": user_input.strip(),
            "task_type": "",
            "result": "",
            "error": None,
            "retry_count": 0,
            "messages": [],
            "correction_notes": None,
        }
        try:
            final_state = task_router.invoke(initial_state)

            # Update session stats
            st.session_state.total_tasks += 1
            st.session_state.total_retries += final_state.get("retry_count", 0)
            st.session_state.history.append({
                "task": user_input.strip(),
                "type": final_state.get("task_type", "general"),
                "result": final_state.get("result", ""),
                "retries": final_state.get("retry_count", 0),
            })

            # ── Display Results ─────────────────────────────────────────
            task_type = final_state.get("task_type", "general")
            badge_class = f"badge-{task_type}"
            badge_labels = {
                "code":      "💻 Code Agent",
                "research":  "🔍 Research Agent",
                "summarize": "📄 Summarizer Agent",
                "general":   "💬 General Agent",
            }

            col_left, col_right = st.columns([3, 1])

            with col_left:
                st.markdown(f'<span class="agent-badge {badge_class}">{badge_labels.get(task_type, "🤖 Agent")}</span>', unsafe_allow_html=True)

            with col_right:
                retries = final_state.get("retry_count", 0)
                color = "#ef4444" if retries > 0 else "#34d399"
                st.markdown(f'<p style="text-align:right;color:{color};font-size:0.85rem;padding-top:0.4rem">🔄 Retries: {retries}</p>', unsafe_allow_html=True)

            # Result
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            result = final_state.get("result") or "⚠️ No result was produced."
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)

            # Error (if still present after retries)
            if final_state.get("error"):
                st.error(f"⚠️ Final Error: {final_state['error']}")

            # Agent trace
            with st.expander("🧠 Agent Execution Trace", expanded=False):
                for msg in final_state.get("messages", []):
                    st.markdown(f'<div class="trace-item">{msg}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Pipeline Error: {str(e)}")
            st.exception(e)

elif run_btn and not user_input.strip():
    st.warning("⚠️ Please enter a task before running.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#475569;font-size:0.8rem;">Multi-Agent Task Router · Built with LangGraph + Groq + Gemini · Router-Worker Pattern</p>',
    unsafe_allow_html=True
)
