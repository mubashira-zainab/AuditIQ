"""
Recommendation Engine — analyses financial data and generates
structured, actionable recommendations with a risk score.

Risk Categories:
  - Profitability  (profit margin, EBITDA trend)
  - Cash Flow      (cash position, burn rate)
  - Debt           (leverage, debt-to-equity)
  - Growth         (revenue trend, forecast direction)
  - Compliance     (anomalies, missing data)
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


# ─── RISK SCORE CALCULATION ───────────────────────────────────────────────────

def _trend_direction(series: list[float]) -> str:
    """Return 'up', 'down', or 'flat' based on last half vs first half."""
    if len(series) < 2:
        return "flat"
    mid = len(series) // 2
    first_half_avg = sum(series[:mid]) / max(mid, 1)
    second_half_avg = sum(series[mid:]) / max(len(series) - mid, 1)
    if first_half_avg == 0:
        return "flat"
    change_pct = (second_half_avg - first_half_avg) / abs(first_half_avg)
    if change_pct > 0.05:
        return "up"
    elif change_pct < -0.05:
        return "down"
    return "flat"


def _forecast_direction(forecast_points: list[float], current_total: float) -> str:
    if not forecast_points or current_total == 0:
        return "flat"
    avg_forecast = sum(forecast_points) / len(forecast_points)
    change_pct = (avg_forecast - current_total) / abs(current_total)
    if change_pct > 0.03:
        return "up"
    elif change_pct < -0.03:
        return "down"
    return "flat"


def calculate_risk_score(context: dict[str, Any]) -> dict[str, Any]:
    """
    Returns:
        risk_score     : 0–100 (0 = no risk, 100 = critical)
        risk_level     : 'Low' | 'Medium' | 'High' | 'Critical'
        risk_flags     : list of identified risk strings
        recommendations: list of actionable suggestion strings
    """
    series          = context.get("series", []) or []
    forecast_points = context.get("forecast_points", []) or []
    total           = context.get("total", 0.0) or 0.0
    row_count       = context.get("row_count", 0) or 0
    target_column   = context.get("target_column") or "unknown"
    ticker          = context.get("ticker") or ""
    market_data     = context.get("market_data") or {}

    risk_score    = 0
    risk_flags    : list[str] = []
    recommendations: list[str] = []

    # ── DATA QUALITY ────────────────────────────────────────────────────────
    if row_count == 0:
        risk_score += 20
        risk_flags.append("⚠️ No data rows found — analysis may be incomplete.")
        recommendations.append("📋 Ensure your uploaded file contains numeric data rows.")

    if not series:
        risk_score += 15
        risk_flags.append("⚠️ No numeric series detected for trend analysis.")
        recommendations.append("📊 Upload a file with a clear numeric column (revenue, expenses, etc.).")

    # ── TREND ANALYSIS ──────────────────────────────────────────────────────
    trend = _trend_direction(series)
    if trend == "down":
        risk_score += 25
        risk_flags.append(f"📉 Declining trend detected in '{target_column}'.")
        recommendations.append(f"🔍 Investigate the root cause of declining {target_column}.")
        recommendations.append("💡 Consider cost optimization or revenue diversification strategies.")
    elif trend == "up":
        risk_flags.append(f"📈 Growth trend detected in '{target_column}' — positive signal.")
        recommendations.append("✅ Maintain current growth strategies and monitor for sustainability.")

    # ── FORECAST ANALYSIS ───────────────────────────────────────────────────
    fc_dir = _forecast_direction(forecast_points, total / max(row_count, 1))
    if fc_dir == "down":
        risk_score += 20
        risk_flags.append("📉 AI forecast shows declining values in upcoming periods.")
        recommendations.append("🛡️ Build cash reserves to buffer projected decline.")
        recommendations.append("📞 Consider consulting a financial advisor for restructuring.")
    elif fc_dir == "up":
        risk_flags.append("📈 AI forecast projects growth — prepare for scaling.")
        recommendations.append("🚀 Plan for capacity expansion to support projected growth.")

    # ── MARKET DATA ─────────────────────────────────────────────────────────
    if market_data.get("resolved"):
        pe = market_data.get("pe_ratio")
        if pe and isinstance(pe, (int, float)):
            if pe > 40:
                risk_score += 10
                risk_flags.append(f"📊 High P/E ratio ({pe:.1f}) — stock may be overvalued.")
                recommendations.append("⚖️ Evaluate whether current valuation is justified by earnings.")
            elif pe < 5:
                risk_score += 10
                risk_flags.append(f"📊 Very low P/E ratio ({pe:.1f}) — possible undervaluation or distress.")
                recommendations.append("🔎 Investigate low P/E: could indicate opportunity or warning sign.")

    # ── HIGH VALUE RISK ──────────────────────────────────────────────────────
    if total > 10_000_000:
        recommendations.append("🏦 Large transaction volumes detected — ensure regulatory compliance (SECP/FBR).")

    if total < 0:
        risk_score += 30
        risk_flags.append(f"🔴 Negative cumulative total ({total:,.2f}) — potential net loss or liability position.")
        recommendations.append("🚨 Immediate review required: net negative position may indicate insolvency risk.")
        recommendations.append("💰 Explore debt restructuring or emergency cost reduction measures.")

    # ── FINAL SCORE ─────────────────────────────────────────────────────────
    risk_score = min(risk_score, 100)

    if risk_score < 20:
        risk_level = "Low"
    elif risk_score < 45:
        risk_level = "Medium"
    elif risk_score < 70:
        risk_level = "High"
    else:
        risk_level = "Critical"

    # Always add general recommendations
    if not recommendations:
        recommendations.append("✅ No critical risks detected. Continue monitoring monthly.")
    recommendations.append("📅 Schedule quarterly financial reviews to track KPI trends.")
    recommendations.append("🔒 Maintain audit trail for all financial transactions (SECP requirement).")

    return {
        "risk_score":      risk_score,
        "risk_level":      risk_level,
        "risk_flags":      risk_flags,
        "recommendations": recommendations,
        "trend":           trend,
        "forecast_direction": fc_dir,
    }


def format_recommendations_for_ai(risk_result: dict[str, Any]) -> str:
    """Format risk analysis into a string for injection into AI prompts."""
    lines = [
        f"\n=== AUTOMATED RISK ANALYSIS ===",
        f"Risk Score: {risk_result['risk_score']}/100 ({risk_result['risk_level']})",
        f"Trend: {risk_result['trend'].upper()}",
        f"Forecast: {risk_result['forecast_direction'].upper()}",
    ]
    if risk_result["risk_flags"]:
        lines.append("\nRisk Flags:")
        lines.extend(f"  {f}" for f in risk_result["risk_flags"])
    if risk_result["recommendations"]:
        lines.append("\nRecommendations:")
        lines.extend(f"  {r}" for r in risk_result["recommendations"])
    lines.append("=== END RISK ANALYSIS ===\n")
    return "\n".join(lines)
