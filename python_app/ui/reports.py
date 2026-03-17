"""
Reports page — view and download all generated scan reports.
"""

import streamlit as st
import json
import os

HISTORY_FILE = "scan_history.json"
REPORTS_DIR = "reports"


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def render():
    st.markdown("# 📋 Reports")
    st.markdown("All completed scan reports.")
    st.markdown("---")

    history = load_history()

    if not history:
        st.info("No reports yet. Run a scan to generate reports.")
        return

    # Filters
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search URL", placeholder="Filter by URL...")
    with col2:
        sev_filter = st.selectbox("Severity Filter", ["All", "Has Critical", "Has High", "No Vulns"])

    filtered = list(reversed(history))

    if search:
        filtered = [h for h in filtered if search.lower() in h.get("url", "").lower()]

    if sev_filter == "Has Critical":
        filtered = [h for h in filtered if h.get("critical", 0) > 0]
    elif sev_filter == "Has High":
        filtered = [h for h in filtered if h.get("high", 0) > 0]
    elif sev_filter == "No Vulns":
        filtered = [h for h in filtered if h.get("vuln_count", 0) == 0]

    st.markdown(f"**{len(filtered)} report(s)**")
    st.markdown("---")

    for h in filtered:
        url = h.get("url", "")
        ts = h.get("timestamp", "")[:16].replace("T", " ")

        sev_parts = []
        if h.get("critical"): sev_parts.append(f"🔴 {h['critical']} Critical")
        if h.get("high"): sev_parts.append(f"🟠 {h['high']} High")
        if h.get("medium"): sev_parts.append(f"🟡 {h['medium']} Medium")
        if h.get("low"): sev_parts.append(f"🔵 {h['low']} Low")
        sev_str = "  ·  ".join(sev_parts) if sev_parts else "✅ Clean"

        with st.expander(f"**{url}** — {h.get('vuln_count', 0)} vulns  |  {ts}"):
            st.markdown(f"**Severity:** {sev_str}")

            # Load report file
            safe = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
            report_path = f"{REPORTS_DIR}/{safe}.md"

            if os.path.exists(report_path):
                with open(report_path) as f:
                    report_content = f.read()

                tab1, tab2 = st.tabs(["📄 Report Preview", "📥 Download"])
                with tab1:
                    st.markdown(report_content)
                with tab2:
                    st.download_button(
                        "⬇️ Download Markdown Report",
                        data=report_content,
                        file_name=f"{safe}.md",
                        mime="text/markdown",
                        key=f"dl_{safe}",
                    )
            else:
                st.warning("Report file not found on disk.")

    st.markdown("---")
    if st.button("🗑️ Clear All History", type="secondary"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()