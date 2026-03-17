"""
Auto Crawler page — autonomous continuous crawling with pause/resume/stop.
Shows live activity feed, queue, and real-time vuln discoveries.
"""

import streamlit as st
import json
import os
import time
import threading
from pipeline import run_pipeline
from crawler_state import load_state, save_state, default_state, add_to_queue, pop_next, mark_visited, add_scan_result

HISTORY_FILE = "scan_history.json"
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

DEFAULT_SEEDS = [
    "https://httpbin.org",
    "https://jsonplaceholder.typicode.com",
    "https://example.com",
]

# ── Global crawler thread control ────────────────────────────────────────────
_crawler_thread = None
_stop_event = threading.Event()
_pause_event = threading.Event()


def save_full_result(result: dict):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
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
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    # Save report
    safe = result["url"].replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
    with open(f"{REPORTS_DIR}/{safe}.md", "w") as f:
        f.write(result.get("report", ""))


def crawler_loop(state_ref: dict, activity_log: list, stop_evt: threading.Event, pause_evt: threading.Event):
    """Runs in a background thread. Processes one URL at a time."""
    while not stop_evt.is_set():
        if pause_evt.is_set():
            time.sleep(0.5)
            continue

        state = load_state()
        if state["status"] == "stopped" or stop_evt.is_set():
            break

        if not state["queue"]:
            activity_log.append({"type": "info", "msg": "Queue empty. Waiting...", "time": time.strftime("%H:%M:%S")})
            time.sleep(3)
            continue

        url, state = pop_next(state)
        state["status"] = "running"
        save_state(state)

        activity_log.append({"type": "navigate", "msg": f"Navigating to {url}", "time": time.strftime("%H:%M:%S")})

        def progress_cb(stage, message, data=None):
            icon_map = {"crawl": "🌐", "recon": "🔍", "detect": "🛡️", "triage": "⚖️", "report": "📝", "error": "❌"}
            activity_log.append({
                "type": stage,
                "msg": f"{icon_map.get(stage, '•')} [{stage.upper()}] {message}",
                "time": time.strftime("%H:%M:%S"),
            })
            # Capture streaming URL for live browser embed
            if "[STREAMING_URL]" in message or "Live browser:" in message:
                # Extract URL from message like "[STREAMING_URL] Live browser: https://..."
                parts = message.split("Live browser: ")
                if len(parts) > 1:
                    activity_log.append({"__stream_url__": parts[1].strip()})
            # Keep log bounded
            if len(activity_log) > 300:
                activity_log.pop(0)

        try:
            result = run_pipeline(url, progress_callback=progress_cb)
        except Exception as e:
            activity_log.append({"type": "error", "msg": f"❌ Error on {url}: {e}", "time": time.strftime("%H:%M:%S")})
            state = load_state()
            state = mark_visited(state, url)
            save_state(state)
            continue

        if not result.get("error"):
            save_full_result(result)
            state = load_state()
            state = mark_visited(state, url)
            state = add_scan_result(state, result)

            # Add newly discovered links to queue
            new_links = result.get("crawl", {}).get("links", [])
            if new_links:
                state = add_to_queue(state, new_links[:5])
                activity_log.append({"type": "discover", "msg": f"🔗 Queued {min(5, len(new_links))} new links from {url}", "time": time.strftime("%H:%M:%S")})

            vuln_count = len(result.get("triage", {}).get("triaged_vulnerabilities", []))
            activity_log.append({"type": "complete", "msg": f"✅ Done: {url} — {vuln_count} vulns found", "time": time.strftime("%H:%M:%S")})
            save_state(state)
        else:
            state = load_state()
            state = mark_visited(state, url)
            save_state(state)
            activity_log.append({"type": "error", "msg": f"❌ Failed: {url} — {result['error']}", "time": time.strftime("%H:%M:%S")})

        time.sleep(2)

    state = load_state()
    state["status"] = "idle"
    state["current_url"] = None
    save_state(state)


def render():
    global _crawler_thread, _stop_event, _pause_event

    st.markdown("# 🕷️ Auto Crawler")
    st.markdown("Autonomous web security crawler — runs continuously in the background.")
    st.markdown("---")

    # Initialize session state
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []
    if "crawler_running" not in st.session_state:
        st.session_state.crawler_running = False
    if "crawler_paused" not in st.session_state:
        st.session_state.crawler_paused = False
    if "seeds" not in st.session_state:
        st.session_state.seeds = list(DEFAULT_SEEDS)
    if "live_stream_url" not in st.session_state:
        st.session_state.live_stream_url = None

    state = load_state()

    # ── Status badge ─────────────────────────────────────────────────────────
    status = state.get("status", "idle")
    status_colors = {"running": "🟢", "paused": "🟡", "idle": "⚫", "stopped": "🔴"}
    col_s, col_b1, col_b2, col_b3 = st.columns([3, 1, 1, 1])
    with col_s:
        st.markdown(f"**Status:** {status_colors.get(status, '⚫')} `{status.upper()}`")
        if state.get("current_url"):
            st.caption(f"Currently scanning: `{state['current_url']}`")

    with col_b1:
        if not st.session_state.crawler_running:
            if st.button("▶️ Start", use_container_width=True):
                new_state = load_state()
                if new_state["status"] == "idle" or not new_state["queue"]:
                    new_state = default_state()
                    new_state["queue"] = list(st.session_state.seeds)
                    new_state["status"] = "running"
                    save_state(new_state)
                else:
                    new_state["status"] = "running"
                    save_state(new_state)

                _stop_event = threading.Event()
                _pause_event = threading.Event()
                st.session_state.activity_log = []
                _crawler_thread = threading.Thread(
                    target=crawler_loop,
                    args=(new_state, st.session_state.activity_log, _stop_event, _pause_event),
                    daemon=True,
                )
                _crawler_thread.start()
                st.session_state.crawler_running = True
                st.session_state.crawler_paused = False
                st.rerun()

    with col_b2:
        if st.session_state.crawler_running and not st.session_state.crawler_paused:
            if st.button("⏸️ Pause", use_container_width=True):
                _pause_event.set()
                s = load_state()
                s["status"] = "paused"
                save_state(s)
                st.session_state.crawler_paused = True
                st.rerun()
        elif st.session_state.crawler_running and st.session_state.crawler_paused:
            if st.button("▶️ Resume", use_container_width=True):
                _pause_event.clear()
                s = load_state()
                s["status"] = "running"
                save_state(s)
                st.session_state.crawler_paused = False
                st.rerun()

    with col_b3:
        if st.session_state.crawler_running:
            if st.button("⏹️ Stop", use_container_width=True):
                _stop_event.set()
                s = load_state()
                s["status"] = "stopped"
                save_state(s)
                st.session_state.crawler_running = False
                st.session_state.crawler_paused = False
                st.rerun()

    st.markdown("---")

    # ── Stats ─────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("🌐 Sites Scanned", state.get("total_sites", 0))
    c2.metric("🐛 Vulns Found", state.get("total_vulns", 0))
    c3.metric("🔴 Critical", state.get("total_critical", 0))

    st.markdown("---")

    # ── LIVE BROWSER VIEW (TinyFish streaming iframe) ─────────────────────────
    streaming_url = state.get("streaming_url")
    if streaming_url and st.session_state.crawler_running:
        st.markdown("### 🔴 Live Browser — Agent in Action")
        st.caption("Watching TinyFish navigate the web in real-time")
        iframe_html = f"""
        <div style="border:2px solid #06b6d4;border-radius:10px;overflow:hidden;position:relative;">
            <div style="background:#0d1117;padding:6px 12px;display:flex;align-items:center;gap:8px;border-bottom:1px solid #21262d;">
                <span style="width:10px;height:10px;border-radius:50%;background:#ef4444;display:inline-block;"></span>
                <span style="width:10px;height:10px;border-radius:50%;background:#eab308;display:inline-block;"></span>
                <span style="width:10px;height:10px;border-radius:50%;background:#10b981;display:inline-block;"></span>
                <span style="font-family:monospace;font-size:11px;color:#06b6d4;margin-left:8px;">
                    🤖 TinyFish Agent &nbsp;·&nbsp; {state.get('current_url', 'browsing...')}
                </span>
                <span style="margin-left:auto;font-size:10px;color:#374151;">LIVE</span>
                <span style="width:8px;height:8px;border-radius:50%;background:#ef4444;display:inline-block;animation:pulse 1s infinite;"></span>
            </div>
            <iframe src="{streaming_url}" width="100%" height="540"
                style="border:none;display:block;background:#fff;"
                allow="*">
            </iframe>
        </div>
        <style>@keyframes pulse {{ 0%,100%{{opacity:0.3}} 50%{{opacity:1}} }}</style>
        """
        st.markdown(iframe_html, unsafe_allow_html=True)
        st.markdown("---")
    elif st.session_state.crawler_running and not streaming_url:
        st.info("⏳ Waiting for TinyFish to start a browser session...")
        st.markdown("---")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Seed URLs config (only when not running)
        if not st.session_state.crawler_running:
            st.markdown("### 🌱 Seed URLs")
            seeds_text = st.text_area(
                "One URL per line",
                value="\n".join(st.session_state.seeds),
                height=140,
                label_visibility="collapsed",
            )
            st.session_state.seeds = [u.strip() for u in seeds_text.split("\n") if u.strip()]

        # Queue
        st.markdown("### 📋 URL Queue")
        queue = state.get("queue", [])
        visited = state.get("visited", [])
        current = state.get("current_url", "")

        st.caption(f"{len(visited)} visited · {len(queue)} queued")

        for u in visited[-5:]:
            st.markdown(f"<div style='font-family:monospace;font-size:11px;color:#10b981;padding:2px 6px;'>✅ {u}</div>", unsafe_allow_html=True)

        if current:
            st.markdown(f"<div style='font-family:monospace;font-size:11px;color:#06b6d4;padding:2px 6px;'>⟳ {current}</div>", unsafe_allow_html=True)

        for u in queue[:8]:
            st.markdown(f"<div style='font-family:monospace;font-size:11px;color:#475569;padding:2px 6px;'>🕐 {u}</div>", unsafe_allow_html=True)

        if len(queue) > 8:
            st.caption(f"...and {len(queue) - 8} more")

    with col_right:
        st.markdown("### 📡 Live Activity")
        log = [e for e in st.session_state.activity_log if "msg" in e]

        if not log:
            st.info("No activity yet. Start the crawler to see live events.")
        else:
            type_colors = {
                "navigate": "#06b6d4",
                "crawl": "#06b6d4",
                "recon": "#a855f7",
                "detect": "#f97316",
                "triage": "#eab308",
                "report": "#94a3b8",
                "discover": "#10b981",
                "complete": "#10b981",
                "error": "#ef4444",
                "info": "#475569",
            }
            log_html = "<div style='font-family:monospace;font-size:11px;height:440px;overflow-y:auto;background:#0d1117;padding:12px;border-radius:8px;border:1px solid #21262d;'>"
            for entry in reversed(log[-80:]):
                color = type_colors.get(entry.get("type", "info"), "#475569")
                t = entry.get("time", "")
                msg = entry.get("msg", "").replace("<", "&lt;").replace(">", "&gt;")
                log_html += f"<div style='color:{color};padding:1px 0;'><span style='color:#374151;'>[{t}]</span> {msg}</div>"
            log_html += "</div>"
            st.markdown(log_html, unsafe_allow_html=True)

    # Auto-refresh when running
    if st.session_state.crawler_running and not st.session_state.crawler_paused:
        time.sleep(3)
        st.rerun()