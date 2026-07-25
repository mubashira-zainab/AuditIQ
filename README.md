# AuditIQ — Financial AI Agent & Compliance Auditing Platform

> **AuditIQ** is an AI-powered financial auditing, compliance, and forecasting
> platform built to help businesses navigate SECP (Securities and Exchange
> Commission of Pakistan) and IFRS (International Financial Reporting
> Standards) guidelines.

**Live app:** https://mubashira-zainab.github.io/AuditIQ/
**Live backend (API):** https://auditiq-f8t8.onrender.com
**API docs (Swagger):** https://auditiq-f8t8.onrender.com/docs

---

## Developed By

* **Creator:** Mubashira Zainab
* **Institution:** BZU CASPAM (Centre for Advanced Studies in Pure and Applied Mathematics, Bahauddin Zakariya University, Multan, Pakistan)

---

## Core Features

* **Multi-agent report pipeline** — separate compliance-auditing and
  forecasting/narrative agents, with bilingual output (English, Urdu, Roman Urdu).
* **Reads more than spreadsheets** — parses `.xlsx`/`.csv`/`.pdf`, and reads
  uploaded images (receipts, screenshots, scanned pages) through a
  vision-capable model instead of treating them as opaque attachments.
* **Dynamic file & report generation** — on-demand chart (`.png`/`.jpg`),
  sample dataset (`.csv`), and PDF audit report generation.
* **Intelligent forecasting** — linear trend analysis over an uploaded
  ledger's numeric series, with a documented fallback for single-point data.
* **Persistent chat sessions** — conversations are stored server-side per
  session so a chat can be reopened later, not just cached in the browser.
* **Session-based architecture** — in-memory sessions with sanitized
  filenames, extension/size validation, and typed error responses.

---

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, Pandas, NumPy, scikit-learn, Matplotlib, FPDF
* **Frontend:** HTML5, CSS, vanilla JavaScript — no build step, no framework
* **AI Integration:** LLM-backed report pipeline via the Groq API (text and vision models)
* **Market data:** yfinance (PSX `.KA` ticker resolution)
* **Audio:** gTTS, with optional ffmpeg speed-up
* **Deployment:** frontend on GitHub Pages, backend on Render

---

## Architecture

```
┌─────────────────────────────┐        HTTPS/JSON           ┌──────────────────────────────┐
│   Frontend (GitHub Pages)   │ ────────────────────────▶ │   Backend (Render)            │
│   index.html + style.css    │ ◀──────────────────────── │   FastAPI (app/)               │
│   + app.js                  │                           │   Groq LLM · yfinance · gTTS   │
└─────────────────────────────┘                           └──────────────────────────────┘
```

The frontend is a static site with no backend logic of its own — it calls the
FastAPI backend over HTTPS. The Settings panel's **Backend URL** field points
at the Render URL above by default, so the deployed site works without any
manual configuration; change it only if you're pointing at your own backend
(e.g. `http://127.0.0.1:8000` for local development).

---

## Project Layout

```
index.html, style.css, app.js       Frontend (served by GitHub Pages)
logo-*.svg/png, favicon.ico         Branding assets
app/
  main.py              FastAPI app factory: routers, CORS, error handling, static serving
  config.py            All settings, loaded from environment / .env
  logging_config.py    Logging setup
  schemas.py           Every request/response Pydantic model
  dependencies.py      Shared FastAPI dependencies
  core/
    exceptions.py      Domain exceptions (SessionNotFoundError, etc.)
    security.py        Filename sanitization, extension/size validation
  services/
    session_store.py   In-memory session store (per-upload + per-chat state)
    data_processor.py  Excel/CSV/PDF parsing
    image_reader.py    Reads uploaded images via a Groq vision model
    forecaster.py      Linear regression trend forecasting
    market_watcher.py  yfinance lookup, PSX .KA ticker resolution
    ai_pipeline.py     Two-stage Groq report pipeline + free-form chat
    audio_service.py   gTTS narration + optional ffmpeg speed-up
  routers/
    health.py, upload.py, analysis.py, audio.py, report.py, chat.py
.env.example
requirements.txt
```

---

## Local Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/mubashira-zainab/AuditIQ.git
cd AuditIQ
```

### 2. Set up the backend

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env         # Windows: copy, macOS/Linux: cp
# then edit .env and add your own GROQ_API_KEY
```

```bash
uvicorn app.main:app --reload --port 8000
```

The backend now runs at `http://localhost:8000` — interactive API docs at `/docs`.

### 3. Run the frontend

Open `index.html` directly in a browser, or serve the folder with any static
file server. In Settings, set **Backend URL** to `http://localhost:8000` for
local development, or leave it pointed at the Render URL to use the live backend.

> **Never commit a real Groq API key to this repo.** `.env` is git-ignored —
> keep your key there, or in Render's environment variable settings for the
> deployed backend. A key committed to source or hardcoded in `app.js` is
> visible to anyone who opens dev tools or browses the repo.

---

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness check |
| POST | `/api/upload` | Upload a file (spreadsheet, PDF, image, or text), returns `session_id` + parsed content |
| POST | `/api/analyze` | Runs forecast + market lookup + AI compliance/forecast report for a session |
| POST | `/api/chat` | Free-form chat, optionally grounded in the uploaded ledger; persists conversation history |
| GET | `/api/chat/history/{session_id}` | Replays a past conversation |
| POST | `/api/audio` | Generates a spoken briefing (mp3) from the latest analysis |
| GET | `/api/report/{session_id}/download` | Downloads the compiled `.txt` report |

---

## Design Decisions Worth Knowing About

- **Sessions are in-memory**, keyed by UUID, with a 2-hour TTL. Fine for a
  single-instance deployment like this one. Render's free tier spins the
  service down when idle, so the first request after inactivity can be slow
  (cold start), and sessions don't survive a redeploy.
- **Uploaded files are sanitized** — filenames are stripped of path
  components before touching disk, and extensions/size are allow-listed
  server-side regardless of what the frontend sends.
- **No API key = no fake report.** Without a Groq key, `/api/analyze` and
  `/api/chat` return a clearly-labeled offline preview instead of pretending
  to be a real AI response.

## Known Limitations

- **Login/signup is client-side only** (browser storage) — suitable for a
  demo/personal tool, not a substitute for real backend authentication
  (password hashing, sessions, etc.).
- Render's free tier has a cold-start delay and no persistent storage across
  restarts.

## License

Add a license of your choice here (MIT is a common default for a project
like this) before making the repo public, if one isn't set already.
