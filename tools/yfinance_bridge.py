#!/usr/bin/env python3
"""
Yahoo Finance Bridge — Investment Operating System
ดึงข้อมูลหุ้นครบจาก Yahoo Finance: ราคา, งบการเงิน, Analyst, Holders, Insider

Usage:
  python tools/yfinance_bridge.py price NVDA
  python tools/yfinance_bridge.py portfolio
  python tools/yfinance_bridge.py info NVDA
  python tools/yfinance_bridge.py financials SOFI [--quarterly]
  python tools/yfinance_bridge.py holders NVDA
  python tools/yfinance_bridge.py insider NVDA
  python tools/yfinance_bridge.py calendar NVDA
  python tools/yfinance_bridge.py history NVDA [--period 1y]
  python tools/yfinance_bridge.py analyst NVDA
"""

import sys
import json
import argparse
import os
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def _load_portfolio_from_sheets():
    """Load live portfolio from Google Sheets. Returns dict or None if unavailable."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        return None

    _SPREADSHEET_ID = "1JC_SMTlWNBwuqDne3MJ229CAOWRw5KMDZeQM8_Vcr4s"
    _SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")

    if not os.path.exists(token_path):
        return None
    try:
        creds = Credentials.from_authorized_user_file(token_path, _SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=_SPREADSHEET_ID, range="A:K"
        ).execute()
        values = result.get("values", [])
    except Exception:
        return None

    if not values:
        return None

    headers = values[0]
    portfolio = {}
    for row in values[1:]:
        row_padded = row + [""] * (len(headers) - len(row))
        r = dict(zip(headers, row_padded))
        ticker = r.get("Tracker", "").strip().upper()
        if not ticker:
            continue
        try:
            shares = float(r.get("Shares", "0").replace(",", "").strip())
            avg_cost = float(
                r.get(" Avg. Cost ", "0").strip().replace("$", "").replace("฿", "").replace(",", "")
            )
            if shares > 0 and avg_cost > 0:
                portfolio[ticker] = {"shares": round(shares, 6), "avg_cost": round(avg_cost, 4)}
        except (ValueError, AttributeError) as e:
            print(f"[yfinance] WARNING: Skipped {ticker} — parse error: {e}", file=sys.stderr)
            continue

    return portfolio if portfolio else None


_PORTFOLIO_SOURCE = "hardcoded_snapshot"

_PORTFOLIO_FALLBACK = {
    "NVDA":  {"shares": 7.56,  "avg_cost": 127.01},
    "RKLB":  {"shares": 35.46, "avg_cost": 22.91},
    "SOFI":  {"shares": 24.04, "avg_cost": 16.24},
    "GOOGL": {"shares": 2.43,  "avg_cost": 190.35},
    "PLTR":  {"shares": 0.88,  "avg_cost": 154.23},
    "AMZN":  {"shares": 1.92,  "avg_cost": 215.96},
    "NVO":   {"shares": 8.43,  "avg_cost": 49.63},
    "UNH":   {"shares": 1.27,  "avg_cost": 326.85},
}


_PORTFOLIO_LAZY = None

def get_portfolio_lazy():
    """Return portfolio dict — live from Google Sheets, fallback to hardcoded snapshot."""
    global _PORTFOLIO_LAZY, _PORTFOLIO_SOURCE
    if _PORTFOLIO_LAZY is None:
        try:
            live = _load_portfolio_from_sheets()
            if live:
                print(f"[yfinance] Portfolio: Google Sheets live ({len(live)} holdings)", file=sys.stderr)
                _PORTFOLIO_SOURCE = "google_sheets_live"
                _PORTFOLIO_LAZY = live
                return _PORTFOLIO_LAZY
        except Exception as e:
            print(f"[yfinance] Sheets error: {e}", file=sys.stderr)

        print("[yfinance] WARNING: Using hardcoded portfolio snapshot — may be outdated", file=sys.stderr)
        _PORTFOLIO_SOURCE = "hardcoded_snapshot_WARNING_may_be_outdated"
        _PORTFOLIO_LAZY = _PORTFOLIO_FALLBACK.copy()
    return _PORTFOLIO_LAZY


def safe(val, decimals=2):
    """Convert numpy/pandas value to plain Python type safely."""
    try:
        if val is None or (hasattr(val, '__class__') and val.__class__.__name__ == 'NaT'):
            return None
        if hasattr(val, 'item'):
            val = val.item()
        if isinstance(val, float):
            if val != val:  # NaN check
                return None
            return round(val, decimals)
        if isinstance(val, int):
            return val
        return str(val)
    except Exception:
        return None


def fmt_num(val, prefix="", suffix="", decimals=2):
    v = safe(val, decimals)
    if v is None:
        return "N/A"
    if abs(v) >= 1_000_000_000:
        return f"{prefix}{v/1_000_000_000:.2f}B{suffix}"
    if abs(v) >= 1_000_000:
        return f"{prefix}{v/1_000_000:.2f}M{suffix}"
    return f"{prefix}{v:,.{decimals}f}{suffix}"


def cmd_price(ticker_sym: str):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())
    fi = t.fast_info

    price = safe(fi.last_price)
    prev_close = safe(fi.previous_close)
    change = round(price - prev_close, 4) if price and prev_close else None
    change_pct = round((change / prev_close) * 100, 2) if change and prev_close else None

    result = {
        "ticker": ticker_sym.upper(),
        "price": price,
        "change": change,
        "change_pct": change_pct,
        "prev_close": prev_close,
        "open": safe(fi.open),
        "day_high": safe(fi.day_high),
        "day_low": safe(fi.day_low),
        "volume": safe(fi.last_volume, 0),
        "market_cap": safe(fi.market_cap, 0),
        "52w_high": safe(fi.year_high),
        "52w_low": safe(fi.year_low),
        "50d_avg": safe(fi.fifty_day_average),
        "200d_avg": safe(fi.two_hundred_day_average),
        "year_change_pct": safe(fi.year_change),
        "currency": getattr(fi, "currency", "USD"),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # ถ้าอยู่ในพอร์ต — คำนวณ P/L
    sym = ticker_sym.upper()
    portfolio = get_portfolio_lazy()
    if sym in portfolio and price:
        pos = portfolio[sym]
        equity = round(pos["shares"] * price, 2)
        cost = round(pos["shares"] * pos["avg_cost"], 2)
        pl = round(equity - cost, 2)
        pl_pct = round((pl / cost) * 100, 2) if cost else None
        result["portfolio"] = {
            "shares": pos["shares"],
            "avg_cost": pos["avg_cost"],
            "total_equity": equity,
            "total_cost": cost,
            "gain_loss": pl,
            "gain_loss_pct": pl_pct,
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_portfolio():
    import yfinance as yf
    portfolio = get_portfolio_lazy()
    tickers_str = " ".join(portfolio.keys())
    data = yf.download(list(portfolio.keys()), period="1d", auto_adjust=True, progress=False)

    rows = []
    total_equity = 0
    total_cost = 0

    for sym, pos in portfolio.items():
        try:
            price = float(data["Close"][sym].dropna().iloc[-1])
        except Exception:
            price = None

        shares = pos["shares"]
        avg_cost = pos["avg_cost"]
        equity = round(shares * price, 2) if price else None
        cost = round(shares * avg_cost, 2)
        pl = round(equity - cost, 2) if equity is not None else None
        pl_pct = round((pl / cost) * 100, 2) if pl is not None and cost else None

        if equity:
            total_equity += equity
        total_cost += cost

        rows.append({
            "ticker": sym,
            "shares": shares,
            "avg_cost": avg_cost,
            "current_price": round(price, 2) if price else None,
            "total_equity": equity,
            "total_cost": cost,
            "gain_loss": pl,
            "gain_loss_pct": pl_pct,
        })

    total_pl = round(total_equity - total_cost, 2)
    total_pl_pct = round((total_pl / total_cost) * 100, 2) if total_cost else None

    # เพิ่ม allocation
    for row in rows:
        if row["total_equity"] and total_equity:
            row["allocation"] = round((row["total_equity"] / total_equity) * 100, 2)

    print(json.dumps({
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "portfolio_source": _PORTFOLIO_SOURCE,
        "summary": {
            "total_equity": round(total_equity, 2),
            "total_cost": round(total_cost, 2),
            "total_gain_loss": total_pl,
            "total_gain_loss_pct": total_pl_pct,
        },
        "holdings": rows,
    }, ensure_ascii=False, indent=2))


def cmd_info(ticker_sym: str):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())
    info = t.info

    fields = [
        "shortName", "sector", "industry", "country",
        "currentPrice", "previousClose", "marketCap", "enterpriseValue",
        "trailingPE", "forwardPE", "priceToBook", "priceToSalesTrailing12Months",
        "pegRatio", "beta",
        "trailingEps", "forwardEps",
        "revenueGrowth", "earningsGrowth", "grossMargins", "operatingMargins", "profitMargins",
        "totalRevenue", "netIncomeToCommon", "freeCashflow",
        "totalDebt", "totalCash",
        "returnOnEquity", "returnOnAssets",
        "dividendYield", "payoutRatio",
        "52WeekChange", "SandP52WeekChange",
        "targetMeanPrice", "targetHighPrice", "targetLowPrice",
        "recommendationMean", "recommendationKey",
        "numberOfAnalystOpinions",
        "shortPercentOfFloat", "sharesShort",
        "heldPercentInsiders", "heldPercentInstitutions", "sharesOutstanding",
        "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk", "overallRisk",
        "fullTimeEmployees", "longBusinessSummary",
    ]

    result = {"ticker": ticker_sym.upper(), "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
    for f in fields:
        val = info.get(f)
        if isinstance(val, (int, float)):
            result[f] = safe(val)
        elif val is not None:
            result[f] = val

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_financials(ticker_sym: str, quarterly: bool = False):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())

    if quarterly:
        income = t.quarterly_income_stmt
        balance = t.quarterly_balance_sheet
        cashflow = t.quarterly_cashflow
        label = "quarterly"
    else:
        income = t.income_stmt
        balance = t.balance_sheet
        cashflow = t.cashflow
        label = "annual"

    def df_to_dict(df):
        if df is None or df.empty:
            return {}
        out = {}
        for col in df.columns:
            col_str = str(col)[:10]  # เอาแค่ YYYY-MM-DD
            out[col_str] = {}
            for idx in df.index:
                val = df.loc[idx, col]
                out[col_str][str(idx)] = safe(val, 0)
        return out

    print(json.dumps({
        "ticker": ticker_sym.upper(),
        "period": label,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "income_statement": df_to_dict(income),
        "balance_sheet": df_to_dict(balance),
        "cashflow": df_to_dict(cashflow),
    }, ensure_ascii=False, indent=2))


def cmd_holders(ticker_sym: str):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())

    def df_to_list(df, limit=15):
        if df is None or df.empty:
            return []
        rows = []
        for _, row in df.head(limit).iterrows():
            rows.append({str(k): safe(v) if isinstance(v, (int, float)) else str(v) for k, v in row.items()})
        return rows

    print(json.dumps({
        "ticker": ticker_sym.upper(),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "institutional_holders": df_to_list(t.institutional_holders),
        "major_holders": df_to_list(t.major_holders),
    }, ensure_ascii=False, indent=2))


def cmd_insider(ticker_sym: str):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())
    df = t.insider_transactions

    if df is None or df.empty:
        print(json.dumps({"ticker": ticker_sym.upper(), "insider_transactions": []}))
        return

    rows = []
    for _, row in df.head(20).iterrows():
        rows.append({str(k): safe(v) if isinstance(v, (int, float)) else str(v) for k, v in row.items()})

    print(json.dumps({
        "ticker": ticker_sym.upper(),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "insider_transactions": rows,
    }, ensure_ascii=False, indent=2))


def cmd_calendar(ticker_sym: str):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())

    cal = t.calendar
    earnings_dates = t.earnings_dates

    cal_out = {}
    if cal:
        for k, v in cal.items():
            cal_out[str(k)] = str(v) if not isinstance(v, (int, float)) else safe(v)

    dates_out = []
    if earnings_dates is not None and not earnings_dates.empty:
        for idx, row in earnings_dates.head(6).iterrows():
            dates_out.append({
                "date": str(idx)[:10],
                "eps_estimate": safe(row.get("EPS Estimate")),
                "reported_eps": safe(row.get("Reported EPS")),
                "surprise_pct": safe(row.get("Surprise(%)")),
            })

    print(json.dumps({
        "ticker": ticker_sym.upper(),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "calendar": cal_out,
        "earnings_dates": dates_out,
    }, ensure_ascii=False, indent=2))


def cmd_history(ticker_sym: str, period: str = "1y"):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())
    df = t.history(period=period, auto_adjust=True)

    if df.empty:
        print(json.dumps({"error": f"No history for {ticker_sym}"}))
        return

    rows = []
    for idx, row in df.iterrows():
        rows.append({
            "date": str(idx)[:10],
            "open": safe(row["Open"]),
            "high": safe(row["High"]),
            "low": safe(row["Low"]),
            "close": safe(row["Close"]),
            "volume": safe(row["Volume"], 0),
        })

    print(json.dumps({
        "ticker": ticker_sym.upper(),
        "period": period,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(rows),
        "history": rows,
    }, ensure_ascii=False, indent=2))


def cmd_analyst(ticker_sym: str):
    import yfinance as yf
    t = yf.Ticker(ticker_sym.upper())

    recs = t.recommendations
    upgrades = t.upgrades_downgrades

    recs_list = []
    if recs is not None and not recs.empty:
        for idx, row in recs.head(20).iterrows():
            recs_list.append({
                "date": str(idx)[:10],
                "firm": str(row.get("Firm", "")),
                "to_grade": str(row.get("To Grade", "")),
                "from_grade": str(row.get("From Grade", "")),
                "action": str(row.get("Action", "")),
            })

    upgrades_list = []
    if upgrades is not None and not upgrades.empty:
        for idx, row in upgrades.head(20).iterrows():
            upgrades_list.append({
                "date": str(idx)[:10],
                "firm": str(row.get("Firm", "")),
                "to_grade": str(row.get("To Grade", "")),
                "from_grade": str(row.get("From Grade", "")),
                "action": str(row.get("Action", "")),
            })

    info = t.info
    print(json.dumps({
        "ticker": ticker_sym.upper(),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "consensus": {
            "recommendation": info.get("recommendationKey"),
            "mean_rating": safe(info.get("recommendationMean")),
            "target_mean": safe(info.get("targetMeanPrice")),
            "target_high": safe(info.get("targetHighPrice")),
            "target_low": safe(info.get("targetLowPrice")),
            "analyst_count": info.get("numberOfAnalystOpinions"),
        },
        "recent_ratings": recs_list,
        "upgrades_downgrades": upgrades_list,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Yahoo Finance Bridge — Investment Operating System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/yfinance_bridge.py price NVDA
  python tools/yfinance_bridge.py portfolio
  python tools/yfinance_bridge.py info SOFI
  python tools/yfinance_bridge.py financials SOFI --quarterly
  python tools/yfinance_bridge.py holders NVDA
  python tools/yfinance_bridge.py insider SOFI
  python tools/yfinance_bridge.py calendar NVDA
  python tools/yfinance_bridge.py history RKLB --period 6mo
  python tools/yfinance_bridge.py analyst NVDA
        """
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # price
    p = sub.add_parser("price", help="ราคาล่าสุด + P/L ถ้าอยู่ในพอร์ต")
    p.add_argument("ticker", help="Stock ticker เช่น NVDA")

    # portfolio
    sub.add_parser("portfolio", help="ราคาสดพอร์ตทั้งหมด + P/L ทุกตัว")

    # info
    p = sub.add_parser("info", help="ข้อมูลพื้นฐานครบ: P/E, EPS, Revenue, Analyst Target ฯลฯ")
    p.add_argument("ticker")

    # financials
    p = sub.add_parser("financials", help="งบการเงิน: Income Statement, Balance Sheet, Cash Flow")
    p.add_argument("ticker")
    p.add_argument("--quarterly", action="store_true", help="ดึงรายไตรมาสแทนรายปี")

    # holders
    p = sub.add_parser("holders", help="Institutional holders และ Major holders")
    p.add_argument("ticker")

    # insider
    p = sub.add_parser("insider", help="Insider transactions (CEO, CFO, Directors)")
    p.add_argument("ticker")

    # calendar
    p = sub.add_parser("calendar", help="Earnings dates และ Dividend calendar")
    p.add_argument("ticker")

    # history
    p = sub.add_parser("history", help="ราคาประวัติศาสตร์ OHLCV")
    p.add_argument("ticker")
    p.add_argument("--period", default="1y",
                   help="1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max (default: 1y)")

    # analyst
    p = sub.add_parser("analyst", help="Analyst recommendations และ Upgrades/Downgrades")
    p.add_argument("ticker")

    args = parser.parse_args()

    if args.command == "price":
        cmd_price(args.ticker)
    elif args.command == "portfolio":
        cmd_portfolio()
    elif args.command == "info":
        cmd_info(args.ticker)
    elif args.command == "financials":
        cmd_financials(args.ticker, args.quarterly)
    elif args.command == "holders":
        cmd_holders(args.ticker)
    elif args.command == "insider":
        cmd_insider(args.ticker)
    elif args.command == "calendar":
        cmd_calendar(args.ticker)
    elif args.command == "history":
        cmd_history(args.ticker, args.period)
    elif args.command == "analyst":
        cmd_analyst(args.ticker)


if __name__ == "__main__":
    main()
