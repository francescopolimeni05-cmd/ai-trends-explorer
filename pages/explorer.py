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
    has_kb = len(kb_sources) > 0
    has_web = len(web_sources) > 0
    if has_kb and not has_web:
        label, color, bg, bar, bar_color = "Sourced from knowledge base", "#1a1a1a", "#f0f0ec", "100%", "#1a1a1a"
        note = "This answer draws exclusively from indexed research papers and curated news feeds."
    elif has_kb and has_web:
        label, color, bg, bar, bar_color = "Partially sourced from knowledge base", "#92400e", "#fef3c7", "50%", "#d97706"
        note = "The knowledge base provided partial context. Live web sources were used to supplement."
    else:
        label, color, bg, bar, bar_color = "Sourced from live web search", "#7f1d1d", "#fef2f2", "0%", "#ef4444"
        note = "No relevant items were found in the knowledge base. This answer relies on live web search."

    st.markdown(f"""
    <div style="background:{bg};border:1px solid {color}22;border-left:3px solid {color};
    padding:0.75rem 1rem;margin:0.75rem 0 0.5rem 0;border-radius:2px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem;">
            <span style="font-size:0.72rem;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;color:{color};">{label}</span>
            <span style="font-size:0.72rem;color:{color};opacity:0.7;letter-spacing:0.04em;">KB · WEB</span>
        </div>
        <div style="background:#e5e5e0;border-radius:1px;height:3px;width:100%;">
            <div style="background:{bar_color};height:3px;width:{bar};border-radius:1px;"></div>
        </div>
        <div style="margin-top:0.4rem;font-size:0.72rem;color:{color};opacity:0.8;">{note}</div>
    </div>
    """, unsafe_allow_html=True)

def render_sources(kb_sources, web_sources):
    if kb_sources:
        with st.expander(f"Official sources  ({len(kb_sources)})"):
            for i, src in enumerate(kb_sources, 1):
                url, title = src['url'], src['title']
                meta = f"{i} · {src['source'].upper()} · {src['date']}"
                if url:
                    st.markdown(f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'><span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{meta}</span><br><a href='{url}' style='color:#1a1a1a;text-decoration:none;'>{title}</a></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'><span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{meta}</span><br>{title}</div>", unsafe_allow_html=True)

    if web_sources:
        with st.expander(f"Non-official sources  ({len(web_sources)})"):
            st.caption("Retrieved via live web search. Not part of the curated knowledge base.")
            for i, src in enumerate(web_sources, 1):
                url, title = src['url'], src['title']
                if url:
                    st.markdown(f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'><span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{i} · WEB</span><br><a href='{url}' style='color:#1a1a1a;text-decoration:none;'>{title}</a></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='padding:0.3rem 0;font-size:0.82rem;'><span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{i} · WEB</span><br>{title}</div>", unsafe_allow_html=True)

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

    # Save to persistent history
    save_qa(question, result["answer"], kb, web)

    st.session_state["messages"].append({
        "role": "assistant",
        "content": result["answer"],
        "kb_sources": kb,
        "web_sources": web,
    })