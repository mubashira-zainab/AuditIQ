"""
Pure-math forecasting: linear trend regression over an uploaded numeric series.
No AI/LLM calls here on purpose -- this stays fast, deterministic, and testable
independent of any API key.
"""
import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_series(series: list[float], horizon: int = 3) -> dict:
    """
    Forecast the next `horizon` points of a numeric series (e.g. monthly revenue rows).
    Falls back to a flat +5% projection when there's only one data point to work with.
    """
    n = len(series)

    if n == 0:
        return {"next_points": [], "method": "none", "slope": None, "note": "No numeric data found in the upload."}

    if n == 1:
        next_val = round(series[0] * 1.05, 2)
        return {
            "next_points": [next_val] * horizon,
            "method": "flat_projection",
            "slope": None,
            "note": "Only one data point supplied; used a conservative +5% projection instead of a trend line.",
        }

    X = np.arange(n).reshape(-1, 1)
    y = np.array(series, dtype=float)
    model = LinearRegression().fit(X, y)

    future_idx = np.arange(n, n + horizon).reshape(-1, 1)
    predictions = model.predict(future_idx)

    return {
        "next_points": [round(float(v), 2) for v in predictions],
        "method": "linear_regression",
        "slope": round(float(model.coef_[0]), 4),
        "note": None,
    }


def calculate_financial_ratios(
    revenue: float,
    net_income: float,
    total_assets: float,
    total_liabilities: float,
) -> dict:
    """Standard health-check ratios, used by future report features."""
    equity = total_assets - total_liabilities
    return {
        "net_profit_margin_percent": round((net_income / revenue) * 100, 2) if revenue else None,
        "asset_turnover": round(revenue / total_assets, 2) if total_assets else None,
        "debt_to_equity": round(total_liabilities / equity, 2) if equity else None,
    }
