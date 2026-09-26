# app.py — Enterprise RAG Home Page
import streamlit as st

st.set_page_config(
    page_title="Enterprise RAG",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #888;
        margin-bottom: 2rem;
    }

    .card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a3e);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }

    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #eee;
        margin-bottom: 0.5rem;
    }

    .card-desc {
        font-size: 0.9rem;
        color: #999;
        line-height: 1.5;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .feature-item {
        text-align: center;
        padding: 1rem;
    }

    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }

    .feature-text {
        font-size: 0.85rem;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🏢 Enterprise Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">'
    'AI-powered document Q&A with department-level data isolation'
    '</div>',
    unsafe_allow_html=True,
)

# ── Role Selection ────────────────────────────────────────────────────
col1, spacer, col2 = st.columns([1, 0.3, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">💬</div>
        <div class="card-title">Employee Chat</div>
        <div class="card-desc">
            Ask questions about your department's documents.
            Answers are grounded in your indexed knowledge base.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Chat →", use_container_width=True, type="primary", key="btn_chat"):
        st.switch_page("pages/2_Chat.py")

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">🔑</div>
        <div class="card-title">Admin Panel</div>
        <div class="card-desc">
            Upload documents, manage departments, and monitor
            the knowledge base.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Admin →", use_container_width=True, key="btn_admin"):
        st.switch_page("pages/1_Admin_Panel.py")

# ── Features ──────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-item">
        <div class="feature-icon">🔒</div>
        <div class="feature-text">ABAC Data Isolation</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">⚡</div>
        <div class="feature-text">Sub-2s Latency</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🧠</div>
        <div class="feature-text">Hybrid ANN + BM25</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">💾</div>
        <div class="feature-text">Persistent LanceDB</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🖥️</div>
        <div class="feature-text">100% Local / Private</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">📄</div>
        <div class="feature-text">PDF + Text Upload</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Enterprise RAG · Local-first · Zero cloud dependency · Powered by Ollama + LanceDB")
