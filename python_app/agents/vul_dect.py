"""
Vulnerability Detection Agent — powered by Groq (llama-3.3-70b)
Analyzes recon output and identifies specific vulnerabilities with evidence.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior bug bounty hunter and penetration tester.
Your job is to analyze reconnaissance data and identify real, exploitable vulnerabilities.
Be specific, evidence-based, and realistic. Do NOT hallucinate vulnerabilities without evidence.
Always respond with valid JSON only."""

DETECTION_PROMPT = """Based on this recon data for {url}, identify all security vulnerabilities.

RECON DATA:
{recon_data}

ORIGINAL HTML SNIPPET:
{html_snippet}

For each vulnerability found, provide:
- Only include findings with actual evidence from the recon data
- Be specific about WHERE the vulnerability is
- Assign realistic CVSS scores (0.0-10.0)

Return JSON:
{{
  "vulnerabilities": [
    {{
      "id": "VULN-001",
      "title": "Descriptive title",
      "type": "xss|sql_injection|exposed_api_key|open_redirect|insecure_form|missing_headers|information_disclosure|outdated_library|cors_misconfiguration|sensitive_data_exposure|csrf|idor|other",
      "severity": "critical|high|medium|low|info",
      "cvss_score": 7.5,
      "cwe_id": "CWE-79",
      "description": "Detailed description of the vulnerability",
      "location": "Where exactly it was found",
      "evidence": "Exact evidence from the crawl data",
      "impact": "What an attacker could do",
      "reproduction_steps": "Step-by-step how to reproduce",
      "remediation": "How to fix it"
    }}
  ],
  "total_found": 3,
  "scan_notes": "Any overall observations"
}}"""


def detect_vulnerabilities(recon_result: dict, crawl_result: dict) -> dict:
    """
    Takes recon data and returns a list of identified vulnerabilities.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = DETECTION_PROMPT.format(
        url=recon_result.get("url", crawl_result.get("url", "")),
        recon_data=json.dumps(recon_result, indent=2)[:4000],
        html_snippet=str(crawl_result.get("html_snippet", ""))[:2000],
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)