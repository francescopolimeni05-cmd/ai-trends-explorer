import streamlit as st
from trend_engine import answer_question
from styles import inject_css, sidebar_nav
from history import save_qa, load_history

st.set_page_config(page_title="Explorer — AI Trends Explorer", layout="wide")
inject_css()
sidebar_nav()

with st.sidebar:
    st.divider()
    st.markdown('<div class="section-label">Example queries</div>', unsafe_allow_html=True)
    examples = [
        "What are the main approaches to AI alignment?",
        "What efficiency techniques are emerging for LLMs?",
        "What is the state of multimodal AI models?",
        "How are AI agents being developed and evaluated?",
    ]
    for q in examples:
        if st.button(q, use_container_width=True, key=q):
            st.session_state["prefill_q"] = q

st.title("Explorer")
st.markdown("Ask any question about AI trends. Every answer is grounded in retrieved source material.")
st.divider()

def source_badge(kb_sources, web_sources):
    has_web = len(web_sources) > 0
    if has_web:
        label = "Knowledge base + live web search"
    else:
        label = "Knowledge base"
    st.markdown(
        f'<div class="trend-meta" style="margin: 0.5rem 0 0.3rem 0;">Source: {label}</div>',
        unsafe_allow_html=True
    )

def render_sources(kb_sources, web_sources):
    if kb_sources:
        with st.expander(f"Official sources  ({len(kb_sources)})"):
            for i, src in enumerate(kb_sources, 1):
                url = src.get("url", "")
                title = src.get("title", "")
                meta = f"{i} · {src.get('source','').upper()} · {src.get('date','')}"
                if url:
                    st.markdown(
                        f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'>"
                        f"<span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{meta}</span><br>"
                        f"<a href='{url}' style='color:#1a1a1a;text-decoration:none;'>{title}</a></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'>"
                        f"<span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{meta}</span><br>"
                        f"{title}</div>",
                        unsafe_allow_html=True
                    )

    if web_sources:
        with st.expander(f"Non-official sources  ({len(web_sources)})"):
            st.caption("Retrieved via live web search. Not part of the curated knowledge base.")
            for i, src in enumerate(web_sources, 1):
                url = src.get("url", "")
                title = src.get("title", "")
                if url:
                    st.markdown(
                        f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'>"
                        f"<span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{i} · WEB</span><br>"
                        f"<a href='{url}' style='color:#1a1a1a;text-decoration:none;'>{title}</a></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='padding:0.3rem 0;font-size:0.82rem;'>"
                        f"<span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{i} · WEB</span><br>"
                        f"{title}</div>",
                        unsafe_allow_html=True
                    )

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            source_badge(msg.get("kb_sources", []), msg.get("web_sources", []))
            render_sources(msg.get("kb_sources", []), msg.get("web_sources", []))

prefill = st.session_state.pop("prefill_q", "")
question = st.chat_input("Ask about AI trends...") or prefill

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            result = answer_question(question, top_k=6)

        st.markdown(result["answer"])
        kb = result.get("kb_sources", [])
        web = result.get("web_sources", [])
        source_badge(kb, web)
        render_sources(kb, web)

    save_qa(question, result["answer"], kb, web)

    st.session_state["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "kb_sources": kb,
        "web_sources": web,
    })