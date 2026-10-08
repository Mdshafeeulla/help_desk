# pages/2_Chat.py — Employee Q&A Interface
import threading
import time
import streamlit as st
from core.pipeline import query_department, is_greeting
from core.store import store
from core.config import cfg
from core.llm import prewarm_model

st.set_page_config(page_title="MSU Corp Support", page_icon="🛡️", layout="wide")

# ── Styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }

    .dept-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar: Department & Settings ────────────────────────────────────
with st.sidebar:
    st.title("🛡️ MSU Corp Support")

    department = "it"

    st.markdown(
        '<div class="dept-badge">🔒 MSU CORP SUPPORT</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("⚙️ Settings")
    model = st.selectbox("LLM Model", cfg.available_models)
    top_k = st.slider("Chunks to retrieve", min_value=3, max_value=15, value=cfg.top_k)

    # Pre-warm model in background thread when selected
    if "active_model" not in st.session_state or st.session_state.active_model != model:
        st.session_state.active_model = model
        threading.Thread(target=prewarm_model, args=(model,), daemon=True).start()

    st.divider()

    # Show indexed support documents
    sources = store.list_sources(department)
    if sources:
        st.subheader("📄 Support Knowledge Base")
        for s in sources:
            st.caption(f"• {s}")
    else:
        st.warning(
            "⚠️ No support documents indexed yet.\n\n"
            "Ask an Admin to upload FAQs, manuals, and guides first."
        )

    st.divider()
    st.caption(f"Model: `{model}`")
    st.caption("Powered by MSU Corp Knowledge Base")
    st.caption("Available 24/7 · No ticket needed")

# ── Main Chat Area ────────────────────────────────────────────────────
st.title("🛡️ MSU Corp Support Assistant")
st.caption("AI-powered L1 customer support · Describe your issue and get instant help from our knowledge base")

# ── Session state for chat history ────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_dept" not in st.session_state:
    st.session_state.active_dept = department

# Clear chat when department changes
if st.session_state.active_dept != department:
    st.session_state.messages = []
    st.session_state.active_dept = department

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "metadata" in msg and msg["metadata"]:
            st.caption(msg["metadata"])

# ── Chat Input ────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask an IT support question..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        # If it's not a greeting and no docs indexed, show warning
        from core.instant_responses import get_instant_response as _check_instant
        is_instant_query = _check_instant(prompt) is not None

        if not is_instant_query and not is_greeting(prompt) and store.is_empty(department):
            answer = (
                "⚠️ There are no documents indexed for **IT Support** yet. "
                "Please ask an Admin to upload documents first."
            )
            st.warning(answer)
            metadata_str = ""
        else:
            try:
                t0 = time.perf_counter()

                # ── Instant cache queries get no spinner (already sub-ms) ──
                if is_instant_query:
                    result = query_department(
                        question=prompt,
                        department=department,
                        model=model,
                        top_k=top_k,
                        stream=False,
                        history=st.session_state.messages[:-1],
                    )
                else:
                    spinner_msg = "💬 Thinking..." if is_greeting(prompt) else "🔍 Searching IT knowledge base..."
                    with st.spinner(spinner_msg):
                        result = query_department(
                            question=prompt,
                            department=department,
                            model=model,
                            top_k=top_k,
                            stream=True,
                            history=st.session_state.messages[:-1],
                        )

                total_latency_ms = int((time.perf_counter() - t0) * 1000)

                # ── Render answer ──────────────────────────────────────────
                if result.get("is_instant"):
                    # Instant answer — display directly, no streaming
                    answer = result["answer"]
                    st.markdown(answer)
                else:
                    # Streamed answer from LLM
                    if result.get("stream") is not None:
                        answer = st.write_stream(result["stream"])
                    else:
                        answer = result.get("answer", "")
                        st.markdown(answer)

                # ── Metadata bar ───────────────────────────────────────────
                chunks_count = len(result.get("chunks", []))
                if result.get("is_instant"):
                    chunks_label = "⚡ Instant"
                    model_label = "cache"
                elif chunks_count > 0:
                    chunks_label = f"📄 {chunks_count} chunks"
                    model_label = result["model"]
                else:
                    chunks_label = "💬 Conversational"
                    model_label = result["model"]

                metadata_str = (
                    f"⏱ {total_latency_ms}ms · "
                    f"🔒 IT SUPPORT · "
                    f"🤖 {model_label} · "
                    f"{chunks_label}"
                )
                st.caption(metadata_str)

                # ── Source chunks (only for RAG answers) ──────────────────
                if result.get("chunks"):
                    with st.expander("🔍 View Source Chunks"):
                        for i, chunk in enumerate(result["chunks"], 1):
                            st.markdown(
                                f"**Chunk {i}** · `{chunk['source']}` · "
                                f"Score: `{chunk['score']:.3f}`"
                            )
                            st.markdown(
                                f"> {chunk['text'][:400]}{'...' if len(chunk['text']) > 400 else ''}"
                            )
                            if i < len(result["chunks"]):
                                st.divider()

            except ValueError as e:
                answer = f"⚠️ {str(e)}"
                st.warning(answer)
                metadata_str = ""
            except RuntimeError as e:
                answer = f"❌ {str(e)}"
                st.error(answer)
                metadata_str = ""

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "metadata": metadata_str if metadata_str else None,
        })

