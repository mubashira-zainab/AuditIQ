"""
Two-stage report pipeline:

  Agent 1 (Compliance Auditor)  - reviews ledger/PDF text + market data,
                                   flags anomalies against SECP/IFRS-style
                                   expectations.
  Agent 2 (Bilingual Forecaster) - turns the math forecast into a narrative
                                   report in the user's chosen language.

Runs as two sequential Groq chat-completion calls. If no API key is present
(or the call fails), returns a clearly-labeled offline placeholder instead
of silently pretending to be a real AI report.
"""
import logging

import requests

from app.config import Settings

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

LANGUAGE_INSTRUCTIONS = {
    "English": "Write the entire report in clear, professional English.",
    "Roman Urdu": "Write the entire report in Roman Urdu (Urdu written in Latin/English script, e.g. 'Company ki financial health theek hai').",
    "Urdu": "Write the entire report in the Urdu script (اردو رسم الخط).",
}


def _call_groq(api_key: str, model: str, timeout: int, system_prompt: str, user_prompt: str, max_tokens: int = 700) -> str:
    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def _fallback_report(context: dict) -> dict:
    """Error message instead of offline preview mode placeholder."""
    return {
        "compliance_report": "Error: Groq API Key is missing or invalid. Please configure a valid key.",
        "narrative_report": "Error: Groq API Key is missing or invalid.",
        "mode": "error",
        "error": "Groq API Key is missing."
    }


def run_report_pipeline(context: dict, language: str, api_key: str | None, settings: Settings) -> dict:
    """
    context expects: ticker, market_data (dict), total, row_count, target_column,
    forecast_points, source_preview (raw ledger/PDF text sample).
    """
    resolved_key = api_key or settings.groq_api_key
    if not resolved_key:
        return _fallback_report(context)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
    market_data = context.get("market_data", {})

    market_summary = (
        f"Resolved: {market_data.get('resolved')}, price: {market_data.get('current_price', 'N/A')}, "
        f"52wk range: {market_data.get('fifty_two_week_low', 'N/A')}-{market_data.get('fifty_two_week_high', 'N/A')}"
        if market_data.get("resolved")
        else "Market data unavailable for this ticker."
    )

    shared_facts = (
        f"Ticker: {context.get('ticker', 'N/A')}\n"
        f"Ledger rows analyzed: {context.get('row_count', 0)}\n"
        f"Target metric column: {context.get('target_column', 'N/A')}\n"
        f"Cumulative total: {context.get('total', 0):,.2f}\n"
        f"Forecasted next {len(context.get('forecast_points', []))} periods: {context.get('forecast_points', [])}\n"
        f"Live market snapshot: {market_summary}\n"
        f"Ledger/document sample:\n{context.get('source_preview', '')[:50000]}"
    )

    try:
        compliance_report = _call_groq(
            resolved_key,
            settings.groq_model,
            settings.groq_timeout_seconds,
            system_prompt=(
                "You are a senior financial compliance auditor familiar with SECP and IFRS "
                "expectations for Pakistani companies. Review the ledger data and market context "
                "given to you. Flag any numerical anomalies, missing data, or compliance red flags "
                "you can reasonably infer. Be concise and use bullet points. If nothing stands out, "
                "say so plainly rather than inventing issues."
            ),
            user_prompt=shared_facts,
        )

        narrative_report = _call_groq(
            resolved_key,
            settings.groq_model,
            settings.groq_timeout_seconds,
            system_prompt=(
                "You are a bilingual financial forecaster who explains numbers to business owners "
                f"in plain language. {lang_instruction} Reference the actual figures given to you. "
                "Structure the report as: 1) Current Position 2) Forecast Outlook 3) Recommended Actions."
            ),
            user_prompt=shared_facts,
        )

        return {
            "compliance_report": compliance_report,
            "narrative_report": narrative_report,
            "mode": "live",
            "error": None,
        }

    except Exception as e:
        logger.warning("Groq call failed, falling back to offline report: %s", e)
        fallback = _fallback_report(context)
        fallback["error"] = str(e)
        return fallback


def answer_chat_message(message: str, context: str, language: str, api_key: str | None, settings: Settings) -> dict:
    """
    Free-form chat reply, optionally grounded in the most recent uploaded ledger
    (passed in as `context`, empty string if nothing uploaded yet).
    """
    resolved_key = api_key or settings.groq_api_key
    if not resolved_key:
        return {
            "reply": "Error: Groq API Key is missing. Please configure a valid GROQ_API_KEY in the backend .env configuration.",
            "mode": "error",
        }

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
    
    dynamic_instruction = (
        "IMPORTANT: You can dynamically generate downloadable files and charts for the user! "
        "If the user asks for a chart/graph, include this exact block in your reply: <GENERATE_CHART>{\"title\": \"Chart Title\", \"x_label\": \"Months\", \"y_label\": \"PKR\", \"series\": [{\"name\": \"Revenue\", \"x\": [1,2], \"y\": [10,20]}]}</GENERATE_CHART>. "
        "If the user asks for a sample dataset or CSV file, include this exact block: <GENERATE_CSV>Col1,Col2\nVal1,Val2</GENERATE_CSV>. "
        "If the user asks for an audit report or PDF file, include this exact block: <GENERATE_PDF>Your markdown report text here</GENERATE_PDF>. "
        "The backend will automatically convert these blocks into actual files and provide download links. "
        "Ensure your JSON for charts is strictly valid. Do NOT wrap the JSON in markdown code blocks inside the tag."
    )

    system_prompt = (
        "You are AuditIQ, a helpful assistant for a financial compliance and forecasting tool "
        "aimed at Pakistani businesses (SECP/IFRS context). Answer the user's message naturally "
        f"and concisely. {lang_instruction}\n{dynamic_instruction}\n"
        + (
            f"They have an uploaded ledger with this context available: {context[:50000]}"
            if context
            else "No ledger has been uploaded in this session yet."
        )
    )

    try:
        reply = _call_groq(resolved_key, settings.groq_model, settings.groq_timeout_seconds, system_prompt, message, max_tokens=400)
        return {"reply": reply, "mode": "live"}
    except Exception as e:
        logger.warning("Groq chat call failed: %s", e)
        return {"reply": f"Sorry, I couldn't reach the AI service right now ({e}). Please try again.", "mode": "error"}
