"""
Report Generation Agent — powered by Groq (llama-3.3-70b)
Generates a professional bug bounty / penetration test report in Markdown.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SYSTEM_PROMPT = """You are a professional security consultant writing a bug bounty report.
Write clear, professional, well-structured Markdown. Use tables, headers, and code blocks where appropriate.
Be thorough but concise."""

REPORT_PROMPT = """Generate a professional bug bounty security report for the following scan.

TARGET: {url}
SCAN DATE: {date}

TECH STACK: {tech_stack}
ATTACK SURFACE NOTES: {attack_surface_notes}

TRIAGED VULNERABILITIES:
{vulnerabilities}

TRIAGE SUMMARY:
{summary}

Write a full Markdown report with these sections:
1. Executive Summary (2-3 sentences, non-technical)
2. Scope & Target Information
3. Methodology (briefly describe the 5-agent pipeline used)
4. Vulnerability Summary Table (severity, title, CVSS, CWE)
5. Detailed Findings (one section per vulnerability with: description, impact, evidence, steps to reproduce, remediation)
6. Risk Matrix
7. Recommendations (top 5 prioritized action items)
8. Conclusion

Use professional bug bounty report language."""


def generate_report(
    url: str,
    recon_result: dict,
    triage_result: dict,
) -> str:
    """
    Generates a full markdown bug bounty report.
    Returns markdown string.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    vulns = triage_result.get("triaged_vulnerabilities", [])
    summary = triage_result.get("summary", {})
    tech_stack = recon_result.get("tech_stack", [])
    attack_surface = recon_result.get("attack_surface", {})

    prompt = REPORT_PROMPT.format(
        url=url,
        date=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        tech_stack=", ".join(tech_stack) if tech_stack else "Unknown",
        attack_surface_notes=json.dumps(attack_surface, indent=2)[:1500],
        vulnerabilities=json.dumps(vulns, indent=2)[:4000],
        summary=json.dumps(summary, indent=2),
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    return response.choices[0].message.content