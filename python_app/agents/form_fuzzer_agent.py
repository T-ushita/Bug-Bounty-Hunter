"""
Form Fuzzer Agent — powered by TinyFish Web Agent API
Submits forms with XSS and SQLi fuzzing payloads and observes responses.
"""

import os
import json
from tinyfish import TinyFish
from dotenv import load_dotenv

load_dotenv()

# Common fuzzing payloads
XSS_PAYLOADS = [
    '<script>alert("XSS")</script>',
    '"><img src=x onerror=alert(1)>',
    "javascript:alert(1)",
]

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "1; DROP TABLE users--",
]


def fuzz_forms(crawl_data: dict, progress_callback=None) -> dict:
    """
    For each form discovered in crawl_data, instruct TinyFish to:
    1. Navigate to the page
    2. Fill each input field with an XSS and SQLi payload
    3. Submit the form and observe the response for reflections or errors

    Returns structured findings dict.
    """

    def emit(msg, sub=""):
        if progress_callback:
            progress_callback("fuzz", msg, sub)

    url = crawl_data.get("url", "")
    forms = crawl_data.get("forms", [])

    result = {
        "forms_tested": 0,
        "xss_findings": [],
        "sqli_findings": [],
        "errors": [],
    }

    if not forms:
        emit("No forms found to fuzz — skipping form fuzzing")
        return result

    client = TinyFish(api_key=os.getenv("TINYFISH_API_KEY"))

    emit(f"Found {len(forms)} form(s) — starting payload fuzzing", url)

    for i, form in enumerate(forms[:3]):  # limit to first 3 forms
        action = form.get("action", url)
        method = form.get("method", "POST").upper()
        inputs = form.get("inputs", form.get("fields", []))

        emit(f"Fuzzing form {i+1}/{min(len(forms), 3)}: {action} [{method}]", str(inputs))

        for payload_type, payloads in [("XSS", XSS_PAYLOADS), ("SQLi", SQLI_PAYLOADS)]:
            for payload in payloads[:2]:  # test 2 payloads per type per form
                goal = f"""
You are a security tester performing authorized form fuzzing.

Navigate to: {url}
Find the form with action "{action}" (method: {method}).
Fill ALL text input fields with this exact payload: {payload}
Submit the form.
Observe the response carefully:
- Does the payload appear reflected in the response HTML? (XSS indicator)
- Are there database error messages? (SQLi indicator)
- Is there any unusual error or behavior?

Report your findings as JSON:
{{
  "payload": "{payload}",
  "payload_type": "{payload_type}",
  "form_action": "{action}",
  "reflected": true/false,
  "error_message_found": true/false,
  "response_snippet": "first 500 chars of response...",
  "vulnerable": true/false,
  "notes": "explanation"
}}
"""
                try:
                    fuzz_result = {"payload": payload, "payload_type": payload_type, "form_action": action}
                    with client.agent.stream(url=url, goal=goal) as stream:
                        for event in stream:
                            etype = event.get("type", "")

                            if etype == "STREAMING_URL":
                                stream_url = event.get("streamingUrl")
                                if progress_callback:
                                    progress_callback("STREAMING_URL", f"Live browser: {stream_url}")

                            elif etype == "PROGRESS":
                                purpose = event.get("purpose", "")
                                if purpose:
                                    emit(f"[{payload_type}] {purpose}", action)

                            elif etype == "COMPLETE" and event.get("status") == "COMPLETED":
                                raw = event.get("resultJson", {})
                                fuzz_result.update(raw)
                                if raw.get("vulnerable"):
                                    finding = {
                                        "form_action": action,
                                        "payload": payload,
                                        "payload_type": payload_type,
                                        "response_snippet": raw.get("response_snippet", ""),
                                        "notes": raw.get("notes", ""),
                                    }
                                    if payload_type == "XSS":
                                        result["xss_findings"].append(finding)
                                        emit(f"⚠️ Potential XSS found in form: {action}", payload)
                                    else:
                                        result["sqli_findings"].append(finding)
                                        emit(f"⚠️ Potential SQLi found in form: {action}", payload)
                                else:
                                    emit(f"[{payload_type}] No reflection detected", payload)

                except Exception as e:
                    result["errors"].append(str(e))
                    emit(f"Error fuzzing form: {e}", action)

        result["forms_tested"] += 1

    total = len(result["xss_findings"]) + len(result["sqli_findings"])
    emit(f"Form fuzzing complete — {result['forms_tested']} forms tested, {total} potential findings", "")
    return result