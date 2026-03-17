"""
Dashboard page — shows stats and recent scan history.
"""

import streamlit as st
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from crawler_state import load_state

RESULTS_FILE = "scan_history.json"


def load_history():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return []


def render():
    st.markdown("# 🏠 Dashboard")
    st.markdown("Overview of all autonomous security scanning activity.")
    st.markdown("---")

    history = load_history()
    state = load_state()

    col1, col2, col3, col4 = st.columns(4)
    total_sites = len(history)
    total_vulns = sum(h.get("vuln_count", 0) for h in history)
    total_critical = sum(h.get("critical", 0) for h in history)
    total_high = sum(h.get("high", 0) for h in history)

    with col1:
        st.metric("🌐 Sites Scanned", total_sites)
    with col2:
        st.metric("🐛 Total Vulns", total_vulns)
    with col3:
        st.metric("🔴 Critical", total_critical)
    with col4:
        st.metric("🟠 High", total_high)

    st.markdown("---")

    if not history:
        st.info("No scans yet. Run a Single Scan or start the Auto Crawler to begin.")
        return

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### Recent Scans")
        for h in reversed(history[-10:]):
            sev_bar = ""
            if h.get("critical", 0): sev_bar += f"🔴×{h['critical']} "
            if h.get("high", 0): sev_bar += f"🟠×{h['high']} "
            if h.get("medium", 0): sev_bar += f"🟡×{h['medium']} "
            if h.get("low", 0): sev_bar += f"🔵×{h['low']} "

            with st.container():
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**`{h['url']}`**")
                    st.caption(f"{h.get('timestamp', '')[:16]}  |  {sev_bar or 'No vulns'}")
                with c2:
                    st.markdown(f"**{h.get('vuln_count', 0)}** vulns")
            st.divider()

    with col_right:
        st.markdown("### Severity Breakdown")
        labels = ["Critical", "High", "Medium", "Low", "Info"]
        values = [
            sum(h.get("critical", 0) for h in history),
            sum(h.get("high", 0) for h in history),
            sum(h.get("medium", 0) for h in history),
            sum(h.get("low", 0) for h in history),
            sum(h.get("info", 0) for h in history),
        ]
        colors = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors),
            textfont=dict(color="white"),
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            showlegend=True,
            margin=dict(t=0, b=0, l=0, r=0),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)