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
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: rgba(99, 102, 241, 0.5); }
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
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
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
def render_overview(df: pd.DataFrame, tx_df: pd.DataFrame):
    stock_df = df[df["ticker"] != "CASH"]
    cash_df = df[df["ticker"] == "CASH"]

    total_value = df["total_value"].sum()          # รวม cash
    stock_cost  = stock_df["total_cost"].sum()     # ต้นทุนหุ้นอย่างเดียว
    stock_gain  = stock_df["gain_loss"].sum()      # กำไรหุ้นอย่างเดียว
    gain_pct    = (stock_gain / stock_cost * 100) if stock_cost > 0 else 0
    cash_val    = cash_df["total_value"].sum() if not cash_df.empty else 0

    # ── Top metrics ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("💼 Portfolio Value", f"${total_value:,.2f}", None, "neu"),
        ("💵 Invested (Cost)", f"${stock_cost:,.2f}", None, "neu"),
        ("📈 Unrealized P/L", f"{_sign(stock_gain)}${abs(stock_gain):,.2f}",
         f"{_sign(gain_pct)}{gain_pct:.2f}%", "pos" if stock_gain >= 0 else "neg"),
        ("🏦 Holdings", f"{len(stock_df)}", None, "neu"),
        ("💵 Cash", f"${cash_val:,.2f}", f"{cash_val/total_value*100:.1f}% of port" if total_value > 0 else None, "neu"),
    ]
    for col, (label, val, delta, cls) in zip([c1, c2, c3, c4, c5], metrics):
        d_html = f'<div class="mc-delta {cls}">{delta}</div>' if delta else ""
        col.markdown(
            f'<div class="metric-card">'
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
        fig_pie = go.Figure(go.Pie(
            labels=pie_df["ticker"],
            values=pie_df["total_value"].round(2),
            hole=0.6,
            marker=dict(colors=PALETTE[:len(pie_df)], line=dict(color="#0a0d1a", width=2)),
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
def render_dca(df: pd.DataFrame):
    st.markdown("<div class='section-title'>DCA Average Cost Calculator</div>", unsafe_allow_html=True)

    stock_df = df[df["ticker"] != "CASH"]
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        selected = st.selectbox("Select Stock", stock_df["ticker"].tolist(), key="dca_ticker")
        row = stock_df[stock_df["ticker"] == selected].iloc[0]
        default_p = float(row["price"]) if row["price"] > 0 else float(row["avg_cost"])

        buy_price = st.number_input("Buy Price ($)", min_value=0.01, value=round(default_p, 2),
                                    step=0.01, format="%.4f", key="dca_price")
        method = st.radio("Buy by", ["Shares", "Dollar Amount"], horizontal=True, key="dca_method")

        if method == "Shares":
            buy_qty = st.number_input("Shares", min_value=0.0001, value=1.0, step=0.5, format="%.4f", key="dca_qty")
            buy_cost = buy_qty * buy_price
        else:
            buy_cost = st.number_input("Amount ($)", min_value=1.0, value=500.0, step=50.0, format="%.2f", key="dca_amt")
            buy_qty = buy_cost / buy_price

        st.markdown(
            f'<div class="glass-card" style="margin-top:12px;">'
            f'<div style="color:#6b7280; font-size:0.7rem; letter-spacing:1px; text-transform:uppercase;">Current</div>'
            f'<div style="font-family:JetBrains Mono,monospace; color:#e2e8f0; margin-top:6px;">'
            f'{row["shares"]:.4f} shares @ <span style="color:#ffd166;">${row["avg_cost"]:.2f}</span><br>'
            f'Cost: <b>${row["total_cost"]:,.2f}</b></div></div>',
            unsafe_allow_html=True,
        )

    # Calc
    cur_shares, cur_avg, cur_cost = row["shares"], row["avg_cost"], row["total_cost"]
    new_shares = cur_shares + buy_qty
    new_cost = cur_cost + buy_cost
    new_avg = new_cost / new_shares
    avg_delta = new_avg - cur_avg
    avg_delta_pct = avg_delta / cur_avg * 100
    avg_arrow = "↑" if avg_delta > 0 else "↓"
    avg_color = "#f87171" if avg_delta > 0 else "#00d4aa"
    vs_price = (buy_price - new_avg) / new_avg * 100
    vs_color = _gc(vs_price)

    port_total_ex = df["total_value"].sum() - row["total_value"]
    new_pos_val = new_shares * buy_price
    new_alloc = new_pos_val / (port_total_ex + new_pos_val) * 100 if (port_total_ex + new_pos_val) > 0 else 0

    with col_out:
        st.markdown(
            f'<div class="dca-card">'
            f'<div style="color:#6366f1; font-size:0.7rem; letter-spacing:1px; text-transform:uppercase; margin-bottom:4px;">Purchase</div>'
            f'🛒 {buy_qty:.4f} sh @ <span style="color:#ffd166;">${buy_price:.2f}</span> = <b>${buy_cost:,.2f}</b>'
            f'<div class="dca-sep"></div>'
            f'<div style="color:#6366f1; font-size:0.7rem; letter-spacing:1px; text-transform:uppercase; margin-bottom:4px;">After Purchase</div>'
            f'📦 Shares &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <b>{new_shares:.4f}</b><br>'
            f'💰 New Avg &nbsp;&nbsp;&nbsp;&nbsp;: <b style="color:{avg_color};">${new_avg:.2f}</b>'
            f' &nbsp;<span style="color:{avg_color};">{avg_arrow} {avg_delta:+.2f} ({avg_delta_pct:+.2f}%)</span><br>'
            f'💵 Total Cost &nbsp;: <b>${new_cost:,.2f}</b><br>'
            f'📊 New Alloc &nbsp;&nbsp;: <b style="color:#a5b4fc;">{new_alloc:.1f}%</b>'
            f'<div class="dca-sep"></div>'
            f'📈 vs Buy Price: <b style="color:{vs_color};">{_sign(vs_price)}{vs_price:.2f}%</b>'
            f'<span style="color:#4b5563; font-size:0.8rem;"> ({"upside" if vs_price>=0 else "downside"} from new avg)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Sensitivity chart
    st.markdown("<div class='section-title' style='margin-top:20px;'>Avg Cost Sensitivity</div>", unsafe_allow_html=True)
    px_range = [buy_price * (0.5 + i * 0.05) for i in range(21)]
    avgs = [(cur_cost + buy_cost) / (cur_shares + buy_cost / p) for p in px_range if p > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=px_range[:len(avgs)], y=avgs,
        mode="lines+markers",
        line=dict(color="#6366f1", width=2),
        marker=dict(size=5, color="#6366f1"),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.06)",
        hovertemplate="Buy @ $%{x:.2f}<br>New Avg: $%{y:.2f}<extra></extra>",
    ))
    fig.add_hline(y=cur_avg, line_dash="dash", line_color="#ffd166",
                  annotation_text=f"Current ${cur_avg:.2f}", annotation_font_color="#ffd166")
    fig.add_vline(x=buy_price, line_dash="dot", line_color="#6b7280",
                  annotation_text=f"Buy @ ${buy_price:.2f}", annotation_font_color="#6b7280")
    fig.update_layout(height=280, showlegend=False, **_plotly_base())
    fig.update_xaxes(title="Buy Price ($)")
    fig.update_yaxes(title="New Avg Cost ($)")
    st.plotly_chart(fig, use_container_width=True)


# ── Tab 4: Transaction History ────────────────────────────────────────────────────
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

    # Header
    st.markdown(
        '<div class="portfolio-header">'
        '<div class="header-title">💼 My Investment Portfolio</div>'
        '<div class="header-sub">Real-time data · Google Sheets + yfinance · '
        f'{datetime.now().strftime("%d %b %Y %H:%M")}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Loading..."):
        df = load_portfolio(cash=cash)
        tx_df = load_transactions()

    if df.empty:
        st.error("Could not load portfolio from Google Sheets.")
        st.stop()

    current_tickers = set(df[df["ticker"] != "CASH"]["ticker"].tolist())

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🎯 Allocation",
        "🧮 DCA Calc",
        "📋 Transactions",
    ])

    with tab1:
        render_overview(df, tx_df)
    with tab2:
        render_allocation(df, saved)
    with tab3:
        render_dca(df)
    with tab4:
        render_transactions(tx_df, current_tickers)


if __name__ == "__main__":
    main()
