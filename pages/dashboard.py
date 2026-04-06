import streamlit as st
from trend_engine import get_all_trends
from styles import inject_css, sidebar_nav
from history import load_history

st.set_page_config(page_title="Dashboard — AI Trends Explorer", layout="wide")
inject_css()
sidebar_nav()

st.title("Trend Dashboard")
st.markdown("Synthesized signals across seven active areas in artificial intelligence.")
st.divider()

@st.cache_data(ttl=3600, show_spinner=False)
def load_trends():
    return get_all_trends()

col_refresh, _ = st.columns([1, 5])
with col_refresh:
    if st.button("Refresh", type="secondary"):
        st.cache_data.clear()
        st.rerun()

try:
    with st.spinner("Retrieving and synthesizing signals across all topics..."):
        trends = load_trends()

    if not trends:
        st.warning("No trends returned. Make sure Qdrant is running and seed_db.py has been executed.")
        st.stop()

    cols = st.columns(2, gap="large")
    for i, trend in enumerate(trends):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f'<div class="trend-meta">{trend["signal_count"]} signals</div>', unsafe_allow_html=True)
                st.markdown(f"### {trend['topic']}")
                st.markdown(trend["summary"])
                if trend["key_signals"]:
                    with st.expander("Sources"):
                        for sig in trend["key_signals"]:
                            label = f"{sig['source'].upper()} · {sig['date']} · {sig['title']}"
                            if sig["url"]:
                                st.markdown(f"- [{label}]({sig['url']})")
                            else:
                                st.markdown(f"- {label}")

except Exception as e:
    st.error(f"Error loading trends: {e}")
    st.info("Check that Qdrant is running and your OPENAI_API_KEY is valid.")
    st.cache_data.clear()

# ── Query history ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### Query History")
st.markdown("All questions asked in the Explorer, most recent first.")

history = load_history()

if not history:
    st.markdown(
        "<div style='padding:2rem;border:1px dashed #d1cfc9;text-align:center;'>"
        "<p style='color:#9ca3af;font-size:0.82rem;letter-spacing:0.05em;text-transform:uppercase;margin:0;'>"
        "No queries yet — ask a question in the Explorer to see history here."
        "</p></div>",
        unsafe_allow_html=True
    )
else:
    cols = st.columns(2, gap="large")
    for i, entry in enumerate(history):
        with cols[i % 2]:
            with st.container(border=True):
                # Timestamp + source badge
                kb = entry.get("kb_sources", [])
                web = entry.get("web_sources", [])
                has_web = len(web) > 0

                if has_web:
                    badge_color, badge_bg, badge_label = "#92400e", "#fef3c7", "KB + Web"
                else:
                    badge_color, badge_bg, badge_label = "#1a1a1a", "#f0f0ec", "Knowledge base"

                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;'>"
                    f"<span style='font-size:0.68rem;letter-spacing:0.07em;text-transform:uppercase;"
                    f"background:{badge_bg};color:{badge_color};padding:0.2rem 0.5rem;"
                    f"border:1px solid {badge_color}22;border-radius:2px;'>{badge_label}</span>"
                    f"<span class='trend-meta'>{entry['timestamp']}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Question as card title
                st.markdown(f"### {entry['question']}")

                # Full answer — no truncation
                st.markdown(entry["answer"])

                # Sources
                if kb:
                    with st.expander(f"Official sources ({len(kb)})"):
                        for j, src in enumerate(kb, 1):
                            meta = f"{j} · {src['source'].upper()} · {src['date']}"
                            title = src['title']
                            url = src['url']
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
                if web:
                    with st.expander(f"Non-official sources ({len(web)})"):
                        st.caption("Retrieved via live web search.")
                        for j, src in enumerate(web, 1):
                            url, title = src['url'], src['title']
                            if url:
                                st.markdown(
                                    f"<div style='padding:0.3rem 0;font-size:0.82rem;border-bottom:1px solid #f0ede8;'>"
                                    f"<span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{j} · WEB</span><br>"
                                    f"<a href='{url}' style='color:#1a1a1a;text-decoration:none;'>{title}</a></div>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    f"<div style='padding:0.3rem 0;font-size:0.82rem;'>"
                                    f"<span style='color:#9ca3af;font-size:0.7rem;letter-spacing:0.06em;text-transform:uppercase;'>{j} · WEB</span><br>"
                                    f"{title}</div>",
                                    unsafe_allow_html=True
                                )