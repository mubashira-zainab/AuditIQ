# AuditIQ Backend — Clean Build

A properly structured FastAPI backend for the AuditIQ financial ledger/forecast
tool. Rebuilt from zero: real config management, input validation, custom
exceptions mapped to correct HTTP status codes, structured logging, and a
test suite — no more silent `except: pass` fallbacks hiding real bugs.

Frontend/design is intentionally not included here — you're building that
yourself. This backend serves plain JSON + file responses so it'll work with
whatever frontend you build.

## Project layout

```
app/
  main.py              FastAPI app factory: wires routers, CORS, error handling
  config.py            All settings, loaded from environment / .env
  logging_config.py    Logging setup
  schemas.py           Every request/response Pydantic model
  dependencies.py      Shared FastAPI dependencies
  core/
    exceptions.py      Domain exceptions (SessionNotFoundError, etc.)
    security.py        Filename sanitization, extension/size validation
  services/
    session_store.py   In-memory session store (per-upload state)
    data_processor.py  Excel/CSV/PDF parsing
    forecaster.py       Linear regression trend forecasting
    market_watcher.py   yfinance lookup, PSX .KA ticker resolution
    ai_pipeline.py       Two-stage Groq report pipeline
    audio_service.py    gTTS narration + optional ffmpeg speed-up
  routers/
    health.py, upload.py, analysis.py, audio.py, report.py
tests/
  test_health.py, test_forecaster.py, test_security.py
.env.example
requirements.txt
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env         # Windows: copy, macOS/Linux: cp
```

Edit `.env` if you want a default Groq API key baked in server-side (optional —
the key can also be sent per-request from the frontend, which always wins).

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API docs (try every endpoint from the browser): `http://localhost:8000/docs`

## Test

```bash
pytest
```

Covers: health check, forecaster math (empty series, single-point fallback,
linear trend), and filename/upload security validation (path traversal,
disallowed extensions, size limits).

**A note on how far I could verify this**: this sandbox has no network
access, so I could not `pip install` the dependencies here and actually run
`uvicorn`/`pytest` end-to-end. Every file passed a Python syntax check
(`py_compile`), and I traced the request/response shapes by hand across
routers → services → schemas to make sure field names line up everywhere.
Please run `pytest` yourself after `pip install -r requirements.txt` as a
final check before you build on top of this — if anything fails, send me
the output and I'll fix it immediately.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness check |
| POST | `/api/upload` | Upload `.xlsx`/`.csv`/`.pdf`, returns `session_id` + parsed summary |
| POST | `/api/analyze` | Runs forecast + market lookup + AI report for a session |
| POST | `/api/audio` | Generates spoken briefing mp3 from the latest analysis |
| GET | `/api/report/{session_id}/download` | Downloads the compiled `.txt` report |

## Design decisions worth knowing about

- **Sessions are in-memory**, keyed by UUID, with a 2-hour TTL (`SESSION_TTL_MINUTES`
  in `.env`). Fine for local/single-instance use. If you ever deploy multi-process
  or need sessions to survive a restart, swap `SessionStore` for a Redis-backed
  version — routers only depend on its interface, not its internals.
- **Uploaded files are sanitized**: filenames are stripped of path components
  before touching disk, so a malicious filename can't write outside the
  storage folder. Extension allow-list and size limit are enforced server-side
  regardless of what the frontend does.
- **No API key = no fake report.** If no Groq key is supplied, `/api/analyze`
  returns a clearly-labeled offline preview instead of pretending to be a real
  AI audit — this was a real bug in the original version.
- **Errors map to real HTTP status codes** (404 for missing session, 409 for
  "analysis not run yet", 413 for oversized file, 422 for unparseable file)
  instead of everything being a vague generic error.
