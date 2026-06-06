#!/usr/bin/env python3
"""
Twelve Data Bridge — Technical Analysis & Real-Time Pricing
ใช้ official Twelve Data API

Rate Limits (Basic Free Plan):
  - 800 credits/day
  - 8 credits/minute  ← สำคัญ: technicals ใช้ 5 credits → รัน 1 ตัวต่อนาทีได้
  - 1 credit per symbol per request (most endpoints)

ข้อดีกว่า yfinance:
  - Real-time price (ไม่ delay 15 นาที)
  - Technical indicators ครบ 100+ built-in (RSI, MACD, Bollinger Bands, ATR, Stochastic)
  - Official API (ไม่ใช่ web scrape)

Not available on free plan:
  - earnings (ต้อง grow/pro plan)
  - financial statements

Usage:
  python tools/twelvedata_bridge.py quote NVDA
  python tools/twelvedata_bridge.py portfolio
  python tools/twelvedata_bridge.py technicals RKLB
  python tools/twelvedata_bridge.py time_series NVDA [--interval 1day] [--bars 60]
  python tools/twelvedata_bridge.py indicator NVDA --type RSI [--interval 1day]
  python tools/twelvedata_bridge.py credits

Config: tools/twelvedata.json  →  {"api_key": "YOUR_KEY_HERE"}
"""

import sys
import json
import argparse
import os
import time
from datetime import datetime
from urllib.request import urlopen, Request as URLRequest
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "https://api.twelvedata.com"
RATE_LIMIT_WAIT = 8.0  # seconds between requests for cmd_technicals (free plan: 8 credits/min)

# Fallback ticker list if Google Sheets is unavailable
PORTFOLIO_TICKERS_FALLBACK = ["NVDA", "RKLB", "SOFI", "GOOGL", "PLTR", "AMZN", "NVO", "UNH"]


def _get_portfolio_tickers() -> tuple[list, str]:
    """Load ticker list live from Google Sheets. Returns (tickers, source_label)."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        return PORTFOLIO_TICKERS_FALLBACK, "hardcoded_fallback"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")
    if not os.path.exists(token_path):
        return PORTFOLIO_TICKERS_FALLBACK, "hardcoded_fallback"

    try:
        creds = Credentials.from_authorized_user_file(
            token_path, ["https://www.googleapis.com/auth/spreadsheets"]
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId="1JC_SMTlWNBwuqDne3MJ229CAOWRw5KMDZeQM8_Vcr4s",
            range="A:A"
        ).execute()
        values = result.get("values", [])
        # values[0] = header row ("Tracker"), values[1:] = data rows; empty Tracker = summary row
        tickers = [
            row[0].strip().upper()
            for row in values[1:]
            if row and row[0].strip()
        ]
        return (tickers, "google_sheets_live") if tickers else (PORTFOLIO_TICKERS_FALLBACK, "hardcoded_fallback")
    except Exception as e:
        print(f"[twelvedata] Sheets unavailable: {e} — using hardcoded ticker list", file=sys.stderr)
        return PORTFOLIO_TICKERS_FALLBACK, "hardcoded_fallback"


def _load_api_key() -> str:
    """Load API key from tools/twelvedata.json or env var TWELVE_DATA_API_KEY."""
    env_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if env_key:
        return env_key

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "twelvedata.json")

    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        key = cfg.get("api_key", "").strip()
        if key and key != "YOUR_KEY_HERE":
            return key

    print(json.dumps({
        "error": "API key not found",
        "fix": "ใส่ key ใน tools/twelvedata.json: {\"api_key\": \"YOUR_KEY_HERE\"} หรือ set env var TWELVE_DATA_API_KEY"
    }, ensure_ascii=False, indent=2))
    sys.exit(1)


def _get(endpoint: str, params: dict) -> dict:
    """Make a GET request to Twelve Data API and return parsed JSON."""
    api_key = _load_api_key()
    params["apikey"] = api_key
    url = f"{BASE_URL}/{endpoint}?{urlencode(params)}"
    try:
        req = URLRequest(url, headers={"User-Agent": "InvestmentOS/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if isinstance(data, dict) and data.get("status") == "error":
            print(json.dumps({"error": data.get("message", "Twelve Data error"), "code": data.get("code")}, indent=2))
            sys.exit(1)
        return data
    except HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}: {e.reason}"}))
        sys.exit(1)
    except URLError as e:
        print(json.dumps({"error": f"Network error: {e.reason}"}))
        sys.exit(1)


def _safe_float(val):
    try:
        return round(float(val), 4) if val not in (None, "", "N/A") else None
    except (ValueError, TypeError):
        return None


def cmd_quote(ticker: str):
    """Real-time quote for a single ticker. Cost: 1 credit."""
    data = _get("quote", {"symbol": ticker.upper()})
    print(json.dumps({
        "source": "Twelve Data (real-time)",
        "ticker": data.get("symbol"),
        "name": data.get("name"),
        "exchange": data.get("exchange"),
        "price": _safe_float(data.get("close")),
        "open": _safe_float(data.get("open")),
        "high": _safe_float(data.get("high")),
        "low": _safe_float(data.get("low")),
        "prev_close": _safe_float(data.get("previous_close")),
        "change": _safe_float(data.get("change")),
        "change_pct": _safe_float(data.get("percent_change")),
        "volume": _safe_float(data.get("volume")),
        "avg_volume": _safe_float(data.get("average_volume")),
        "52w_high": _safe_float(data.get("fifty_two_week", {}).get("high")),
        "52w_low": _safe_float(data.get("fifty_two_week", {}).get("low")),
        "market_cap": _safe_float(data.get("market_cap")),
        "pe_ratio": _safe_float(data.get("pe")),
        "eps": _safe_float(data.get("eps")),
        "is_market_open": data.get("is_market_open"),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }, ensure_ascii=False, indent=2))


def cmd_portfolio():
    """Batch real-time quotes for all portfolio holdings. Cost: 1 credit per ticker."""
    tickers, source = _get_portfolio_tickers()
    tickers_str = ",".join(tickers)
    data = _get("quote", {"symbol": tickers_str})

    # When multiple symbols, returns dict keyed by symbol
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "symbol" in data:
        items = [data]
    else:
        items = list(data.values()) if isinstance(data, dict) else []

    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append({
            "ticker": item.get("symbol"),
            "price": _safe_float(item.get("close")),
            "change_pct": _safe_float(item.get("percent_change")),
            "volume": _safe_float(item.get("volume")),
            "52w_high": _safe_float(item.get("fifty_two_week", {}).get("high")),
            "52w_low": _safe_float(item.get("fifty_two_week", {}).get("low")),
            "pe": _safe_float(item.get("pe")),
            "eps": _safe_float(item.get("eps")),
        })

    print(json.dumps({
        "source": "Twelve Data (real-time)",
        "portfolio_source": source,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(rows),
        "holdings": rows,
    }, ensure_ascii=False, indent=2))


def cmd_time_series(ticker: str, interval: str = "1day", bars: int = 60):
    """OHLCV history. Cost: 1 credit per symbol.
    Intervals: 1min, 5min, 15min, 30min, 1h, 2h, 4h, 1day, 1week, 1month
    """
    data = _get("time_series", {
        "symbol": ticker.upper(),
        "interval": interval,
        "outputsize": bars,
        "order": "DESC",
    })
    values = data.get("values", [])
    print(json.dumps({
        "source": "Twelve Data",
        "ticker": ticker.upper(),
        "interval": interval,
        "bars": len(values),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ohlcv": [
            {
                "date": v.get("datetime"),
                "open": _safe_float(v.get("open")),
                "high": _safe_float(v.get("high")),
                "low": _safe_float(v.get("low")),
                "close": _safe_float(v.get("close")),
                "volume": _safe_float(v.get("volume")),
            }
            for v in values
        ],
    }, ensure_ascii=False, indent=2))


def cmd_indicator(ticker: str, indicator_type: str = "RSI", interval: str = "1day", period: int = 14):
    """Single technical indicator. Cost: 1 credit.
    Common types: RSI, MACD, BBANDS, STOCH, ATR, ADX, EMA, SMA, SUPERTREND
    """
    params = {
        "symbol": ticker.upper(),
        "interval": interval,
        "outputsize": 30,
    }
    # Indicator-specific params
    ind = indicator_type.upper()
    if ind in ("RSI", "ATR", "ADX", "EMA", "SMA"):
        params["time_period"] = period
    elif ind == "MACD":
        params["fast_period"] = 12
        params["slow_period"] = 26
        params["signal_period"] = 9
    elif ind == "BBANDS":
        params["time_period"] = period
        params["sd"] = 2
    elif ind == "STOCH":
        params["fast_k_period"] = 14
        params["slow_d_period"] = 3

    data = _get(ind.lower(), params)
    values = data.get("values", [])
    meta = data.get("meta", {})

    print(json.dumps({
        "source": "Twelve Data",
        "ticker": ticker.upper(),
        "indicator": ind,
        "interval": interval,
        "period": period,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "latest": values[0] if values else None,
        "history": values[:10],
        "meta": meta,
    }, ensure_ascii=False, indent=2))


def cmd_technicals(ticker: str, interval: str = "1day"):
    """Get RSI + MACD + Bollinger Bands + ATR for a ticker in one shot.
    Cost: 4 credits (1 per indicator)
    Use for Agent 03 Technical Analysis.
    """
    sym = ticker.upper()
    results = {}

    indicators = [
        ("rsi",    {"symbol": sym, "interval": interval, "time_period": 14, "outputsize": 5}),
        ("macd",   {"symbol": sym, "interval": interval, "fast_period": 12, "slow_period": 26, "signal_period": 9, "outputsize": 5}),
        ("bbands", {"symbol": sym, "interval": interval, "time_period": 20, "sd": 2, "outputsize": 5}),
        ("atr",    {"symbol": sym, "interval": interval, "time_period": 14, "outputsize": 5}),
    ]

    # Free plan = 8 credits/min — space indicator calls to avoid 429
    for i, (ind_name, params) in enumerate(indicators):
        if i > 0:
            print(f"[twelvedata] Rate limit guard: waiting {RATE_LIMIT_WAIT:.0f}s before next request ({i+1}/4)...", file=sys.stderr)
            time.sleep(RATE_LIMIT_WAIT)
        try:
            data = _get(ind_name, params)
            vals = data.get("values", [])
            results[ind_name.upper()] = vals[0] if vals else None
        except Exception as e:
            results[ind_name.upper()] = {"error": str(e)}

    # Also get current price
    try:
        quote = _get("price", {"symbol": sym})
        results["price"] = _safe_float(quote.get("price"))
    except Exception:
        pass

    print(json.dumps({
        "source": "Twelve Data — Technical Suite",
        "ticker": sym,
        "interval": interval,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "technicals": results,
        "credits_used": 5,
        "interpretation": {
            "RSI": "< 30 = Oversold / > 70 = Overbought",
            "MACD": "histogram > 0 = bullish momentum",
            "BBANDS": "price near upper = overbought / near lower = oversold",
            "ATR": "volatility measure — higher = more volatile",
        }
    }, ensure_ascii=False, indent=2))


def cmd_earnings(ticker: str):
    """Earnings history. NOTE: ต้องการ grow/pro plan — ไม่พร้อมใช้บน Basic free plan."""
    print(json.dumps({
        "error": "earnings endpoint requires grow/pro/ultra plan",
        "alternative": f"ใช้ yfinance แทน: python tools/yfinance_bridge.py calendar {ticker.upper()}",
        "twelvedata_pricing": "https://twelvedata.com/pricing",
    }, ensure_ascii=False, indent=2))


def cmd_credits():
    """Check remaining API credits (free). Cost: 0 credits."""
    data = _get("api_usage", {})
    print(json.dumps({
        "source": "Twelve Data",
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "usage": data,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Twelve Data Bridge — Real-Time Pricing + Technical Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/twelvedata_bridge.py quote RKLB
  python tools/twelvedata_bridge.py portfolio
  python tools/twelvedata_bridge.py technicals NVDA
  python tools/twelvedata_bridge.py technicals RKLB --interval 1week
  python tools/twelvedata_bridge.py time_series SOFI --interval 1day --bars 90
  python tools/twelvedata_bridge.py indicator NVDA --type MACD
  python tools/twelvedata_bridge.py indicator RKLB --type RSI --interval 1week
  python tools/twelvedata_bridge.py earnings NVDA
  python tools/twelvedata_bridge.py credits
        """
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("quote", help="Real-time quote (1 credit)")
    p.add_argument("ticker")

    sub.add_parser("portfolio", help="Batch quotes for all 8 holdings (8 credits)")

    p = sub.add_parser("time_series", help="OHLCV history (1 credit)")
    p.add_argument("ticker")
    p.add_argument("--interval", default="1day",
                   help="1min/5min/15min/30min/1h/4h/1day/1week/1month (default: 1day)")
    p.add_argument("--bars", type=int, default=60, help="Number of bars (default: 60)")

    p = sub.add_parser("indicator", help="Single technical indicator (1 credit)")
    p.add_argument("ticker")
    p.add_argument("--type", default="RSI", help="RSI/MACD/BBANDS/STOCH/ATR/ADX/EMA/SMA/SUPERTREND")
    p.add_argument("--interval", default="1day")
    p.add_argument("--period", type=int, default=14)

    p = sub.add_parser("technicals", help="RSI+MACD+BB+ATR bundle for Agent 03 (4-5 credits)")
    p.add_argument("ticker")
    p.add_argument("--interval", default="1day")

    p = sub.add_parser("earnings", help="Earnings history (1 credit)")
    p.add_argument("ticker")

    sub.add_parser("credits", help="Check remaining API credits (0 credits)")

    args = parser.parse_args()

    if args.command == "quote":
        cmd_quote(args.ticker)
    elif args.command == "portfolio":
        cmd_portfolio()
    elif args.command == "time_series":
        cmd_time_series(args.ticker, args.interval, args.bars)
    elif args.command == "indicator":
        cmd_indicator(args.ticker, args.type, args.interval, args.period)
    elif args.command == "technicals":
        cmd_technicals(args.ticker, args.interval)
    elif args.command == "earnings":
        cmd_earnings(args.ticker)
    elif args.command == "credits":
        cmd_credits()


if __name__ == "__main__":
    main()
