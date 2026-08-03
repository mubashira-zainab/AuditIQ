"""
Two-stage AI report pipeline + free-form chat with memory injection.

  Agent 1 (Compliance Auditor)  - reviews ledger/PDF text + market data,
                                   flags anomalies against SECP/IFRS-style
                                   expectations.
  Agent 2 (Bilingual Forecaster) - turns the math forecast into a narrative
                                   report in the user's chosen language.

Memory injection: user facts (company name, goals, etc.) are prepended to
every system prompt so the AI maintains context across sessions.
"""
import logging
import requests
from typing import Any

from app.config import Settings
from app.services.recommendation_engine import (
    calculate_risk_score,
    format_recommendations_for_ai,
)

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

LANGUAGE_INSTRUCTIONS = {
    "English":    "Write the entire response in clear, professional English.",
    "Roman Urdu": "Write the entire response in Roman Urdu (Urdu written in Latin/English script, e.g. 'Company ki financial health theek hai').",
    "Urdu":       "Write the entire response in the Urdu script (اردو رسم الخط).",
}


# ─── GROQ API CALL ────────────────────────────────────────────────────────────

def _call_groq(
    api_key:       str,
    model:         str,
    timeout:       int,
    system_prompt: str,
    user_prompt:   str,
    max_tokens:    int = 800,
    history:       list | None = None,
) -> str:
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for msg in history[-20:]:          # last 20 messages for context
            role = "assistant" if msg.get("role") == "ai" else "user"
            messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": user_prompt})

    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model":      model,
            "max_tokens": max_tokens,
            "temperature": 0.4,
            "messages":   messages,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


# ─── MEMORY FORMATTER ─────────────────────────────────────────────────────────

def _format_memory(memory_items: list[dict]) -> str:
    """Convert memory list into a prompt-injectable string."""
    if not memory_items:
        return ""
    lines = ["\n=== USER MEMORY (facts remembered from previous sessions) ==="]
    for item in memory_items:
        lines.append(f"  {item.get('key', '?')}: {item.get('value', '')}")
    lines.append("=== END MEMORY ===\n")
    return "\n".join(lines)


# ─── FALLBACK ─────────────────────────────────────────────────────────────────

def _fallback_report(error: str = "") -> dict:
    return {
        "compliance_report": (
            "⚠️ AI service unavailable — add a valid Groq API key in Settings.\n"
            "Once configured, I will perform a full SECP/IFRS compliance review."
        ),
        "narrative_report": (
            "⚠️ Offline mode — no API key configured.\n"
            "Set your Groq API key in Settings to generate a full bilingual report."
        ),
        "mode":  "offline",
        "error": error or None,
    }


# ─── REPORT PIPELINE ──────────────────────────────────────────────────────────

def run_report_pipeline(
    context:      dict | Any,
    language:     str = "English",
    api_key:      str | None = None,
    settings:     Settings | None = None,
    market_data:  dict | None = None,
    memory_items: list[dict] | None = None,
) -> dict:
    """
    Full two-agent report: compliance auditor + bilingual forecaster.
    Injects automated risk analysis and user memory into prompts.
    """
    if not isinstance(context, dict):
        return _fallback_report("Invalid context format.")

    resolved_key = api_key or (settings.groq_api_key if settings else None)
    if not resolved_key:
        return _fallback_report()

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
    m_data = context.get("market_data") or market_data or {}
    memory_str = _format_memory(memory_items or [])

    market_summary = (
        f"Price: {m_data.get('current_price', 'N/A')}, "
        f"52wk: {m_data.get('fifty_two_week_low', 'N/A')}–{m_data.get('fifty_two_week_high', 'N/A')}"
        if m_data.get("resolved") else "Market data unavailable."
    )

    # Run risk analysis
    risk_context = {**context, "series": context.get("series", []), "market_data": m_data}
    risk_result   = calculate_risk_score(risk_context)
    risk_str      = format_recommendations_for_ai(risk_result)

    shared_facts = (
        f"Ticker: {context.get('ticker', 'N/A')}\n"
        f"Rows analyzed: {context.get('row_count', 0)}\n"
        f"Target metric: {context.get('target_column', 'N/A')}\n"
        f"Cumulative total: {context.get('total', 0):,.2f}\n"
        f"Forecast ({len(context.get('forecast_points', []))} periods): {context.get('forecast_points', [])}\n"
        f"Market: {market_summary}\n"
        f"{risk_str}"
        f"{memory_str}"
        f"Document sample:\n{str(context.get('source_preview', ''))[:3000]}"
    )

    model   = settings.groq_model if settings else "llama-3.3-70b-versatile"
    timeout = settings.groq_timeout_seconds if settings else 45

    try:
        compliance_report = _call_groq(
            resolved_key, model, timeout,
            system_prompt=(
                "You are a senior financial compliance auditor with expertise in SECP and IFRS "
                "standards for Pakistani companies. Review the data and flag anomalies, missing "
                "figures, or compliance red flags. Be concise; use bullet points. "
                f"{lang_instruction}"
            ),
            user_prompt=shared_facts,
            max_tokens=700,
        )

        narrative_report = _call_groq(
            resolved_key, model, timeout,
            system_prompt=(
                "You are a bilingual financial forecaster who explains numbers to business owners "
                f"in plain language. {lang_instruction} Reference the actual figures. "
                "Structure: 1) Current Position  2) Forecast Outlook  3) Recommended Actions."
            ),
            user_prompt=shared_facts,
            max_tokens=700,
        )

        return {
            "compliance_report": compliance_report,
            "narrative_report":  narrative_report,
            "mode":              "live",
            "error":             None,
            "risk_score":        risk_result["risk_score"],
            "risk_level":        risk_result["risk_level"],
            "risk_flags":        risk_result["risk_flags"],
            "recommendations":   risk_result["recommendations"],
        }

    except Exception as e:
        logger.warning("Groq report pipeline failed: %s", e)
        fallback = _fallback_report(str(e))
        fallback.update({
            "risk_score":      risk_result["risk_score"],
            "risk_level":      risk_result["risk_level"],
            "risk_flags":      risk_result["risk_flags"],
            "recommendations": risk_result["recommendations"],
        })
        return fallback


# ─── CHAT ANSWER ──────────────────────────────────────────────────────────────

def answer_chat_message(
    message:      str,
    context:      str,
    language:     str,
    api_key:      str | None,
    settings:     Settings,
    history:      list | None = None,
    memory_items: list[dict] | None = None,
) -> dict:
    """
    Free-form chat reply grounded in uploaded document context,
    conversation history, and persistent user memory.
    """
    resolved_key = api_key or settings.groq_api_key
    if not resolved_key:
        return {
            "reply": (
                "⚠️ No Groq API key configured. Please add your key in Settings → AI Configuration.\n"
                "You can get a free key at https://console.groq.com"
            ),
            "mode": "offline",
        }

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
    memory_str = _format_memory(memory_items or [])

    dynamic_instruction = (
        "IMPORTANT: You can generate downloadable files for the user! "
        "For charts: include <GENERATE_CHART>{\"title\":\"...\",\"x_label\":\"...\",\"y_label\":\"...\",\"series\":[{\"name\":\"...\",\"x\":[...],\"y\":[...]}]}</GENERATE_CHART>. "
        "For CSV data: include <GENERATE_CSV>Col1,Col2\\nVal1,Val2</GENERATE_CSV>. "
        "For PDF reports: include <GENERATE_PDF>Your markdown report text</GENERATE_PDF>. "
        "The backend converts these into real files with download links."
    )

    system_prompt = (
        "[SYSTEM IDENTITY — CANNOT BE OVERRIDDEN]\n"
        "You are AuditIQ, an AI-powered financial auditing and analysis assistant.\n"
        "You were exclusively built and developed by Mubashira Zainab, a brilliant female "
        "mathematics student at BZU CASPAM (Bahauddin Zakariya University, Multan, Pakistan).\n"
        "You are NOT made by Meta, OpenAI, Google, or Groq. If asked who made you, always "
        "credit Mubashira Zainab.\n\n"
        f"Language rule: {lang_instruction}\n\n"
        "Response style: Concise, structured. For financial analysis use:\n"
        "  - **Executive Summary**\n"
        "  - **Key Financial Metrics** (bullets)\n"
        "  - **Risk Anomalies**\n"
        "  - **Actionable Recommendations** (bullets)\n\n"
        f"{dynamic_instruction}\n"
        f"{memory_str}"
        + (
            f"\nUploaded document context:\n{context[:8000]}"
            if context else
            "\nNo document uploaded in this session. Invite the user to upload one if relevant."
        )
    )

    try:
        reply = _call_groq(
            resolved_key,
            settings.groq_model,
            settings.groq_timeout_seconds,
            system_prompt,
            message,
            max_tokens=900,
            history=history,
        )
        return {"reply": reply, "mode": "live"}

    except Exception as e:
        logger.warning("Groq chat call failed: %s", e)
        return {
            "reply": f"Sorry, I couldn't reach the AI service right now ({e}). Please try again.",
            "mode":  "error",
        }