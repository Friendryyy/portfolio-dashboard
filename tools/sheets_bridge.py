#!/usr/bin/env python3
"""
Google Sheets Portfolio Bridge — real-time portfolio reader for Claude Code.

Usage:
    python tools/sheets_bridge.py portfolio          # Full portfolio table
    python tools/sheets_bridge.py holding RKLB       # Single ticker detail
    python tools/sheets_bridge.py summary            # Portfolio totals only
"""

import sys
import json
import argparse
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SPREADSHEET_ID = "1JC_SMTlWNBwuqDne3MJ229CAOWRw5KMDZeQM8_Vcr4s"
PORTFOLIO_RANGE = "A:K"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-api-python-client google-auth-oauthlib"}))
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")
    creds_path = os.path.join(script_dir, "credentials.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("sheets", "v4", credentials=creds)


EXPECTED_COLUMNS = {
    "Tracker", "Company Name", "Shares", " Avg. Cost ",
    "Share Price", "Total Equity", " Total Cost ",
    "Total Gain/Loss", "%Gain/Loss", "Alocation",
}


def _fetch_rows():
    try:
        service = _get_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=PORTFOLIO_RANGE
        ).execute()
    except Exception as e:
        print(json.dumps({"error": f"Google Sheets API error: {e}"}))
        sys.exit(1)

    values = result.get("values", [])
    if not values:
        return [], {}

    headers = values[0]
    missing = EXPECTED_COLUMNS - set(headers)
    if missing:
        print(f"[sheets_bridge] WARNING: Missing expected columns: {missing}", file=sys.stderr)
    holdings = []
    summary = {}

    for row in values[1:]:
        row_padded = row + [""] * (len(headers) - len(row))
        r = dict(zip(headers, row_padded))
        ticker = r.get("Tracker", "").strip()

        if ticker:
            holdings.append({
                "ticker":      ticker,
                "name":        r.get("Company Name", "").strip(),
                "industry":    r.get("Industry", "").strip(),
                "shares":      r.get("Shares", "").strip(),
                "avg_cost":    r.get(" Avg. Cost ", "").strip(),
                "price":       r.get("Share Price", "").strip(),
                "equity":      r.get("Total Equity", "").strip(),
                "cost":        r.get(" Total Cost ", "").strip(),
                "gain_loss":   r.get("Total Gain/Loss", "").strip(),
                "gain_pct":    r.get("%Gain/Loss", "").strip(),
                "allocation":  r.get("Alocation", "").strip(),
            })
        else:
            # Summary rows use " Total Cost " column as label
            label = r.get(" Total Cost ", "").strip()
            val_usd = r.get("Total Gain/Loss", "").strip()
            val_thb = r.get("%Gain/Loss", "").strip()
            if label and val_usd:
                summary[label] = {"usd": val_usd, "thb": val_thb}

    return holdings, summary


def cmd_portfolio(_args):
    holdings, summary = _fetch_rows()
    print(json.dumps({
        "source": "Google Sheets (live)",
        "spreadsheet_id": SPREADSHEET_ID,
        "holdings": holdings,
        "summary": summary,
        "count": len(holdings)
    }, ensure_ascii=False, indent=2))


def cmd_holding(args):
    ticker = args.ticker.upper()
    holdings, summary = _fetch_rows()
    match = next((h for h in holdings if h["ticker"] == ticker), None)
    if not match:
        print(json.dumps({"error": f"{ticker} not found in portfolio", "available": [h["ticker"] for h in holdings]}))
        sys.exit(1)
    print(json.dumps({"source": "Google Sheets (live)", "holding": match}, ensure_ascii=False, indent=2))


def cmd_summary(_args):
    _holdings, summary = _fetch_rows()
    print(json.dumps({"source": "Google Sheets (live)", "summary": summary}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Google Sheets Portfolio Bridge")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("portfolio", help="Full portfolio from Google Sheets")
    sub.add_parser("summary",   help="Portfolio totals only")
    p_h = sub.add_parser("holding", help="Single ticker detail")
    p_h.add_argument("ticker", help="Ticker symbol e.g. RKLB")

    args = parser.parse_args()
    {"portfolio": cmd_portfolio, "summary": cmd_summary, "holding": cmd_holding}[args.command](args)


if __name__ == "__main__":
    main()
