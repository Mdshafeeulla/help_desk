# app.py — Enterprise RAG Home Page
import streamlit as st

st.set_page_config(
    page_title="MSU Corp Support",
    page_icon="🛡️",
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
st.markdown('<div class="hero-title">🛡️ MSU Corp Support Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">'
    'AI-powered 24/7 Customer Support — Resolve platform issues instantly without waiting for an agent'
    '</div>',
    unsafe_allow_html=True,
)

# ── Role Selection ────────────────────────────────────────────────────
col1, spacer, col2 = st.columns([1, 0.3, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">💬</div>
        <div class="card-title">Customer Support Chat</div>
        <div class="card-desc">
            Facing a platform issue? Chat with our AI support agent to get instant answers and step-by-step resolutions — no wait times.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Support Chat →", use_container_width=True, type="primary", key="btn_chat"):
        st.switch_page("pages/2_Chat.py")

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">🔑</div>
        <div class="card-title">Admin Panel</div>
        <div class="card-desc">
            Upload support manuals, FAQs, troubleshooting guides, and manage the MSU Corp knowledge base.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Admin Panel →", use_container_width=True, key="btn_admin"):
        st.switch_page("pages/1_Admin_Panel.py")

# ── Features ──────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-item">
        <div class="feature-icon">⚡</div>
        <div class="feature-text">Instant Responses</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🔒</div>
        <div class="feature-text">Private & Secure</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🧠</div>
        <div class="feature-text">Knowledge-Grounded AI</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">📄</div>
        <div class="feature-text">Document-Based Answers</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🕐</div>
        <div class="feature-text">24/7 Availability</div>
    </div>
    <div class="feature-item">
        <div class="feature-icon">🎯</div>
        <div class="feature-text">L1 Support Automation</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("MSU Corp Support Assistant · AI-powered L1 Customer Support · Powered by RAG + Local LLM")
