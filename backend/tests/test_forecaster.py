from app.services.forecaster import calculate_financial_ratios, forecast_series


def test_forecast_series_empty():
    result = forecast_series([], horizon=3)
    assert result["next_points"] == []
    assert result["method"] == "none"


def test_forecast_series_single_point_uses_flat_projection():
    result = forecast_series([100.0], horizon=2)
    assert result["method"] == "flat_projection"
    assert result["next_points"] == [105.0, 105.0]


def test_forecast_series_linear_trend():
    result = forecast_series([10, 20, 30, 40], horizon=2)
    assert result["method"] == "linear_regression"
    assert result["next_points"][0] == 50.0
    assert result["next_points"][1] == 60.0


def test_calculate_financial_ratios_handles_zero_denominators():
    ratios = calculate_financial_ratios(revenue=0, net_income=10, total_assets=0, total_liabilities=0)
    assert ratios["net_profit_margin_percent"] is None
    assert ratios["asset_turnover"] is None
