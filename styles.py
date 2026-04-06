import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

    /* Hide Streamlit's auto-generated page nav */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
        color: #1a1a1a !important;
    }

    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.1rem !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * {
        color: #d1d5db !important;
    }
    [data-testid="stSidebar"] a {
        color: #f9fafb !important;
        text-decoration: none !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] a:hover {
        color: #ffffff !important;
    }
    [data-testid="stSidebarContent"] hr {
        border-color: #374151 !important;
    }
    [data-testid="stSidebarContent"] .stCaption {
        color: #6b7280 !important;
        font-size: 0.72rem !important;
    }

    /* Main area */
    .main .block-container {
        padding-top: 2.5rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 1100px !important;
    }

    /* Buttons — main area */
    .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 2px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        padding: 0.5rem 1.2rem !important;
        transition: background 0.15s ease !important;
    }
    .stButton > button:hover {
        background-color: #374151 !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: #1a1a1a !important;
        border: 1px solid #1a1a1a !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    /* Sidebar example query buttons — override uppercase */
    [data-testid="stSidebar"] .stButton > button {
        text-transform: none !important;
        font-size: 0.78rem !important;
        text-align: left !important;
        background-color: transparent !important;
        color: #d1d5db !important;
        border: none !important;
        padding: 0.3rem 0 !important;
        font-weight: 300 !important;
        letter-spacing: 0 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    /* Cards / containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #e5e0d8 !important;
        border-radius: 2px !important;
        background: #ffffff !important;
        padding: 1.5rem !important;
        box-shadow: none !important;
    }

    /* Chat */
    [data-testid="stChatInput"] textarea {
        font-family: 'DM Sans', sans-serif !important;
        border-radius: 2px !important;
        border: 1px solid #d1cfc9 !important;
        background: #ffffff !important;
    }
    [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid #e5e0d8 !important;
        border-radius: 2px !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #e5e0d8 !important;
        border-radius: 2px !important;
        background: #fafaf8 !important;
    }
    [data-testid="stExpander"] summary {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        color: #6b7280 !important;
    }

    /* Captions and labels */
    .stCaption {
        color: #9ca3af !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.03em !important;
    }

    /* Info boxes */
    [data-testid="stNotification"] {
        border-radius: 2px !important;
        border-left: 3px solid #1a1a1a !important;
        background: #f7f6f3 !important;
    }

    /* Divider */
    hr {
        border-color: #e5e0d8 !important;
        margin: 1.5rem 0 !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #1a1a1a !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: transparent !important;
        color: #1a1a1a !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 2px !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }
    .stDownloadButton > button:hover {
        background: #1a1a1a !important;
        color: #ffffff !important;
    }

    /* Sidebar branding */
    .sidebar-brand {
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        color: #f9fafb;
        letter-spacing: -0.01em;
        margin-bottom: 0.2rem;
    }
    .sidebar-tagline {
        font-size: 0.72rem;
        color: #6b7280;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    .section-label {
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
    .trend-meta {
        font-size: 0.72rem;
        color: #9ca3af;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    </style>
    """, unsafe_allow_html=True)

def sidebar_nav():
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">AI Trends Explorer</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">Intelligence for decision makers</div>', unsafe_allow_html=True)
        st.page_link("streamlit_app.py",   label="Home")
        st.page_link("pages/digest.py",    label="Weekly Digest")
        st.page_link("pages/explorer.py",  label="Explorer")
        st.page_link("pages/upload.py",    label="Upload Report")
        st.page_link("pages/dashboard.py", label="Dashboard")
        st.divider()
        st.caption("OpenAI · Qdrant · arXiv · RSS")