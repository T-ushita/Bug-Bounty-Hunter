# """
# BugHunter AI — Streamlit App
# Main entry point with sidebar navigation.
# """

# import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()

# st.set_page_config(
#     page_title="BugHunter AI",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # ── Dark theme override ──────────────────────────────────────────────────────
# st.markdown("""
# <style>
#   [data-testid="stSidebar"] { background-color: #0d1117; }
#   .main { background-color: #0a0f1a; }
#   .stApp { background-color: #0a0f1a; color: #e2e8f0; }
#   .stTextInput > div > div > input { background-color: #161b22; color: #e2e8f0; border: 1px solid #30363d; }
#   .stButton > button { background-color: #0e7490; color: white; border: none; border-radius: 8px; }
#   .stButton > button:hover { background-color: #0891b2; }
#   div[data-testid="metric-container"] { background-color: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 12px; }
#   .stTabs [data-baseweb="tab"] { background-color: #161b22; color: #94a3b8; }
#   .stTabs [aria-selected="true"] { background-color: #0e7490 !important; color: white !important; }
#   code { background-color: #161b22 !important; color: #06b6d4 !important; }
#   .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #06b6d4; }
#   .vuln-critical { border-left: 4px solid #ef4444; background: #1a0a0a; padding: 12px; border-radius: 4px; margin: 8px 0; }
#   .vuln-high { border-left: 4px solid #f97316; background: #1a0f08; padding: 12px; border-radius: 4px; margin: 8px 0; }
#   .vuln-medium { border-left: 4px solid #eab308; background: #1a1608; padding: 12px; border-radius: 4px; margin: 8px 0; }
#   .vuln-low { border-left: 4px solid #3b82f6; background: #080f1a; padding: 12px; border-radius: 4px; margin: 8px 0; }
#   .vuln-info { border-left: 4px solid #64748b; background: #0f1117; padding: 12px; border-radius: 4px; margin: 8px 0; }
#   .log-line { font-family: monospace; font-size: 12px; padding: 2px 8px; border-radius: 3px; margin: 1px 0; }
#   .log-navigate { color: #06b6d4; }
#   .log-recon { color: #a855f7; }
#   .log-detect { color: #f97316; }
#   .log-vuln { color: #ef4444; }
#   .log-complete { color: #10b981; }
#   .log-info { color: #64748b; }
# </style>
# """, unsafe_allow_html=True)

# # ── Sidebar navigation ────────────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("## 🛡️ BugHunter **AI**")
#     st.markdown("---")
#     page = st.radio(
#         "Navigate",
#         ["🏠 Dashboard", "🔍 Single Scan", "🕷️ Auto Crawler", "📋 Reports"],
#         label_visibility="collapsed",
#     )
#     st.markdown("---")
#     st.caption("Powered by TinyFish + Groq")

# # ── Route to pages ────────────────────────────────────────────────────────────
# if page == "🏠 Dashboard":
#     from ui.dashboard import render
#     render()
# elif page == "🔍 Single Scan":
#     from ui.single_scan import render
#     render()
# elif page == "🕷️ Auto Crawler":
#     from ui.auto_crawler import render
#     render()
# elif page == "📋 Reports":
#     from ui.reports import render
#     render()

"""
BugHunter AI — Streamlit App
Main entry point with sidebar navigation.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="BugHunter AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark theme override ──────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background-color: #0d1117; }
  .main { background-color: #0a0f1a; }
  .stApp { background-color: #0a0f1a; color: #e2e8f0; }
  .stTextInput > div > div > input {
    background-color: #161b22; color: #e2e8f0; border: 1px solid #30363d;
    border-radius: 8px; padding: 10px 14px;
  }
  .stButton > button {
    background-color: #0e7490; color: white; border: none;
    border-radius: 8px; font-weight: 600;
  }
  .stButton > button:hover { background-color: #0891b2; }
  div[data-testid="metric-container"] {
    background-color: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 12px;
  }
  .stTabs [data-baseweb="tab"] { background-color: #161b22; color: #94a3b8; border-radius: 6px 6px 0 0; }
  .stTabs [aria-selected="true"] { background-color: #0e7490 !important; color: white !important; }
  code { background-color: #161b22 !important; color: #06b6d4 !important; }
  .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #06b6d4; }
  .vuln-critical { border-left: 4px solid #ef4444; background: #1a0a0a; padding: 12px; border-radius: 4px; margin: 8px 0; }
  .vuln-high     { border-left: 4px solid #f97316; background: #1a0f08; padding: 12px; border-radius: 4px; margin: 8px 0; }
  .vuln-medium   { border-left: 4px solid #eab308; background: #1a1608; padding: 12px; border-radius: 4px; margin: 8px 0; }
  .vuln-low      { border-left: 4px solid #3b82f6; background: #080f1a; padding: 12px; border-radius: 4px; margin: 8px 0; }
  .vuln-info     { border-left: 4px solid #64748b; background: #0f1117; padding: 12px; border-radius: 4px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state page routing ────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "🏠 Dashboard"

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:8px 0 16px 0;">
  <div style="background:#0e4a5c;border:1px solid #06b6d4;border-radius:8px;
              width:34px;height:34px;display:flex;align-items:center;justify-content:center;">
    🛡️
  </div>
  <span style="font-size:17px;font-weight:700;color:#f1f5f9;">BugHunter <span style="color:#06b6d4;">AI</span></span>
</div>
""", unsafe_allow_html=True)

    pages = ["🏠 Dashboard", "🔍 Single Scan", "🕷️ Auto Crawler", "📋 Reports"]
    for p in pages:
        is_active = st.session_state["page"] == p
        btn_style = "background:#0e4a5c;color:#06b6d4;" if is_active else "background:transparent;color:#94a3b8;"
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state["page"] = p
            st.rerun()

    st.markdown("<div style='margin-top:auto;padding-top:24px;'></div>", unsafe_allow_html=True)
    st.caption("Powered by TinyFish + Groq")

# ── Route to pages ────────────────────────────────────────────────────────────
page = st.session_state["page"]

if page == "🏠 Dashboard":
    from ui.dashboard import render
    render()
elif page == "🔍 Single Scan":
    from ui.single_scan import render
    render()
elif page == "🕷️ Auto Crawler":
    from ui.auto_crawler import render
    render()
elif page == "📋 Reports":
    from ui.reports import render
    render()