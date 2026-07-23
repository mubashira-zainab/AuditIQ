"""
Live market data lookup via yfinance. Pakistani Stock Exchange (PSX) tickers
need a `.KA` suffix to resolve on Yahoo Finance -- a plain 'ENGRO' will not
return data, so that suffix is tried automatically before the bare symbol.
"""
import logging

import yfinance as yf

logger = logging.getLogger(__name__)


def _candidate_symbols(ticker: str) -> list[str]:
    ticker = ticker.strip().upper()
    if not ticker:
        return []
    if "." in ticker:
        return [ticker]
    return [f"{ticker}.KA", ticker]


def get_live_market_data(ticker_symbol: str) -> dict:
    """
    Returns live pricing/basic corporate info for a ticker. Tries PSX (.KA)
    resolution first, falling back to the bare symbol (useful for non-PSX
    tickers like AAPL, MSFT). Never raises -- returns {"resolved": False, ...}
    on failure so callers can degrade gracefully instead of erroring out.
    """
    if not ticker_symbol:
        return {"resolved": False, "error": "No ticker supplied."}

    last_error: str | None = None

    for symbol in _candidate_symbols(ticker_symbol):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            price = info.get("currentPrice", info.get("regularMarketPrice"))

            if not info or price is None:
                continue

            return {
                "resolved": True,
                "symbol_used": symbol,
                "company_name": info.get("longName", "N/A"),
                "current_price": price,
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "currency": info.get("currency", "PKR"),
            }
        except Exception as e:
            logger.info("Market lookup failed for symbol '%s': %s", symbol, e)
            last_error = str(e)
            continue

    return {"resolved": False, "error": last_error or f"No market data found for '{ticker_symbol}'."}
