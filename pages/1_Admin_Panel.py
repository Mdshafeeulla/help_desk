# pages/1_Admin_Panel.py — Document Management
import streamlit as st
from core.pipeline import index_documents
from core.store import store
from core.config import cfg
from utils.pdf_parser import extract_pdf_text
from utils.image_parser import extract_image_text
import json

st.set_page_config(page_title="Admin Panel", page_icon="🔑", layout="wide")

# ── Header ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("🔑 Admin Panel")
st.caption("Upload documents to departments · Manage the knowledge base")

# ── Tabs ──────────────────────────────────────────────────────────────
tab_upload, tab_manage, tab_stats = st.tabs([
    "📥 Upload Documents",
    "🗂️ Manage Documents",
    "📊 Dashboard",
])

# ━━ Tab 1: Upload ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_upload:
    st.subheader("Upload Documents to a Department")

    col_dept, col_files = st.columns([1, 2])

    with col_dept:
        department = st.selectbox(
            "Target Department",
            [d.upper() for d in cfg.departments],
            help="Documents will be tagged with this department for ABAC isolation.",
        )

    with col_files:
        files = st.file_uploader(
            "Upload PDF, TXT, or Image files (PNG, JPG, JPEG, WEBP, BMP)",
            type=["pdf", "txt", "png", "jpg", "jpeg", "webp", "bmp"],
            accept_multiple_files=True,
            help="You can upload multiple files at once. Images will be processed with GPU OCR.",
        )

    if st.button("📥 Index Documents", type="primary", disabled=not files, use_container_width=True):
        dept_lower = department.lower()
        progress_bar = st.progress(0)
        status = st.empty()

        for i, f in enumerate(files):
            fname = f.name.lower()
            status.info(f"Processing {f.name}...")

            # Extract text
            file_bytes = f.read()
            if fname.endswith(".pdf"):
                text = extract_pdf_text(file_bytes)
            elif any(fname.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]):
                text = extract_image_text(file_bytes)
            else:
                # Try UTF-8 first, fall back to latin-1
                try:
                    text = file_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text = file_bytes.decode("latin-1")


            if not text.strip():
                st.warning(f"⚠️ {f.name} — no text extracted, skipping.")
                continue

            # Index
            n = index_documents(text, department=dept_lower, source=f.name)
            st.success(f"✅ **{f.name}** → {n} chunks indexed under **{department}**")

            progress_bar.progress((i + 1) / len(files))

        status.empty()
        progress_bar.empty()
        st.balloons()

    st.divider()
    st.subheader("Direct JSON Ingestion")
    st.caption("Paste JSON containing `department`, `title` (optional), and `content` fields to auto-route to departments.")
    
    json_input = st.text_area(
        "Paste JSON here", 
        height=250, 
        placeholder='[\n  {\n    "id": "management_001",\n    "department": "MANAGEMENT",\n    "title": "Strategic Goals 2025",\n    "content": "The company\'s strategic priorities..."\n  }\n]'
    )
    
    if st.button("📥 Index JSON", type="primary", disabled=not json_input.strip(), use_container_width=True):
        try:
            data = json.loads(json_input)
            if isinstance(data, dict):
                data = [data]
                
            if not isinstance(data, list):
                st.error("JSON must be an object or an array of objects.")
            else:
                progress_bar = st.progress(0)
                status = st.empty()
                success_count = 0
                
                for i, item in enumerate(data):
                    dept = str(item.get("department", "")).lower().strip()
                    title = str(item.get("title", item.get("id", f"json_doc_{i}")))
                    content = str(item.get("content", ""))
                    
                    status.info(f"Processing {title}...")
                    
                    if not dept:
                        st.warning(f"⚠️ **{title}** — missing 'department', skipping.")
                        continue
                    if not content.strip():
                        st.warning(f"⚠️ **{title}** — missing 'content', skipping.")
                        continue
                        
                    n = index_documents(content, department=dept, source=title)
                    st.success(f"✅ **{title}** → {n} chunks indexed under **{dept.upper()}**")
                    success_count += 1
                    
                    progress_bar.progress((i + 1) / len(data))
                    
                status.empty()
                progress_bar.empty()
                if success_count > 0:
                    st.balloons()
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")

# ━━ Tab 2: Manage ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_manage:
    st.subheader("Indexed Documents by Department")

    has_any = False
    for dept in cfg.departments:
        sources = store.list_sources(dept)
        if not sources:
            continue
        has_any = True

        with st.expander(f"**{dept.upper()}** — {len(sources)} document(s)", expanded=False):
            for src in sources:
                col_name, col_del = st.columns([4, 1])
                col_name.markdown(f"📄 `{src}`")
                if col_del.button("🗑️ Delete", key=f"del_{dept}_{src}"):
                    store.delete_source(dept, src)
                    st.success(f"Deleted '{src}' from {dept.upper()}")
                    st.rerun()

            st.divider()
            if st.button(f"🗑️ Delete ALL {dept.upper()} documents", key=f"del_all_{dept}"):
                store.delete_department(dept)
                st.warning(f"All documents for {dept.upper()} have been deleted.")
                st.rerun()

    if not has_any:
        st.info("No documents indexed yet. Go to the Upload tab to add documents.")

# ━━ Tab 3: Dashboard ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_stats:
    st.subheader("Knowledge Base Overview")

    stats = store.get_stats()

    if stats:
        # Metrics row
        total_chunks = sum(stats.values())
        total_depts = len(stats)

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Chunks", f"{total_chunks:,}")
        m2.metric("Active Departments", total_depts)
        m3.metric("Vector Dimensions", cfg.embed_dimensions)

        st.divider()

        # Bar chart
        import pandas as pd
        df = pd.DataFrame(
            [{"Department": k.upper(), "Chunks": v} for k, v in stats.items()]
        ).sort_values("Chunks", ascending=False)

        st.bar_chart(df.set_index("Department"))

        # Table
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data indexed yet.")

    st.divider()
    st.caption(f"Embedder: `{cfg.embed_model}` · Dims: {cfg.embed_dimensions} (MRL) · DB: LanceDB")
