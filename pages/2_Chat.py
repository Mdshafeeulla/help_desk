# pages/2_Chat.py — Employee Q&A Interface
import streamlit as st
from core.pipeline import query_department
from core.store import store
from core.config import cfg

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

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
    st.title("🏢 Access Control")

    department = st.selectbox(
        "Your Department",
        cfg.departments,
        format_func=lambda x: x.upper(),
        help="You can ONLY access documents from this department.",
    )

    st.markdown(
        f'<div class="dept-badge">🔒 {department.upper()} ACCESS</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("⚙️ Settings")
    model = st.selectbox("LLM Model", cfg.available_models)
    top_k = st.slider("Chunks to retrieve", min_value=3, max_value=15, value=cfg.top_k)

    st.divider()

    # Show indexed sources for this department
    sources = store.list_sources(department)
    if sources:
        st.subheader(f"📄 {department.upper()} Documents")
        for s in sources:
            st.caption(f"• {s}")
    else:
        st.warning(
            f"⚠️ No documents indexed for **{department.upper()}**.\n\n"
            f"Ask an Admin to upload documents first."
        )

    st.divider()
    st.caption(f"Model: `{model}`")
    st.caption(f"Embedder: `{cfg.embed_model}`")
    st.caption(f"DB: LanceDB (persistent)")

# ── Main Chat Area ────────────────────────────────────────────────────
st.title("💬 Knowledge Assistant")
st.caption(f"Querying **{department.upper()}** department documents · Answers are grounded in your indexed knowledge base")

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
        if "metadata" in msg:
            st.caption(msg["metadata"])

# ── Chat Input ────────────────────────────────────────────────────────
if prompt := st.chat_input(f"Ask about {department.upper()} documents..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        if store.is_empty(department):
            answer = (
                f"⚠️ There are no documents indexed for the **{department.upper()}** department yet. "
                f"Please ask an Admin to upload documents first."
            )
            st.warning(answer)
            metadata_str = ""
        else:
            with st.spinner("🔍 Searching documents & generating answer..."):
                try:
                    result = query_department(
                        question=prompt,
                        department=department,
                        model=model,
                        top_k=top_k,
                    )

                    answer = result["answer"]
                    st.markdown(answer)

                    # Metadata bar
                    metadata_str = (
                        f"⏱ {result['latency_ms']}ms · "
                        f"🔒 {department.upper()} · "
                        f"🤖 {result['model']} · "
                        f"📄 {len(result['chunks'])} chunks"
                    )
                    st.caption(metadata_str)

                    # Expandable source chunks
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
