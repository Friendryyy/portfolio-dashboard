#!/usr/bin/env python3
"""
YouTube Research & Google Sheets Bridge — Investment Operating System
Usage:
  python tools/youtube_to_sheets.py search "NVDA stock analysis" [--max 10]
  python tools/youtube_to_sheets.py read-sheet [--range "Portfolio!A:H"] [--id SHEET_ID]
  python tools/youtube_to_sheets.py log-research NVDA "https://youtube.com/..." [--id SHEET_ID]
  python tools/youtube_to_sheets.py setup

Environment variables (optional):
  GOOGLE_SPREADSHEET_ID  — default Spreadsheet ID for portfolio sheet
"""
import sys
import json
import argparse
import os
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Config — override via env var or --id flag
# ---------------------------------------------------------------------------
DEFAULT_SPREADSHEET_ID = os.environ.get("GOOGLE_SPREADSHEET_ID", "")
RESEARCH_LOG_RANGE = "YouTube_Research!A:F"   # sheet tab for logging research videos
PORTFOLIO_RANGE = "Portfolio!A:H"             # sheet tab for portfolio data

# ---------------------------------------------------------------------------
# YouTube search via Innertube API (no API key required)
# ---------------------------------------------------------------------------
_INNERTUBE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_INNERTUBE_PAYLOAD_BASE = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20240101.00.00",
            "hl": "en",
            "gl": "US",
        }
    }
}


def _extract_text(obj: dict, *keys) -> str:
    for key in keys:
        runs = obj.get(key, {}).get("runs", [])
        if runs:
            return runs[0].get("text", "")
        simple = obj.get(key, {}).get("simpleText", "")
        if simple:
            return simple
    return ""


def _search_youtube_innertube(query: str, max_results: int = 10) -> list:
    payload = {**_INNERTUBE_PAYLOAD_BASE, "query": query}
    try:
        resp = requests.post(
            "https://www.youtube.com/youtubei/v1/search",
            headers=_INNERTUBE_HEADERS,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"HTTP error contacting YouTube: {e}")

    data = resp.json()
    sections = (
        data.get("contents", {})
        .get("twoColumnSearchResultsRenderer", {})
        .get("primaryContents", {})
        .get("sectionListRenderer", {})
        .get("contents", [])
    )

    videos = []
    for section in sections:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            vr = item.get("videoRenderer", {})
            if not vr:
                continue
            video_id = vr.get("videoId", "")
            title = _extract_text(vr, "title")
            channel = _extract_text(vr, "ownerText", "longBylineText")
            published = _extract_text(vr, "publishedTimeText")
            views = _extract_text(vr, "viewCountText", "shortViewCountText")
            duration = _extract_text(vr, "lengthText")
            if video_id and title:
                videos.append({
                    "title": title,
                    "channel": channel,
                    "published": published,
                    "views": views,
                    "duration": duration,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "query": query,
                })
            if len(videos) >= max_results:
                return videos
    return videos


def cmd_search(args):
    try:
        videos = _search_youtube_innertube(args.query, args.max)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"query": args.query, "count": len(videos), "videos": videos}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Google Sheets auth helper
# ---------------------------------------------------------------------------
def _get_sheets_service(spreadsheet_id):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print(json.dumps({"error": "Google API packages missing. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"}))
        sys.exit(1)

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")
    credentials_path = os.path.join(script_dir, "credentials.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(json.dumps({
                    "error": "credentials.json not found",
                    "fix": f"Download OAuth credentials from Google Cloud Console and save to: {credentials_path}",
                    "steps": [
                        "1. Go to console.cloud.google.com",
                        "2. Create project → Enable Google Sheets API",
                        "3. APIs & Services → Credentials → Create OAuth 2.0 Client ID (Desktop app)",
                        "4. Download JSON → rename to credentials.json → place in tools/",
                        "5. Run this command again — browser will open for login",
                    ]
                }, ensure_ascii=False, indent=2))
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    return service


# ---------------------------------------------------------------------------
# Read Google Sheets
# ---------------------------------------------------------------------------
def cmd_read_sheet(args):
    sheet_id = args.id or DEFAULT_SPREADSHEET_ID
    if not sheet_id:
        print(json.dumps({
            "error": "No SPREADSHEET_ID provided",
            "fix": "Pass --id YOUR_SHEET_ID or set env var GOOGLE_SPREADSHEET_ID",
            "example": 'python tools/youtube_to_sheets.py read-sheet --id 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms'
        }, ensure_ascii=False))
        sys.exit(1)

    range_name = args.range
    service = _get_sheets_service(sheet_id)

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    values = result.get("values", [])
    if not values:
        print(json.dumps({"sheet_id": sheet_id, "range": range_name, "rows": []}))
        return

    headers = values[0] if values else []
    rows = []
    for row in values[1:]:
        row_padded = row + [""] * (len(headers) - len(row))
        rows.append(dict(zip(headers, row_padded)))

    print(json.dumps({
        "sheet_id": sheet_id,
        "range": range_name,
        "count": len(rows),
        "headers": headers,
        "rows": rows
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Log research video URL to Sheets
# ---------------------------------------------------------------------------
def cmd_log_research(args):
    sheet_id = args.id or DEFAULT_SPREADSHEET_ID
    if not sheet_id:
        print(json.dumps({"error": "No SPREADSHEET_ID — pass --id or set GOOGLE_SPREADSHEET_ID"}))
        sys.exit(1)

    service = _get_sheets_service(sheet_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [[now, args.ticker.upper(), args.url, args.note or "", "", ""]]

    try:
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=RESEARCH_LOG_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": row}
        ).execute()
        print(json.dumps({"status": "ok", "logged": {"ticker": args.ticker.upper(), "url": args.url, "date": now}}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


# ---------------------------------------------------------------------------
# Setup instructions
# ---------------------------------------------------------------------------
def cmd_setup(args):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, "credentials.json")
    token_path = os.path.join(script_dir, "token.json")

    creds_exists = os.path.exists(credentials_path)
    token_exists = os.path.exists(token_path)

    print(json.dumps({
        "status": {
            "credentials.json": "FOUND" if creds_exists else "MISSING",
            "token.json": "FOUND" if token_exists else "MISSING (will be created on first login)",
            "GOOGLE_SPREADSHEET_ID env": os.environ.get("GOOGLE_SPREADSHEET_ID", "NOT SET"),
        },
        "setup_steps": [
            "Step 1: Go to console.cloud.google.com",
            "Step 2: Create a new project (e.g. 'Investment Research')",
            "Step 3: Enable APIs: 'Google Sheets API' + 'YouTube Data API v3'",
            "Step 4: APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID",
            "Step 5: Application type = Desktop app → Download JSON",
            f"Step 6: Rename downloaded file to 'credentials.json' and place in: {script_dir}",
            "Step 7: Run any command (e.g. read-sheet) — browser will open for Google login",
            "Step 8: Set GOOGLE_SPREADSHEET_ID in your environment or pass --id flag each time",
        ],
        "examples": [
            'python tools/youtube_to_sheets.py search "NVDA stock analysis 2026" --max 10',
            'python tools/youtube_to_sheets.py read-sheet --id YOUR_SHEET_ID --range "Portfolio!A:H"',
            'python tools/youtube_to_sheets.py log-research NVDA "https://youtube.com/watch?v=xxx" --note "Q1 2026 earnings review"',
        ]
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="YouTube Research & Google Sheets Bridge for Investment OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Search YouTube videos (no API key needed)")
    p_search.add_argument("query", help="Search query, e.g. 'NVDA stock analysis 2026'")
    p_search.add_argument("--max", type=int, default=10, help="Max results (default: 10)")

    # read-sheet
    p_read = sub.add_parser("read-sheet", help="Read data from Google Sheets")
    p_read.add_argument("--range", default=PORTFOLIO_RANGE, help=f"Sheet range (default: {PORTFOLIO_RANGE})")
    p_read.add_argument("--id", default="", help="Spreadsheet ID (overrides env var)")

    # log-research
    p_log = sub.add_parser("log-research", help="Log a YouTube URL to research sheet")
    p_log.add_argument("ticker", help="Stock ticker, e.g. NVDA")
    p_log.add_argument("url", help="YouTube URL")
    p_log.add_argument("--note", default="", help="Optional note")
    p_log.add_argument("--id", default="", help="Spreadsheet ID (overrides env var)")

    # setup
    sub.add_parser("setup", help="Show setup instructions and check credentials")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "read-sheet":
        cmd_read_sheet(args)
    elif args.command == "log-research":
        cmd_log_research(args)
    elif args.command == "setup":
        cmd_setup(args)


if __name__ == "__main__":
    main()
