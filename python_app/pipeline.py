"""
Main pipeline orchestrator.
Runs all 5 agents in sequence for a given URL.
"""

from agents.crawler_agent import crawl_url
from agents.recon_agent import run_recon
from agents.vuln_detection_agent import detect_vulnerabilities
from agents.triage_agent import triage_vulnerabilities
from agents.report_agent import generate_report


def run_pipeline(url: str, progress_callback=None) -> dict:
    """
    Full 5-agent pipeline for a single URL.
    progress_callback(stage, message, data=None) is called at each step.

    Returns:
    {
        "url": str,
        "crawl": dict,
        "recon": dict,
        "vulns_raw": dict,
        "triage": dict,
        "report": str,
        "error": str | None
    }
    """

    def emit(stage, message, data=None):
        if progress_callback:
            progress_callback(stage, message, data)

    result = {
        "url": url,
        "crawl": None,
        "recon": None,
        "vulns_raw": None,
        "triage": None,
        "report": None,
        "error": None,
    }

    try:
        # ── Stage 1: Crawl ──────────────────────────────────────────────
        emit("crawl", f"🌐 TinyFish crawling {url}...")

        def crawl_progress(event_type, message):
            emit("crawl", f"[{event_type}] {message}")

        crawl_data = crawl_url(url, progress_callback=crawl_progress)
        result["crawl"] = crawl_data

        if crawl_data.get("error"):
            emit("error", f"Crawl failed: {crawl_data['error']}")
            result["error"] = crawl_data["error"]
            return result

        emit("crawl", f"✅ Crawl complete. {len(crawl_data.get('links', []))} links, {len(crawl_data.get('forms', []))} forms found.")

        # ── Stage 2: Recon ──────────────────────────────────────────────
        emit("recon", "🔍 Recon agent analyzing attack surface...")
        recon_data = run_recon(crawl_data)
        result["recon"] = recon_data
        tech = ", ".join(recon_data.get("tech_stack", [])) or "Unknown"
        emit("recon", f"✅ Recon complete. Tech stack: {tech}")

        # ── Stage 3: Vulnerability Detection ───────────────────────────
        emit("detect", "🛡️ Vulnerability detection agent scanning...")
        vuln_data = detect_vulnerabilities(recon_data, crawl_data)
        result["vulns_raw"] = vuln_data
        raw_count = len(vuln_data.get("vulnerabilities", []))
        emit("detect", f"✅ Detection complete. {raw_count} raw findings.")

        # ── Stage 4: Triage ─────────────────────────────────────────────
        emit("triage", "⚖️ Triage agent deduplicating and ranking...")
        triage_data = triage_vulnerabilities(vuln_data, url)
        result["triage"] = triage_data
        final_count = len(triage_data.get("triaged_vulnerabilities", []))
        emit("triage", f"✅ Triage complete. {final_count} confirmed vulnerabilities.")

        # ── Stage 5: Report ─────────────────────────────────────────────
        emit("report", "📝 Report agent generating full report...")
        report_md = generate_report(url, recon_data, triage_data)
        result["report"] = report_md
        emit("report", "✅ Report generated.")

    except Exception as e:
        result["error"] = str(e)
        emit("error", f"Pipeline error: {str(e)}")

    return result