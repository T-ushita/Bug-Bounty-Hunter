"""
Recon Agent — powered by Groq (llama-3.3-70b)
Takes raw crawl data and extracts structured attack surface information.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert web application security researcher performing reconnaissance.
Your job is to analyze raw crawl data from a website and extract a structured attack surface profile.
Always respond with valid JSON only — no markdown, no explanation."""

RECON_PROMPT = """Analyze this crawl data from {url} and produce a detailed recon profile.

CRAWL DATA:
HTML Snippet: {html_snippet}
Links Found: {links}
Forms: {forms}
Scripts: {scripts}
API Endpoints: {api_endpoints}
Header Hints: {headers_hints}
Tech Stack: {tech_stack}
Exposed Secrets: {exposed_secrets}
Cookies: {cookies}

Return JSON with this structure:
{{
  "url": "...",
  "tech_stack": ["framework/library names"],
  "attack_surface": {{
    "forms": [{{ "action": "...", "method": "...", "inputs": ["..."], "risk": "high/medium/low" }}],
    "endpoints": ["url paths"],
    "js_libraries": [{{ "name": "...", "version": "...", "cve_prone": true/false }}],
    "auth_mechanisms": ["cookie-based", "JWT", "basic-auth", etc],
    "input_vectors": ["query params", "form fields", "JSON body", etc],
    "interesting_comments": ["any comments found in HTML/JS"],
    "exposed_data": ["any sensitive looking data"]
  }},
  "security_observations": [
    "observation 1",
    "observation 2"
  ],
  "severity_hints": {{
    "has_login_form": true/false,
    "has_file_upload": true/false,
    "has_admin_panel": true/false,
    "has_api": true/false,
    "has_external_scripts": true/false
  }}
}}"""


def run_recon(crawl_result: dict) -> dict:
    """
    Takes crawl data and produces structured recon profile.
    Returns recon dict.
    """

    prompt = RECON_PROMPT.format(
        url=crawl_result.get("url", ""),
        html_snippet=str(crawl_result.get("html_snippet", ""))[:4000],
        links=json.dumps(crawl_result.get("links", [])[:30]),
        forms=json.dumps(crawl_result.get("forms", [])),
        scripts=json.dumps(crawl_result.get("scripts", [])[:20]),
        api_endpoints=json.dumps(crawl_result.get("api_endpoints", [])),
        headers_hints=json.dumps(crawl_result.get("headers_hints", [])),
        tech_stack=json.dumps(crawl_result.get("tech_stack", [])),
        exposed_secrets=json.dumps(crawl_result.get("exposed_secrets", [])),
        cookies=json.dumps(crawl_result.get("cookies", [])),
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)