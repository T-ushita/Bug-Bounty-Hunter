"""
Main pipeline orchestrator.
Runs all 7 agents in sequence for a given URL.
Stages: crawl → form_fuzz → auth_crawl → recon → detect → triage → report
"""

from agents.crawler_agent import crawl_url
from agents.form_fuzzer_agent import fuzz_forms
from agents.auth_crawler_agent import crawl_authenticated
from agents.recon_agent import run_recon
from agents.vul_dect import detect_vulnerabilities
from agents.triage_agent import triage_vulnerabilities
from agents.report_agent import generate_report

def run_pipeline(
    url: str,
    progress_callback=None,
    auth_cookies: dict = None,
    auth_header: str = None,
    auth_username: str = None,
    auth_password: str = None,
    enable_form_fuzzing: bool = True,
    enable_auth_crawl: bool = False,   # off by default unless credentials provided
) -> dict:
    """
    Full 7-agent pipeline for a single URL.
    progress_callback(stage, message, data=None) is called at each step.

    Returns:
    {
        "url": str,
        "crawl": dict,
        "fuzz": dict,
        "auth_crawl": dict | None,
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
        "fuzz": None,
        "auth_crawl": None,
        "recon": None,
        "vulns_raw": None,
        "triage": None,
        "report": None,
        "error": None,
    }

    try:
        # ── Stage 1: Crawl ──────────────────────────────────────────────────
        emit("crawl", f"TinyFish crawling {url}...")

        def crawl_progress(event_type, message):
            emit("crawl", f"[{event_type}] {message}")

        crawl_data = crawl_url(url, progress_callback=crawl_progress)
        result["crawl"] = crawl_data

        if crawl_data.get("error"):
            emit("error", f"Crawl failed: {crawl_data['error']}")
            result["error"] = crawl_data["error"]
            return result

        links_n = len(crawl_data.get("links", []))
        forms_n = len(crawl_data.get("forms", []))
        emit("crawl", f"Crawl complete — {links_n} links, {forms_n} forms found")

        # ── Stage 2: Form Fuzzing (XSS + SQLi) ─────────────────────────────
        if enable_form_fuzzing and forms_n > 0:
            emit("fuzz", f"Starting form fuzzing on {forms_n} form(s) with XSS & SQLi payloads...")

            def fuzz_progress(event_type, message, sub=None):
                emit("fuzz", message)

            fuzz_data = fuzz_forms(crawl_data, progress_callback=fuzz_progress)
            result["fuzz"] = fuzz_data

            xss_n = len(fuzz_data.get("xss_findings", []))
            sqli_n = len(fuzz_data.get("sqli_findings", []))
            emit("fuzz", f"Form fuzzing complete — {xss_n} XSS, {sqli_n} SQLi potential findings")
        else:
            if forms_n == 0:
                emit("fuzz", "No forms found — skipping form fuzzing")
            result["fuzz"] = {"forms_tested": 0, "xss_findings": [], "sqli_findings": [], "errors": []}

        # ── Stage 3: Authenticated Crawl (optional) ─────────────────────────
        has_auth = any([auth_cookies, auth_header, auth_username])
        if enable_auth_crawl or has_auth:
            emit("auth", "Starting authenticated crawl with TinyFish...")

            def auth_progress(event_type, message, sub=None):
                emit("auth", message)

            auth_data = crawl_authenticated(
                url,
                cookies=auth_cookies,
                auth_header=auth_header,
                username=auth_username,
                password=auth_password,
                progress_callback=auth_progress,
            )
            result["auth_crawl"] = auth_data

            if auth_data.get("authenticated"):
                protected_n = len(auth_data.get("protected_links", []))
                admin_n = len(auth_data.get("admin_panels", []))
                emit("auth", f"Auth crawl complete — {protected_n} protected pages, {admin_n} admin panels found")
                # Merge authenticated links into crawl_data for downstream agents
                crawl_data["links"] = list(set(
                    crawl_data.get("links", []) + auth_data.get("protected_links", [])
                ))
                crawl_data["admin_panels"] = auth_data.get("admin_panels", [])
                crawl_data["idor_hints"] = auth_data.get("session_data", {}).get("idor_hints", [])
            else:
                emit("auth", "Auth crawl returned unauthenticated results")
        else:
            emit("auth", "No auth credentials provided — skipping authenticated crawl")

        # ── Stage 4: Recon ──────────────────────────────────────────────────
        emit("recon", "Recon agent analyzing attack surface...")
        recon_data = run_recon(crawl_data)
        result["recon"] = recon_data
        tech = ", ".join(recon_data.get("tech_stack", [])) or "Unknown"
        emit("recon", f"Recon complete — tech stack: {tech}")

        # ── Stage 5: Vulnerability Detection ───────────────────────────────
        emit("detect", "Vulnerability detection agent scanning — checking headers, forms, scripts, APIs...")

        # Enrich vuln detection with fuzz findings
        enriched_crawl = dict(crawl_data)
        if result["fuzz"]:
            enriched_crawl["fuzz_xss"] = result["fuzz"].get("xss_findings", [])
            enriched_crawl["fuzz_sqli"] = result["fuzz"].get("sqli_findings", [])

        vuln_data = detect_vulnerabilities(recon_data, enriched_crawl)
        result["vulns_raw"] = vuln_data
        raw_count = len(vuln_data.get("vulnerabilities", []))
        emit("detect", f"Detection complete — {raw_count} raw findings")

        # ── Stage 6: Triage ─────────────────────────────────────────────────
        emit("triage", "Triage agent deduplicating and ranking...")
        triage_data = triage_vulnerabilities(vuln_data, url)
        result["triage"] = triage_data
        final_count = len(triage_data.get("triaged_vulnerabilities", []))
        emit("triage", f"Triage complete — {final_count} confirmed vulnerabilities")

        # ── Stage 7: Report ─────────────────────────────────────────────────
        emit("report", f"Generating report for {url}...")
        report_md = generate_report(url, recon_data, triage_data)
        result["report"] = report_md
        emit("report", "Report generated")

    except Exception as e:
        result["error"] = str(e)
        emit("error", f"Pipeline error: {str(e)}")

    return result