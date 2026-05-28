#!/usr/bin/env python3
"""
Portfolio Dashboard — Streamlit web app for investment portfolio tracking.
Run: streamlit run tools/portfolio_dashboard.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── Paths ──────────────────────────────────────────────────────────────────────
TOOLS_DIR = Path(__file__).parent
TARGETS_FILE = TOOLS_DIR / "portfolio_targets.json"
SPREADSHEET_ID = "1JC_SMTlWNBwuqDne3MJ229CAOWRw5KMDZeQM8_Vcr4s"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEETS_SUMMARY = {}


@st.cache_data(ttl=3600)
def get_usd_thb() -> float:
    try:
        import yfinance as yf
        hist = yf.Ticker("USDTHB=X").history(period="2d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return 35.0


def fmt_usd(val: float) -> str:
    return f"${val:,.2f}"


def fmt_thb(val: float, fx: float) -> str:
    return f"฿{val * fx:,.0f}"


def fmt_money(val: float, fx: float, show_thb: bool) -> str:
    if show_thb:
        return f"฿{val * fx:,.0f}"
    return f"${val:,.2f}"

# ── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💼 My Portfolio",
    layout="wide",
    page_icon="💼",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

  /* ── Design Tokens ── */
  :root {
    --bg:         #EDF4F9; /* Soothing sky base */
    --surface:    #FFFFFF; /* Crisp white cards */
    --elevated:   #F1F6FA; /* Light pastel blue-grey */
    --overlay:    #E2EDF5; /* Muted pastel blue */
    --border:     rgba(180, 200, 220, 0.45); /* Soft slate blue border */
    --border-hi:  rgba(56, 189, 248, 0.6); /* Soft sky blue glow */
    --violet:     #0284C7; /* Primary ocean blue */
    --cyan:       #06B6D4; /* Secondary teal-sky blue */
    --gold:       #D97706; /* Rich warm amber */
    --rose:       #EF4444; /* Vivid soft red */
    --blue:       #38BDF8; /* Sky blue */
    --green:      #10B981; /* Emerald green */
    --txt1:       #1E293B; /* Deep slate navy */
    --txt2:       #475569; /* Slate grey */
    --txt3:       #64748B; /* Muted slate text */
  }

  /* ── Base ── */
  .stApp {
    background: var(--bg);
    background-image:
      radial-gradient(ellipse at 15% 0%,   rgba(2,132,199,0.06) 0%, transparent 55%),
      radial-gradient(ellipse at 85% 100%, rgba(13,148,136,0.04)  0%, transparent 55%);
    font-family: 'Space Grotesk', sans-serif;
  }
  * { box-sizing: border-box; }

  /* ── Header ── */
  .portfolio-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 26px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(148,163,184,0.04);
  }
  .portfolio-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--violet) 0%, var(--cyan) 60%, var(--blue) 100%);
  }
  .header-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--txt1);
    letter-spacing: -0.4px;
    margin: 0;
  }
  .header-sub { color: var(--txt3); font-size: 0.78rem; margin-top: 3px; letter-spacing: 0.2px; }

  /* ── Metric cards ── */
  .metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 15px 18px 15px 22px;
    margin: 4px 0;
    position: relative;
    overflow: hidden;
    transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
    box-shadow: 0 4px 12px rgba(148,163,184,0.03);
  }
  .metric-card::after {
    content: '';
    position: absolute;
    left: 0; top: 12%; bottom: 12%;
    width: 3.5px;
    border-radius: 0 3.5px 3.5px 0;
  }
  .metric-card.card-value::after  { background: var(--violet); box-shadow: 0 0 6px rgba(2,132,199,0.4); }
  .metric-card.card-cost::after   { background: var(--txt3); }
  .metric-card.card-gain-pos::after { background: var(--green); box-shadow: 0 0 6px rgba(16,185,129,0.4); }
  .metric-card.card-gain-neg::after { background: var(--rose); box-shadow: 0 0 6px rgba(239,68,68,0.4); }
  .metric-card.card-hold::after   { background: var(--gold); }
  .metric-card.card-cash::after   { background: var(--blue); }
  .metric-card.card-gain-pos { border-color: rgba(16,185,129,0.22); }
  .metric-card:hover { border-color: var(--border-hi); transform: translateY(-1.5px); box-shadow: 0 6px 16px rgba(148,163,184,0.06); }

  .mc-label {
    font-size: 0.62rem;
    color: var(--txt3);
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
    margin-bottom: 7px;
  }
  .mc-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.42rem;
    font-weight: 700;
    color: var(--txt1);
    line-height: 1.1;
    letter-spacing: -0.5px;
  }
  .mc-delta { font-size: 0.76rem; font-family: 'JetBrains Mono', monospace; margin-top: 5px; font-weight: 600; }
  .pos { color: var(--green); }
  .neg { color: var(--rose); }
  .neu { color: var(--violet); }

  /* ── Section titles ── */
  .section-title {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--txt2);
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin: 22px 0 10px;
    padding-left: 10px;
    border-left: 2.5px solid var(--violet);
  }

  /* ── Glass card ── */
  .glass-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 6px 0;
    box-shadow: 0 4px 12px rgba(148,163,184,0.03);
  }

  /* ── Allocation rows ── */
  .alloc-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 11px 16px;
    margin: 4px 0;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 2px 8px rgba(148,163,184,0.02);
  }
  .alloc-row:hover { border-color: var(--border-hi); box-shadow: 0 4px 12px rgba(148,163,184,0.04); }
  .bar-track {
    background: var(--elevated);
    border-radius: 3px;
    height: 6px;
    width: 100%;
    margin-top: 7px;
    overflow: hidden;
  }
  .bar-fill { height: 6px; border-radius: 3px; }

  /* ── Transaction rows ── */
  .tx-group-header {
    background: var(--elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 16px;
    margin: 8px 0 2px;
  }
  .tx-row {
    background: var(--surface);
    border-left: 3.5px solid transparent;
    border-radius: 0 6px 6px 0;
    padding: 7px 16px 7px 13px;
    margin: 2px 0 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.79rem;
    box-shadow: 0 1px 4px rgba(148,163,184,0.01);
  }
  .tx-buy  { border-left-color: var(--green); }
  .tx-sell { border-left-color: var(--rose); }
  .tx-div  { border-left-color: var(--gold); }

  /* ── DCA card ── */
  .dca-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    line-height: 2.05;
    box-shadow: 0 4px 12px rgba(148,163,184,0.03);
  }
  .dca-sep { border-top: 1px solid var(--border); margin: 12px 0; }

  /* ── Streamlit overrides ── */
  div[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    box-shadow: 0 4px 12px rgba(148,163,184,0.03) !important;
  }
  .stDataFrame { border-radius: 10px; border: 1px solid var(--border); }

  /* Tab bar — pill style */
  div[data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px 5px !important;
    border: 1px solid var(--border) !important;
    gap: 3px !important;
    box-shadow: 0 2px 8px rgba(148,163,184,0.02) !important;
  }
  button[data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.81rem !important;
    font-weight: 500 !important;
    color: var(--txt2) !important;
    border-radius: 7px !important;
    padding: 6px 13px !important;
    border-bottom: none !important;
    transition: all 0.15s !important;
  }
  button[data-baseweb="tab"]:hover {
    color: var(--txt1) !important;
    background: var(--elevated) !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--violet) !important;
    color: #ffffff !important;
    border-bottom: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(2,132,199,0.3) !important;
  }
  div[data-baseweb="tab-highlight"],
  div[data-baseweb="tab-border"] { display: none !important; }

  .stCaption { color: var(--txt3) !important; font-size: 0.73rem !important; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }
  section[data-testid="stSidebar"] > div { background: transparent !important; }

  /* Buttons */
  .stButton > button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--txt2) !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 3px rgba(148,163,184,0.03) !important;
  }
  .stButton > button:hover {
    border-color: var(--border-hi) !important;
    color: var(--txt1) !important;
    background: var(--elevated) !important;
  }
  .stDownloadButton > button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--txt2) !important;
    border-radius: 8px !important;
    font-size: 1.0rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 3px rgba(148,163,184,0.03) !important;
  }
  .stDownloadButton > button:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    background: var(--elevated) !important;
  }

  /* Select / Input */
  .stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--txt1) !important;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2.5px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--border-hi); }

  /* Expander */
  details summary {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--txt2) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.84rem !important;
    box-shadow: 0 1px 4px rgba(148,163,184,0.01) !important;
  }
  details[open] summary { border-color: var(--border-hi) !important; color: var(--txt1) !important; }

  /* ── News Tab ── */
  .news-date-header {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    color: var(--txt2);
    margin: 24px 0 10px;
    padding: 0 0 7px 10px;
    border-left: 2.5px solid var(--violet);
    border-bottom: 1px solid var(--border);
  }
  .news-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px 17px;
    margin-bottom: 8px;
    transition: border-color 0.15s, transform 0.1s, box-shadow 0.15s;
    box-shadow: 0 2px 8px rgba(148,163,184,0.02);
  }
  .news-card:hover { border-color: var(--border-hi); transform: translateX(2.5px); box-shadow: 0 4px 12px rgba(148,163,184,0.05); }
  .news-card-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--txt1);
    margin-bottom: 8px;
    line-height: 1.45;
  }
  .news-tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    margin-right: 5px;
    margin-bottom: 2px;
    letter-spacing: 0.3px;
  }
  .news-tag-ticker {
    background: rgba(2,132,199,0.08);
    color: var(--violet);
    border: 1px solid rgba(2,132,199,0.22);
  }
  .news-tag-type { border: none; }
  .news-content-wrapper {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 8px;
    box-shadow: 0 4px 12px rgba(148,163,184,0.03);
  }

  /* Reader meta bar */
  .reader-meta-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 20px;
    position: relative;
    box-shadow: 0 4px 16px rgba(148,163,184,0.04);
  }
  .reader-meta-bar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: 12px 12px 0 0;
    background: linear-gradient(90deg, var(--violet), var(--cyan));
  }
  .reader-title { font-size: 1.35rem; font-weight: 700; color: var(--txt1); line-height: 1.4; margin-bottom: 10px; }
  .reader-date  { color: var(--txt3); font-size: 0.78rem; margin-bottom: 8px; }
  .reader-body  { max-width: 860px; color: var(--txt1); }
</style>
""", unsafe_allow_html=True)


# ── Google Sheets service ────────────────────────────────────────────────────────
@st.cache_resource
def _sheets_service():
    try:
        from googleapiclient.discovery import build
    except ImportError:
        st.error("Run: pip install google-api-python-client google-auth-oauthlib")
        st.stop()

    # ── Cloud mode: use Service Account from st.secrets ──────────────────────
    try:
        has_secret = "gcp_service_account" in st.secrets
    except Exception:
        has_secret = False
    if has_secret:
        from google.oauth2 import service_account
        sa_info = dict(st.secrets["gcp_service_account"])
        # Fix literal \n in private_key (common Streamlit Secrets paste issue)
        if "private_key" in sa_info:
            sa_info["private_key"] = sa_info["private_key"].replace("\\n", "\n")
        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=SCOPES,
        )
        return build("sheets", "v4", credentials=creds)

    # ── Local mode: OAuth2 flow with credentials.json ─────────────────────────
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    token_path = TOOLS_DIR / "token.json"
    creds_path = TOOLS_DIR / "credentials.json"
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                token_path.unlink(missing_ok=True)
                creds = None
        if not creds or not creds.valid:
            if not creds_path.exists():
                st.error(f"credentials.json not found at {creds_path}")
                st.stop()
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("sheets", "v4", credentials=creds)


def _read_sheet(range_: str) -> list[list]:
    import time
    retries = 3
    delay = 1.0
    for attempt in range(retries):
        try:
            svc = _sheets_service()
            result = svc.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=range_
            ).execute()
            return result.get("values", [])
        except Exception as e:
            # Handle Google Auth expiration immediately
            if any(k in str(e) for k in ("invalid_grant", "Token", "revoked")):
                _sheets_service.clear()
                st.error("🔑 Google auth expired — please refresh the page.")
                st.stop()
            
            # Detect transient socket/connection errors
            err_str = str(e).lower()
            is_transient = any(k in err_str or k in str(type(e)).lower() for k in (
                "connection", "timeout", "socket", "winerror", "10053", "10054", "aborted", "reset"
            ))
            
            if is_transient and attempt < retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
                continue
            
            # On the final attempt, display a clean user-facing error and stop cleanly
            if attempt == retries - 1:
                st.error("📡 Connection to Google Sheets API failed. Please check your internet connection or refresh the page.")
                st.stop()
            raise


# ── Parse helpers ─────────────────────────────────────────────────────────────────
def _parse_money(s: str) -> float:
    if not s:
        return 0.0
    cleaned = re.sub(r"[^\d.\-]", "", str(s))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_thai_date(s: str) -> datetime | None:
    try:
        parts = s.strip().split("/")
        if len(parts) == 3:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            if y > 2400:
                y -= 543          # full Thai Buddhist year → Gregorian
            elif 1940 <= y <= 2100:
                y += 57           # Google Sheets auto-shortened "69"→1969; recover: +600-543=+57
            return datetime(y, m, d)
    except Exception:
        pass
    return None


# ── Portfolio data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _load_portfolio_raw() -> tuple[list[dict], float, dict]:
    """Read all computed values directly from Google Sheets (single source of truth)."""
    values = _read_sheet("Portfolio!A:K")
    if not values:
        return [], 0.0, {}
    headers = values[0]
    rows = []
    summary_total = 0.0
    summary_cash_pct = 0.0
    sheets_cash_val = 0.0
    sheets_summary = {}
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        r = dict(zip(headers, padded))
        ticker = r.get("Tracker", "").strip()
        if ticker:
            shares    = _parse_money(r.get("Shares", ""))
            avg_cost  = _parse_money(r.get(" Avg. Cost ", ""))
            if shares > 0 and avg_cost > 0:
                gain_pct_raw = r.get("%Gain/Loss", "").replace("%", "").strip()
                alloc_raw    = r.get("Alocation",  "").replace("%", "").strip()
                try:
                    gain_pct = float(gain_pct_raw)
                except Exception:
                    gain_pct = 0.0
                try:
                    allocation = float(alloc_raw)
                except Exception:
                    allocation = 0.0
                rows.append({
                    "ticker":      ticker,
                    "name":        r.get("Company Name", ticker).strip() or ticker,
                    "industry":    r.get("Industry", "").strip(),
                    "shares":      shares,
                    "avg_cost":    avg_cost,
                    "price":       _parse_money(r.get("Share Price", "")),
                    "total_value": _parse_money(r.get("Total Equity", "")),
                    "total_cost":  _parse_money(r.get(" Total Cost ", "")),
                    "gain_loss":   _parse_money(r.get("Total Gain/Loss", "")),
                    "gain_pct":    gain_pct,
                    "allocation":  allocation,
                })
        else:
            # Summary rows: label in " Total Cost ", value in "Total Gain/Loss"
            label = r.get(" Total Cost ", "").strip()
            val   = r.get("Total Gain/Loss", "").strip()
            val_thb = r.get("%Gain/Loss", "").strip()
            if label:
                if label == "Cash Flow":
                    if "%" in val or (val.replace(".", "").replace("-", "").strip().isdigit() and float(val) < 1.0):
                        try:
                            summary_cash_pct = float(val.replace("%", "").strip()) / 100
                        except Exception:
                            pass
                    else:
                        try:
                            sheets_cash_val = _parse_money(val)
                            sheets_summary["Cash Flow"] = {
                                "usd": sheets_cash_val,
                                "thb": _parse_money(val_thb) if val_thb else 0.0
                            }
                        except Exception:
                            pass
                else:
                    sheets_summary[label] = {
                        "usd": _parse_money(val),
                        "thb": _parse_money(val_thb) if val_thb else 0.0
                    }
            if label == "Total":
                summary_total = _parse_money(val)
            elif label == "Cash Flow" and ("%" in val or (val.replace(".", "").replace("-", "").strip().isdigit() and float(val) < 1.0)):
                try:
                    summary_cash_pct = float(val.replace("%", "").strip()) / 100
                except Exception:
                    pass
    if sheets_cash_val > 0:
        sheets_cash = sheets_cash_val
    elif summary_total > 0 and summary_cash_pct > 0:
        total_equity_sum = sum(r["total_value"] for r in rows)
        sheets_cash = round(summary_total - total_equity_sum, 2)
    else:
        sheets_cash = 0.0
    return rows, sheets_cash, sheets_summary


def load_portfolio(cash: float = 0.0) -> tuple[pd.DataFrame, dict]:
    """Build portfolio DataFrame using Sheets as single source of truth."""
    rows, sheets_cash, sheets_summary = _load_portfolio_raw()
    if not rows:
        return pd.DataFrame(), {}
    effective_cash = sheets_cash if sheets_cash > 0 else cash
    df = pd.DataFrame(rows)

    # Load targets to append missing targeted tickers with 0.0 values
    try:
        saved = load_targets()
        saved_tgts = saved.get("targets", {})
        for ticker in saved_tgts:
            if ticker != "CASH" and ticker not in df["ticker"].values:
                zero_row = pd.DataFrame([{
                    "ticker":      ticker,
                    "name":        ticker,
                    "industry":    "Other",
                    "shares":      0.0,
                    "avg_cost":    0.0,
                    "price":       0.0,
                    "total_cost":  0.0,
                    "total_value": 0.0,
                    "gain_loss":   0.0,
                    "gain_pct":    0.0,
                    "allocation":  0.0,
                }])
                df = pd.concat([df, zero_row], ignore_index=True)
    except Exception:
        pass

    # Add cash row — allocation = remainder after stocks
    if effective_cash > 0:
        stock_alloc = df["allocation"].sum()
        cash_alloc  = round(max(0.0, 100.0 - stock_alloc), 2)
        cash_row = pd.DataFrame([{
            "ticker":      "CASH",
            "name":        "Cash / USD",
            "industry":    "Cash",
            "shares":      effective_cash,
            "avg_cost":    1.0,
            "price":       1.0,
            "total_cost":  effective_cash,
            "total_value": effective_cash,
            "gain_loss":   0.0,
            "gain_pct":    0.0,
            "allocation":  cash_alloc,
        }])
        df = pd.concat([df, cash_row], ignore_index=True)

    return df, sheets_summary


@st.cache_data(ttl=300)
def _load_realized_breakdown_raw() -> tuple[list[dict], dict]:
    """Read the realized profit breakdown from the spreadsheet tab."""
    values = _read_sheet("Realized Profit Breakdown !A:D")
    if not values or len(values) < 2:
        return [], {}
    headers = values[0]
    rows = []
    total = {}
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        r = dict(zip(headers, padded))
        ticker = r.get("ชื่อย่อหุ้น (Ticker)", "").strip()
        if not ticker:
            continue
        if "รวมสุทธิ" in ticker or "Total" in ticker:
            total = {
                "sells": _parse_money(r.get("ยอดเงินที่ขายได้ทั้งหมด (Total Sells)", "")),
                "cost": _parse_money(r.get("ต้นทุนของหุ้นส่วนที่ขายไป (Cost of Sells)", "")),
                "profit": _parse_money(r.get("💰 กำไร/ขาดทุน สุทธิ (Net Realized Profit)", ""))
            }
        else:
            rows.append({
                "ticker": ticker,
                "sells": _parse_money(r.get("ยอดเงินที่ขายได้ทั้งหมด (Total Sells)", "")),
                "cost": _parse_money(r.get("ต้นทุนของหุ้นส่วนที่ขายไป (Cost of Sells)", "")),
                "profit": _parse_money(r.get("💰 กำไร/ขาดทุน สุทธิ (Net Realized Profit)", ""))
            })
    return rows, total


def load_realized_breakdown() -> tuple[pd.DataFrame, dict]:
    """Build realized breakdown DataFrame and total dictionary."""
    rows, total = _load_realized_breakdown_raw()
    if not rows:
        return pd.DataFrame(), {}
    return pd.DataFrame(rows), total


# ── Transaction data ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_transactions() -> pd.DataFrame:
    values = _read_sheet("Transaction!A:H")
    if not values or len(values) < 2:
        return pd.DataFrame()
    headers = values[0]
    rows = []
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        r = dict(zip(headers, padded))
        ticker = r.get("Ticker", "").strip()
        if not ticker:
            continue
        qty = _parse_money(r.get("Quantity", ""))
        price = _parse_money(r.get("Price", ""))
        total = _parse_money(r.get(" Total Amount ", ""))
        tx_type = r.get("Transaction", "").strip()
        date_raw = r.get("Date", "").strip()
        date = _parse_thai_date(date_raw)
        dividend_val = _parse_money(r.get("Dividend", ""))
        # Dividend DRIP: if qty > 0, count reinvested shares as a Buy entry too
        if tx_type == "Dividend" and qty > 0:
            rows.append({
                "ticker": ticker,
                "name": r.get("Stock Name", ticker).strip(),
                "type": "Buy",
                "date": date, "date_raw": date_raw,
                "qty": qty, "price": price,
                "dividend": dividend_val, "total": total,
                "note": "DRIP",
            })
            tx_type = "Dividend"
            qty = 0  # original dividend row keeps qty=0
        rows.append({
            "ticker": ticker,
            "name": r.get("Stock Name", ticker).strip(),
            "type": tx_type,
            "date": date,
            "date_raw": date_raw,
            "qty": qty,
            "price": price,
            "dividend": dividend_val,
            "total": total,
            "note": "",
        })
    df = pd.DataFrame(rows)
    if not df.empty and "date" in df.columns:
        df = df.sort_values("date", ascending=False, na_position="last")
    return df


# ── Targets / Cash ────────────────────────────────────────────────────────────────
def load_targets() -> dict:
    if TARGETS_FILE.exists():
        with open(TARGETS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"targets": {}, "cash": 0.0}


def save_targets(targets: dict, cash: float):
    existing = load_targets()
    existing["targets"] = targets
    existing["cash"] = cash
    existing["updated"] = datetime.now().isoformat()
    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def get_target_pcts(df: pd.DataFrame, saved: dict) -> dict:
    saved_tgts = saved.get("targets", {})
    return {r["ticker"]: float(saved_tgts.get(r["ticker"], 0.0)) for _, r in df.iterrows()}


# ── Color helpers ─────────────────────────────────────────────────────────────────
def _gc(v: float) -> str:
    return "#059669" if v >= 0 else "#EF4444"


def _sign(v: float) -> str:
    return "+" if v >= 0 else ""


def _plotly_base() -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569", family="Space Grotesk, Inter, sans-serif", size=12),
        margin=dict(t=20, b=20, l=10, r=10),
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.22)"),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)", zerolinecolor="rgba(148, 163, 184, 0.22)"),
    )


PALETTE = ["#6366f1", "#00d4aa", "#ffd166", "#f87171", "#a78bfa",
           "#34d399", "#fb923c", "#60a5fa", "#e879f9", "#4ade80"]

TICKER_COLORS = {
    "NVDA": "#76b900",   # NVIDIA green
    "RKLB": "#00d4aa",   # teal
    "SOFI": "#6366f1",   # indigo
    "GOOGL": "#4285f4",  # Google blue
    "PLTR": "#f87171",   # red
    "AMZN": "#fb923c",   # Amazon orange
    "NVO":  "#e879f9",   # purple
    "UNH":  "#38bdf8",   # sky blue
    "TSM":  "#ffb703",   # TSMC gold-orange
    "BTC":  "#f7931a",   # Bitcoin orange
    "SPCX": "#005288",   # SpaceX blue
    "CASH": "#64748b",   # slate
}

INDICES = {
    "S&P 500 (SPY)":   "SPY",
    "NASDAQ (QQQ)":    "QQQ",
    "Dow Jones (DIA)": "DIA",
    "Russell 2000 (IWM)": "IWM",
}

PERIOD_MAP = {
    "1D":  ("1d",  "5m"),
    "1W":  ("5d",  "1h"),
    "1M":  ("1mo", "1d"),
    "3M":  ("3mo", "1d"),
    "YTD": ("ytd", "1d"),
    "1Y":  ("1y",  "1d"),
    "ALL": ("5y",  "1wk"),
}

CHART_PERIODS = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y"}


@st.cache_data(ttl=3600)
def load_technicals(ticker: str, period: str = "6mo") -> dict:
    """OHLCV + SMA 20/50/200 + RSI(14) + Classic Pivot Points."""
    import yfinance as yf
    try:
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if hist.empty or len(hist) < 21:
            return {}
        close = hist["Close"]
        sma20  = close.rolling(20).mean()
        sma50  = close.rolling(50).mean()
        sma200 = close.rolling(200).mean()
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs   = gain / loss
        rsi  = float((100 - 100 / (1 + rs)).iloc[-1])
        prev = hist.iloc[-2]
        P  = (float(prev["High"]) + float(prev["Low"]) + float(prev["Close"])) / 3
        S1 = 2*P - float(prev["High"])
        R1 = 2*P - float(prev["Low"])
        S2 = P - (float(prev["High"]) - float(prev["Low"]))
        R2 = P + (float(prev["High"]) - float(prev["Low"]))
        hist = hist.copy()
        hist["SMA20"]  = sma20
        hist["SMA50"]  = sma50
        hist["SMA200"] = sma200
        def _last(s): return float(s.iloc[-1]) if not s.isna().iloc[-1] else None
        return {
            "hist": hist, "rsi": rsi,
            "pivot": P, "S1": S1, "R1": R1, "S2": S2, "R2": R2,
            "sma20": _last(sma20), "sma50": _last(sma50), "sma200": _last(sma200),
        }
    except Exception:
        return {}


def _tech_status(price: float, rsi: float, S1: float, R1: float, sma200) -> str:
    near_sup = price <= S1 * 1.04
    near_res = price >= R1 * 0.97
    above200 = sma200 and price > sma200
    if rsi > 70 and near_res:
        return "🔴 Overbought"
    elif rsi < 30 and near_sup:
        return "🟢 Oversold"
    elif rsi >= 50 and above200:
        return "🟢 Bullish"
    elif rsi < 40:
        return "🔴 Bearish"
    return "🟡 Neutral"


def _ma_label(price: float, sma20, sma50, sma200) -> str:
    if sma200 and price > sma200:
        return "↑ SMA200"
    if sma50 and price > sma50:
        return "↑ SMA50"
    if sma20 and price > sma20:
        return "↑ SMA20"
    return "↓ Below MAs"


@st.cache_data(ttl=300)
def load_portfolio_history(tx_records: tuple, cash: float, period: str) -> pd.DataFrame:
    """
    คำนวณ portfolio value รายวัน โดยใช้ transaction history จริง
    tx_records: tuple of (ticker, tx_type, date, qty) — hashable for caching
    """
    import yfinance as yf

    if not tx_records:
        return pd.DataFrame()

    yf_period, interval = PERIOD_MAP.get(period, ("1y", "1d"))

    # สร้าง cumulative shares timeline สำหรับแต่ละ ticker
    shares_timeline: dict[str, dict] = {}
    for ticker, tx_type, date, qty in tx_records:
        if date is None:
            continue
        if ticker not in shares_timeline:
            shares_timeline[ticker] = {}
        shares_timeline[ticker][date] = shares_timeline[ticker].get(date, 0.0)

    # คำนวณ cumulative shares ตามลำดับวันที่
    shares_series: dict[str, pd.Series] = {}
    for ticker, tx_type, date, qty in sorted(tx_records, key=lambda x: x[2] or datetime.min):
        if date is None:
            continue
        if ticker not in shares_series:
            shares_series[ticker] = {}
        prev_dates = [d for d in shares_series[ticker]]
        prev_shares = shares_series[ticker][max(prev_dates)] if prev_dates else 0.0
        delta = qty if tx_type == "Buy" else -qty
        shares_series[ticker][date] = prev_shares + delta

    if not shares_series:
        return pd.DataFrame()

    tickers = list(shares_series.keys())

    # ดึงราคาประวัติศาสตร์
    raw = yf.download(tickers, period=yf_period, interval=interval,
                      auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()

    close = raw["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(name=tickers[0])
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)

    # สร้าง shares DataFrame — reindex ให้ตรงกับ price dates แล้ว forward-fill
    shares_df = pd.DataFrame(
        {t: pd.Series(v) for t, v in shares_series.items()}
    )
    # รวม index ของ transactions + ราคา แล้ว forward-fill
    full_idx = shares_df.index.union(close.index).sort_values()
    shares_df = shares_df.reindex(full_idx).ffill().fillna(0).reindex(close.index)
    shares_df = shares_df.clip(lower=0)  # ไม่ให้ติดลบจากการ round

    # หาคอลัมน์ที่มีทั้งใน shares_df และ close
    common = [t for t in tickers if t in close.columns]
    port_value = (shares_df[common] * close[common]).sum(axis=1) + cash

    return port_value.rename("portfolio").to_frame().dropna()


@st.cache_data(ttl=300)
def load_index_history(symbol: str, period: str) -> pd.DataFrame:
    import yfinance as yf
    yf_period, interval = PERIOD_MAP.get(period, ("1y", "1d"))
    raw = yf.download(symbol, period=yf_period, interval=interval,
                      auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    close = raw["Close"]
    # yfinance single-ticker may return DataFrame with MultiIndex columns
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)
    return close.to_frame(name=symbol).dropna()  # avoid Series.rename(str) bug in pandas 2.x


def render_performance_chart(df: pd.DataFrame, tx_df: pd.DataFrame):
    """กราฟ Portfolio Value + เทียบ index"""
    cash_val = df[df["ticker"] == "CASH"]["total_value"].sum()
    # สร้าง tx_records จาก transaction history (hashable tuple สำหรับ cache)
    tx_records = tuple(
        (row["ticker"], row["type"], row["date"], float(row["qty"]))
        for _, row in tx_df.iterrows()
        if pd.notna(row["date"]) and row["qty"] > 0
    ) if not tx_df.empty else ()

    st.markdown("<div class='section-title'>Portfolio Performance</div>", unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([2, 3])
    with ctrl1:
        period = st.radio(
            "Period", list(PERIOD_MAP.keys()),
            index=5, horizontal=True, key="perf_period",
            label_visibility="collapsed",
        )
    with ctrl2:
        compare_with = st.multiselect(
            "Compare with", list(INDICES.keys()),
            default=["S&P 500 (SPY)"],
            key="perf_compare",
        )

    normalize = st.toggle("Show as % return (normalized)", value=True, key="perf_norm")

    with st.spinner("Loading price history..."):
        port_hist = load_portfolio_history(tx_records, cash_val, period)

    if port_hist.empty:
        st.warning("No historical data available.")
        return

    fig = go.Figure()

    def _add_series(series: pd.Series, name: str, color: str, dash="solid", width=2.5):
        if normalize:
            base = series.iloc[0]
            y = ((series / base) - 1) * 100 if base != 0 else series
            hover = "%{y:.2f}%"
        else:
            y = series
            hover = "$%{y:,.0f}"
        fig.add_trace(go.Scatter(
            x=series.index, y=y,
            name=name,
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>{hover}<extra></extra>",
            fill="tozeroy" if (name == "My Portfolio" and not normalize) else None,
            fillcolor="rgba(2, 132, 199, 0.08)" if name == "My Portfolio" else None,
        ))

    _add_series(port_hist["portfolio"], "My Portfolio", "#0284C7", width=3)

    index_colors = ["#06B6D4", "#D97706", "#EF4444", "#8B5CF6"]
    for i, label in enumerate(compare_with):
        symbol = INDICES[label]
        idx_hist = load_index_history(symbol, period)
        if not idx_hist.empty:
            _add_series(idx_hist[symbol], label, index_colors[i % len(index_colors)], dash="dot", width=1.8)

    base = _plotly_base()
    base["margin"] = dict(t=10, b=30, l=60, r=20)
    fig.update_layout(
        height=400,
        hovermode="x unified",
        legend=dict(
            orientation="h", y=1.08, x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
        **base,
    )
    if normalize:
        fig.update_yaxes(ticksuffix="%", title="Return (%)")
        fig.add_hline(y=0, line_color="rgba(15,23,42,0.1)", line_width=1)
    else:
        fig.update_yaxes(tickprefix="$", title="Portfolio Value ($)")

    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)


# ── Portfolio Snapshot (PNG) ──────────────────────────────────────────────────────
def generate_portfolio_snapshot(df: pd.DataFrame, fx_rate: float, show_thb: bool) -> bytes | None:
    """Build a self-contained portfolio card PNG using Plotly + kaleido."""
    try:
        from plotly.subplots import make_subplots
        global SHEETS_SUMMARY

        stock_df = df[df["ticker"] != "CASH"]
        cash_df  = df[df["ticker"] == "CASH"]

        total_value = df["total_value"].sum()
        stock_cost  = stock_df["total_cost"].sum()
        stock_gain  = stock_df["gain_loss"].sum()
        
        gain_pct = (stock_gain / stock_cost * 100) if stock_cost > 0 else 0
            
        cash_val    = cash_df["total_value"].sum() if not cash_df.empty else 0.0
        cash_pct    = (cash_val / total_value * 100) if total_value > 0 else 0
        n_holdings  = len(stock_df)

        # ── Build figure: 2 rows — metrics banner + (table | donut) ──────────
        fig = make_subplots(
            rows=2, cols=2,
            row_heights=[0.12, 0.88],
            column_widths=[0.57, 0.43],
            specs=[[{"type": "xy", "colspan": 2}, None],
                   [{"type": "table"},             {"type": "domain"}]],
            vertical_spacing=0.02,
            horizontal_spacing=0.03,
        )

        # ── Row 1: invisible scatter to anchor metric annotations ─────────────
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                                 marker=dict(opacity=0)), row=1, col=1)
        fig.update_xaxes(visible=False, row=1, col=1)
        fig.update_yaxes(visible=False, row=1, col=1)

        # ── Row 2 left: Holdings table ────────────────────────────────────────
        header_cols = ["Ticker", "Shares", "Avg Cost", "Price",
                       "Value", "P/L ($)", "P/L %", "Alloc %"]
        col_data: dict[str, list] = {h: [] for h in header_cols}
        text_colors = []
        for _, row in df.iterrows():
            pl  = float(row["total_value"]) - float(row["total_cost"])
            pct = (pl / float(row["total_cost"]) * 100) if float(row["total_cost"]) > 0 else 0
            col_data["Ticker"].append(row["ticker"])
            col_data["Shares"].append(f"{float(row['shares']):.4f}")
            col_data["Avg Cost"].append(f"${float(row['avg_cost']):.2f}")
            col_data["Price"].append(f"${float(row['price']):.2f}")
            col_data["Value"].append(f"${float(row['total_value']):,.2f}")
            col_data["P/L ($)"].append(f"{'+'if pl>=0 else ''}${pl:,.2f}")
            col_data["P/L %"].append(f"{'+'if pct>=0 else ''}{pct:.2f}%")
            col_data["Alloc %"].append(f"{float(row['allocation']):.1f}%")
            text_colors.append("#10B981" if pl >= 0 else "#EF4444")

        cell_bg = ["#ffffff" if i % 2 == 0 else "#f8fafc" for i in range(len(df))]
        col_text_colors = [
            ["#1E293B"] * len(df), # Ticker
            ["#475569"] * len(df), # Shares
            ["#475569"] * len(df), # Avg Cost
            ["#475569"] * len(df), # Price
            ["#1E293B"] * len(df), # Value
            text_colors,           # P/L ($)
            text_colors,           # P/L %
            ["#0284C7"] * len(df), # Alloc %
        ]

        fig.add_trace(go.Table(
            header=dict(
                values=[f"<b>{h}</b>" for h in header_cols],
                fill_color="#E2EDF5",
                font=dict(color="#0284C7", size=11, family="Arial", bold=True),
                align="center", height=30,
                line=dict(color="rgba(180, 200, 220, 0.4)", width=1),
            ),
            cells=dict(
                values=[col_data[h] for h in header_cols],
                fill_color=[cell_bg] * len(header_cols),
                font=dict(color=col_text_colors, size=11, family="Arial"),
                align=["center"] * len(header_cols),
                height=27,
                line=dict(color="rgba(180, 200, 220, 0.2)", width=1),
            ),
        ), row=2, col=1)

        # ── Row 2 right: Donut chart ──────────────────────────────────────────
        snap_palette = ["#0284C7", "#06B6D4", "#D97706", "#EF4444", "#8B5CF6",
                        "#10B981", "#FB923C", "#38BDF8", "#EC4899", "#10B981", "#94A3B8"]
        pie_df = df[df["total_value"] > 0]
        pie_colors = [TICKER_COLORS.get(t, snap_palette[i % len(snap_palette)])
                      for i, t in enumerate(pie_df["ticker"])]
        fig.add_trace(go.Pie(
            labels=pie_df["ticker"],
            values=pie_df["total_value"].round(2),
            hole=0.55,
            marker=dict(colors=pie_colors, line=dict(color="#FFFFFF", width=2)),
            textinfo="percent+label",
            textfont=dict(size=10, color="#1E293B", family="Arial"),
            hoverinfo="skip",
        ), row=2, col=2)

        # ── Metric annotations (centred in row 1) ─────────────────────────────
        pl_color = "#10B981" if stock_gain >= 0 else "#EF4444"
        pl_sign  = "+" if stock_gain >= 0 else ""
        ts = datetime.now().strftime("%d %b %Y %H:%M")

        def _mv(label, val, sub=None, color="#1E293B"):
            sub_part = f"<br><span style='color:#475569;font-size:11px;font-weight:600;'>{sub}</span>" if sub else ""
            return (f"<span style='color:#64748B;font-size:10px;font-weight:600;letter-spacing:1px;'>{label}</span><br>"
                    f"<span style='color:{color};font-size:17px;font-weight:bold;'>{val}</span>{sub_part}")

        annotations = [
            # Title
            dict(text="<b>💼  My Investment Portfolio</b>",
                 x=0.5, y=0.995, xref="paper", yref="paper",
                 font=dict(size=18, color="#1E293B", family="Arial"),
                 showarrow=False, align="center"),
            # 5 metric cards (evenly spaced)
            dict(text=_mv("PORTFOLIO VALUE",   f"${total_value:,.2f}"),
                 x=0.04, y=0.925, xref="paper", yref="paper",
                 font=dict(size=11, family="Arial"), showarrow=False),
            dict(text=_mv("INVESTED (COST)",   f"${stock_cost:,.2f}"),
                 x=0.22, y=0.925, xref="paper", yref="paper",
                 font=dict(size=11, family="Arial"), showarrow=False),
            dict(text=_mv("UNREALIZED P/L",
                           f"{pl_sign}${stock_gain:,.2f}",
                           f"{pl_sign}{gain_pct:.2f}%", pl_color),
                 x=0.42, y=0.925, xref="paper", yref="paper",
                 font=dict(size=11, color=pl_color, family="Arial"), showarrow=False),
            dict(text=_mv("HOLDINGS",          str(n_holdings)),
                 x=0.62, y=0.925, xref="paper", yref="paper",
                 font=dict(size=11, family="Arial"), showarrow=False),
            dict(text=_mv("CASH",
                           f"${cash_val:,.2f}",
                           f"{cash_pct:.1f}% of port", "#0284C7"),
                 x=0.80, y=0.925, xref="paper", yref="paper",
                 font=dict(size=11, color="#0284C7", family="Arial"), showarrow=False),
            # Timestamp
            dict(text=f"<i>Generated {ts}</i>",
                 x=1.0, y=-0.01, xref="paper", yref="paper",
                 font=dict(size=9, color="#64748B", family="Arial"),
                 showarrow=False, align="right"),
        ]

        fig.update_layout(
            paper_bgcolor="#EDF4F9",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#475569", family="Arial"),
            height=580, width=1200,
            margin=dict(t=55, b=20, l=10, r=10),
            annotations=annotations,
            showlegend=False,
        )

        return fig.to_image(format="png", scale=2)

    except ImportError:
        return None  # kaleido not installed
    except Exception:
        return None


# ── Tab 1: Portfolio Overview ─────────────────────────────────────────────────────
def render_overview(df: pd.DataFrame, tx_df: pd.DataFrame, fx_rate: float = 35.0, show_thb: bool = False, sheets_summary: dict = None):
    global SHEETS_SUMMARY
    if sheets_summary:
        SHEETS_SUMMARY = sheets_summary
    stock_df = df[df["ticker"] != "CASH"]
    cash_df = df[df["ticker"] == "CASH"]

    total_value = df["total_value"].sum()
    stock_cost  = stock_df["total_cost"].sum()
    stock_gain  = stock_df["gain_loss"].sum()
    
    gain_pct = (stock_gain / stock_cost * 100) if stock_cost > 0 else 0
        
    cash_val    = cash_df["total_value"].sum() if not cash_df.empty else 0.0

    def _m(v): return fmt_money(v, fx_rate, show_thb)

    # ── True Return Calculations ─────────────────────────────────────────────
    if tx_df is not None and not tx_df.empty:
        total_buys = tx_df[tx_df["type"] == "Buy"]["total"].sum()
        total_sells = tx_df[tx_df["type"] == "Sell"]["total"].sum()
        total_dividends = tx_df[tx_df["type"] == "Dividend"]["total"].sum()
        wallet_deployed = max(0.0, cash_val - total_sells - total_dividends + total_buys)
        true_gain = total_value - wallet_deployed
        true_gain_pct = (true_gain / wallet_deployed * 100) if wallet_deployed > 0 else 0.0
    else:
        wallet_deployed = stock_cost
        true_gain = stock_gain
        true_gain_pct = gain_pct

    # ── View Mode Selector ────────────────────────────────────────────────────
    col_lbl, col_sel = st.columns([6, 4])
    with col_lbl:
        st.markdown("<div class='section-title' style='margin-top:0;'>Portfolio Summary</div>", unsafe_allow_html=True)
    with col_sel:
        acc_mode = st.radio(
            "Performance Mode",
            ["💼 Standard (Holding Cost)", "💳 Audited (True Wallet Return)"],
            horizontal=True,
            label_visibility="collapsed",
            key="accounting_mode_toggle_main"
        )

    # ── Top metrics ──────────────────────────────────────────────────────────
    cash_pct = f"{cash_val/total_value*100:.1f}% of port" if total_value > 0 else None
    
    if "Audited" in acc_mode:
        # Sourcing exact metrics from Google Sheets summary
        def _m_sheet(label, default_usd):
            if show_thb:
                thb_val = SHEETS_SUMMARY.get(label, {}).get("thb", 0.0)
                if thb_val > 0:
                    return f"฿{thb_val:,.0f}"
                return f"฿{default_usd * fx_rate:,.0f}"
            else:
                usd_val = SHEETS_SUMMARY.get(label, {}).get("usd", 0.0)
                if usd_val > 0:
                    return f"${usd_val:,.2f}"
                return f"${default_usd:,.2f}"

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        sheet_true_gain = SHEETS_SUMMARY.get("True Net Profit", {}).get("usd", true_gain)
        sheet_true_pct = SHEETS_SUMMARY.get("True Return %", {}).get("usd", true_gain_pct)
        
        if show_thb:
            thb_gain = SHEETS_SUMMARY.get("True Net Profit", {}).get("thb", 0.0)
            true_gain_val = f"{_sign(thb_gain)}฿{thb_gain:,.0f}" if thb_gain > 0 else f"{_sign(sheet_true_gain)}{_m(abs(sheet_true_gain))}"
        else:
            true_gain_val = f"{_sign(sheet_true_gain)}${sheet_true_gain:,.2f}"
            
        true_gain_pct_val = f"{_sign(sheet_true_pct)}{sheet_true_pct:.2f}%"
        gain_card_cls = "card-gain-pos" if sheet_true_gain >= 0 else "card-gain-neg"
        
        metrics = [
            ("💼 Portfolio Value", _m_sheet("Total", total_value), None, "neu", "card-value"),
            ("💳 True Deployed", _m_sheet("True Deployed Capital", wallet_deployed), None, "neu", "card-cost"),
            ("🚀 True Wallet Return", true_gain_val, true_gain_pct_val, "pos" if sheet_true_gain >= 0 else "neg", gain_card_cls),
            ("💰 Realized Profit", _m_sheet("Realized profit", 0.0), None, "neu", "card-hold"),
            ("🏦 Holdings", f"{len(stock_df)}", None, "neu", "card-hold"),
            ("💵 Cash Flow", _m_sheet("Cash Flow", cash_val), cash_pct, "neu", "card-cash"),
        ]
        
        for col, (label, val, delta, cls, card_cls) in zip([c1, c2, c3, c4, c5, c6], metrics):
            d_html = f'<div class="mc-delta {cls}">{delta}</div>' if delta else ""
            col.markdown(
                f'<div class="metric-card {card_cls}">'
                f'<div class="mc-label">{label}</div>'
                f'<div class="mc-value">{val}</div>'
                f'{d_html}</div>',
                unsafe_allow_html=True,
            )
            
        st.markdown(
            f'''
            <div style="background-color: rgba(2,132,199,0.06); border: 1px solid rgba(2,132,199,0.22); border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; font-size: 0.88rem; color: var(--txt2);">
                ✨ <b>โหมดต้นทุนเงินกระเป๋าจริง (True Return Audit - Live Sheets Precision):</b> ตัวเลขทั้งหมดถูกดึงและตรวจสอบทางบัญชีโดยตรงจาก Google Sheets แบบเรียลไทม์ โดยคำนวณจากเงินสดที่คุณเติมจริงลบยอดขายและปันผลสะสม เพื่อความถูกต้องของผลตอบแทนที่แท้จริง
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        # Realized profit breakdown section
        realized_df, realized_total = load_realized_breakdown()
        if not realized_df.empty:
            st.markdown("<div class='section-title' style='margin-top:20px;'>💰 Realized Profit Breakdown (สรุปกำไรสะสมรายตัวที่ขายจริง)</div>", unsafe_allow_html=True)
            
            display_realized = realized_df.copy()
            display_realized.columns = ["Ticker", "Total Sells", "Cost of Sells", "Net Realized Profit"]
            
            def _style_profit(val):
                if isinstance(val, (int, float)):
                    return f"color: {_gc(val)}"
                return ""
            
            if show_thb:
                display_realized["Total Sells"] = display_realized["Total Sells"] * fx_rate
                display_realized["Cost of Sells"] = display_realized["Cost of Sells"] * fx_rate
                display_realized["Net Realized Profit"] = display_realized["Net Realized Profit"] * fx_rate
                
                fmt_dict = {
                    "Total Sells": "฿{:,.0f}",
                    "Cost of Sells": "฿{:,.0f}",
                    "Net Realized Profit": "฿{:+,.0f}"
                }
            else:
                fmt_dict = {
                    "Total Sells": "${:,.2f}",
                    "Cost of Sells": "${:,.2f}",
                    "Net Realized Profit": "${:+,.2f}"
                }
                
            styled_realized = (
                display_realized.style
                .format(fmt_dict)
                .map(_style_profit, subset=["Net Realized Profit"])
                .set_properties(**{
                    "background-color": "#ffffff",
                    "color": "#1e293b",
                    "border": "1px solid rgba(180, 200, 220, 0.4)",
                    "font-family": "JetBrains Mono, monospace",
                    "font-size": "0.82rem",
                })
            )
            st.dataframe(styled_realized, use_container_width=True, hide_index=True)
            
            if realized_total:
                total_sells = realized_total.get("sells", 0.0)
                total_cost = realized_total.get("cost", 0.0)
                total_profit = realized_total.get("profit", 0.0)
                
                if show_thb:
                    total_sells_str = f"฿{total_sells * fx_rate:,.0f}"
                    total_cost_str = f"฿{total_cost * fx_rate:,.0f}"
                    total_profit_str = f"฿{total_profit * fx_rate:,.0f}"
                else:
                    total_sells_str = f"${total_sells:,.2f}"
                    total_cost_str = f"${total_cost:,.2f}"
                    total_profit_str = f"${total_profit:,.2f}"
                    
                profit_color = "#059669" if total_profit >= 0 else "#EF4444"
                
                st.markdown(
                    f'''
                    <div style="background-color: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 18px; margin-top: 8px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.88rem;">
                        <span style="font-weight: 700; color: var(--txt1);">🌟 รวมสุทธิ (Total Realized)</span>
                        <span style="color: var(--txt2);">ยอดเงินขาย: {total_sells_str}</span>
                        <span style="color: var(--txt3);">ต้นทุนหุ้นขาย: {total_cost_str}</span>
                        <span style="font-weight: 700; color: {profit_color};">กำไรสุทธิ: {total_profit_str}</span>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        gain_card_cls = "card-gain-pos" if stock_gain >= 0 else "card-gain-neg"
        gain_val = f"{_sign(stock_gain)}{_m(abs(stock_gain))}"
        metrics = [
            ("💼 Portfolio Value", _m(total_value), None, "neu", "card-value"),
            ("💵 Invested (Cost)", _m(stock_cost), None, "neu", "card-cost"),
            ("📈 Unrealized P/L", gain_val, f"{_sign(gain_pct)}{gain_pct:.2f}%", "pos" if stock_gain >= 0 else "neg", gain_card_cls),
            ("🏦 Holdings", f"{len(stock_df)}", None, "neu", "card-hold"),
            ("💵 Cash", _m(cash_val), cash_pct, "neu", "card-cash"),
        ]
        
        for col, (label, val, delta, cls, card_cls) in zip([c1, c2, c3, c4, c5], metrics):
            d_html = f'<div class="mc-delta {cls}">{delta}</div>' if delta else ""
            col.markdown(
                f'<div class="metric-card {card_cls}">'
                f'<div class="mc-label">{label}</div>'
                f'<div class="mc-value">{val}</div>'
                f'{d_html}</div>',
                unsafe_allow_html=True,
            )

    # ── Holdings header + snapshot button ───────────────────────────────────
    hdr_col, btn_col = st.columns([6, 1])
    with hdr_col:
        st.markdown("<div class='section-title'>Holdings</div>", unsafe_allow_html=True)
    with btn_col:
        snap_bytes = generate_portfolio_snapshot(df, fx_rate, show_thb)
        if snap_bytes:
            fname = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            st.download_button(
                label="📷",
                data=snap_bytes,
                file_name=fname,
                mime="image/png",
                help="ดาวน์โหลด Portfolio Snapshot เป็น PNG",
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div style="color:#4b5563;font-size:0.75rem;text-align:center;padding-top:8px;" '
                'title="pip install kaleido">📷 install kaleido</div>',
                unsafe_allow_html=True,
            )

    # ── Table + Donut ────────────────────────────────────────────────────────
    col_tbl, col_pie = st.columns([3, 2], gap="large")

    with col_tbl:
        display = df[[
            "ticker", "name", "shares", "avg_cost",
            "price", "total_value", "gain_loss", "gain_pct", "allocation"
        ]].copy()
        display.columns = [
            "Ticker", "Company", "Shares", "Avg Cost", "Price",
            "Value", "P/L ($)", "P/L %", "Alloc %",
        ]

        def _style_cell(val):
            if isinstance(val, (int, float)):
                return f"color: {_gc(val)}"
            return ""

        styled = (
            display.style
            .format({
                "Shares": "{:.4f}",
                "Avg Cost": "${:.2f}",
                "Price": "${:.2f}",
                "Value": "${:,.2f}",
                "P/L ($)": "${:+,.2f}",
                "P/L %": "{:+.2f}%",
                "Alloc %": "{:.1f}%",
            })
            .map(_style_cell, subset=["P/L ($)", "P/L %"])
            .set_properties(**{
                "background-color": "#ffffff",
                "color": "#1e293b",
                "border": "1px solid rgba(180, 200, 220, 0.4)",
                "font-family": "JetBrains Mono, monospace",
                "font-size": "0.82rem",
            })
        )
        st.dataframe(styled, use_container_width=True, height=440, hide_index=True)

    with col_pie:
        pie_df = df[df["total_value"] > 0]
        pie_colors = [TICKER_COLORS.get(t, PALETTE[i % len(PALETTE)]) for i, t in enumerate(pie_df["ticker"])]
        fig_pie = go.Figure(go.Pie(
            labels=pie_df["ticker"],
            values=pie_df["total_value"].round(2),
            hole=0.6,
            marker=dict(colors=pie_colors, line=dict(color="#ffffff", width=2)),
            textinfo="percent+label",
            textfont=dict(size=11, family="Inter", color="#1e293b"),
            hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>",
        ))
        fig_pie.update_layout(
            showlegend=False,
            height=340,
            **_plotly_base(),
        )
        # Center annotation
        fig_pie.add_annotation(
            text=f"<b>${total_value:,.0f}</b>",
            font=dict(size=16, color="#1e293b", family="JetBrains Mono"),
            showarrow=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Bar chart ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Unrealized Gain / Loss by Stock</div>", unsafe_allow_html=True)
    bar_df = stock_df.sort_values("gain_loss", ascending=True)
    fig_bar = go.Figure(go.Bar(
        x=bar_df["gain_loss"].round(2),
        y=bar_df["ticker"],
        orientation="h",
        marker=dict(
            color=[_gc(g) for g in bar_df["gain_loss"]],
            line=dict(width=0),
        ),
        text=[f"${g:+,.0f}  ({p:+.1f}%)" for g, p in zip(bar_df["gain_loss"], bar_df["gain_pct"])],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11),
        hovertemplate="<b>%{y}</b><br>P/L: $%{x:+,.2f}<extra></extra>",
    ))
    fig_bar.update_layout(height=max(240, len(bar_df) * 36), **_plotly_base())
    fig_bar.update_xaxes(tickprefix="$")
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Technical Snapshot table ─────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:20px;'>📡 Technical Snapshot — แนวรับ / แนวต้าน / RSI</div>", unsafe_allow_html=True)
    tech_rows = []
    with st.spinner("Loading technical data..."):
        for _, row in stock_df.iterrows():
            t = row["ticker"]
            price = float(row["price"])
            tech = load_technicals(t, "6mo")
            if not tech:
                continue
            rsi   = tech["rsi"]
            S1, R1 = tech["S1"], tech["R1"]
            status = _tech_status(price, rsi, S1, R1, tech["sma200"])
            ma_lbl = _ma_label(price, tech["sma20"], tech["sma50"], tech["sma200"])
            rsi_color = "#EF4444" if rsi > 70 else "#059669" if rsi < 30 else "#D97706"
            tech_rows.append({
                "Ticker": t,
                "Price": price,
                "Support (S1)": S1,
                "Resist (R1)":  R1,
                "RSI": rsi,
                "MA Trend": ma_lbl,
                "Status": status,
            })
    if tech_rows:
        tech_df = pd.DataFrame(tech_rows).set_index("Ticker")
        def _color_rsi(val):
            if isinstance(val, float):
                if val > 70: return "color: #EF4444"
                if val < 30: return "color: #059669"
            return "color: #D97706"
        styled_t = (
            tech_df.style
            .format({"Price": "${:.2f}", "Support (S1)": "${:.2f}", "Resist (R1)": "${:.2f}", "RSI": "{:.0f}"})
            .map(_color_rsi, subset=["RSI"])
            .set_properties(**{
                "background-color": "#ffffff",
                "color": "#1e293b",
                "border": "1px solid rgba(180, 200, 220, 0.4)",
                "font-family": "JetBrains Mono, monospace",
                "font-size": "0.82rem",
            })
        )
        st.dataframe(styled_t, use_container_width=True)
        st.caption("S1/R1 = Classic Pivot Points (yesterday's OHLC) · RSI 14-day · คลิก Charts tab เพื่อดู candlestick chart ของแต่ละหุ้น")

    st.markdown("---")
    render_performance_chart(df, tx_df)

    st.caption(
        f"Prices via yfinance (60s cache) · Portfolio via Google Sheets (5min cache) · "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )


# ── Tab 2: Allocation Manager ─────────────────────────────────────────────────────
def render_allocation(df: pd.DataFrame, saved: dict):
    targets = get_target_pcts(df, saved)

    st.markdown("<div class='section-title'>Current vs Target</div>", unsafe_allow_html=True)

    max_val = max(df["allocation"].max(), max(targets.values(), default=0), 1.0)

    bars_html = ""
    for _, row in df.iterrows():
        t = row["ticker"]
        cur = row["allocation"]
        tgt = targets.get(t, 0.0)
        diff = cur - tgt
        is_cash = t == "CASH"

        if is_cash:
            bar_color, icon = "#a5b4fc", "💵"
        elif abs(diff) <= 3:
            bar_color, icon = "#00d4aa", "✅"
        elif abs(diff) <= 8:
            bar_color, icon = "#ffd166", "⚠️"
        else:
            bar_color, icon = "#f87171", "🔴"

        fill = cur / max_val * 100
        tgt_pos = tgt / max_val * 100
        diff_str = f"{_sign(diff)}{abs(diff):.1f}%"

        bars_html += f"""
        <div class="alloc-row">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-family:'Space Grotesk',sans-serif; font-weight:600; color:var(--txt1); font-size:0.95rem;">{t}</span>
            <span style="color:var(--txt3); font-size:0.78rem;">{row['name']}</span>
            <span style="font-family:'JetBrains Mono',monospace; font-size:0.82rem;">
              <span style="color:{bar_color}; font-weight:600;">{cur:.1f}%</span>
              <span style="color:var(--txt3);"> / tgt {tgt:.0f}% &nbsp;{icon} {diff_str}</span>
            </span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{fill:.1f}%; background:linear-gradient(90deg, {bar_color}cc, {bar_color});"></div>
          </div>
          <div style="position:relative; height:0;">
            <div style="position:absolute; left:{tgt_pos:.1f}%; top:-8px; width:2px; height:8px;
                        background:var(--gold); border-radius:1px;" title="Target {tgt:.0f}%"></div>
          </div>
        </div>
        """
    st.markdown(bars_html, unsafe_allow_html=True)
    st.caption("🟡 Yellow tick = target | Gradient bar = current allocation")

    st.markdown("---")
    st.markdown("<div class='section-title'>Edit Targets</div>", unsafe_allow_html=True)

    new_targets = {}
    cols = st.columns(4)
    for i, (_, row) in enumerate(df.iterrows()):
        t = row["ticker"]
        with cols[i % 4]:
            new_targets[t] = st.number_input(
                f"{t} %", min_value=0.0, max_value=100.0,
                value=float(targets.get(t, 0.0)),
                step=0.5, format="%.1f", key=f"tgt_{t}",
            )

    total_tgt = sum(new_targets.values())
    ok = abs(total_tgt - 100) < 0.5
    tgt_color = "#10B981" if ok else "#EF4444"
    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace; font-size:0.95rem;">'
        f'Total: <span style="color:{tgt_color}; font-weight:600;">{total_tgt:.1f}%</span>'
        f'<span style="color:var(--txt3);"> (target = 100%)</span></p>',
        unsafe_allow_html=True,
    )

    cash_val = float(saved.get("cash", 0.0))
    new_cash = st.number_input("💵 Cash balance ($)", min_value=0.0, value=cash_val, step=10.0, format="%.2f")

    if st.button("💾 Save", type="primary"):
        save_targets(new_targets, new_cash)
        st.cache_data.clear()
        st.success("Saved!")
        st.rerun()

    st.markdown("---")
    st.markdown("<div class='section-title'>Rebalance Calculator</div>", unsafe_allow_html=True)

    total_value = df["total_value"].sum()
    fresh = st.number_input("Fresh capital ($)", min_value=0.0, value=500.0, step=50.0, format="%.2f")
    new_total = total_value + fresh

    rebal = []
    for _, row in df.iterrows():
        t = row["ticker"]
        tgt_v = new_total * targets.get(t, 0.0) / 100
        diff_v = tgt_v - row["total_value"]
        if abs(diff_v) < 1:
            continue
        action = "BUY" if diff_v > 0 else "TRIM"
        price = row["price"] if row["price"] > 0 else 1.0
        rebal.append({
            "Ticker": t, "Action": action,
            "Amount ($)": abs(diff_v),
            "Shares": abs(diff_v) / price,
            "Current %": row["allocation"],
            "Target %": targets.get(t, 0.0),
        })
    if rebal:
        rdf = pd.DataFrame(rebal)
        def _ac(v):
            return "color: #059669; font-weight:700" if v == "BUY" else "color: #EF4444; font-weight:700"
        styled_r = (
            rdf.style.map(_ac, subset=["Action"])
            .format({"Amount ($)": "${:,.2f}", "Shares": "{:.4f}",
                     "Current %": "{:.1f}%", "Target %": "{:.1f}%"})
            .set_properties(**{
                "background-color": "#ffffff", "color": "#1e293b",
                "border": "1px solid rgba(180, 200, 220, 0.4)",
                "font-family": "JetBrains Mono, monospace", "font-size": "0.82rem",
            })
        )
        st.dataframe(styled_r, use_container_width=True)
    else:
        st.success("Portfolio is on target — no rebalancing needed!")


# ── Tab 3: DCA Calculator ─────────────────────────────────────────────────────────
def render_dca(df: pd.DataFrame, fx_rate: float = 35.0, show_thb: bool = False):
    def _m(v): return fmt_money(v, fx_rate, show_thb)
    currency = "฿" if show_thb else "$"

    stock_df = df[df["ticker"] != "CASH"]

    # ── Input section ────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>เลือกหุ้นและจำนวนที่ต้องการซื้อ</div>", unsafe_allow_html=True)
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        tickers = stock_df["ticker"].tolist()
        names   = stock_df["name"].tolist()
        options = [f"{t}  —  {n}" for t, n in zip(tickers, names)]
        sel_idx = st.selectbox("หุ้น", range(len(options)), format_func=lambda i: options[i], key="dca_ticker")
        selected = tickers[sel_idx]
        row = stock_df[stock_df["ticker"] == selected].iloc[0]
        default_p = float(row["price"]) if row["price"] > 0 else float(row["avg_cost"])

        st.markdown(
            f'<div class="glass-card" style="display:flex; gap:32px; align-items:center; margin-bottom:12px;">'
            f'<div><div style="color:var(--txt3);font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">ถืออยู่</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:var(--txt1);font-family:JetBrains Mono,monospace;">{row["shares"]:.4f} <span style="font-size:0.8rem;color:var(--txt3);">shares</span></div></div>'
            f'<div><div style="color:var(--txt3);font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">ต้นทุนเฉลี่ย</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:var(--gold);font-family:JetBrains Mono,monospace;">${row["avg_cost"]:.2f}</div></div>'
            f'<div><div style="color:var(--txt3);font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">ต้นทุนรวม</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:var(--violet);font-family:JetBrains Mono,monospace;">{_m(row["total_cost"])}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        buy_price = st.number_input(f"ราคาที่จะซื้อ ($)", min_value=0.01, value=round(default_p, 2),
                                    step=0.01, format="%.2f", key="dca_price",
                                    help="ค่าเริ่มต้นคือราคาตลาดปัจจุบัน")

        method = st.radio("ซื้อโดยระบุ", ["จำนวนเงิน ($)", "จำนวนหุ้น (shares)"], horizontal=True, key="dca_method")
        if method == "จำนวนเงิน ($)":
            buy_cost = st.number_input("จำนวนเงิน ($)", min_value=1.0, value=500.0, step=50.0,
                                       format="%.2f", key="dca_amt")
            buy_qty = buy_cost / buy_price
        else:
            buy_qty = st.number_input("จำนวนหุ้น", min_value=0.0001, value=1.0, step=0.5,
                                      format="%.4f", key="dca_qty")
            buy_cost = buy_qty * buy_price

        st.caption(f"→ ซื้อ {buy_qty:.4f} shares มูลค่า {_m(buy_cost)}")

    # ── Calculations ─────────────────────────────────────────────────────────
    cur_shares, cur_avg, cur_cost = row["shares"], row["avg_cost"], row["total_cost"]
    new_shares = cur_shares + buy_qty
    new_cost   = cur_cost + buy_cost
    new_avg    = new_cost / new_shares
    avg_delta  = new_avg - cur_avg
    avg_delta_pct = avg_delta / cur_avg * 100
    avg_color  = "#EF4444" if avg_delta > 0 else "#10B981"
    avg_arrow  = "↑" if avg_delta > 0 else "↓"
    vs_price   = (buy_price - new_avg) / new_avg * 100
    vs_color   = _gc(vs_price)
    port_total_ex = df["total_value"].sum() - row["total_value"]
    new_pos_val   = new_shares * buy_price
    new_alloc     = new_pos_val / (port_total_ex + new_pos_val) * 100 if (port_total_ex + new_pos_val) > 0 else 0

    # ── Result cards ─────────────────────────────────────────────────────────
    with col_out:
        st.markdown("<div class='section-title'>ผลลัพธ์หลังซื้อ</div>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        r3, r4 = st.columns(2)

        def _result_card(col, label, value, sub="", color="var(--txt1)"):
            col.markdown(
                f'<div class="metric-card" style="text-align:center;padding:16px 12px;">'
                f'<div class="mc-label">{label}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:1.4rem;font-weight:700;color:{color};line-height:1.2;">{value}</div>'
                f'{"<div style=\"font-size:0.78rem;color:var(--txt3);margin-top:4px;\">"+sub+"</div>" if sub else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

        _result_card(r1, "📦 จำนวนหุ้นหลังซื้อ", f"{new_shares:.4f} sh")
        _result_card(r2, "💰 ต้นทุนเฉลี่ยใหม่", f"${new_avg:.2f}",
                     f'{avg_arrow} {avg_delta:+.2f} ({avg_delta_pct:+.2f}%)', avg_color)
        _result_card(r3, "💵 ต้นทุนรวมหลังซื้อ", _m(new_cost))
        _result_card(r4, "📊 สัดส่วนใหม่ในพอร์ต", f"{new_alloc:.1f}%", "", "var(--violet)")

        st.markdown(
            f'<div class="glass-card" style="margin-top:8px;text-align:center;">'
            f'<div style="color:var(--txt3);font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">ราคาตลาด vs ต้นทุนใหม่</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:1.6rem;font-weight:700;color:{vs_color};">'
            f'{_sign(vs_price)}{vs_price:.2f}%</div>'
            f'<div style="color:var(--txt3);font-size:0.8rem;">{"📈 ราคาตลาดสูงกว่าต้นทุนใหม่" if vs_price >= 0 else "📉 ราคาตลาดต่ำกว่าต้นทุนใหม่"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Sensitivity chart ────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:20px;'>Sensitivity — ถ้าซื้อในราคาต่างกัน ต้นทุนเฉลี่ยจะเปลี่ยนอย่างไร?</div>", unsafe_allow_html=True)
    px_range = [buy_price * (0.5 + i * 0.05) for i in range(21)]
    avgs_y = [(cur_cost + (buy_cost if method == "จำนวนเงิน ($)" else buy_qty * p)) /
              (cur_shares + (buy_cost / p if method == "จำนวนเงิน ($)" else buy_qty))
              for p in px_range if p > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=px_range[:len(avgs_y)], y=avgs_y,
        mode="lines+markers",
        line=dict(color="#0284C7", width=2.5),
        marker=dict(size=6, color="#0284C7"),
        fill="tozeroy", fillcolor="rgba(2,132,199,0.07)",
        hovertemplate="ซื้อ @ $%{x:.2f}<br>ต้นทุนใหม่: $%{y:.2f}<extra></extra>",
        name="New Avg Cost",
    ))
    fig.add_hline(y=cur_avg, line_dash="dash", line_color="#D97706",
                  annotation_text=f"ต้นทุนเดิม ${cur_avg:.2f}", annotation_font_color="#D97706",
                  annotation_position="top left")
    fig.add_vline(x=buy_price, line_dash="dot", line_color="#10B981",
                  annotation_text=f"ราคาที่เลือก ${buy_price:.2f}", annotation_font_color="#10B981")
    fig.update_layout(height=300, showlegend=False, **_plotly_base())
    fig.update_xaxes(title="ราคาที่ซื้อ ($)", tickprefix="$")
    fig.update_yaxes(title="ต้นทุนเฉลี่ยใหม่ ($)", tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)

    # ── Position Sizing ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:8px;'>⚖️ Position Sizing — คำนวณจากความเสี่ยงที่รับได้</div>", unsafe_allow_html=True)
    port_val = df["total_value"].sum()
    ps1, ps2, ps3 = st.columns(3)
    with ps1:
        risk_pct = st.slider("ความเสี่ยงต่อ trade (%)", 0.5, 5.0, 1.0, 0.5,
                             help="กี่ % ของพอร์ตที่ยอมขาดทุนได้ถ้า stop-loss โดน")
    with ps2:
        ps_entry = st.number_input("Entry Price ($)", min_value=0.01, value=round(default_p, 2),
                                   step=0.01, format="%.2f", key="ps_entry")
    with ps3:
        tech_snap = load_technicals(selected, "6mo")
        default_sl = round(tech_snap["S1"], 2) if tech_snap else round(default_p * 0.92, 2)
        ps_stop = st.number_input("Stop-Loss ($)", min_value=0.01, value=default_sl,
                                  step=0.01, format="%.2f", key="ps_stop",
                                  help="ค่าเริ่มต้นคือ S1 (Classic Pivot Support)")

    if ps_entry > ps_stop > 0:
        max_loss_usd   = port_val * risk_pct / 100
        risk_per_share = ps_entry - ps_stop
        ps_shares      = max_loss_usd / risk_per_share
        ps_cost        = ps_shares * ps_entry
        cur_alloc      = row["total_value"] / port_val * 100
        new_alloc_ps   = (row["total_value"] + ps_cost) / (port_val + ps_cost) * 100

        pr1, pr2, pr3, pr4 = st.columns(4)
        def _ps_card(col, label, val, sub="", color="var(--txt1)"):
            sub_html = f'<div style="font-size:0.78rem;color:var(--txt3);margin-top:4px;">{sub}</div>' if sub else ""
            col.markdown(
                f'<div class="metric-card" style="text-align:center;">'
                f'<div class="mc-label">{label}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:{color};">{val}</div>'
                f'{sub_html}</div>',
                unsafe_allow_html=True,
            )
        _ps_card(pr1, "💸 Max Loss ยอมรับได้", _m(max_loss_usd), f"{risk_pct}% ของพอร์ต", "#EF4444")
        _ps_card(pr2, "📉 Risk ต่อ Share", f"${risk_per_share:.2f}", f"entry - stop")
        _ps_card(pr3, "📦 ซื้อได้", f"{ps_shares:.2f} shares", _m(ps_cost))
        _ps_card(pr4, "📊 Alloc หลังซื้อ", f"{new_alloc_ps:.1f}%",
                 f"ปัจจุบัน {cur_alloc:.1f}%",
                 "#EF4444" if new_alloc_ps > 30 else "#D97706" if new_alloc_ps > 20 else "#10B981")
    else:
        st.warning("Stop-loss ต้องต่ำกว่า Entry price")


# ── Tab 4: Compounding Effect Calculator ─────────────────────────────────────────
def render_compound(df: pd.DataFrame, fx_rate: float = 35.0, show_thb: bool = False):
    def _m(v): return fmt_money(v, fx_rate, show_thb)

    st.markdown("<div class='section-title'>Compounding Effect — พลังของดอกเบี้ยทบต้น</div>", unsafe_allow_html=True)

    total_val = df["total_value"].sum()

    # ── Inputs ────────────────────────────────────────────────────────────────
    ic1, ic2 = st.columns(2, gap="large")
    with ic1:
        st.markdown("##### ⚙️ ตั้งค่าการลงทุน")
        initial = st.number_input("เงินเริ่มต้น ($)", min_value=0.0, value=round(total_val, 0),
                                   step=100.0, format="%.0f",
                                   help="ค่าเริ่มต้นคือมูลค่าพอร์ตปัจจุบัน")
        monthly = st.number_input("DCA รายเดือน ($)", min_value=0.0, value=500.0, step=50.0, format="%.0f")
        years   = st.slider("ระยะเวลาการลงทุน (ปี)", min_value=1, max_value=50, value=30)

    with ic2:
        st.markdown("##### 📈 ผลตอบแทนและการเปรียบเทียบ")
        annual_r = st.slider("ผลตอบแทนคาดหวัง (% ต่อปี)", min_value=1.0, max_value=40.0, value=15.0, step=0.5,
                              help="พอร์ต Growth Stocks โดยเฉลี่ยอยู่ที่ 12-20% ต่อปีในระยะยาว")
        compare_opts = {
            "S&P 500 (~10%/yr)": 10.0,
            "QQQ NASDAQ (~13%/yr)": 13.0,
            "SET Index (~7%/yr)": 7.0,
            "เงินฝากธนาคาร (~1.5%/yr)": 1.5,
        }
        compare_label = st.selectbox("เปรียบเทียบกับ", list(compare_opts.keys()))
        compare_r = compare_opts[compare_label]

    # ── Calculate year-by-year ────────────────────────────────────────────────
    monthly_r   = annual_r / 100 / 12
    monthly_cr  = compare_r / 100 / 12
    total_invested = initial + monthly * 12 * years

    port_vals, comp_vals, inv_vals, year_labels = [], [], [], []
    pv, cv = float(initial), float(initial)
    for y in range(1, years + 1):
        for _ in range(12):
            pv = pv * (1 + monthly_r) + monthly
            cv = cv * (1 + monthly_cr) + monthly
        port_vals.append(pv)
        comp_vals.append(cv)
        inv_vals.append(initial + monthly * 12 * y)
        year_labels.append(y)

    final_val    = port_vals[-1]
    final_gain   = final_val - total_invested
    final_gain_p = (final_gain / total_invested * 100) if total_invested > 0 else 0
    comp_final   = comp_vals[-1]

    # ── Summary cards ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:16px;'>ผลลัพธ์หลังจาก {} ปี</div>".format(years), unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    def _scard(col, label, val, sub="", color="var(--txt1)"):
        col.markdown(
            f'<div class="metric-card" style="text-align:center;">'
            f'<div class="mc-label">{label}</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:{color};">{val}</div>'
            f'{"<div style=\"font-size:0.78rem;color:var(--txt3);margin-top:4px;\">"+sub+"</div>" if sub else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

    _scard(sc1, "💰 มูลค่าพอร์ตสุดท้าย", _m(final_val), f"@ {annual_r}%/yr", "#10B981")
    _scard(sc2, "💵 เงินลงทุนสะสมรวม",   _m(total_invested))
    _scard(sc3, "📈 กำไรสุทธิ",           _m(final_gain), f"+{final_gain_p:.0f}%", "#10B981")
    _scard(sc4, "📊 vs " + compare_label.split("(")[0].strip(),
           _m(comp_final), f"@ {compare_r}%/yr", "#0284C7")

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:20px;'>กราฟการเติบโตรายปี</div>", unsafe_allow_html=True)

    display_mult = fx_rate if show_thb else 1.0
    pv_disp  = [v * display_mult for v in port_vals]
    cv_disp  = [v * display_mult for v in comp_vals]
    inv_disp = [v * display_mult for v in inv_vals]
    prefix   = "฿" if show_thb else "$"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=year_labels, y=inv_disp,
        name="เงินลงทุนสะสม",
        mode="lines",
        line=dict(color="#64748b", width=1.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(100,116,139,0.05)",
        hovertemplate=f"ปีที่ %{{x}}<br>ลงทุนสะสม: {prefix}%{{y:,.0f}}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=year_labels, y=cv_disp,
        name=compare_label,
        mode="lines",
        line=dict(color="#0284C7", width=2),
        hovertemplate=f"ปีที่ %{{x}}<br>{compare_label}: {prefix}%{{y:,.0f}}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=year_labels, y=pv_disp,
        name=f"พอร์ตของเรา ({annual_r}%/yr)",
        mode="lines",
        line=dict(color="#10B981", width=3),
        fill="tonexty", fillcolor="rgba(16,185,129,0.06)",
        hovertemplate=f"ปีที่ %{{x}}<br>พอร์ต: {prefix}%{{y:,.0f}}<extra></extra>",
    ))

    fig.update_layout(
        height=420,
        legend=dict(orientation="h", y=1.05, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        hovermode="x unified",
        **_plotly_base(),
    )
    fig.update_yaxes(tickprefix=prefix, title=f"มูลค่า ({prefix})")
    fig.update_xaxes(title="ปีที่ลงทุน", dtick=5)
    st.plotly_chart(fig, use_container_width=True)

    # ── Milestone table ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Milestones — จุดสำคัญในเส้นทาง</div>", unsafe_allow_html=True)
    milestones = [1, 3, 5, 10, 15, 20, 25, 30, years] if years not in [1,3,5,10,15,20,25,30] else [1, 3, 5, 10, 15, 20, 25, 30]
    milestones = sorted(set(m for m in milestones if 1 <= m <= years))

    rows = []
    for y in milestones:
        pv_y = port_vals[y - 1]
        cv_y = comp_vals[y - 1]
        iv_y = inv_vals[y - 1]
        gain_y = pv_y - iv_y
        rows.append({
            "ปีที่": y,
            f"มูลค่าพอร์ต ({prefix})": pv_y * display_mult,
            f"เงินลงทุนสะสม ({prefix})": iv_y * display_mult,
            f"กำไรสุทธิ ({prefix})": gain_y * display_mult,
            "กำไร (%)": (gain_y / iv_y * 100) if iv_y > 0 else 0,
            f"vs {compare_label.split('(')[0].strip()} ({prefix})": cv_y * display_mult,
        })
    ms_df = pd.DataFrame(rows).set_index("ปีที่")
    num_cols = [c for c in ms_df.columns if c != "กำไร (%)"]
    fmt_dict = {c: f"{prefix}{{:,.0f}}" for c in num_cols}
    fmt_dict["กำไร (%)"] = "{:+.0f}%"

    def _color_gain(val):
        if isinstance(val, (int, float)):
            return f"color: {'#10B981' if val >= 0 else '#EF4444'}"
        return ""

    styled_ms = (
        ms_df.style
        .format(fmt_dict)
        .map(_color_gain, subset=[f"กำไรสุทธิ ({prefix})", "กำไร (%)"])
        .set_properties(**{
            "background-color": "#ffffff",
            "color": "#1e293b",
            "border": "1px solid rgba(180, 200, 220, 0.4)",
            "font-family": "JetBrains Mono, monospace",
            "font-size": "0.82rem",
        })
    )
    st.dataframe(styled_ms, use_container_width=True)


# ── Tab 5: Transaction History ────────────────────────────────────────────────────
def render_transactions(tx_df: pd.DataFrame, current_tickers: set):
    if tx_df.empty:
        st.info("No transaction data found.")
        return

    st.markdown("<div class='section-title'>Transaction History — Grouped by Stock</div>", unsafe_allow_html=True)

    # Summary chart: total bought vs sold per ticker
    summary = (
        tx_df.groupby(["ticker", "type"])["total"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    if "Buy" in summary.columns or "Sell" in summary.columns:
        fig_sum = go.Figure()
        if "Buy" in summary.columns:
            fig_sum.add_trace(go.Bar(
                name="Total Bought",
                x=summary["ticker"],
                y=summary.get("Buy", 0),
                marker_color="#6366f1",
                hovertemplate="<b>%{x}</b><br>Bought: $%{y:,.2f}<extra></extra>",
            ))
        if "Sell" in summary.columns:
            fig_sum.add_trace(go.Bar(
                name="Total Sold",
                x=summary["ticker"],
                y=summary.get("Sell", 0),
                marker_color="#00d4aa",
                hovertemplate="<b>%{x}</b><br>Sold: $%{y:,.2f}<extra></extra>",
            ))
        fig_sum.update_layout(
            barmode="group",
            height=280,
            legend=dict(orientation="h", y=1.1),
            **_plotly_base(),
        )
        fig_sum.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_sum, use_container_width=True)

    st.markdown("---")

    # Group by ticker — active stocks first, then inactive
    all_tickers = tx_df["ticker"].unique().tolist()
    active = sorted([t for t in all_tickers if t in current_tickers])
    inactive = sorted([t for t in all_tickers if t not in current_tickers])

    TYPE_ICON = {"Buy": "🟢", "Sell": "🔴", "Dividend": "💛"}
    TYPE_CLASS = {"Buy": "tx-buy", "Sell": "tx-sell", "Dividend": "tx-div"}

    for group_label, tickers, muted in [
        ("🏦 Active Holdings", active, False),
        ("📦 Past / Exited Positions", inactive, True),
    ]:
        if not tickers:
            continue
        st.markdown(
            f'<div style="color:{"#94a3b8" if muted else "#a5b4fc"}; font-size:0.72rem; '
            f'font-weight:600; text-transform:uppercase; letter-spacing:2px; margin:16px 0 8px;">'
            f'{group_label}</div>',
            unsafe_allow_html=True,
        )

        for ticker in tickers:
            grp = tx_df[tx_df["ticker"] == ticker]
            name = grp.iloc[0]["name"]
            total_bought = grp[grp["type"] == "Buy"]["total"].sum()
            total_sold = grp[grp["type"] == "Sell"]["total"].sum()
            tx_count = len(grp)

            opacity = "0.45" if muted else "1"
            border_color = "rgba(99,102,241,0.12)" if muted else "rgba(99,102,241,0.3)"

            with st.expander(
                f"{'⬛' if muted else '🔵'} {ticker}  —  {name}  "
                f"({tx_count} tx | Bought ${total_bought:,.0f}"
                + (f" | Sold ${total_sold:,.0f}" if total_sold > 0 else "")
                + ")",
                expanded=not muted,
            ):
                rows_html = ""
                for _, tx in grp.iterrows():
                    icon = TYPE_ICON.get(tx["type"], "⚪")
                    css_cls = TYPE_CLASS.get(tx["type"], "")
                    date_str = tx["date"].strftime("%Y-%m-%d") if tx["date"] else tx["date_raw"]
                    total_str = f"${tx['total']:,.2f}" if tx["total"] else "—"
                    price_str = f"${tx['price']:.2f}" if tx["price"] else "—"
                    qty_str = f"{tx['qty']:.4f}" if tx["qty"] else "—"
                    note = tx.get("note", "")
                    note_badge = (
                        '<span style="background:rgba(16, 185, 129, 0.1);color:#10B981;'
                        'font-size:0.62rem;padding:1px 5px;border-radius:4px;margin-left:6px;">DRIP</span>'
                        if note == "DRIP" else ""
                    )
                    rows_html += (
                        f'<div class="tx-row {css_cls}" style="opacity:{opacity};">'
                        f'<span style="color:var(--txt3); width:90px; display:inline-block;">{date_str}</span>'
                        f'<span style="width:100px; display:inline-block; color:var(--txt1);">{icon} {tx["type"]}{note_badge}</span>'
                        f'<span style="color:var(--txt2); width:90px; display:inline-block;">{qty_str} sh</span>'
                        f'<span style="color:var(--gold); width:80px; display:inline-block;">@ {price_str}</span>'
                        f'<span style="color:var(--violet); font-weight:600;">{total_str}</span>'
                        f'</div>'
                    )
                st.markdown(rows_html, unsafe_allow_html=True)


# ── Tab 6: Charts & Technical Analysis ───────────────────────────────────────────
def render_charts(df: pd.DataFrame):
    stock_df = df[df["ticker"] != "CASH"]
    tickers  = stock_df["ticker"].tolist()
    names    = stock_df["name"].tolist()

    # ── Controls ─────────────────────────────────────────────────────────────
    cc1, cc2, cc3 = st.columns([2, 1, 2])
    with cc1:
        sel_idx  = st.selectbox("เลือกหุ้น", range(len(tickers)),
                                format_func=lambda i: f"{tickers[i]}  —  {names[i]}",
                                key="chart_ticker")
        selected = tickers[sel_idx]
        row      = stock_df[stock_df["ticker"] == selected].iloc[0]
        avg_cost = float(row["avg_cost"])
        price    = float(row["price"])
    with cc2:
        period_label = st.selectbox("Period", list(CHART_PERIODS.keys()), index=2, key="chart_period")
        period_yf    = CHART_PERIODS[period_label]
    with cc3:
        ma_opts = st.multiselect("Moving Averages", ["SMA20", "SMA50", "SMA200"],
                                 default=["SMA20", "SMA50", "SMA200"], key="chart_mas")

    show_vol = st.checkbox("แสดง Volume", value=True, key="chart_vol")

    # ── Load data ─────────────────────────────────────────────────────────────
    with st.spinner(f"Loading {selected} data..."):
        tech = load_technicals(selected, period_yf)

    if not tech:
        st.error(f"ไม่สามารถดึงข้อมูลของ {selected} ได้")
        return

    hist  = tech["hist"]
    S1, R1, S2, R2, pivot = tech["S1"], tech["R1"], tech["S2"], tech["R2"], tech["pivot"]
    rsi   = tech["rsi"]

    # ── S/R Summary cards ─────────────────────────────────────────────────────
    status = _tech_status(price, rsi, S1, R1, tech["sma200"])
    ma_lbl = _ma_label(price, tech["sma20"], tech["sma50"], tech["sma200"])
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    def _scard(col, lbl, val, color="var(--txt1)"):
        col.markdown(
            f'<div class="metric-card" style="text-align:center;padding:12px 8px;">'
            f'<div class="mc-label">{lbl}</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:1.1rem;font-weight:700;color:{color};">{val}</div>'
            f'</div>', unsafe_allow_html=True)
    _scard(sc1, "🟢 Support S1", f"${S1:.2f}", "#10B981")
    _scard(sc2, "🔴 Resist R1",  f"${R1:.2f}", "#EF4444")
    _scard(sc3, "📊 Pivot",      f"${pivot:.2f}", "#0284C7")
    rsi_color = "#EF4444" if rsi > 70 else "#10B981" if rsi < 30 else "#D97706"
    _scard(sc4, "📈 RSI (14)",   f"{rsi:.0f}", rsi_color)
    _scard(sc5, "🧭 Status",     status)

    # ── Candlestick Chart ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:16px;'>Candlestick Chart</div>", unsafe_allow_html=True)

    if show_vol:
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.75, 0.25], vertical_spacing=0.03)
        row_cs, row_vol = 1, 2
    else:
        fig = go.Figure()
        row_cs = None

    cs_kwargs = dict(row=row_cs, col=1) if show_vol else {}

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"],
        low=hist["Low"],  close=hist["Close"],
        name=selected,
        increasing=dict(line=dict(color="#10B981"), fillcolor="rgba(16,185,129,0.7)"),
        decreasing=dict(line=dict(color="#EF4444"), fillcolor="rgba(239,68,68,0.7)"),
    ), **cs_kwargs)

    ma_styles = {
        "SMA20":  ("#D97706", 1.5),
        "SMA50":  ("#0284C7", 1.8),
        "SMA200": ("#EF4444", 2.0),
    }
    for ma in ma_opts:
        if ma in hist.columns:
            color, width = ma_styles[ma]
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist[ma],
                name=ma, mode="lines",
                line=dict(color=color, width=width),
                hovertemplate=f"{ma}: $%{{y:.2f}}<extra></extra>",
            ), **cs_kwargs)

    # Lines
    line_cfg = [
        (avg_cost, "#D97706", "dash",  f"Entry ${avg_cost:.2f}",  "bottom left"),
        (S1,       "#10B981", "dot",   f"S1 ${S1:.2f}",           "bottom right"),
        (R1,       "#EF4444", "dot",   f"R1 ${R1:.2f}",           "top right"),
        (S2,       "rgba(16,185,129,0.4)", "dashdot", f"S2 ${S2:.2f}", "bottom right"),
        (R2,       "rgba(239,68,68,0.4)", "dashdot", f"R2 ${R2:.2f}", "top right"),
    ]
    hline_fn = fig.add_hline if not show_vol else lambda **kw: fig.add_hline(row=row_cs, col=1, **kw)
    for y_val, color, dash, ann_text, ann_pos in line_cfg:
        hline_fn(y=y_val, line_dash=dash, line_color=color,
                 annotation_text=ann_text, annotation_font_color=color,
                 annotation_position=ann_pos)

    if show_vol:
        colors_vol = ["#10B981" if c >= o else "#EF4444"
                      for c, o in zip(hist["Close"], hist["Open"])]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"],
            name="Volume", marker_color=colors_vol,
            hovertemplate="Volume: %{y:,.0f}<extra></extra>",
        ), row=row_vol, col=1)
        fig.update_yaxes(title_text="Volume", row=row_vol, col=1,
                         gridcolor="rgba(148,163,184,0.12)")

    fig.update_layout(
        height=560, showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569", family="Inter, sans-serif", size=12),
        margin=dict(t=20, b=20, l=10, r=10),
        legend=dict(orientation="h", y=1.04, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)", showgrid=True, rangeslider_visible=False)
    if show_vol:
        fig.update_yaxes(tickprefix="$", gridcolor="rgba(148,163,184,0.12)", row=1, col=1)
        fig.update_yaxes(gridcolor="rgba(148,163,184,0.12)", row=2, col=1)
    else:
        fig.update_yaxes(tickprefix="$", gridcolor="rgba(148,163,184,0.12)")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"S1/R1/S2/R2 = Classic Pivot Points · Entry = ต้นทุนเฉลี่ย ${avg_cost:.2f} · RSI(14) = {rsi:.0f} · {ma_lbl}")


# ── Tab 7: News & Research Reports ───────────────────────────────────────────────

OUTPUT_DIR = TOOLS_DIR.parent / "output"

_KNOWN_TICKERS = [
    "NVDA", "RKLB", "ASTS", "SOFI", "NVO", "UNH", "AMZN", "GOOGL", "PLTR",
    "META", "VST", "OKLO", "SPCX", "MSFT", "TSLA", "AAPL", "AMD", "INTC",
    "ARM", "MSTR", "COIN", "SHOP", "SQ", "PYPL", "HOOD", "ABNB", "UBER",
    "SPY", "QQQ", "IWM",
]

_TYPE_MAP = [
    # (substring_in_filename_lower, icon, label, hex_color)
    ("portfolio_analysis",  "📊", "Portfolio Analysis",  "#6366f1"),
    ("portfolio_full",      "📊", "Portfolio Analysis",  "#6366f1"),
    ("daily_evolve",        "⚡", "Daily Evolve",         "#a5b4fc"),
    ("dream_review",        "💭", "Dream Review",         "#94a3b8"),
    ("dca_",                "💵", "DCA Decision",         "#00d4aa"),
    ("dca_assessment",      "💵", "DCA Decision",         "#00d4aa"),
    ("dca_decision",        "💵", "DCA Decision",         "#00d4aa"),
    ("monitoring_update",   "📡", "Monitoring Update",    "#ffd166"),
    ("youtube_",            "📺", "YouTube Research",     "#f87171"),
    ("youtube",             "📺", "YouTube Research",     "#f87171"),
    ("macro_",              "🌍", "Macro",                "#fb923c"),
    ("geopolitical",        "🗺️", "Geopolitical",         "#fb923c"),
    ("trump_xi",            "🤝", "Geopolitical",         "#fb923c"),
    ("israel",              "🗺️", "Geopolitical",         "#fb923c"),
    ("china_taiwan",        "🗺️", "Geopolitical",         "#fb923c"),
    ("fear_arbitrage",      "🎯", "Fear Arbitrage",       "#f87171"),
    ("berkshire",           "🏛️", "Smart Money",          "#fb923c"),
    ("shay_boloor",         "🧠", "Smart Money",          "#fb923c"),
    ("energy_",             "⚡", "Sector — Energy",      "#ffd166"),
    ("space_",              "🚀", "Sector — Space",       "#a5b4fc"),
    ("_analysis",           "🔬", "Stock Analysis",       "#00d4aa"),
    ("analysis",            "🔬", "Stock Analysis",       "#00d4aa"),
    ("swarm_verdict",       "🤖", "Swarm Verdict",        "#a5b4fc"),
    ("stress_audit",        "🔍", "Risk Audit",           "#f87171"),
    ("thesis_breaker",      "🔍", "Risk Audit",           "#f87171"),
    ("geopolitical",        "🗺️", "Geopolitical",         "#fb923c"),
    ("system_upgrade",      "🔧", "System",               "#94a3b8"),
    ("antigravity",         "🚀", "Feature Ideas",        "#a5b4fc"),
]


def _detect_report_type(rest: str):
    low = rest.lower()
    for key, icon, label, color in _TYPE_MAP:
        if key in low:
            return icon, label, color
    return "📄", "Report", "#6b7280"


def _extract_tickers(text: str) -> list[str]:
    found = []
    upper = text.upper()
    for t in _KNOWN_TICKERS:
        if t in upper:
            found.append(t)
    return found


def _extract_title(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            title = re.sub(r"^#+\s*", "", line)
            title = re.sub(r"[📊📺🌍🗺️🔬💵💭⚡📡🎯🏛️🚀🤝📄🤖🔧]+\s*", "", title)
            # Remove any raw HTML tags to prevent broken DOM layout
            title = re.sub(r"<[^>]*>", "", title)
            # Replace raw $ with fullwidth ＄ to prevent Streamlit LaTeX parser collision
            title = title.replace("$", "＄")
            return title.strip()[:120]
    return ""


@st.cache_data(ttl=30)
def parse_output_files() -> list[dict]:
    reports = []
    if not OUTPUT_DIR.exists():
        return reports
    
    # Load or initialize file times cache (preserves local mtimes on git checkouts)
    cache_path = OUTPUT_DIR / ".file_times.json"
    file_times = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                file_times = json.load(f)
        except Exception:
            pass
            
    cache_dirty = False
    
    file_list = list(OUTPUT_DIR.glob("*.md"))
    for md_file in file_list:
        stem = md_file.stem
        m = re.match(r"^(\d{4}-\d{2}-\d{2})_?(.*)", stem)
        if not m:
            continue
        date_str, rest = m.group(1), m.group(2)
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        type_icon, type_name, type_color = _detect_report_type(rest)
        tickers = _extract_tickers(rest)
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            content = ""
        title = _extract_title(content) or rest.replace("_", " ").title()
        if not tickers:
            tickers = _extract_tickers(content[:800])
            
        # Get preserved modification time
        filename = md_file.name
        mtime_str = file_times.get(filename, "")
        mtime_dt = None
        if mtime_str:
            try:
                mtime_dt = datetime.fromisoformat(mtime_str)
            except Exception:
                pass
                
        if mtime_dt is None:
            try:
                mtime = md_file.stat().st_mtime
                mtime_dt = datetime.fromtimestamp(mtime)
                file_times[filename] = mtime_dt.isoformat()
                cache_dirty = True
            except Exception:
                mtime_dt = datetime.now()
                
        time_str = mtime_dt.strftime("%H:%M")
        reports.append({
            "date": date,
            "date_str": date_str,
            "filename": filename,
            "rest": rest,
            "title": title,
            "tickers": tickers,
            "type_icon": type_icon,
            "type_name": type_name,
            "type_color": type_color,
            "content": content,
            "mtime": mtime_dt,
            "time_str": time_str,
        })
        
    if cache_dirty:
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(file_times, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
            
    reports.sort(key=lambda r: (r["date"], r["mtime"]), reverse=True)
    return reports



def _card_html(rep: dict) -> str:
    """Build the clickable card HTML for one report."""
    import urllib.parse, html as _html
    url = "?" + urllib.parse.urlencode({"report": rep["filename"]})
    safe_title = _html.escape(rep["title"])  # prevent HTML in titles from breaking card structure
    # Replace $ with fullwidth ＄ to prevent Streamlit's LaTeX engine from breaking DOM structure across multiple cards
    safe_title = safe_title.replace("$", "＄")

    ticker_tags = "".join(
        f'<span class="news-tag news-tag-ticker">{t}</span>'
        for t in rep["tickers"]
    )
    type_tag = (
        f'<span class="news-tag news-tag-type" '
        f'style="background:{rep["type_color"]}22;'
        f'border:1px solid {rep["type_color"]}55;'
        f'color:{rep["type_color"]};">'
        f'{rep["type_icon"]} {rep["type_name"]}</span>'
    )
    time_tag = (
        f'<span class="news-tag" style="background:rgba(148,163,184,0.1);'
        f'border:1px solid rgba(148,163,184,0.25);color:#94a3b8;">'
        f'🕒 {rep["time_str"]}</span>'
    )
    return (
        f'<a href="{url}" target="_blank" style="text-decoration:none;display:block;">'
        f'<div class="news-card">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
        f'<div class="news-card-title" style="flex:1;margin-right:12px;">{safe_title}</div>'
        f'<div style="color:#4b5563;font-size:1rem;margin-top:2px;">↗</div>'
        f'</div>'
        f'<div style="margin-top:8px;">{time_tag}{type_tag}{ticker_tags}</div>'
        f'</div>'
        f'</a>'
    )


def render_news():
    reports = parse_output_files()
    if not reports:
        st.info("ไม่พบไฟล์ใน /output — รัน analysis ก่อนแล้วกลับมาใหม่")
        return

    # ── Filter bar ────────────────────────────────────────────────────────────
    all_tickers = sorted({t for r in reports for t in r["tickers"]})
    all_types   = sorted({r["type_name"] for r in reports})
    all_dates   = sorted({r["date"] for r in reports}, reverse=True)

    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        sel_ticker = st.selectbox("🏷️ กรองตาม Ticker", ["ทั้งหมด"] + all_tickers, key="news_ticker")
    with fc2:
        sel_type = st.selectbox("📂 ประเภทรายงาน", ["ทั้งหมด"] + all_types, key="news_type")
    with fc3:
        if len(all_dates) >= 2:
            date_range = st.select_slider(
                "📅 ช่วงวันที่", options=all_dates,
                value=(all_dates[-1], all_dates[0]),
                format_func=lambda d: d.strftime("%d %b %y"),
                key="news_dates",
            )
            date_min = min(date_range)
            date_max = max(date_range)
        else:
            date_min = all_dates[-1] if all_dates else None
            date_max = all_dates[0]  if all_dates else None

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = [r for r in reports
                if (sel_ticker == "ทั้งหมด" or sel_ticker in r["tickers"])
                and (sel_type == "ทั้งหมด" or r["type_name"] == sel_type)
                and (date_min is None or date_min <= r["date"] <= date_max)]

    st.markdown(
        f'<div style="color:#6b7280;font-size:0.8rem;margin:4px 0 12px;">'
        f'แสดง {len(filtered)} จาก {len(reports)} รายงาน · คลิกการ์ดเพื่อเปิดอ่านในแท็บใหม่</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.warning("ไม่พบรายงานที่ตรงกับตัวกรอง")
        return

    # ── Group by date ─────────────────────────────────────────────────────────
    from itertools import groupby
    filtered.sort(key=lambda r: (r["date"], r["mtime"]), reverse=True)

    THAI_MONTHS = {
        1:"ม.ค.", 2:"ก.พ.", 3:"มี.ค.", 4:"เม.ย.", 5:"พ.ค.", 6:"มิ.ย.",
        7:"ก.ค.", 8:"ส.ค.", 9:"ก.ย.", 10:"ต.ค.", 11:"พ.ย.", 12:"ธ.ค.",
    }
    WEEKDAY_TH = ["จันทร์","อังคาร","พุธ","พฤหัส","ศุกร์","เสาร์","อาทิตย์"]

    for date_val, group in groupby(filtered, key=lambda r: r["date"]):
        day_reports = list(group)
        thai_date = f"{date_val.day} {THAI_MONTHS[date_val.month]} {date_val.year}"
        weekday_th = WEEKDAY_TH[date_val.weekday()]
        st.markdown(
            f'<div class="news-date-header">วัน{weekday_th} · {thai_date} '
            f'<span style="color:#4b5563;font-weight:400;">({len(day_reports)} รายงาน)</span></div>',
            unsafe_allow_html=True,
        )
        cards_html = "".join(_card_html(r) for r in day_reports)
        st.markdown(cards_html, unsafe_allow_html=True)


def render_article_reader(filename: str):
    """Full article reader — rendered when ?report=FILENAME is in the URL."""
    reports = parse_output_files()
    rep = next((r for r in reports if r["filename"] == filename), None)

    # ── Reader CSS ────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
      .reader-meta-bar {
        background: linear-gradient(135deg, #1a1d3a 0%, #12152b 100%);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 24px;
        position: relative;
      }
      .reader-meta-bar::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        border-radius: 14px 14px 0 0;
        background: linear-gradient(90deg, #6366f1, #00d4aa);
      }
      .reader-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.4;
        margin-bottom: 12px;
      }
      .reader-date { color: #6b7280; font-size: 0.8rem; margin-bottom: 10px; }
      .reader-body { max-width: 860px; }
    </style>
    """, unsafe_allow_html=True)

    if rep is None:
        st.error(f"ไม่พบรายงาน: {filename}")
        return

    # ── Metadata header ───────────────────────────────────────────────────────
    ticker_tags = "".join(
        f'<span class="news-tag news-tag-ticker">{t}</span>'
        for t in rep["tickers"]
    )
    type_tag = (
        f'<span class="news-tag news-tag-type" '
        f'style="background:{rep["type_color"]}22;border:1px solid {rep["type_color"]}55;'
        f'color:{rep["type_color"]};">'
        f'{rep["type_icon"]} {rep["type_name"]}</span>'
    )
    THAI_MONTHS = {
        1:"ม.ค.", 2:"ก.พ.", 3:"มี.ค.", 4:"เม.ย.", 5:"พ.ค.", 6:"มิ.ย.",
        7:"ก.ค.", 8:"ส.ค.", 9:"ก.ย.", 10:"ต.ค.", 11:"พ.ย.", 12:"ธ.ค.",
    }
    WEEKDAY_TH = ["จันทร์","อังคาร","พุธ","พฤหัส","ศุกร์","เสาร์","อาทิตย์"]
    d = rep["date"]
    date_th = f"วัน{WEEKDAY_TH[d.weekday()]} · {d.day} {THAI_MONTHS[d.month]} {d.year}"

    import html as _html
    safe_reader_title = _html.escape(rep["title"]).replace("$", "＄")
    st.markdown(
        f'<div class="reader-meta-bar">'
        f'<div class="reader-date">📅 {date_th} &nbsp;·&nbsp; 🕒 {rep["time_str"]} &nbsp;·&nbsp; 📁 {_html.escape(rep["filename"])}</div>'
        f'<div class="reader-title">{safe_reader_title}</div>'
        f'<div>{type_tag}{ticker_tags}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Full content ──────────────────────────────────────────────────────────
    st.markdown('<div class="reader-body">', unsafe_allow_html=True)
    if rep["content"]:
        st.markdown(rep["content"])
    else:
        st.warning("ไม่สามารถอ่านเนื้อหาของไฟล์นี้ได้")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Controls")
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        st.caption("**Sources**\n\n📊 Google Sheets (5min)\n💹 yfinance prices (60s)")


# ── Main ──────────────────────────────────────────────────────────────────────────
def main():
    # ── Article reader mode — triggered by ?report=FILENAME ──────────────────
    try:
        report_param = st.query_params.get("report", "")
    except Exception:
        report_param = ""
    if report_param:
        render_article_reader(report_param)
        return

    render_sidebar()

    # Load config
    saved = load_targets()
    cash = float(saved.get("cash", 0.0))

    # FX rate
    fx_rate = get_usd_thb()

    # Header
    hcol1, hcol2 = st.columns([5, 1])
    with hcol1:
        st.markdown(
            '<div class="portfolio-header">'
            '<div class="header-title">💼 My Investment Portfolio</div>'
            '<div class="header-sub">Real-time data · Google Sheets + yfinance · '
            f'{datetime.now().strftime("%d %b %Y %H:%M")} · USD/THB ฿{fx_rate:.2f}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with hcol2:
        st.markdown("<br>", unsafe_allow_html=True)
        show_thb = st.toggle("🇹🇭 แสดงเป็นบาท", value=False, key="thb_toggle")

    with st.spinner("Loading..."):
        df, sheets_summary = load_portfolio(cash=cash)
        tx_df = load_transactions()

    if df.empty:
        st.error("Could not load portfolio from Google Sheets.")
        st.stop()

    # Align 100% with Google Sheets — Keep BTC and SPCX in Overview
    df_overview = df.copy().reset_index(drop=True)
    tx_df_overview = tx_df.copy().reset_index(drop=True)
    current_tickers_overview = set(df_overview[df_overview["ticker"] != "CASH"]["ticker"].tolist())

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview",
        "🎯 Allocation",
        "🧮 DCA Calc",
        "📈 Compounding",
        "📉 Charts",
        "📋 Transactions",
        "📰 News",
    ])

    with tab1:
        render_overview(df_overview, tx_df_overview, fx_rate, show_thb, sheets_summary)
    with tab2:
        render_allocation(df, saved)  # Keeps full list including SPCX & BTC in Allocation tab
    with tab3:
        render_dca(df_overview, fx_rate, show_thb)
    with tab4:
        render_compound(df_overview, fx_rate, show_thb)
    with tab5:
        render_charts(df_overview)
    with tab6:
        render_transactions(tx_df_overview, current_tickers_overview)
    with tab7:
        render_news()


if __name__ == "__main__":
    main()
