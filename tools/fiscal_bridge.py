#!/usr/bin/env python3
"""
Fiscal.ai Bridge — Institutional-Grade Fundamental Data
ดึง standardized financials, ratios, filings, earnings, news จาก Fiscal.ai API

ข้อดีกว่า yfinance:
  - As-reported + Standardized financials พร้อม source document links
  - Adjusted metrics (Adj EPS, Adj EBITDA, non-GAAP)
  - Financial ratios คำนวณแล้ว (P/E, P/S, EV/EBITDA, ROE ฯลฯ)
  - Filing PDFs โดยตรง (10-K, 10-Q, 8-K)
  - Company news พร้อม importance score
  - Shares outstanding class-level breakdown

Rate Limits:
  - 50 requests/minute
  - 250 requests/day (free plan)
  - 25 companies max (free plan)

Usage:
  python tools/fiscal_bridge.py profile NVDA
  python tools/fiscal_bridge.py financials NVDA [--type income|balance|cashflow] [--period quarterly|annual] [--standardized]
  python tools/fiscal_bridge.py ratios NVDA [--period quarterly|annual]
  python tools/fiscal_bridge.py filings NVDA [--limit 10]
  python tools/fiscal_bridge.py earnings NVDA
  python tools/fiscal_bridge.py news NVDA [--limit 10]
  python tools/fiscal_bridge.py adjusted NVDA [--period quarterly|annual]
  python tools/fiscal_bridge.py shares NVDA
  python tools/fiscal_bridge.py prices NVDA [--start 2025-01-01]

Config: tools/fiscal.json → {"api_key": "YOUR_KEY_HERE"}
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

BASE_URL = "https://api.fiscal.ai"
_MIN_REQUEST_INTERVAL = 1.2  # 50 req/min limit → 1.2s min between requests
_last_request_time = 0.0


# ─────────────────────────────────────────────
# Config & Auth
# ─────────────────────────────────────────────

def _load_api_key() -> str:
    """Load API key from tools/fiscal.json or env var FISCAL_AI_API_KEY."""
    env_key = os.environ.get("FISCAL_AI_API_KEY", "").strip()
    if env_key:
        return env_key

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "fiscal.json")

    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        key = cfg.get("api_key", "").strip()
        if key and key != "YOUR_KEY_HERE":
            return key

    print(json.dumps({
        "error": "API key not found",
        "fix": "สร้างไฟล์ tools/fiscal.json: {\"api_key\": \"YOUR_KEY_HERE\"} หรือ set env var FISCAL_AI_API_KEY"
    }, ensure_ascii=False, indent=2))
    sys.exit(1)


# ─────────────────────────────────────────────
# HTTP Helper
# ─────────────────────────────────────────────

def _get(path: str, params: dict) -> dict:
    """GET request to Fiscal.ai API → parsed JSON."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()

    api_key = _load_api_key()
    params["apiKey"] = api_key
    url = f"{BASE_URL}{path}?{urlencode(params)}"

    try:
        req = URLRequest(url, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        })
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        if e.code == 429:
            return {"error": "Rate limit exceeded (50 req/min or 250 req/day)", "status": 429}
        if e.code == 401:
            return {"error": "Invalid API key — ตรวจสอบ tools/fiscal.json", "status": 401}
        if e.code == 404:
            return {"error": f"Ticker not found or endpoint unavailable", "status": 404, "detail": body}
        return {"error": f"HTTP {e.code}", "detail": body}
    except URLError as e:
        return {"error": f"Network error: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def _print(data: dict | list) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


# ─────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────

def cmd_profile(ticker: str) -> None:
    """Company profile — sector, industry, exchange, description."""
    data = _get("/v2/company/profile", {"ticker": ticker})
    _print(data)


def cmd_financials(ticker: str, stmt_type: str, period: str, standardized: bool) -> None:
    """
    Financial statements — income, balance sheet, cash flow.
    stmt_type: income | balance | cashflow
    period: quarterly | annual | ltm | latest  (maps to periodType param)
    standardized: True = normalized schema; False = as-reported (exact as filed)
    """
    type_map = {
        "income":   "income-statement",
        "balance":  "balance-sheet",
        "cashflow": "cash-flow-statement",
    }
    if stmt_type not in type_map:
        _print({"error": f"--type must be one of: {list(type_map.keys())}"})
        return

    variant = "standardized" if standardized else "as-reported"
    path = f"/v1/company/financials/{type_map[stmt_type]}/{variant}"
    data = _get(path, {"ticker": ticker, "periodType": period})
    _print(data)


def cmd_ratios(ticker: str, period: str) -> None:
    """
    Key financial ratios — P/E, P/S, EV/EBITDA, ROE, ROA, Debt/Equity, FCF Yield ฯลฯ
    Output: สรุป key metrics 4 quarters ล่าสุด (ไม่ dump raw 400KB)
    """
    raw = _get("/v1/company/ratios", {"ticker": ticker, "periodType": period})
    if "error" in raw:
        _print(raw)
        return

    # Key ratios ที่ Agent 02 ใช้จริง
    KEY_RATIOS = [
        "ratio_price_to_earnings",
        "ratio_forward_price_to_earnings",
        "ratio_price_to_sales",
        "ratio_price_to_book_value",
        "calculated_tev_to_ebitda",
        "calculated_tev_to_revenue",
        "ratio_return_on_equity",
        "ratio_return_on_assets",
        "ratio_return_on_invested_capital",
        "ratio_gross_profit_margin",
        "ratio_ebitda_margin",
        "ratio_net_profit_margin",
        "ratio_debt_to_equity",
        "ratio_net_debt_to_ebitda",
        "calculated_fcf",
        "calculated_fcf_yield",
        "ratio_price_to_ocf",
        "ratio_peg_ratio",
        "calculated_market_cap",
        "calculated_tev",
        "calculated_dividend_yield",
    ]

    periods_data = raw.get("data", [])
    # เรียงจากใหม่ไปเก่า, เอา 4 periods ล่าสุด
    periods_data = sorted(periods_data, key=lambda x: x.get("reportDate", ""), reverse=True)[:4]

    result = {
        "ticker": ticker,
        "period_type": period,
        "generated_at": datetime.now().isoformat(),
        "periods": []
    }

    for p in periods_data:
        mv = p.get("metricValues", {})
        entry = {
            "period": p.get("periodId", ""),
            "report_date": p.get("reportDate", ""),
            "fiscal_year": p.get("fiscalYear"),
            "fiscal_quarter": p.get("fiscalQuarter"),
            "ratios": {k: mv.get(k) for k in KEY_RATIOS if mv.get(k) is not None},
        }
        result["periods"].append(entry)

    _print(result)


def cmd_filings(ticker: str, limit: int) -> None:
    """Filing list (10-K, 10-Q, 8-K, earnings releases) พร้อม PDF links."""
    data = _get("/v2/company/filings", {"ticker": ticker, "limit": limit})
    api_key = _load_api_key()

    def _attach_pdf(f: dict) -> None:
        fid = f.get("filingId") or f.get("id", "")
        if fid:
            f["pdf_url"] = f"{BASE_URL}/v1/filing/{fid}/pdf?apiKey={api_key}"

    if isinstance(data, dict) and "filings" in data:
        for f in data["filings"]:
            _attach_pdf(f)
    elif isinstance(data, list):
        for f in data:
            _attach_pdf(f)
    _print(data)


def cmd_earnings(ticker: str, date_from: str | None, date_to: str | None) -> None:
    """Earnings calendar — scheduled dates, EPS/revenue estimates, importance score."""
    params: dict = {"tickers": ticker}  # API uses 'tickers' (plural), accepts plain ticker
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    data = _get("/v1/calendar/earnings", params)
    _print(data)


def cmd_news(ticker: str, limit: int) -> None:
    """Company news with importance score (0-5, higher = more market-moving)."""
    raw = _get("/v1/company/news", {"ticker": ticker})
    if "error" in raw:
        _print(raw)
        return
    items = raw if isinstance(raw, list) else raw.get("news", raw.get("data", []))
    if not isinstance(items, list):
        print(f"[fiscal] WARNING: Unexpected news response format: {type(items)}", file=sys.stderr)
        _print({"error": "unexpected response format", "raw_type": str(type(items))})
        return

    def _importance_key(x: dict) -> float:
        val = x.get("importance", 0)
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    items = sorted(items, key=_importance_key, reverse=True)[:limit]
    _print(items)


def cmd_adjusted(ticker: str, period: str) -> None:
    """Adjusted metrics — Adj EPS, Adj EBITDA, non-GAAP items."""
    data = _get("/v1/company/adjusted-metrics", {"ticker": ticker, "periodType": period})
    _print(data)


def cmd_shares(ticker: str) -> None:
    """Shares outstanding — total + class-level breakdown from latest filing."""
    data = _get("/v1/company/shares-outstanding", {"ticker": ticker})
    _print(data)


def cmd_prices(ticker: str, start: str | None) -> None:
    """Historical daily closing prices (split-adjusted)."""
    params: dict = {"ticker": ticker}
    if start:
        params["startDate"] = start
    data = _get("/v2/stock-prices", params)
    _print(data)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fiscal.ai Bridge — Institutional Fundamental Data"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # profile
    p = sub.add_parser("profile", help="Company profile")
    p.add_argument("ticker")

    # financials
    p = sub.add_parser("financials", help="Financial statements")
    p.add_argument("ticker")
    p.add_argument("--type", dest="stmt_type", default="income",
                   choices=["income", "balance", "cashflow"],
                   help="Statement type (default: income)")
    p.add_argument("--period", default="quarterly",
                   choices=["quarterly", "annual", "ltm", "ytd", "latest"],
                   help="Reporting period (default: quarterly)")
    p.add_argument("--standardized", action="store_true",
                   help="Use standardized schema (default: as-reported)")

    # ratios
    p = sub.add_parser("ratios", help="Financial ratios (P/E, P/S, EV/EBITDA ฯลฯ)")
    p.add_argument("ticker")
    p.add_argument("--period", default="quarterly",
                   choices=["quarterly", "annual", "ltm", "latest"],
                   help="Reporting period (default: quarterly)")

    # filings
    p = sub.add_parser("filings", help="SEC/filing list with PDF links")
    p.add_argument("ticker")
    p.add_argument("--limit", type=int, default=10)

    # earnings
    p = sub.add_parser("earnings", help="Earnings calendar + EPS/revenue estimates")
    p.add_argument("ticker")
    p.add_argument("--from", dest="date_from", default=None, help="Start date YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", default=None, help="End date YYYY-MM-DD")

    # news
    p = sub.add_parser("news", help="Company news with importance score")
    p.add_argument("ticker")
    p.add_argument("--limit", type=int, default=10)

    # adjusted
    p = sub.add_parser("adjusted", help="Adjusted metrics (Adj EPS, Adj EBITDA)")
    p.add_argument("ticker")
    p.add_argument("--period", default="quarterly",
                   choices=["quarterly", "annual", "ltm", "latest"])

    # shares
    p = sub.add_parser("shares", help="Shares outstanding breakdown")
    p.add_argument("ticker")

    # prices
    p = sub.add_parser("prices", help="Historical daily closing prices")
    p.add_argument("ticker")
    p.add_argument("--start", default=None, help="Start date YYYY-MM-DD")

    args = parser.parse_args()

    dispatch = {
        "profile":    lambda: cmd_profile(args.ticker),
        "financials": lambda: cmd_financials(args.ticker, args.stmt_type, args.period, args.standardized),
        "ratios":     lambda: cmd_ratios(args.ticker, args.period),
        "filings":    lambda: cmd_filings(args.ticker, args.limit),
        "earnings":   lambda: cmd_earnings(args.ticker, getattr(args, "date_from", None), getattr(args, "date_to", None)),
        "news":       lambda: cmd_news(args.ticker, args.limit),
        "adjusted":   lambda: cmd_adjusted(args.ticker, args.period),
        "shares":     lambda: cmd_shares(args.ticker),
        "prices":     lambda: cmd_prices(args.ticker, getattr(args, "start", None)),
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()
