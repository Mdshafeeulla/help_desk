# app.py — Enterprise RAG Home Page (Redesigned)
# pyrefly: ignore [missing-import]
import streamlit as st

st.set_page_config(
    page_title="MSU Corp Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hero Section ────────────────────────────────── */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem 2rem;
        animation: fadeIn 0.6s ease-out;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: linear-gradient(135deg, rgba(242, 167, 195, 0.18), rgba(255, 214, 229, 0.08));
        border: 1px solid rgba(242, 167, 195, 0.32);
        color: #ffd6e5;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 1.2rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(110deg, #fff8fb 12%, #f2a7c3 55%, #ffd6e5 92%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }

    .hero-brand {
        color: #fff;
        background: none;
        -webkit-text-fill-color: #fff;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 550px;
        margin: 0 auto 2.5rem;
        line-height: 1.6;
        font-weight: 400;
    }

    /* ── Role Cards ──────────────────────────────────── */
    .card {
        background: linear-gradient(145deg, rgba(27, 24, 31, 0.98), rgba(16, 15, 19, 0.97));
        border: 1px solid rgba(255, 214, 229, 0.1);
        border-radius: 20px;
        padding: 2.2rem 1.8rem;
        text-align: center;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #f2a7c3, #ffd6e5, transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .card:hover {
        transform: translateY(-6px);
        border-color: rgba(242, 167, 195, 0.52);
        box-shadow: 0 22px 65px rgba(0, 0, 0, 0.58), 0 0 35px rgba(242, 167, 195, 0.1);
    }

    .card:hover::before {
        opacity: 1;
    }

    .card-icon {
        font-size: 3.5rem;
        margin-bottom: 1.2rem;
        filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f1f1f1;
        margin-bottom: 0.6rem;
        letter-spacing: -0.01em;
    }

    .card-desc {
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.6;
    }

    /* ── Feature Pills ───────────────────────────────── */
    .features-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.6rem;
        margin: 2.5rem auto 1.5rem;
        max-width: 600px;
    }

    .feature-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.5rem 1rem;
        background: rgba(27, 24, 31, 0.86);
        border: 1px solid rgba(255, 214, 229, 0.1);
        border-radius: 50px;
        font-size: 0.8rem;
        color: #94a3b8;
        transition: all 0.25s ease;
        backdrop-filter: blur(8px);
    }

    .feature-pill:hover {
        border-color: rgba(242, 167, 195, 0.42);
        color: #fff0f6;
        background: rgba(242, 167, 195, 0.1);
        transform: translateY(-2px);
    }

    .feature-pill-icon {
        font-size: 0.95rem;
    }

    /* ── Stats Bar ────────────────────────────────────── */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        margin: 2rem auto;
        padding: 1.2rem 2rem;
        background: linear-gradient(145deg, rgba(27, 24, 31, 0.86), rgba(16, 15, 19, 0.82));
        border: 1px solid rgba(255, 214, 229, 0.1);
        border-radius: 16px;
        max-width: 500px;
    }

    .stats-item {
        text-align: center;
    }

    .stats-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f1f1;
    }

    .stats-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    /* ── Footer ──────────────────────────────────────── */
    .home-footer {
        text-align: center;
        padding: 1rem;
        margin-top: 1rem;
        color: #475569;
        font-size: 0.78rem;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
    }

    /* ── Animations ──────────────────────────────────── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    .stApp {
        background:
            radial-gradient(ellipse at 50% 0%, rgba(242, 167, 195, 0.13), transparent 48%),
            radial-gradient(ellipse at 92% 70%, rgba(255, 214, 229, 0.045), transparent 36%),
            #09090c;
        color: #f8f2f5;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero-container {
        padding-top: 3.5rem;
    }

    .card {
        min-height: 235px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .stButton > button {
        min-height: 3rem;
        border-radius: 12px;
        font-weight: 650;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        border-color: rgba(242, 167, 195, 0.7);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.42);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(110deg, #f2a7c3, #d982a4);
        border: 1px solid rgba(255, 214, 229, 0.42);
        color: #fff;
    }

    .home-footer {
        border-color: rgba(255, 214, 229, 0.1);
        color: #a99aa1;
    }

    @media (max-width: 640px) {
        .hero-container { padding: 2rem 0.25rem 1rem; }
        .hero-title { font-size: 2.25rem; }
        .stats-bar { gap: 1rem; padding: 1rem; }
        .stats-number { font-size: 1.25rem; }
        .card { min-height: 0; padding: 1.7rem 1.2rem; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🔒 Enterprise-Grade · Private & Secure</div>
    <div class="hero-title">🛡️ <span class="hero-brand">MSU Corp</span><br>Support Assistant</div>
    <div class="hero-subtitle">
        AI-powered 24/7 L1 Customer Support — Resolve platform issues instantly 
        with grounded, knowledge-base answers. No wait times, no ticket queues.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Role Selection ────────────────────────────────────────────────────
col1, spacer, col2 = st.columns([1, 0.2, 1])

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">💬</div>
        <div class="card-title">Customer Support Chat</div>
        <div class="card-desc">
            Facing a platform issue? Chat with our AI support agent for instant answers 
            and step-by-step resolutions — available 24/7.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Support Chat →", use_container_width=True, type="primary", key="btn_chat"):
        st.switch_page("pages/2_Chat.py")

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">🔑</div>
        <div class="card-title">Admin Console</div>
        <div class="card-desc">
            Upload support manuals, FAQs, and troubleshooting guides. 
            Monitor and manage the knowledge base.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Admin Console →", use_container_width=True, key="btn_admin"):
        st.switch_page("pages/1_Admin_Panel.py")

# ── Feature Pills ─────────────────────────────────────────────────────
st.markdown("""
<div class="features-container">
    <div class="feature-pill">
        <span class="feature-pill-icon">⚡</span>
        <span>Instant Responses</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">🔒</span>
        <span>Private & Secure</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">🧠</span>
        <span>Knowledge-Grounded AI</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">📄</span>
        <span>Document-Based Answers</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">🕐</span>
        <span>24/7 Availability</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">🎯</span>
        <span>L1 Support Automation</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">🔎</span>
        <span>RAG + Vector Search</span>
    </div>
    <div class="feature-pill">
        <span class="feature-pill-icon">🖼️</span>
        <span>OCR Image Processing</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats Bar ─────────────────────────────────────────────────────────
st.markdown("""
<div class="stats-bar">
    <div class="stats-item">
        <div class="stats-number">&lt;1s</div>
        <div class="stats-label">Response Time</div>
    </div>
    <div class="stats-item">
        <div class="stats-number">24/7</div>
        <div class="stats-label">Availability</div>
    </div>
    <div class="stats-item">
        <div class="stats-number">100%</div>
        <div class="stats-label">Private</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("""
<div class="home-footer">
    MSU Corp Support Assistant · AI-powered L1 Customer Support · Powered by RAG + Local LLM + LanceDB
</div>
""", unsafe_allow_html=True)
