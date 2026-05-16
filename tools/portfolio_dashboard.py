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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  .stApp {
    background: radial-gradient(ellipse at top left, #0f1229 0%, #0a0d1a 50%, #050710 100%);
    font-family: 'Inter', sans-serif;
  }

  /* Header */
  .portfolio-header {
    background: linear-gradient(135deg, #1a1d3a 0%, #12152b 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
  }
  .portfolio-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #00d4aa, #ffd166);
  }
  .header-title {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .header-sub { color: #6b7280; font-size: 0.85rem; margin-top: 2px; }

  /* Metric cards */
  .metric-card {
    background: linear-gradient(145deg, #1e2140 0%, #161929 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 14px;
    padding: 18px 22px;
    margin: 4px 0;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
  }
  .metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: rgba(99, 102, 241, 0.5);
  }
  .metric-card.card-value::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
  .metric-card.card-cost::before  { background: linear-gradient(90deg, #64748b, #94a3b8); }
  .metric-card.card-gain-pos::before { background: linear-gradient(90deg, #00d4aa, #34d399); box-shadow: 0 0 12px rgba(0,212,170,0.5); }
  .metric-card.card-gain-neg::before { background: linear-gradient(90deg, #f87171, #ef4444); }
  .metric-card.card-hold::before  { background: linear-gradient(90deg, #ffd166, #f59e0b); }
  .metric-card.card-cash::before  { background: linear-gradient(90deg, #38bdf8, #0ea5e9); }
  .metric-card.card-gain-pos {
    border-color: rgba(0, 212, 170, 0.3);
    box-shadow: 0 0 20px rgba(0, 212, 170, 0.08);
  }
  .metric-card:hover { border-color: rgba(99, 102, 241, 0.5); transform: translateY(-1px); }
  .mc-label {
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 500;
    margin-bottom: 6px;
  }
  .mc-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #f1f5f9;
    line-height: 1.2;
  }
  .mc-delta { font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }
  .pos { color: #00d4aa; }
  .neg { color: #f87171; }
  .neu { color: #a5b4fc; }

  /* Section headers */
  .section-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #6366f1;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 20px 0 10px;
  }

  /* Glass cards */
  .glass-card {
    background: rgba(30, 33, 64, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 14px;
    padding: 16px 20px;
    backdrop-filter: blur(10px);
    margin: 6px 0;
  }

  /* Allocation bar rows */
  .alloc-row {
    background: rgba(30, 33, 64, 0.5);
    border: 1px solid rgba(99, 102, 241, 0.12);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 5px 0;
    transition: border-color 0.2s;
  }
  .alloc-row:hover { border-color: rgba(99, 102, 241, 0.35); }
  .bar-track {
    background: rgba(45, 48, 87, 0.8);
    border-radius: 6px;
    height: 8px;
    width: 100%;
    margin-top: 8px;
    overflow: hidden;
  }
  .bar-fill { height: 8px; border-radius: 6px; }

  /* Transaction rows */
  .tx-group-header {
    background: linear-gradient(135deg, #1e2140 0%, #16192a 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 10px;
    padding: 12px 18px;
    margin: 8px 0 2px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .tx-row {
    background: rgba(20, 23, 40, 0.6);
    border-left: 3px solid transparent;
    border-radius: 0 8px 8px 0;
    padding: 8px 16px 8px 14px;
    margin: 2px 0 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
  }
  .tx-buy { border-left-color: #00d4aa; }
  .tx-sell { border-left-color: #f87171; }
  .tx-div { border-left-color: #ffd166; }

  /* DCA */
  .dca-card {
    background: linear-gradient(145deg, #1e2140 0%, #161929 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 14px;
    padding: 22px 26px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    line-height: 2.1;
  }
  .dca-sep { border-top: 1px solid rgba(99,102,241,0.15); margin: 12px 0; }

  /* Override Streamlit defaults */
  div[data-testid="stMetric"] {
    background: rgba(30, 33, 64, 0.6) !important;
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
  }
  .stDataFrame { border-radius: 12px; overflow: hidden; }
  button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #6366f1 !important;
    color: #a5b4fc !important;
  }
  .stCaption { color: #4b5563 !important; font-size: 0.78rem !important; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1229 0%, #0a0d1a 100%);
    border-right: 1px solid rgba(99,102,241,0.15);
  }
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
    if "gcp_service_account" in st.secrets:
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
    try:
        svc = _sheets_service()
        result = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=range_
        ).execute()
        return result.get("values", [])
    except Exception as e:
        if any(k in str(e) for k in ("invalid_grant", "Token", "revoked")):
            _sheets_service.clear()
            st.error("🔑 Google auth expired — please refresh the page.")
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
                y -= 543  # Thai Buddhist year → Gregorian
            return datetime(y, m, d)
    except Exception:
        pass
    return None


# ── Portfolio data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _load_portfolio_raw() -> list[dict]:
    values = _read_sheet("Portfolio!A:K")
    if not values:
        return []
    headers = values[0]
    rows = []
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        r = dict(zip(headers, padded))
        ticker = r.get("Tracker", "").strip()
        if not ticker:
            continue
        shares = _parse_money(r.get("Shares", ""))
        avg_cost = _parse_money(r.get(" Avg. Cost ", ""))
        if shares > 0 and avg_cost > 0:
            rows.append({
                "ticker": ticker,
                "name": r.get("Company Name", ticker).strip() or ticker,
                "industry": r.get("Industry", "").strip(),
                "shares": shares,
                "avg_cost": avg_cost,
            })
    return rows


@st.cache_data(ttl=60)
def _fetch_prices(tickers: tuple) -> dict[str, float]:
    try:
        import yfinance as yf
        prices = {}
        for t in tickers:
            try:
                prices[t] = float(yf.Ticker(t).fast_info.last_price or 0)
            except Exception:
                prices[t] = 0.0
        return prices
    except ImportError:
        return {t: 0.0 for t in tickers}


def load_portfolio(cash: float = 0.0) -> pd.DataFrame:
    rows = _load_portfolio_raw()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    prices = _fetch_prices(tuple(df["ticker"].tolist()))
    df["price"] = df["ticker"].map(prices).fillna(0.0)
    df["total_cost"] = df["shares"] * df["avg_cost"]
    df["total_value"] = df["shares"] * df["price"]
    df["gain_loss"] = df["total_value"] - df["total_cost"]
    df["gain_pct"] = (df["gain_loss"] / df["total_cost"].replace(0, float("nan")) * 100).round(2)

    # Add cash row
    if cash > 0:
        cash_row = pd.DataFrame([{
            "ticker": "CASH",
            "name": "Cash / USD",
            "industry": "Cash",
            "shares": cash,
            "avg_cost": 1.0,
            "price": 1.0,
            "total_cost": cash,
            "total_value": cash,
            "gain_loss": 0.0,
            "gain_pct": 0.0,
        }])
        df = pd.concat([df, cash_row], ignore_index=True)

    port_total = df["total_value"].sum()
    df["allocation"] = (df["total_value"] / port_total * 100 if port_total > 0 else 0).round(2)
    return df


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
        rows.append({
            "ticker": ticker,
            "name": r.get("Stock Name", ticker).strip(),
            "type": tx_type,
            "date": date,
            "date_raw": date_raw,
            "qty": qty,
            "price": price,
            "dividend": _parse_money(r.get("Dividend", "")),
            "total": total,
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
    return "#00d4aa" if v >= 0 else "#f87171"


def _sign(v: float) -> str:
    return "+" if v >= 0 else ""


def _plotly_base() -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=12),
        margin=dict(t=20, b=20, l=10, r=10),
        xaxis=dict(gridcolor="rgba(99,102,241,0.08)", zerolinecolor="rgba(99,102,241,0.15)"),
        yaxis=dict(gridcolor="rgba(99,102,241,0.08)", zerolinecolor="rgba(99,102,241,0.15)"),
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
            fillcolor="rgba(99,102,241,0.06)" if name == "My Portfolio" else None,
        ))

    _add_series(port_hist["portfolio"], "My Portfolio", "#6366f1", width=3)

    index_colors = ["#00d4aa", "#ffd166", "#f87171", "#a78bfa"]
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
        fig.add_hline(y=0, line_color="rgba(255,255,255,0.1)", line_width=1)
    else:
        fig.update_yaxes(tickprefix="$", title="Portfolio Value ($)")

    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)


# ── Tab 1: Portfolio Overview ─────────────────────────────────────────────────────
def render_overview(df: pd.DataFrame, tx_df: pd.DataFrame, fx_rate: float = 35.0, show_thb: bool = False):
    stock_df = df[df["ticker"] != "CASH"]
    cash_df = df[df["ticker"] == "CASH"]

    total_value = df["total_value"].sum()
    stock_cost  = stock_df["total_cost"].sum()
    stock_gain  = stock_df["gain_loss"].sum()
    gain_pct    = (stock_gain / stock_cost * 100) if stock_cost > 0 else 0
    cash_val    = cash_df["total_value"].sum() if not cash_df.empty else 0

    def _m(v): return fmt_money(v, fx_rate, show_thb)

    # ── Top metrics ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    gain_card_cls = "card-gain-pos" if stock_gain >= 0 else "card-gain-neg"
    gain_val = f"{_sign(stock_gain)}{_m(abs(stock_gain))}"
    cash_pct = f"{cash_val/total_value*100:.1f}% of port" if total_value > 0 else None
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

    st.markdown("<div class='section-title'>Holdings</div>", unsafe_allow_html=True)

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
                "background-color": "rgba(30,33,64,0.6)",
                "color": "#e2e8f0",
                "border": "1px solid rgba(99,102,241,0.12)",
                "font-family": "JetBrains Mono, monospace",
                "font-size": "0.82rem",
            })
        )
        st.dataframe(styled, use_container_width=True, height=360)

    with col_pie:
        pie_df = df[df["total_value"] > 0]
        pie_colors = [TICKER_COLORS.get(t, PALETTE[i % len(PALETTE)]) for i, t in enumerate(pie_df["ticker"])]
        fig_pie = go.Figure(go.Pie(
            labels=pie_df["ticker"],
            values=pie_df["total_value"].round(2),
            hole=0.6,
            marker=dict(colors=pie_colors, line=dict(color="#0a0d1a", width=2)),
            textinfo="percent+label",
            textfont=dict(size=11, family="Inter"),
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
            font=dict(size=16, color="#f1f5f9", family="JetBrains Mono"),
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
            rsi_color = "#f87171" if rsi > 70 else "#00d4aa" if rsi < 30 else "#ffd166"
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
                if val > 70: return "color: #f87171"
                if val < 30: return "color: #00d4aa"
            return "color: #ffd166"
        styled_t = (
            tech_df.style
            .format({"Price": "${:.2f}", "Support (S1)": "${:.2f}", "Resist (R1)": "${:.2f}", "RSI": "{:.0f}"})
            .map(_color_rsi, subset=["RSI"])
            .set_properties(**{
                "background-color": "rgba(30,33,64,0.6)",
                "color": "#e2e8f0",
                "border": "1px solid rgba(99,102,241,0.12)",
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
            <span style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#f1f5f9; font-size:0.95rem;">{t}</span>
            <span style="color:#6b7280; font-size:0.78rem;">{row['name']}</span>
            <span style="font-family:'JetBrains Mono',monospace; font-size:0.82rem;">
              <span style="color:{bar_color}; font-weight:600;">{cur:.1f}%</span>
              <span style="color:#4b5563;"> / tgt {tgt:.0f}% &nbsp;{icon} {diff_str}</span>
            </span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{fill:.1f}%; background:linear-gradient(90deg, {bar_color}cc, {bar_color});"></div>
          </div>
          <div style="position:relative; height:0;">
            <div style="position:absolute; left:{tgt_pos:.1f}%; top:-8px; width:2px; height:8px;
                        background:#ffd166; border-radius:1px;" title="Target {tgt:.0f}%"></div>
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
    tgt_color = "#00d4aa" if ok else "#f87171"
    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace; font-size:0.95rem;">'
        f'Total: <span style="color:{tgt_color}; font-weight:600;">{total_tgt:.1f}%</span>'
        f'<span style="color:#4b5563;"> (target = 100%)</span></p>',
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
            return "color: #00d4aa; font-weight:700" if v == "BUY" else "color: #f87171; font-weight:700"
        styled_r = (
            rdf.style.map(_ac, subset=["Action"])
            .format({"Amount ($)": "${:,.2f}", "Shares": "{:.4f}",
                     "Current %": "{:.1f}%", "Target %": "{:.1f}%"})
            .set_properties(**{
                "background-color": "rgba(30,33,64,0.6)", "color": "#e2e8f0",
                "border": "1px solid rgba(99,102,241,0.12)",
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
            f'<div><div style="color:#6b7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">ถืออยู่</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:#f1f5f9;font-family:JetBrains Mono,monospace;">{row["shares"]:.4f} <span style="font-size:0.8rem;color:#6b7280;">shares</span></div></div>'
            f'<div><div style="color:#6b7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">ต้นทุนเฉลี่ย</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:#ffd166;font-family:JetBrains Mono,monospace;">${row["avg_cost"]:.2f}</div></div>'
            f'<div><div style="color:#6b7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;">ต้นทุนรวม</div>'
            f'<div style="font-size:1.3rem;font-weight:700;color:#a5b4fc;font-family:JetBrains Mono,monospace;">{_m(row["total_cost"])}</div></div>'
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
    avg_color  = "#f87171" if avg_delta > 0 else "#00d4aa"
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

        def _result_card(col, label, value, sub="", color="#f1f5f9"):
            col.markdown(
                f'<div class="metric-card" style="text-align:center;padding:16px 12px;">'
                f'<div class="mc-label">{label}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:1.4rem;font-weight:700;color:{color};line-height:1.2;">{value}</div>'
                f'{"<div style=\"font-size:0.78rem;color:#6b7280;margin-top:4px;\">"+sub+"</div>" if sub else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

        _result_card(r1, "📦 จำนวนหุ้นหลังซื้อ", f"{new_shares:.4f} sh")
        _result_card(r2, "💰 ต้นทุนเฉลี่ยใหม่", f"${new_avg:.2f}",
                     f'{avg_arrow} {avg_delta:+.2f} ({avg_delta_pct:+.2f}%)', avg_color)
        _result_card(r3, "💵 ต้นทุนรวมหลังซื้อ", _m(new_cost))
        _result_card(r4, "📊 สัดส่วนใหม่ในพอร์ต", f"{new_alloc:.1f}%", "", "#a5b4fc")

        st.markdown(
            f'<div class="glass-card" style="margin-top:8px;text-align:center;">'
            f'<div style="color:#6b7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">ราคาตลาด vs ต้นทุนใหม่</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:1.6rem;font-weight:700;color:{vs_color};">'
            f'{_sign(vs_price)}{vs_price:.2f}%</div>'
            f'<div style="color:#6b7280;font-size:0.8rem;">{"📈 ราคาตลาดสูงกว่าต้นทุนใหม่" if vs_price >= 0 else "📉 ราคาตลาดต่ำกว่าต้นทุนใหม่"}</div>'
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
        line=dict(color="#6366f1", width=2.5),
        marker=dict(size=6, color="#6366f1"),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.07)",
        hovertemplate="ซื้อ @ $%{x:.2f}<br>ต้นทุนใหม่: $%{y:.2f}<extra></extra>",
        name="New Avg Cost",
    ))
    fig.add_hline(y=cur_avg, line_dash="dash", line_color="#ffd166",
                  annotation_text=f"ต้นทุนเดิม ${cur_avg:.2f}", annotation_font_color="#ffd166",
                  annotation_position="top left")
    fig.add_vline(x=buy_price, line_dash="dot", line_color="#00d4aa",
                  annotation_text=f"ราคาที่เลือก ${buy_price:.2f}", annotation_font_color="#00d4aa")
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
        def _ps_card(col, label, val, sub="", color="#f1f5f9"):
            col.markdown(
                f'<div class="metric-card" style="text-align:center;">'
                f'<div class="mc-label">{label}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:{color};">{val}</div>'
                f'{"<div style=\'font-size:0.78rem;color:#6b7280;margin-top:4px;\'>"+sub+"</div>" if sub else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )
        _ps_card(pr1, "💸 Max Loss ยอมรับได้", _m(max_loss_usd), f"{risk_pct}% ของพอร์ต", "#f87171")
        _ps_card(pr2, "📉 Risk ต่อ Share", f"${risk_per_share:.2f}", f"entry - stop")
        _ps_card(pr3, "📦 ซื้อได้", f"{ps_shares:.2f} shares", _m(ps_cost))
        _ps_card(pr4, "📊 Alloc หลังซื้อ", f"{new_alloc_ps:.1f}%",
                 f"ปัจจุบัน {cur_alloc:.1f}%",
                 "#f87171" if new_alloc_ps > 30 else "#ffd166" if new_alloc_ps > 20 else "#00d4aa")
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
    def _scard(col, label, val, sub="", color="#f1f5f9"):
        col.markdown(
            f'<div class="metric-card" style="text-align:center;">'
            f'<div class="mc-label">{label}</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:{color};">{val}</div>'
            f'{"<div style=\"font-size:0.78rem;color:#6b7280;margin-top:4px;\">"+sub+"</div>" if sub else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

    _scard(sc1, "💰 มูลค่าพอร์ตสุดท้าย", _m(final_val), f"@ {annual_r}%/yr", "#00d4aa")
    _scard(sc2, "💵 เงินลงทุนสะสมรวม",   _m(total_invested))
    _scard(sc3, "📈 กำไรสุทธิ",           _m(final_gain), f"+{final_gain_p:.0f}%", "#34d399")
    _scard(sc4, "📊 vs " + compare_label.split("(")[0].strip(),
           _m(comp_final), f"@ {compare_r}%/yr", "#a5b4fc")

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
        line=dict(color="#a5b4fc", width=2),
        hovertemplate=f"ปีที่ %{{x}}<br>{compare_label}: {prefix}%{{y:,.0f}}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=year_labels, y=pv_disp,
        name=f"พอร์ตของเรา ({annual_r}%/yr)",
        mode="lines",
        line=dict(color="#00d4aa", width=3),
        fill="tonexty", fillcolor="rgba(0,212,170,0.06)",
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
            return f"color: {'#00d4aa' if val >= 0 else '#f87171'}"
        return ""

    styled_ms = (
        ms_df.style
        .format(fmt_dict)
        .map(_color_gain, subset=[f"กำไรสุทธิ ({prefix})", "กำไร (%)"])
        .set_properties(**{
            "background-color": "rgba(30,33,64,0.6)",
            "color": "#e2e8f0",
            "border": "1px solid rgba(99,102,241,0.12)",
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

                    rows_html += (
                        f'<div class="tx-row {css_cls}" style="opacity:{opacity};">'
                        f'<span style="color:#6b7280; width:90px; display:inline-block;">{date_str}</span>'
                        f'<span style="width:70px; display:inline-block;">{icon} {tx["type"]}</span>'
                        f'<span style="color:#e2e8f0; width:90px; display:inline-block;">{qty_str} sh</span>'
                        f'<span style="color:#ffd166; width:80px; display:inline-block;">@ {price_str}</span>'
                        f'<span style="color:#a5b4fc; font-weight:600;">{total_str}</span>'
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
    def _scard(col, lbl, val, color="#f1f5f9"):
        col.markdown(
            f'<div class="metric-card" style="text-align:center;padding:12px 8px;">'
            f'<div class="mc-label">{lbl}</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:1.1rem;font-weight:700;color:{color};">{val}</div>'
            f'</div>', unsafe_allow_html=True)
    _scard(sc1, "🟢 Support S1", f"${S1:.2f}", "#00d4aa")
    _scard(sc2, "🔴 Resist R1",  f"${R1:.2f}", "#f87171")
    _scard(sc3, "📊 Pivot",      f"${pivot:.2f}", "#a5b4fc")
    rsi_color = "#f87171" if rsi > 70 else "#00d4aa" if rsi < 30 else "#ffd166"
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
        increasing=dict(line=dict(color="#00d4aa"), fillcolor="rgba(0,212,170,0.7)"),
        decreasing=dict(line=dict(color="#f87171"), fillcolor="rgba(248,113,113,0.7)"),
    ), **cs_kwargs)

    ma_styles = {
        "SMA20":  ("#ffd166", 1.5),
        "SMA50":  ("#a5b4fc", 1.8),
        "SMA200": ("#fb923c", 2.0),
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
        (avg_cost, "#ffd166", "dash",  f"Entry ${avg_cost:.2f}",  "bottom left"),
        (S1,       "#00d4aa", "dot",   f"S1 ${S1:.2f}",           "bottom right"),
        (R1,       "#f87171", "dot",   f"R1 ${R1:.2f}",           "top right"),
        (S2,       "rgba(0,212,170,0.4)", "dashdot", f"S2 ${S2:.2f}", "bottom right"),
        (R2,       "rgba(248,113,113,0.4)", "dashdot", f"R2 ${R2:.2f}", "top right"),
    ]
    hline_fn = fig.add_hline if not show_vol else lambda **kw: fig.add_hline(row=row_cs, col=1, **kw)
    for y_val, color, dash, ann_text, ann_pos in line_cfg:
        hline_fn(y=y_val, line_dash=dash, line_color=color,
                 annotation_text=ann_text, annotation_font_color=color,
                 annotation_position=ann_pos)

    if show_vol:
        colors_vol = ["#00d4aa" if c >= o else "#f87171"
                      for c, o in zip(hist["Close"], hist["Open"])]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"],
            name="Volume", marker_color=colors_vol,
            hovertemplate="Volume: %{y:,.0f}<extra></extra>",
        ), row=row_vol, col=1)
        fig.update_yaxes(title_text="Volume", row=row_vol, col=1,
                         gridcolor="rgba(99,102,241,0.08)")

    base = _plotly_base()
    fig.update_layout(
        height=560, showlegend=True,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.04, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        **{k: v for k, v in base.items() if k not in ("xaxis", "yaxis")},
        paper_bgcolor=base["paper_bgcolor"],
        plot_bgcolor=base["plot_bgcolor"],
        font=base["font"],
        margin=base["margin"],
    )
    fig.update_xaxes(gridcolor="rgba(99,102,241,0.08)", showgrid=True)
    fig.update_yaxes(tickprefix="$", gridcolor="rgba(99,102,241,0.08)", row=row_cs if show_vol else None)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"S1/R1/S2/R2 = Classic Pivot Points · Entry = ต้นทุนเฉลี่ย ${avg_cost:.2f} · RSI(14) = {rsi:.0f} · {ma_lbl}")


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
        df = load_portfolio(cash=cash)
        tx_df = load_transactions()

    if df.empty:
        st.error("Could not load portfolio from Google Sheets.")
        st.stop()

    current_tickers = set(df[df["ticker"] != "CASH"]["ticker"].tolist())

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "🎯 Allocation",
        "🧮 DCA Calc",
        "📈 Compounding",
        "📉 Charts",
        "📋 Transactions",
    ])

    with tab1:
        render_overview(df, tx_df, fx_rate, show_thb)
    with tab2:
        render_allocation(df, saved)
    with tab3:
        render_dca(df, fx_rate, show_thb)
    with tab4:
        render_compound(df, fx_rate, show_thb)
    with tab5:
        render_charts(df)
    with tab6:
        render_transactions(tx_df, current_tickers)


if __name__ == "__main__":
    main()
