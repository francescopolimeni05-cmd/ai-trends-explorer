import uuid
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from styles import inject_css, sidebar_nav
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage

load_dotenv()

st.set_page_config(page_title="Upload Report — AI Trends Explorer", layout="wide")
inject_css()
sidebar_nav()

# ── Direct ingestion (no Inngest needed) ────────────────────────────────────

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploaded_docs")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path


def ingest_pdf(file_path: Path) -> int:
    """Load, chunk, embed, and store a PDF directly into Qdrant."""
    chunks = load_and_chunk_pdf(str(file_path))
    if not chunks:
        return 0

    vectors = embed_texts(chunks)
    source_id = file_path.name
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
    payloads = [
        {
            "text": chunks[i],
            "title": file_path.stem,
            "url": "",
            "date": "",
            "source_type": "pdf",
            "category": "uploaded",
            "feed_name": "User Upload",
        }
        for i in range(len(chunks))
    ]

    db = QdrantStorage()
    db.upsert(ids, vectors, payloads)
    return len(chunks)


# ── Page ─────────────────────────────────────────────────────────────────────

st.title("Upload Report")
st.markdown(
    "Upload PDF reports, white papers, or research documents to extend the knowledge base. "
    "Uploaded documents are chunked, embedded, and indexed alongside arXiv papers and news feeds."
)
st.divider()

# Sidebar stats
with st.sidebar:
    st.divider()
    st.markdown('<div class="section-label">Knowledge base</div>', unsafe_allow_html=True)
    uploads_dir = Path("uploaded_docs")
    if uploads_dir.exists():
        pdf_files = list(uploads_dir.glob("*.pdf"))
        st.caption(f"{len(pdf_files)} PDF{'s' if len(pdf_files) != 1 else ''} uploaded")
        if pdf_files:
            total_mb = sum(f.stat().st_size for f in pdf_files) / 1024 / 1024
            st.caption(f"{total_mb:.1f} MB total")
    else:
        st.caption("No PDFs uploaded yet")
    st.divider()
    st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)
    st.caption("Chunk size: 1000 tokens")
    st.caption("Overlap: 200 tokens")
    st.caption("Model: text-embedding-3-large")

# Upload area
uploaded_files = st.file_uploader(
    "Select PDF file(s)",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if not uploaded_files:
    st.markdown(
        """
        <div style='padding: 3rem 2rem; border: 1px dashed #d1cfc9; text-align: center; margin: 1.5rem 0;'>
            <p style='color: #9ca3af; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase; margin: 0;'>
                Drag and drop PDF files here or click to browse
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # File list
    st.markdown('<div class="section-label">Selected files</div>', unsafe_allow_html=True)
    for f in uploaded_files:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"`{f.name}`")
        with col2:
            st.caption(f"{f.size / 1024:.0f} KB")

    st.divider()

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        start = st.button("Ingest", use_container_width=True)

    if start:
        results = []

        for idx, uploaded_file in enumerate(uploaded_files):
            st.markdown(f"**{idx + 1} / {len(uploaded_files)} — {uploaded_file.name}**")

            try:
                with st.spinner("Saving PDF..."):
                    file_path = save_uploaded_pdf(uploaded_file)

                with st.spinner("Chunking, embedding, and storing in Qdrant..."):
                    num_chunks = ingest_pdf(file_path)

                st.success(f"{uploaded_file.name} — {num_chunks} chunks indexed")
                results.append({"file": uploaded_file.name, "status": "success", "chunks": num_chunks})

            except Exception as e:
                st.error(f"{uploaded_file.name} — {e}")
                results.append({"file": uploaded_file.name, "status": "error", "chunks": 0})

            if idx < len(uploaded_files) - 1:
                st.divider()

        # Summary
        st.divider()
        st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
        success = sum(1 for r in results if r["status"] == "success")
        total_chunks = sum(r["chunks"] for r in results)

        col1, col2, col3 = st.columns(3)
        col1.metric("Ingested", success)
        col2.metric("Failed", len(results) - success)
        col3.metric("Total chunks", total_chunks)

        if success > 0:
            st.divider()
            col_exp, _ = st.columns([1, 4])
            with col_exp:
                if st.button("Open Explorer", use_container_width=True):
                    st.switch_page("pages/explorer.py")

st.divider()
st.markdown('<div class="section-label">Services</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.caption("OpenAI Embeddings")
    st.code("text-embedding-3-large", language=None)
with col2:
    st.caption("Qdrant vector database")
    qdrant_url = __import__("os").getenv("QDRANT_URL", "http://localhost:6333")
    st.code(qdrant_url, language=None)
