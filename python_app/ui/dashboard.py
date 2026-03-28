# """
# Dashboard page — shows stats and recent scan history.
# """

# import streamlit as st
# import json
# import os
# import plotly.graph_objects as go
# import plotly.express as px
# from crawler_state import load_state

# RESULTS_FILE = "scan_history.json"


# def load_history():
#     if os.path.exists(RESULTS_FILE):
#         with open(RESULTS_FILE, "r") as f:
#             return json.load(f)
#     return []


# def metric_card(title, value, icon):
#     st.markdown(f"""
#     <div class="metric-card">
#         <div style="font-size:28px">{icon}</div>
#         <div style="font-size:14px; color:#94a3b8">{title}</div>
#         <div class="glow" style="font-size:28px; font-weight:bold">{value}</div>
#     </div>
#     """, unsafe_allow_html=True)


# def render():

#     ##-----------
#     st.markdown("""
#     <style>
#     /* Background */
#     [data-testid="stAppViewContainer"] {
#         background: linear-gradient(180deg, #020617, #020617 60%, #020617);
#         color: #e2e8f0;
#     }

#     /* Section headers */
#     h1, h2, h3 {
#         color: #22d3ee;
#     }

#     /* Metric cards */
#     .metric-card {
#         background: rgba(15, 23, 42, 0.6);
#         border: 1px solid rgba(34, 211, 238, 0.2);
#         border-radius: 16px;
#         padding: 20px;
#         text-align: center;
#         box-shadow: 0 0 20px rgba(34, 211, 238, 0.05);
#     }

#     /* Scan cards */
#     .scan-card {
#         background: rgba(15, 23, 42, 0.7);
#         border: 1px solid rgba(99, 102, 241, 0.2);
#         border-radius: 14px;
#         padding: 16px;
#         margin-bottom: 10px;
#     }

#     /* Glow text */
#     .glow {
#         color: #22d3ee;
#         text-shadow: 0 0 8px #22d3ee;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     # st.markdown("# 🏠 Dashboard")
#     st.markdown("""
#     <h1 class="glow">✌︎㋡ Dashboard</h1>
#     <p style="color:#94a3b8">
#     Overview of autonomous security scanning activity
#     </p>
#     """, unsafe_allow_html=True)
#     # st.markdown("Overview of all autonomous security scanning activity.")
#     st.markdown("---")

#     history = load_history()
#     state = load_state()

#     col1, col2, col3, col4 = st.columns(4)
#     total_sites = len(history)
#     total_vulns = sum(h.get("vuln_count", 0) for h in history)
#     total_critical = sum(h.get("critical", 0) for h in history)
#     total_high = sum(h.get("high", 0) for h in history)

#     # with col1:
#     #     st.metric("🌐 Sites Scanned", total_sites)
#     # with col2:
#     #     st.metric("🐛 Total Vulns", total_vulns)
#     # with col3:
#     #     st.metric("🔴 Critical", total_critical)
#     # with col4:
#     #     st.metric("🟠 High", total_high)

#     with col1:
#         metric_card("Sites Scanned", total_sites, "🌐")

#     with col2:
#         metric_card("Total Vulns", total_vulns, "🐛")

#     with col3:
#         metric_card("Critical", total_critical, "🔴")

#     with col4:
#         metric_card("High", total_high, "🟠")


#     st.markdown("---")

#     if not history:
#         st.info("No scans yet. Run a Single Scan or start the Auto Crawler to begin.")
#         return

    # col_left, col_right = st.columns([3, 2])


    
#     with col_left:
#         st.markdown("### 🚀 Recent Scans")

#         for h in reversed(history[-10:]):
#             sev = []
#             if h.get("critical"): sev.append(f"🔴 {h['critical']}")
#             if h.get("high"): sev.append(f"🟠 {h['high']}")
#             if h.get("medium"): sev.append(f"🟡 {h['medium']}")
#             if h.get("low"): sev.append(f"🔵 {h['low']}")

#             sev_text = " | ".join(sev) if sev else "No vulnerabilities"

#             st.markdown(f"""
#             <div class="scan-card">
#                 <div style="font-size:16px; font-weight:bold; color:#38bdf8">
#                     {h['url']}
#                 </div>
#                 <div style="font-size:12px; color:#94a3b8">
#                     {h.get('timestamp', '')[:16]}
#                 </div>
#                 <div style="margin-top:6px; font-size:13px">
#                     {sev_text}
#                 </div>
#                 <div style="margin-top:6px; font-weight:bold">
#                     Total: {h.get('vuln_count', 0)}
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
#     #     st.markdown("### Recent Scans")
#     #     for h in reversed(history[-10:]):
#     #         sev_bar = ""
#     #         if h.get("critical", 0): sev_bar += f"🔴×{h['critical']} "
#     #         if h.get("high", 0): sev_bar += f"🟠×{h['high']} "
#     #         if h.get("medium", 0): sev_bar += f"🟡×{h['medium']} "
#     #         if h.get("low", 0): sev_bar += f"🔵×{h['low']} "

#     #         with st.container():
#     #             c1, c2 = st.columns([4, 1])
#     #             with c1:
#     #                 st.markdown(f"**`{h['url']}`**")
#     #                 st.caption(f"{h.get('timestamp', '')[:16]}  |  {sev_bar or 'No vulns'}")
#     #             with c2:
#     #                 st.markdown(f"**{h.get('vuln_count', 0)}** vulns")
#     #         st.divider()

#     with col_right:
#         st.markdown("### Severity Breakdown")
#         labels = ["Critical", "High", "Medium", "Low", "Info"]
#         values = [
#             sum(h.get("critical", 0) for h in history),
#             sum(h.get("high", 0) for h in history),
#             sum(h.get("medium", 0) for h in history),
#             sum(h.get("low", 0) for h in history),
#             sum(h.get("info", 0) for h in history),
#         ]
#         colors = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"]

#         fig = go.Figure(data=[go.Pie(
#             labels=labels,
#             values=values,
#             hole=0.5,
#             marker=dict(colors=colors),
#             textfont=dict(color="white"),
#         )])
#         fig.update_layout(
#             paper_bgcolor="rgba(0,0,0,0)",
#             plot_bgcolor="rgba(0,0,0,0)",
#             font=dict(color="white"),
#             showlegend=True,
#             margin=dict(t=0, b=0, l=0, r=0),
#             height=280,
#         )
#         st.plotly_chart(fig, use_container_width=True)

"""
Dashboard page — shows stats and recent scan history.
"""

import streamlit as st
import json
import os
from crawler_state import load_state
import plotly.graph_objects as go
import plotly.express as px
from streamlit_plotly_events import plotly_events

RESULTS_FILE = "scan_history.json"

def load_history():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return []


def render():
    history = load_history()

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d1f2d 0%,#0a1628 100%);
                border:1px solid #1e3a4a;border-radius:14px;padding:28px 32px;margin-bottom:24px;">
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">
        <div style="background:#0e4a5c;border:1px solid #06b6d4;border-radius:10px;
                    width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:20px;">
        🐛
        </div>
        <div>
        <div style="font-size:22px;font-weight:700;color:#f1f5f9;">Autonomous Bug Hunter</div>
        <div style="font-size:13px;color:#64748b;">AI-powered security reconnaissance</div>
        </div>
    </div>
    <p style="color:#94a3b8;font-size:14px;margin:0 0 20px 0;max-width:580px;">
        Multi-agent pipeline that autonomously discovers, explores, and analyzes websites for
        security vulnerabilities. Each scan runs through 7 specialized AI agents.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⊕  Launch New Scan  →", key="launch_scan"):
        st.session_state["page"] = "🔍 Single Scan"
        st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Stat cards ───────────────────────────────────────────────────────────
    total_sites = len(history)
    total_vulns = sum(h.get("vuln_count", 0) for h in history)
    total_critical = sum(h.get("critical", 0) for h in history)
    total_high = sum(h.get("high", 0) for h in history)
    completed = sum(1 for h in history)

    def stat_card(label, value, icon, border_color, value_color):
        return f"""
        <div style="background:#0d1117;border:1px solid {border_color};border-radius:12px;
                padding:20px 22px;height:100%;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:.08em;text-transform:uppercase;">
        {label}
        </div>
        <span style="font-size:18px;">{icon}</span>
        </div>
        <div style="font-size:32px;font-weight:700;color:{value_color};margin-top:10px;">{value}</div>
        </div>"""

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Total Scans", total_sites, "🌐", "#1e3a4a", "#06b6d4"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Vulnerabilities", total_vulns, "🛡️", "#3a2a0a", "#f97316"), unsafe_allow_html=True)
    with c3:
        ch_val = f"{total_critical} / {total_high}"
        st.markdown(stat_card("Critical / High", ch_val, "⚠️", "#3a0a0a", "#ef4444"), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card("Completed", completed, "✅", "#0a2a1a", "#10b981"), unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # ── Recent scans ─────────────────────────────────────────────────────────
    col_title, col_link = st.columns([6, 1])
    # with col_title:
    #     st.markdown("<h3 style='color:#f1f5f9;margin:0;'>Recent Scans</h3>", unsafe_allow_html=True)
    # with col_link:
    #     if st.button("View All →", key="view_all"):
    #         st.session_state["page"] = "📋 Reports"
    #         st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if not history:
        st.markdown("""
        <div style="background:#0d1117;border:1px solid #1e293b;border-radius:12px;
                    padding:32px;text-align:center;color:#64748b;">
        No scans yet. Click <strong style='color:#06b6d4;'>Launch New Scan</strong> to begin.
        </div>""", unsafe_allow_html=True)
        return

    sev_colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#3b82f6", "info": "#64748b"}

    for h in reversed(history[-10:]):
        badges_html = ""
        for sev in ["critical", "high", "medium", "low"]:
            cnt = h.get(sev, 0)
            if cnt:
                col = sev_colors[sev]
                badges_html += f"""<span style="background:{col}22;color:{col};border:1px solid {col}44;
                        border-radius:5px;padding:2px 9px;font-size:11px;font-weight:700;
                        margin-right:5px;text-transform:uppercase;">{sev}</span>"""

        vuln_count = h.get("vuln_count", 0)
        ts = h.get("timestamp", "")[:16].replace("T", "  ")
        url_display = h.get("url", "")

        if vuln_count == 0:
            vuln_html = """<span style="color:#10b981;font-size:13px;font-weight:600;">✓ Clean</span>"""
        else:
            vuln_html = f"""<span style="color:#94a3b8;font-size:13px;">{vuln_count} vulns</span>
            <span style="color:#06b6d4;font-size:16px;">→</span>"""

        st.markdown(f"""
                <div style="background:#0d1117;border:1px solid #1e293b;border-radius:10px;
                padding:16px 20px;margin-bottom:10px;display:flex;
                align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:12px;">
                <span style="width:9px;height:9px;border-radius:50%;background:#10b981;
                display:inline-block;flex-shrink:0;"></span>
                <div>
                <div style="font-size:14px;font-weight:600;color:#e2e8f0;">{url_display}</div>
                <div style="font-size:12px;color:#475569;margin-top:3px;">
                COMPLETED &nbsp;⏱ {ts}
                </div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;">
            {badges_html}
            {vuln_html}
            </div>
            
            </div>""", unsafe_allow_html=True)

    st.markdown("### ⛨ Vulnerability Insights")
    col_left, col_right = st.columns([3, 2])

    # with col_right:
    #     st.markdown("### Severity Breakdown")
    #     labels = ["Critical", "High", "Medium", "Low", "Info"]
    #     values = [
    #         sum(h.get("critical", 0) for h in history),
    #         sum(h.get("high", 0) for h in history),
    #         sum(h.get("medium", 0) for h in history),
    #         sum(h.get("low", 0) for h in history),
    #         sum(h.get("info", 0) for h in history),
    #     ]
    #     colors = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"]
    
    #     fig = go.Figure(data=[go.Pie(
    #         labels=labels,
    #         values=values,
    #         hole=0.5,
    #         marker=dict(colors=colors),
    #         textinfo="label+percent",
    #     )])

    #     fig.update_layout(
    #         paper_bgcolor="rgba(0,0,0,0)",
    #         plot_bgcolor="rgba(0,0,0,0)",
    #         font=dict(color="white"),
    #         showlegend=True,
    #         margin=dict(t=0, b=0, l=0, r=0),
    #         height=300,
    #     )

    #     selected_idx = st.session_state.get("selected_slice", None)
    #     selected_points = plotly_events(fig, click_event=True)

    #     if selected_points:
    #         selected_idx = selected_points[0]["pointNumber"]
    #         st.session_state["selected_slice"] = selected_idx
    
    #     pull = [0] * len(labels)
    #     if selected_idx is not None:
    #         pull[selected_idx] = 0.15

    #     fig.update_traces(pull=pull)
    #     # plotly_events(fig, click_event=True)
    
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

    with col_left:
        # st.markdown("### 🚀 Recent Scans")

        # for h in reversed(history[-10:]):
        #     sev = []
        #     if h.get("critical"): sev.append(f"🔴 {h['critical']}")
        #     if h.get("high"): sev.append(f"🟠 {h['high']}")
        #     if h.get("medium"): sev.append(f"🟡 {h['medium']}")
        #     if h.get("low"): sev.append(f"🔵 {h['low']}")

        #     sev_text = " | ".join(sev) if sev else "No vulnerabilities"

        #     st.markdown(f"""
        #     <div class="scan-card">
        #         <div style="font-size:16px; font-weight:bold; color:#38bdf8">
        #             {h['url']}
        #         </div>
        #         <div style="font-size:12px; color:#94a3b8">
        #             {h.get('timestamp', '')[:16]}
        #         </div>
        #         <div style="margin-top:6px; font-size:13px">
        #             {sev_text}
        #         </div>
        #         <div style="margin-top:6px; font-weight:bold">
        #             Total: {h.get('vuln_count', 0)}
        #         </div>
        #     </div>
        #     """, unsafe_allow_html=True)

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