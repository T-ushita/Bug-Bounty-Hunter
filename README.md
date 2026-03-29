# BugHunter AI - Python App

Autonomous web vulnerability scanner powered by **TinyFish Web Agent** (real browser) + **Groq Llama-3.3-70b** (AI analysis). Runs a 7-stage pipeline that crawls, fuzzes, recons, detects, triages, and reports security findings — with a live Streamlit UI.

---

## Folder Structure

```
python_app/
├── app.py                    # Streamlit entry point & navigation
├── pipeline.py               # 7-stage pipeline orchestrator
├── crawler_state.py          # Persistent state manager for auto crawler
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── crawler_agent.py      # Stage 1 — TinyFish real-browser crawl
│   ├── form_fuzzer_agent.py  # Stage 2 — XSS & SQLi form fuzzing
│   ├── auth_crawler_agent.py # Stage 3 — Authenticated session crawl
│   ├── recon_agent.py        # Stage 4 — Attack surface mapping
│   ├── vuln_detection_agent.py # Stage 5 — Vulnerability identification
│   ├── triage_agent.py       # Stage 6 — Dedup, rank, filter false positives
│   └── report_agent.py       # Stage 7 — Markdown bug bounty report
│
├── ui/
│   ├── dashboard.py          # Stats overview & recent scan history
│   ├── single_scan.py        # Scan a single URL with live progress
│   ├── auto_crawler.py       # Continuous crawler with pause/resume/stop
│   └── reports.py            # View & download all saved reports
│
├── reports/                  # Generated .md reports (auto-created)
├── scan_history.json         # Persisted scan history
└── crawler_state.json        # Auto crawler session state
```

---

## Pipeline

```
crawl → form_fuzz → auth_crawl → recon → detect → triage → report
  ↑          ↑           ↑          ↑        ↑        ↑        ↑
TinyFish  TinyFish   TinyFish    Groq     Groq     Groq     Groq
```

---

## Agents

| Agent | Model | Description |
|-------|-------|-------------|
| `crawler_agent` | TinyFish | Navigates the target in a real browser. Extracts HTML, links, forms, scripts, API endpoints, exposed secrets, and tech stack hints. 5-min timeout. |
| `form_fuzzer_agent` | TinyFish | Submits XSS and SQLi payloads into each discovered form and checks for reflection or error-based injection. 2-min timeout per form. |
| `auth_crawler_agent` | TinyFish | Logs in using provided credentials and crawls authenticated-only pages, admin panels, and IDOR patterns. 3-min timeout. |
| `recon_agent` | Groq llama-3.3-70b | Processes crawl data into a structured attack surface profile — tech stack, exposed endpoints, security misconfigs. |
| `vuln_detection_agent` | Groq llama-3.3-70b | Analyzes recon + fuzz data to identify specific vulnerabilities with evidence, CVSS scores, and CWE IDs. |
| `triage_agent` | Groq llama-3.3-70b | Deduplicates findings, filters false positives, and assigns final severity rankings. |
| `report_agent` | Groq llama-3.3-70b | Produces a professional markdown bug bounty report from triaged results. |

---

## UI Pages

| Page | Description |
|------|-------------|
| 🏠 Dashboard | Aggregate stats, recent scan list, severity summary |
| 🔍 Single Scan | Enter a URL, watch the 7-stage pipeline run live |
| ⚡ Auto Crawler | Continuous autonomous crawl queue with pause/resume/stop |
| 📋 Reports | Browse, read, and download all generated reports |

---

## Setup & Run

### 1. Install dependencies

```bash
cd python_app
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Edit `.env`:

```
TINYFISH_API_KEY=sk-tinyfish-...
GROQ_API_KEY=gsk_...
```

- TinyFish API key → https://agent.tinyfish.ai/api-keys
- Groq API key → https://console.groq.com/keys

### 3. Run

```bash
streamlit run app.py
```

Open **http://localhost:8501**

---

## Output

- Reports saved as `.md` files in `reports/`
- Scan history persisted in `scan_history.json`
- Auto crawler session state in `crawler_state.json
