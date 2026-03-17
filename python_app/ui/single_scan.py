"""
Single Scan page — scan one URL through the full 5-agent pipeline with live output.
"""

import streamlit as st
import json
import os
import time
from pipeline import run_pipeline

RESULTS_FILE = "scan_history.json"
REPORTS_DIR = "reports"

os.makedirs(REPORTS_DIR, exist_ok=True)


def save_to_history(result: dict):
    history = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            history = json.load(f)

    summary = result.get("triage", {}).get("summary", {})
    history.append({
        "url": result["url"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "vuln_count": summary.get("total_after_triage", 0),
        "critical": summary.get("critical_count", 0),
        "high": summary.get("high_count", 0),
        "medium": summary.get("medium_count", 0),
        "low": summary.get("low_count", 0),
        "info": summary.get("info_count", 0),
        "report_file": f"{REPORTS_DIR}/{result['url'].replace('https://', '').replace('http://', '').replace('/', '_')}.md",
    })

    with open(RESULTS_FILE, "w") as f:
        json.dump(history, f, indent=2)


def save_report(result: dict):
    safe_name = result["url"].replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
    path = f"{REPORTS_DIR}/{safe_name}.md"
    with open(path, "w") as f:
        f.write(result.get("report", ""))
    return path


def severity_badge(sev):
    colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}
    return colors.get(sev, "⚪")


def render():
    st.markdown("# 🔍 Single Scan")
    st.markdown("Run the full 5-agent pipeline on a single target URL.")
    st.markdown("---")

    url = st.text_input(
        "Target URL",
        placeholder="https://example.com",
        help="Enter the full URL to scan",
    )

    if st.button("🚀 Start Scan", disabled=not url):
        if not url.startswith("http"):
            url = "https://" + url

        # ── Live pipeline UI ─────────────────────────────────────────────
        progress_bar = st.progress(0)
        stage_progress = {"crawl": 0.15, "recon": 0.35, "detect": 0.60, "triage": 0.80, "report": 1.0}
        stage_icons = {"crawl": "🌐", "recon": "🔍", "detect": "🛡️", "triage": "⚖️", "report": "📝", "error": "❌"}

        # Live browser iframe — shown as soon as TinyFish provides stream URL
        browser_placeholder = st.empty()
        log_area = st.empty()
        logs = []

        def progress_callback(stage, message, data=None):
            icon = stage_icons.get(stage, "•")
            logs.append(f"{icon} **[{stage.upper()}]** {message}")
            log_area.markdown("\n\n".join(logs[-20:]))
            if stage in stage_progress:
                progress_bar.progress(stage_progress[stage])
            # Render live iframe as soon as we get the streaming URL
            if "Live browser:" in message:
                stream_url = message.split("Live browser:")[-1].strip()
                browser_placeholder.markdown(f"""
<div style="border:2px solid #06b6d4;border-radius:10px;overflow:hidden;margin:16px 0;">
    <div style="background:#0d1117;padding:6px 14px;display:flex;align-items:center;gap:8px;border-bottom:1px solid #21262d;">
        <span style="width:9px;height:9px;border-radius:50%;background:#ef4444;display:inline-block;"></span>
        <span style="width:9px;height:9px;border-radius:50%;background:#eab308;display:inline-block;"></span>
        <span style="width:9px;height:9px;border-radius:50%;background:#10b981;display:inline-block;"></span>
        <span style="font-family:monospace;font-size:11px;color:#06b6d4;margin-left:8px;">🤖 TinyFish Agent &nbsp;·&nbsp; {url}</span>
        <span style="margin-left:auto;font-size:10px;color:#ef4444;font-weight:bold;">● LIVE</span>
    </div>
    <iframe src="{stream_url}" width="100%" height="520" style="border:none;display:block;background:#fff;" allow="*"></iframe>
</div>
""", unsafe_allow_html=True)

        with st.spinner("Running pipeline..."):
            result = run_pipeline(url, progress_callback=progress_callback)

        progress_bar.progress(1.0)

        if result.get("error"):
            st.error(f"Pipeline failed: {result['error']}")
            return

        save_to_history(result)
        report_path = save_report(result)

        st.success("✅ Scan complete!")
        st.markdown("---")

        # ── Results tabs ─────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Vulnerabilities", "📝 Report", "🔍 Recon", "🌐 Crawl Data"])

        with tab1:
            vulns = result.get("triage", {}).get("triaged_vulnerabilities", [])
            summary = result.get("triage", {}).get("summary", {})

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔴 Critical", summary.get("critical_count", 0))
            c2.metric("🟠 High", summary.get("high_count", 0))
            c3.metric("🟡 Medium", summary.get("medium_count", 0))
            c4.metric("🔵 Low", summary.get("low_count", 0))

            st.markdown("---")

            if not vulns:
                st.info("No confirmed vulnerabilities found.")
            else:
                for v in vulns:
                    sev = v.get("severity", "info")
                    icon = severity_badge(sev)
                    with st.expander(f"{icon} [{sev.upper()}] {v.get('title', 'Untitled')} — CVSS {v.get('cvss_score', 'N/A')}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**Type:** `{v.get('type', 'unknown')}`")
                            st.markdown(f"**CWE:** `{v.get('cwe_id', 'N/A')}`")
                            st.markdown(f"**Location:** `{v.get('location', 'N/A')}`")
                        with col_b:
                            st.markdown(f"**CVSS Score:** `{v.get('cvss_score', 'N/A')}`")
                            st.markdown(f"**Priority:** `{v.get('priority', 'N/A')}`")

                        st.markdown("**Description:**")
                        st.info(v.get("description", ""))

                        st.markdown("**Evidence:**")
                        st.code(v.get("evidence", "No evidence"), language="text")

                        st.markdown("**Impact:**")
                        st.warning(v.get("impact", ""))

                        st.markdown("**Reproduction Steps:**")
                        st.markdown(v.get("reproduction_steps", ""))

                        st.markdown("**Remediation:**")
                        st.success(v.get("remediation", ""))

        with tab2:
            report_md = result.get("report", "No report generated.")
            st.markdown(report_md)
            st.download_button(
                "⬇️ Download Report (.md)",
                data=report_md,
                file_name=f"report_{url.replace('https://', '').replace('/', '_')}.md",
                mime="text/markdown",
            )

        with tab3:
            recon = result.get("recon", {})
            if recon:
                st.json(recon)
            else:
                st.info("No recon data available.")

        with tab4:
            crawl = result.get("crawl", {})
            if crawl:
                if crawl.get("streaming_url"):
                    st.markdown("**🔴 Browser Replay** *(valid 24h)*")
                    st.markdown(f"""
<iframe src="{crawl['streaming_url']}" width="100%" height="480"
    style="border:2px solid #06b6d4;border-radius:8px;display:block;" allow="*"></iframe>
""", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Links found:** {len(crawl.get('links', []))}")
                    st.markdown(f"**Forms found:** {len(crawl.get('forms', []))}")
                    st.markdown(f"**Scripts found:** {len(crawl.get('scripts', []))}")
                with col2:
                    st.markdown(f"**Tech stack:** {', '.join(crawl.get('tech_stack', [])) or 'Unknown'}")
                    st.markdown(f"**API endpoints:** {len(crawl.get('api_endpoints', []))}")
                    st.markdown(f"**Exposed secrets:** {len(crawl.get('exposed_secrets', []))}")

                if crawl.get("links"):
                    with st.expander("🔗 Links Found"):
                        for l in crawl["links"][:30]:
                            st.markdown(f"- `{l}`")
            else:
                st.info("No crawl data available.")