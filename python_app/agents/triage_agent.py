"""
Vulnerability Triage Agent — powered by Groq (llama-3.3-70b)
Deduplicates, ranks, and filters false positives from vulnerability findings.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior security engineer performing vulnerability triage.
Your job is to take a raw list of findings, remove duplicates, filter false positives,
merge related issues, and produce a clean prioritized list.
Always respond with valid JSON only."""

TRIAGE_PROMPT = """Triage these vulnerability findings for {url}.

RAW FINDINGS:
{raw_vulns}

Tasks:
1. Remove exact duplicates
2. Merge similar vulnerabilities (e.g. two XSS findings in the same location)
3. Filter out likely false positives (mark reason)
4. Re-rank by actual exploitability and business impact
5. Assign final severity and priority

Return JSON:
{{
  "triaged_vulnerabilities": [
    {{
      "id": "VULN-001",
      "title": "...",
      "type": "...",
      "severity": "critical|high|medium|low|info",
      "priority": 1,
      "cvss_score": 7.5,
      "cwe_id": "CWE-79",
      "description": "...",
      "location": "...",
      "evidence": "...",
      "impact": "...",
      "reproduction_steps": "...",
      "remediation": "...",
      "merged_from": ["VULN-001", "VULN-002"],
      "false_positive": false,
      "false_positive_reason": null
    }}
  ],
  "summary": {{
    "total_raw": 5,
    "total_after_triage": 3,
    "duplicates_removed": 1,
    "false_positives_filtered": 1,
    "critical_count": 0,
    "high_count": 1,
    "medium_count": 1,
    "low_count": 1,
    "info_count": 0
  }}
}}"""


def triage_vulnerabilities(vuln_result: dict, url: str) -> dict:
    """
    Deduplicates and ranks vulnerability findings.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    vulnerabilities = vuln_result.get("vulnerabilities", [])

    if not vulnerabilities:
        return {
            "triaged_vulnerabilities": [],
            "summary": {
                "total_raw": 0,
                "total_after_triage": 0,
                "duplicates_removed": 0,
                "false_positives_filtered": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "info_count": 0,
            },
        }

    prompt = TRIAGE_PROMPT.format(
        url=url,
        raw_vulns=json.dumps(vulnerabilities, indent=2)[:5000],
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