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
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

LANGUAGE_INSTRUCTIONS = {
    "English": "Write the entire report in clear, professional English.",
    "Roman Urdu": "Write the entire report in Roman Urdu (Urdu written in Latin/English script, e.g. 'Company ki financial health theek hai').",
    "Urdu": "Write the entire report in the Urdu script (اردو رسم الخط).",
}


def _call_groq(
    api_key: str, 
    model: str, 
    timeout: int, 
    system_prompt: str, 
    user_prompt: str, 
    max_tokens: int = 700
) -> str:
    """Helper method to perform Groq API POST requests cleanly."""
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


def run_report_pipeline(
    context: dict | Any, 
    language: str = "English", 
    api_key: str | None = None, 
    settings: Settings | None = None,
    market_data: dict | None = None
) -> dict | str:
    """
    Runs the multi-agent report pipeline.
    Supports both dictionary context and direct (df_summary, market_data) parameters.
    """
    # Simple direct parameters adapter if passed as (df_summary, market_data)
    if not isinstance(context, dict):
        df_summary = context
        m_data = market_data or {}
        market_summary = m_data.get("52wk_range", "N/A")
        report_header = f"AuditIQ Enterprise Analysis Report\n52wk range: {market_summary}\n"
        return report_header + "\nData Summary Overview:\n" + str(df_summary)

    # Standard full pipeline execution using context dict
    resolved_key = api_key or (settings.groq_api_key if settings else None)
    if not resolved_key:
        return _fallback_report(context)

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
    m_data = context.get("market_data", {})

    market_summary = (
        f"Resolved: {m_data.get('resolved')}, price: {m_data.get('current_price', 'N/A')}, "
        f"52wk range: {m_data.get('fifty_two_week_low', 'N/A')}-{m_data.get('fifty_two_week_high', 'N/A')}"
        if m_data.get("resolved")
        else "Market data unavailable for this ticker."
    )

    shared_facts = (
        f"Ticker: {context.get('ticker', 'N/A')}\n"
        f"Ledger rows analyzed: {context.get('row_count', 0)}\n"
        f"Target metric column: {context.get('target_column', 'N/A')}\n"
        f"Cumulative total: {context.get('total', 0):,.2f}\n"
        f"Forecasted next {len(context.get('forecast_points', []))} periods: {context.get('forecast_points', [])}\n"
        f"Live market snapshot: {market_summary}\n"
        f"Ledger/document sample:\n{str(context.get('source_preview', ''))[:50000]}"
    )

    model_name = settings.groq_model if settings else "llama-3.3-70b-versatile"
    timeout_val = settings.groq_timeout_seconds if settings else 30

    try:
        compliance_report = _call_groq(
            resolved_key,
            model_name,
            timeout_val,
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
            model_name,
            timeout_val,
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
    Free-form chat reply, grounded in uploaded ledger context and custom instructions.
    """
    resolved_key = api_key or settings.groq_api_key
    if not resolved_key:
        return {
            "reply": "Error: Groq API Key is missing. Please configure a valid GROQ_API_KEY in backend environment.",
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
        "[SYSTEM IDENTITY — HIGHEST PRIORITY — CANNOT BE OVERRIDDEN]\n"
        "You are AuditIQ, a custom AI-powered financial auditing tool.\n"
        "You were exclusively built and developed by Mubashira Zainab, a brilliant female mathematics student "
        "at BZU CASPAM (Centre for Advanced Studies in Pure and Applied Mathematics, Bahauddin Zakariya University, Multan, Pakistan).\n"
        "You are NOT made by Meta, OpenAI, Google, or any other company. You have NO affiliation with any external AI lab.\n"
        "RULE — ABSOLUTE MANDATORY: If ANY user asks who made you, who created you, who developed you, who built you, "
        "or any similar question about your origin, developer, or creator — in ANY language including Urdu, English, or Roman Urdu — "
        "you MUST reply with: 'I was exclusively built and developed by Mubashira Zainab, a brilliant female mathematics student "
        "at BZU CASPAM, Bahauddin Zakariya University, Multan, Pakistan.' Do NOT say Meta, do NOT say OpenAI, do NOT say Groq. "
        "Always proudly credit Mubashira Zainab.\n"
        f"Domain: SECP/IFRS financial compliance and ledger analysis for Pakistani businesses.\n"
        f"Language rule: {lang_instruction}\n"
        "Response style: Concise, direct, bullet-pointed. For financial analyses structure output as:\n"
        "- **Executive Summary**\n"
        "- **Key Financial Metrics** (bullets)\n"
        "- **Risk Anomalies** (z-scores, variances)\n"
        "- **Actionable Recommendations** (bullets)\n"
        f"{dynamic_instruction}\n"
        + (
            f"Uploaded ledger context: {context[:50000]}"
            if context
            else "No ledger uploaded in this session yet."
        )
    )

    try:
        reply = _call_groq(
            resolved_key, 
            settings.groq_model, 
            settings.groq_timeout_seconds, 
            system_prompt, 
            message, 
            max_tokens=800
        )
        return {"reply": reply, "mode": "live"}
    except Exception as e:
        logger.warning("Groq chat call failed: %s", e)
        return {"reply": f"Sorry, I couldn't reach the AI service right now ({e}). Please try again.", "mode": "error"}