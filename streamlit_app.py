import streamlit as st
from styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="AI Trends Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

sidebar_nav()

st.title("AI Trends Explorer")
st.markdown(
    "An intelligence dashboard for consulting teams that need to stay ahead of artificial intelligence. "
    "Signals are automatically aggregated from research papers, news feeds, and uploaded reports — "
    "then synthesized into actionable briefings."
)

st.divider()

st.markdown("""
<div style="display:flex;align-items:flex-start;gap:0;margin:2rem 0 2.5rem 0;width:100%;">

  <div style="flex:1;min-width:0;padding:0 1rem 0 0;">
    <div style="font-size:0.7rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:#9ca3af;margin-bottom:0.4rem;">Sources</div>
    <div style="font-size:0.88rem;font-weight:600;color:#1a1a1a;margin-bottom:0.4rem;">arXiv + News</div>
    <div style="font-size:0.8rem;color:#6b7280;line-height:1.6;">cs.AI · cs.LG · cs.CL · stat.ML<br>VentureBeat · MIT Tech Review<br>The Gradient · Google Research<br>OpenAI News · PDF upload</div>
  </div>

  <div style="display:flex;align-items:center;padding:0 0.75rem;margin-top:1.4rem;color:#1a1a1a;font-size:1rem;flex-shrink:0;">→</div>

  <div style="flex:1;min-width:0;padding:0 1rem;">
    <div style="font-size:0.7rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:#9ca3af;margin-bottom:0.4rem;">Ingestion</div>
    <div style="font-size:0.88rem;font-weight:600;color:#1a1a1a;margin-bottom:0.4rem;">Fetch, chunk, embed</div>
    <div style="font-size:0.8rem;color:#6b7280;line-height:1.6;">OpenAI text-embedding-3-large<br>3072-dimensional vectors<br>Inngest async orchestration<br>Deterministic deduplication</div>
  </div>

  <div style="display:flex;align-items:center;padding:0 0.75rem;margin-top:1.4rem;color:#1a1a1a;font-size:1rem;flex-shrink:0;">→</div>

  <div style="flex:1;min-width:0;padding:0 1rem;">
    <div style="font-size:0.7rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:#9ca3af;margin-bottom:0.4rem;">Storage</div>
    <div style="font-size:0.88rem;font-weight:600;color:#1a1a1a;margin-bottom:0.4rem;">Qdrant vector DB</div>
    <div style="font-size:0.8rem;color:#6b7280;line-height:1.6;">COSINE similarity search<br>Metadata: source · date · type<br>~100 items seeded<br>Live web search fallback</div>
  </div>

  <div style="display:flex;align-items:center;padding:0 0.75rem;margin-top:1.4rem;color:#1a1a1a;font-size:1rem;flex-shrink:0;">→</div>

  <div style="flex:1;min-width:0;padding:0 1rem;">
    <div style="font-size:0.7rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:#9ca3af;margin-bottom:0.4rem;">Intelligence</div>
    <div style="font-size:0.88rem;font-weight:600;color:#1a1a1a;margin-bottom:0.4rem;">GPT-4o-mini synthesis</div>
    <div style="font-size:0.8rem;color:#6b7280;line-height:1.6;">7 trend topic clusters<br>Weekly executive digest<br>Semantic Q&amp;A with citations<br>Persistent query history</div>
  </div>

  <div style="display:flex;align-items:center;padding:0 0.75rem;margin-top:1.4rem;color:#1a1a1a;font-size:1rem;flex-shrink:0;">→</div>

  <div style="flex:1;min-width:0;padding:0 0 0 1rem;">
    <div style="font-size:0.7rem;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;color:#9ca3af;margin-bottom:0.4rem;">Output</div>
    <div style="font-size:0.88rem;font-weight:700;color:#1a1a1a;margin-bottom:0.4rem;">Four interfaces</div>
    <div style="font-size:0.8rem;font-weight:500;color:#1a1a1a;line-height:1.6;">Trend dashboard<br>Weekly digest<br>Explorer Q&amp;A<br>PDF ingestion</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns(3, gap="large")
with col1:
    st.markdown('<div class="section-label">Analysis</div>', unsafe_allow_html=True)
    st.markdown("**Dashboard**")
    st.markdown("Seven synthesized trend cards covering the most active areas in AI, grounded in this week's papers and news.")
    if st.button("Open Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
with col2:
    st.markdown('<div class="section-label">Briefing</div>', unsafe_allow_html=True)
    st.markdown("**Weekly Digest**")
    st.markdown("A full narrative briefing formatted for leadership — executive summary, top trends, and strategic implications.")
    if st.button("Open Digest", use_container_width=True):
        st.switch_page("pages/digest.py")
with col3:
    st.markdown('<div class="section-label">Research</div>', unsafe_allow_html=True)
    st.markdown("**Explorer**")
    st.markdown("Ask any question about AI developments and receive grounded answers with citations to source material.")
    if st.button("Open Explorer", use_container_width=True):
        st.switch_page("pages/explorer.py")

st.divider()
st.caption("Sources: arXiv cs.AI / cs.LG / cs.CL / stat.ML · MIT Technology Review · VentureBeat · The Gradient · OpenAI News · Google Research")