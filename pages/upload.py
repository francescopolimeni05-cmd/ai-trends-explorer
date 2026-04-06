import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
from styles import inject_css, sidebar_nav
import os
import requests

load_dotenv()

st.set_page_config(page_title="Upload Report — AI Trends Explorer", layout="wide")
inject_css()
sidebar_nav()

# ── Inngest helpers (unchanged logic) ────────────────────────────────────────

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag-project", is_production=False)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploaded_docs")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path

async def send_rag_ingest_event(pdf_path: Path) -> str:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/ingest-pdf",
            data={
                "pdf_file_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )
    return result[0] if result else None

def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")

def fetch_runs(event_id: str) -> list[dict]:
    try:
        resp = requests.get(
            f"{_inngest_api_base()}/events/{event_id}/runs", timeout=5
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception:
        return []

def wait_for_run_output(event_id: str, timeout_s: float = 120.0) -> dict:
    start = time.time()
    last_status = "Pending"
    progress_bar = st.progress(0)
    status_text = st.empty()

    while True:
        elapsed = time.time() - start
        progress_bar.progress(min(elapsed / timeout_s, 0.99))

        runs = fetch_runs(event_id)
        if runs:
            status = runs[0].get("status", "Running")
            last_status = status
            status_text.caption(f"Status: {status}")

            if status in ("Completed", "Succeeded", "Success", "Finished"):
                progress_bar.progress(1.0)
                status_text.empty()
                return runs[0].get("output") or {}

            if status in ("Failed", "Cancelled"):
                progress_bar.empty()
                status_text.empty()
                raise RuntimeError(f"Ingestion run {status}")

        if elapsed > timeout_s:
            progress_bar.empty()
            status_text.empty()
            raise TimeoutError(f"Timed out (last status: {last_status})")

        time.sleep(0.5)

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
                with st.spinner("Saving..."):
                    file_path = save_uploaded_pdf(uploaded_file)

                with st.spinner("Sending to ingestion pipeline..."):
                    event_id = asyncio.run(send_rag_ingest_event(file_path))
                    if not event_id:
                        raise Exception("Failed to obtain event ID from Inngest")

                st.caption(f"Event ID: {event_id}")
                output = wait_for_run_output(event_id)
                chunks = output.get("ingested", 0)

                st.success(f"{uploaded_file.name} — {chunks} chunks indexed")
                results.append({"file": uploaded_file.name, "status": "success", "chunks": chunks})

            except TimeoutError as e:
                st.warning(f"{uploaded_file.name} — timed out. Check Inngest dashboard.")
                results.append({"file": uploaded_file.name, "status": "timeout", "chunks": 0})

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
    st.caption("Inngest workflow dashboard")
    st.code("http://localhost:8288", language=None)
with col2:
    st.caption("Qdrant vector database")
    st.code("http://localhost:6333/dashboard", language=None)