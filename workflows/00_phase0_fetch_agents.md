# ⚡ Phase 0 — Parallel Data Fetch Agents (Implementation Spec)
> **อ้างอิงจาก:** `00_master_agent.md` ส่วน PHASE 0
> **สถานะ:** Implementation Guide — ใช้งานได้จริง
> **หลักการ:** FETCH agents มีหน้าที่ **fetch + format เท่านั้น** ห้าม analyze, ห้าม verdict, ห้ามตีความ

---

## 🗺️ ภาพรวม Phase 0 — 3-Step Architecture

> **หลักการแก้ไข (จาก Codex audit):** FETCH-C ต้องรู้ wiki_age ก่อนจะรู้ว่าต้อง search หรือไม่ แต่ wiki_age มาจากการอ่าน Database ซึ่งเดิม spawn พร้อม FETCH-C — เป็น race condition
> **Fix:** Master อ่าน wiki ก่อนเสมอ (synchronous) แล้วค่อย spawn agents ด้วย wiki_age ที่รู้แล้ว
> **Fix เพิ่มเติม:** FETCH-C ไม่ spawn sub-agents ซ้อนอีกชั้น — Master spawn platform agents โดยตรงในชั้นเดียว

```
PHASE 0 EXECUTION:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 0 — MASTER PRE-READ (synchronous, NO sub-agent)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Master อ่านเอง (ไม่ spawn):
  อ่าน Database/stocks/{TICKER}.md  → wiki_age, thesis, risks, KPIs, DCA zones
  อ่าน Database/sources/{TICKER}.md → topics ที่ cover แล้ว, delta_needed
  อ่าน Database/log.md (3 entries)   → research context ล่าสุด

→ Master บันทึก wiki_age และ news_scope ก่อน spawn ใดๆ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — PARALLEL SPAWN (1 message, flat — ไม่มี nested agents)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Master spawn ทุกตัวพร้อมกันใน 1 message:

  FETCH-A (portfolio + fundamentals)
  FETCH-B (technicals)
  FETCH-D (NotebookLM query เท่านั้น — wiki อ่านแล้วใน STEP 0)
  [Platform agents ตาม news_scope]:
    P-WEB       (ถ้า news_scope ≥ web)
    P-YOUTUBE   (ถ้า news_scope == full)
    P-X         (ถ้า news_scope ≥ monitoring)
    P-STOCKTWITS (ถ้า news_scope == full)
    P-REDDIT    (ถ้า news_scope == full)

→ รอทุกตัว complete ก่อนไป STEP 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — MASTER AGGREGATES raw_data_pack
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Master รวมผลจาก STEP 0 + STEP 1 ทั้งหมด → raw_data_pack → Phase 1
```

---

## 📋 News Scope Decision Table — Single Source of Truth

> **แก้ปัญหา:** กฎ "wiki_age < 7 วัน = ห้าม WebSearch" ขัดกับ "Mode 5-6 ให้ search" — ตาราง นี้คือ canonical rule ที่ใช้เสมอ

| Mode | wiki_age | news_scope | Platforms ที่ spawn |
|---|---|---|---|
| **1 ⚡ Instant** | any | none | — |
| **2 🔔 Quick Intel** | any | web | P-WEB |
| **3 🎯 Targeted** | ≤ 7d | none | — |
| **3 🎯 Targeted** | 7-30d | web | P-WEB |
| **3 🎯 Targeted** | > 30d | selective | P-WEB + topic platforms |
| **4 🔄 Monitoring** | ≤ 7d | none | — |
| **4 🔄 Monitoring** | 7-30d | monitoring | P-WEB + P-X |
| **4 🔄 Monitoring** | > 30d | monitoring | P-WEB + P-X |
| **5 🏗️ Decision Gate** | ≤ 7d | web | P-WEB (decision ต้องการข่าวล่าสุดเสมอ) |
| **5 🏗️ Decision Gate** | > 7d | full | P-WEB + P-YOUTUBE + P-X + P-STOCKTWITS + P-REDDIT |
| **6 🔬 Full Analysis** | any | full | P-WEB + P-YOUTUBE + P-X + P-STOCKTWITS + P-REDDIT |

**กฎเหล็ก:**
- **Mode 5-6 override wiki_age rule** — Decision Gate ต้องการข่าวล่าสุดเสมอ แม้ wiki จะสด
- **Mode 6 = full search ไม่มีข้อยกเว้น** — ทำ full analysis แล้วต้องค้นครบ
- **USER NEWS INTENT OVERRIDE (บังคับใช้ทุก Mode 2-6)** — หากผู้ใช้ระบุคำว่า "ข่าว", "อัปเดต", "ช่วงนี้", "news", "update" หรือแสดงความต้องการรู้ข่าวสารเหตุการณ์ล่าสุดอย่างชัดเจน ให้เลื่อนระดับ news_scope ขึ้นมาที่อย่างน้อย `monitoring` (P-WEB + P-X) หรือ `full` (ถ้าเจาะลึก) ทันที โดยยกเว้นกฎ wiki_age ทั้งหมด! เพื่อการดึงข้อมูลสดใหม่มาวิเคราะห์แบบเรียลไทม์
- **PORTFOLIO ANALYSIS OVERRIDE (บังคับรันในการวิเคราะห์พอร์ตทั้งหมด)** — บังคับเลื่อนระดับ news_scope ของทุกหุ้นหลักขึ้นมาที่ `monitoring` (P-WEB + P-X) หรือ `full` (ถ้าเจาะลึก) โดยยกเว้นกฎ wiki_age 100% เพื่อให้สอดคล้องกับ **MANDATORY NEWS-HEAVY PROTOCOL** (อย่างน้อย 5 ข่าวสารล่าสุด/ตัวหุ้น สดใหม่ใน 2-3 วัน)
- ถ้า FETCH agent ล้มเหลว → ดู Error Handling ด้านล่าง (ห้าม block ทั้งระบบ)

---

## 📦 FETCH-A — Portfolio & Fundamentals

**หน้าที่:** ดึงข้อมูลพอร์ตสด + ข้อมูลพื้นฐานหุ้นจาก tools
**Tools:** `sheets_bridge.py`, `yfinance_bridge.py`

### Prompt Template สำหรับ FETCH-A sub-agent:

```
คุณคือ FETCH-A — Portfolio & Fundamentals Data Agent สำหรับ {TICKER}
หน้าที่: ดึงข้อมูลด้านล่างแล้วส่งคืนเป็น structured text เท่านั้น
ห้ามวิเคราะห์ ห้ามตีความ ห้ามออก verdict ใดๆ

ทำตาม Mode {MODE}:

[MODE 1 — Instant]:
  1. python tools/sheets_bridge.py portfolio

[MODE 2 — Quick Intel]:
  1. python tools/sheets_bridge.py portfolio
  2. python tools/yfinance_bridge.py info {TICKER}

[MODE 3/4 — Targeted/Monitoring]:
  1. python tools/sheets_bridge.py portfolio
  2. python tools/yfinance_bridge.py price {TICKER}
  3. python tools/yfinance_bridge.py info {TICKER}
  4. python tools/yfinance_bridge.py calendar {TICKER}
  5. python tools/yfinance_bridge.py insider {TICKER}

[MODE 5/6 — Decision/Full]:
  1. python tools/sheets_bridge.py portfolio
  2. python tools/yfinance_bridge.py portfolio
  3. python tools/yfinance_bridge.py price {TICKER}
  4. python tools/yfinance_bridge.py info {TICKER}
  5. python tools/yfinance_bridge.py holders {TICKER}
  6. python tools/yfinance_bridge.py insider {TICKER}
  7. python tools/yfinance_bridge.py calendar {TICKER}
  8. python tools/yfinance_bridge.py financials {TICKER} --quarterly

ส่งคืนในรูปแบบ:
═══════════════════════════════
FETCH-A RESULT: {TICKER} | Status: SUCCESS/PARTIAL/FAILED
═══════════════════════════════
Portfolio snapshot:
  [output จาก sheets_bridge หรือ "sheets_bridge FAILED — ใช้ Database fallback"]

Fundamentals:
  Price: $X.XX | Change: ±X.XX%
  Market Cap: $XB | P/E: X.X | Forward P/E: X.X
  Revenue (TTM): $XB | EPS (TTM): $X.XX
  Analyst PT (mean): $XXX | Analysts: X
  Short Float: X%

Insider Activity (ล่าสุด 90 วัน):
  [สรุป transactions: Buy X shares @ $X / Sell X shares @ $X หรือ "ไม่มี transaction"]

Earnings Calendar:
  Next earnings: [date] | EPS est: $X.XX | Rev est: $XB

Holders Top 5:
  1. [institution] — X%
  2. ...

Quarterly Financials (ถ้า Mode 5-6):
  [ตาราง Revenue/Net Income/FCF 4 ไตรมาสล่าสุด]

Failed tools (ถ้ามี): [list ของ command ที่ fail + error message สั้น]
═══════════════════════════════
```

### FETCH-A Error Handling:

| ล้มเหลว | การจัดการ |
|---|---|
| `sheets_bridge.py` ล้มเหลว | ใช้ `Database/portfolio/overview.md` แทน; ระบุ `portfolio_live: STALE` |
| `yfinance_bridge.py` ล้มเหลว | ใช้ราคาจาก `Database/stocks/{TICKER}.md`; ระบุ `price: STALE` |
| ทั้งสองล้มเหลว | ส่ง `Status: FAILED` — Master ใช้ Database ทั้งหมด; แจ้งใน output |

---

## 📦 FETCH-B — Technicals (Real-Time)

**หน้าที่:** ดึง technical indicators สดจาก Twelve Data
**Tools:** `twelvedata_bridge.py`

> ⚠️ **หมายเหตุ:** `twelvedata_bridge.py portfolio` ใช้ PORTFOLIO_TICKERS ที่ hardcode ไว้ใน tools/twelvedata_bridge.py line 47
> ถ้าซื้อหุ้นใหม่ → ต้องอัปเดต list นั้น manually ด้วย (ต่างจาก yfinance_bridge.py ที่ดึงจาก Sheets อัตโนมัติ)
> FETCH-B ใช้เฉพาะ per-ticker commands (`quote {TICKER}`, `technicals {TICKER}`) — ไม่ได้ใช้ `portfolio` command

### Prompt Template สำหรับ FETCH-B sub-agent:

```
คุณคือ FETCH-B — Technical Data Agent สำหรับ {TICKER}
หน้าที่: ดึง technical indicators แล้วส่งคืนเป็น structured text เท่านั้น
ห้ามวิเคราะห์ ห้ามตีความ ห้ามออก verdict ใดๆ

ทำตาม Mode {MODE}:

[MODE 1-2]:
  1. python tools/twelvedata_bridge.py quote {TICKER}     (1 credit)

[MODE 3-4 — Targeted/Monitoring]:
  1. python tools/twelvedata_bridge.py quote {TICKER}     (1 credit)
  2. python tools/twelvedata_bridge.py technicals {TICKER}  (5 credits)

[MODE 5-6 — Decision/Full]:
  1. python tools/twelvedata_bridge.py quote {TICKER}     (1 credit)
  2. python tools/twelvedata_bridge.py technicals {TICKER}  (5 credits)
  3. python tools/twelvedata_bridge.py time_series {TICKER} --interval 1week --bars 12  (12 credits)

ก่อนรัน ตรวจ credits:
  python tools/twelvedata_bridge.py credits
  ถ้า credits < 20 → รัน quote เท่านั้น, ระบุ "Low credits: technicals skipped"

ส่งคืนในรูปแบบ:
═══════════════════════════════
FETCH-B RESULT: {TICKER} | Status: SUCCESS/PARTIAL/FAILED | Credits used: X
═══════════════════════════════
Price: $X.XX (±X.XX% วันนี้)
  Open: $X.XX | High: $X.XX | Low: $X.XX | Close: $X.XX
  52w High: $X.XX | 52w Low: $X.XX

Technical Indicators (ถ้า technicals ทำงาน):
  RSI(14): X.XX
  MACD: X.XX | Signal: X.XX | Histogram: X.XX
  Bollinger: Upper $X.XX | Middle $X.XX | Lower $X.XX
  ATR(14): $X.XX (expected daily move)

Weekly Trend (12 สัปดาห์, ถ้า time_series ทำงาน):
  [สรุปทิศทาง: Up/Down/Sideways + OHLC สัปดาห์ล่าสุด]

Credits remaining after fetch: X

Failed tools (ถ้ามี): [list + error message]
═══════════════════════════════
```

### FETCH-B Error Handling:

| ล้มเหลว | การจัดการ |
|---|---|
| `twelvedata_bridge.py` ล้มเหลว | ส่ง `Status: FAILED`; Agent 03 จะได้รับ flag `technicals: UNAVAILABLE` |
| Credits หมด | รัน `quote` เท่านั้น; ระบุ `Status: PARTIAL — technicals skipped (low credits)` |
| `time_series` fail (credit ไม่พอ) | ส่ง quote + technicals; ระบุ `weekly_trend: SKIPPED` |

**ถ้า FETCH-B ล้มเหลวทั้งหมด:** Agent 03 ใน Phase 3 ต้องระบุใน output ว่า "Technical data unavailable — analysis based on historical data from Database only"

---

## 📦 Platform Agents — News & Multi-Platform Sentiment

**Architecture (Updated):** Master spawn platform agents โดยตรงในชั้นเดียว — ไม่มี FETCH-C spawner แยกอีกชั้น
**หน้าที่:** แต่ละ platform agent ดึงข้อมูลจาก 1 platform แล้วส่งคืน raw results

> **Master Spawn Rule:** Master ดู `news_scope` จาก News Scope Decision Table แล้ว spawn เฉพาะ platforms ที่จำเป็น
> `news_scope == none` → ไม่ spawn platform agent ใดเลย
> `news_scope == web` → spawn P-WEB เท่านั้น
> `news_scope == monitoring` → spawn P-WEB + P-X
> `news_scope == selective` → spawn P-WEB + platforms ที่เกี่ยวกับ topic
> `news_scope == full` → spawn ครบ P-WEB + P-YOUTUBE + P-X + P-STOCKTWITS + P-REDDIT

**Master รวมผลจาก platform agents ทั้งหมดเป็น `news_platform_results` ใน raw_data_pack**

---

### Platform Prompt: [P-WEB] — Web & Official Sources

```
คุณคือ P-WEB สำหรับ {TICKER}
หน้าที่: ค้นหาข่าวจาก Web และ Official sources เท่านั้น ส่งคืน raw results ไม่ต้องวิเคราะห์

1. WebSearch: "{TICKER} news {CURRENT_MONTH} {CURRENT_YEAR}"
2. WebSearch: "{TICKER} SEC 8-K earnings press release {CURRENT_YEAR}"
3. WebSearch: "{TICKER} analyst upgrade downgrade {CURRENT_YEAR}"
4. WebFetch: https://finance.yahoo.com/quote/{TICKER}/news (ถ้า accessible)

ส่งคืน:
P-WEB RESULT | Status: SUCCESS/PARTIAL/FAILED
  Headlines (เรียงตาม recency, สูงสุด 8):
    1. [headline] | [source] | [URL] | [date] | Tier 1/2
    2. ...
  SEC/IR filings: [filing name + URL หรือ "ไม่มีใหม่"]
  Analyst actions (90d): [upgrade/downgrade + firm + date หรือ "ไม่มี"]
  Failed searches: [list ถ้ามี]
```

---

### Platform Prompt: [P-YOUTUBE] — Video Analysis

```
คุณคือ P-YOUTUBE สำหรับ {TICKER}
หน้าที่: ค้นหา quality YouTube analysis เท่านั้น ส่งคืน raw results ไม่ต้องวิเคราะห์

1. WebSearch: "{TICKER} stock analysis {CURRENT_YEAR} site:youtube.com"
2. WebSearch: "{TICKER} earnings Q{CURRENT_QUARTER} {CURRENT_YEAR} review site:youtube.com"
3. WebSearch: "{TICKER} bull bear case {CURRENT_YEAR} site:youtube.com"

Quality pre-filter (ตัดทิ้งถ้า title มี):
  ❌ "10x in 1 year" / "ขึ้น X เท่า" / "GUARANTEED" / "SECRET"
  ❌ ไม่ระบุ date ใน title หรือ thumbnail เก่ากว่า 90 วัน

ส่งคืน:
P-YOUTUBE RESULT | Status: SUCCESS/PARTIAL/FAILED
  Videos found (สูงสุด 5):
    1. [title] | [channel] | [URL] | [date] | [key point 1 บรรทัด]
    2. ...
  Videos filtered out (clickbait): X รายการ
  ถ้าไม่พบ: "ไม่พบ video ที่ผ่าน pre-filter"
```

---

### Platform Prompt: [P-X] — X/Twitter Analyst Intelligence

```
คุณคือ P-X สำหรับ {TICKER}
หน้าที่: ค้นหา analyst signal บน X/Twitter เท่านั้น ส่งคืน raw results ไม่ต้องวิเคราะห์

1. WebSearch: "site:x.com {TICKER} analysis {CURRENT_YEAR}"
2. WebSearch: "site:x.com unusual_whales {TICKER}"
3. WebSearch: "site:x.com OptionsHawk {TICKER}"
4. WebSearch: "site:x.com Shay Boloor {TICKER}"

ส่งคืน:
P-X RESULT | Status: SUCCESS/PARTIAL/FAILED
  Analyst posts (สูงสุด 5):
    1. [@account] | [key content 1-2 บรรทัด] | [URL] | [date]
    2. ...
  Options flow (unusual_whales): [activity หรือ "ไม่พบ signal"]
  Raw sentiment: Bullish/Neutral/Bearish (จาก keyword count)
  ถ้าไม่พบ: "ไม่พบ quality X content"
```

---

### Platform Prompt: [P-STOCKTWITS] — Retail Sentiment

```
คุณคือ P-STOCKTWITS สำหรับ {TICKER}
หน้าที่: ดู retail sentiment เท่านั้น ส่งคืน raw results ไม่ต้องวิเคราะห์

1. WebSearch: "stocktwits {TICKER} sentiment {CURRENT_YEAR}"
2. WebFetch: https://stocktwits.com/symbol/{TICKER} (ถ้า accessible)

ส่งคืน:
P-STOCKTWITS RESULT | Status: SUCCESS/PARTIAL/FAILED
  Bull/Bear ratio: X% Bull / X% Bear (หรือ "ดึงไม่ได้")
  Message volume: สูง/ปกติ/ต่ำ
  Dominant mood: FOMO/Fear/Neutral/Greed
  ถ้าไม่ได้ข้อมูล: "Stocktwits data unavailable — สาเหตุ: [error]"
```

---

### Platform Prompt: [P-REDDIT] — Community Due Diligence

```
คุณคือ P-REDDIT สำหรับ {TICKER}
หน้าที่: ค้นหา DD และ community analysis เท่านั้น ส่งคืน raw results ไม่ต้องวิเคราะห์

1. WebSearch: "site:reddit.com r/stocks {TICKER} {CURRENT_YEAR}"
2. WebSearch: "site:reddit.com r/SecurityAnalysis {TICKER}"
3. WebSearch: "site:reddit.com r/investing {TICKER} due diligence"

Quality pre-filter:
  ❌ ตัดทิ้งถ้าไม่มีตัวเลขจาก SEC/earnings/IR ใดๆ

ส่งคืน:
P-REDDIT RESULT | Status: SUCCESS/PARTIAL/FAILED
  DD posts (สูงสุด 3):
    1. [post title] | [subreddit] | [URL] | [key argument 1 บรรทัด]
    2. ...
  Community sentiment: Bullish/Neutral/Bearish
  ถ้าไม่พบ DD จริง: "ไม่พบ DD ที่มีข้อมูล — sentiment เท่านั้น"
```

---

### FETCH-C Master — รวมผลจาก 5 Platforms

```
FETCH-C RESULT: {TICKER} | Status: SUCCESS/PARTIAL/FAILED
Platform Coverage:
  🌐 Web (P-WEB):        ✅ SUCCESS / ⚠️ PARTIAL / ❌ FAILED / ⏭️ SKIPPED (reason)
  📺 YouTube (P-YOUTUBE): ✅ SUCCESS / ⚠️ PARTIAL / ❌ FAILED / ⏭️ SKIPPED
  🐦 X/Twitter (P-X):    ✅ SUCCESS / ⚠️ PARTIAL / ❌ FAILED / ⏭️ SKIPPED
  💬 Stocktwits:         ✅ SUCCESS / ⚠️ PARTIAL / ❌ FAILED / ⏭️ SKIPPED
  🔴 Reddit:             ✅ SUCCESS / ⚠️ PARTIAL / ❌ FAILED / ⏭️ SKIPPED

Key Headlines (cross-platform, top 5 เรียงตาม impact):
  1. [headline] | [Source] | [URL] | [date]
  2. ...

Catalysts Found:
  | Catalyst | Date | Impact Est. |
  |---|---|---|
  | [event] | YYYY-MM-DD | High/Med/Low |

Sentiment Summary:
  Web:        Bullish/Neutral/Bearish
  YouTube:    Bullish/Neutral/Bearish / N/A
  X/Twitter:  Bullish/Neutral/Bearish / N/A
  Retail:     X% Bull / X% Bear / N/A

Platforms failed (ถ้ามี): [list + reason]
```

### FETCH-C Error Handling:

| ล้มเหลว | การจัดการ |
|---|---|
| P-WEB ล้มเหลว | ใช้ Database/sources/{TICKER}.md แทน; ระบุ `Web: FAILED - Database fallback` |
| P-YOUTUBE/X/STOCKTWITS/REDDIT ล้มเหลว | ข้ามแพลตฟอร์มนั้น; ระบุ platform status เป็น FAILED; ไม่ block system |
| ทุก platform ล้มเหลว | ส่ง `Status: FAILED`; Agent 01 ใช้ Database wiki; ลด integrity score ของ News section ลง 20 |
| Partial (บาง platform ล้มเหลว) | ส่ง `Status: PARTIAL`; ระบุชัดว่า platform ไหน failed; Agent 01 ทำงานกับข้อมูลที่มี |

---

## 📦 FETCH-D — NotebookLM Query (Simplified)

**หน้าที่:** Query NotebookLM เท่านั้น — การอ่าน Database wiki ถูก Master ทำใน STEP 0 แล้ว
**Tools:** `notebooklm_bridge.py`

> **หมายเหตุ:** FETCH-D เดิมอ่าน Database/stocks/{TICKER}.md + sources/ + log.md ด้วย
> แต่หลัง Fix (Codex audit): งานเหล่านั้นย้ายไปที่ STEP 0 ซึ่ง Master ทำ synchronous ก่อน spawn
> FETCH-D จึงเหลือแค่ NotebookLM query ซึ่ง spawn parallel กับ FETCH-A และ FETCH-B ได้

### Prompt Template สำหรับ FETCH-D sub-agent:

```
คุณคือ FETCH-D — NotebookLM Knowledge Agent สำหรับ {TICKER}
หน้าที่: Query NotebookLM แล้วส่งคืน context ที่เกี่ยวข้อง เท่านั้น
ห้ามวิเคราะห์ ห้ามตีความ ห้ามออก verdict ใดๆ

STEP 1 — Query NotebookLM (ถ้า auth ยังดี)
  python tools/notebooklm_bridge.py query {NOTEBOOK_ID} "latest thesis risks KPIs and catalysts for {TICKER}"

  **Notebook ID Lookup Table** (Master Agent ต้อง substitute ก่อน spawn FETCH-D):
  | TICKER | Notebook ID |
  |---|---|
  | NVDA | 57c70879-a6e5-482e-ad9b-734bbf674950 |
  | RKLB | 78530c2c-b394-4c3c-bc38-f9fd77ec0437 |
  | SOFI | 1f9f76c2-a545-45e0-83c4-421e05b05329 |
  | GOOGL | f524cf09-7a96-4944-9af6-fe52d7476b34 |
  | PLTR | a88d2b0b-6e2b-4961-a245-1d9c4f891238 |
  | AMZN | f380cc6e-a937-4bea-b00a-e62455ca8bd7 |
  | NVO | fd18c356-2817-45ff-9783-2268448f15da |
  | UNH | 4acf1b84-0325-485e-b98b-fdd55c80318d |
  | ASTS | 70898920-4a1b-4b27-8c98-5b8a3e261c14 |
  | Master Hub | d4268735-ab02-40c5-80a1-f1b9768befd9 |

  ถ้า TICKER ไม่อยู่ใน table → ค้นหาก่อน: `python tools/notebooklm_bridge.py find "{TICKER}"`
  ถ้า auth expired → ข้ามและระบุ "NotebookLM: Auth expired — ใช้ Database เท่านั้น"

ส่งคืนในรูปแบบ:
═══════════════════════════════
FETCH-D RESULT: {TICKER} | Status: SUCCESS/FAILED
═══════════════════════════════
NotebookLM context:
  [ข้อมูล thesis, risks, KPIs, catalysts ที่ได้จาก NotebookLM]
  หรือ "Auth expired — ใช้ wiki จาก STEP 0 แทน"
  หรือ "No relevant content found in notebook"
═══════════════════════════════
```

### FETCH-D Error Handling:

| ล้มเหลว | การจัดการ |
|---|---|
| NotebookLM auth expired | ระบุ `Status: FAILED`; ใช้ wiki_summary จาก STEP 0 แทน; ไม่ block ระบบ |
| Notebook ID ไม่อยู่ใน lookup | รัน `notebooklm_bridge.py find "{TICKER}"` ก่อน; ถ้าไม่เจอ → ข้าม |
| NotebookLM ไม่มี content สำหรับ TICKER | ระบุ "No relevant content found"; ไม่ block ระบบ |

---

## 🔄 Master Agent — รับผลและ Build raw_data_pack

หลัง FETCH A-D complete ทั้งหมด Master Agent ทำ:

```python
# STEP 0 result (Master อ่าน synchronous ก่อน spawn — ไม่ใช่จาก FETCH-D)
step0 = {
    "wiki_thesis":     <จาก Database/stocks/{TICKER}.md>,
    "wiki_conviction": <conviction field>,
    "wiki_age":        <วันนี้ - last_updated (คำนวณเอง)>,
    "wiki_risks":      <risk flags ปัจจุบัน>,
    "wiki_kpis":       <KPI watchlist>,
    "wiki_dca_zones":  <DCA zones>,
    "sources_covered": <topics จาก Database/sources/{TICKER}.md>,
    "delta_needed":    <topics ที่ไม่มีใน sources>,
    "log_summary":     <5 entries ล่าสุด จาก log.md>,
    "news_scope":      <none/web/monitoring/selective/full>,
    # news_scope กำหนดจาก News Scope Decision Table ด้านบน
}

# STEP 1 results (parallel agents)
fetch_a = [ผลจาก FETCH-A] or "FAILED"
fetch_b = [ผลจาก FETCH-B] or "FAILED"
fetch_d = [ผลจาก FETCH-D] or "FAILED"   # NotebookLM context เท่านั้น
platform_results = {
    "p_web":        [ผลจาก P-WEB หรือ None ถ้า skip],
    "p_youtube":    [ผลจาก P-YOUTUBE หรือ None],
    "p_x":          [ผลจาก P-X หรือ None],
    "p_stocktwits": [ผลจาก P-STOCKTWITS หรือ None],
    "p_reddit":     [ผลจาก P-REDDIT หรือ None],
}

# STEP 2: Build raw_data_pack (wiki fields มาจาก step0 เสมอ — ไม่ใช่ fetch_d)
raw_data_pack = {
    "ticker":              "{TICKER}",
    "date":                "YYYY-MM-DD",
    # จาก STEP 0 (wiki pre-read)
    "wiki_thesis":         step0.wiki_thesis,
    "wiki_conviction":     step0.wiki_conviction,
    "wiki_age":            step0.wiki_age,
    "wiki_risks":          step0.wiki_risks,
    "wiki_kpis":           step0.wiki_kpis,
    "wiki_dca_zones":      step0.wiki_dca_zones,
    "sources_covered":     step0.sources_covered,
    "delta_needed":        step0.delta_needed,
    "websearch_scope":     step0.news_scope,
    # จาก FETCH-A
    "portfolio_live":      fetch_a.portfolio_snapshot,
    "fundamentals":        fetch_a.fundamentals,
    "insider":             fetch_a.insider_activity,
    "earnings_calendar":   fetch_a.earnings_calendar,
    "holders":             fetch_a.holders_top5,
    # จาก FETCH-B
    "price_live":          fetch_b.price,
    "technicals":          fetch_b.technical_indicators,
    "weekly_trend":        fetch_b.weekly_trend,
    # จาก Platform Agents (P-WEB, P-YOUTUBE, P-X, P-STOCKTWITS, P-REDDIT)
    "news_platform_results": platform_results,
    # จาก FETCH-D (NotebookLM context เท่านั้น)
    "notebooklm_ctx":      fetch_d.notebooklm_context,
    "fetch_status": {
        "A": fetch_a.status,
        "B": fetch_b.status,
        "D": fetch_d.status,
        "platforms": {k: v.status for k, v in platform_results.items() if v},
    }
}

# Gate: abort ถ้าไม่มีข้อมูลพอ
if fetch_a.status == "FAILED" and step0.wiki_age is None:
    → ABORT: แจ้งผู้ใช้ว่าไม่มีข้อมูลพอสำหรับ analysis
else:
    → ส่ง raw_data_pack เข้า Phase 1 พร้อมกัน
```

---

## ⚠️ ข้อควรระวัง

1. **ห้าม FETCH agents วิเคราะห์** — ถ้า FETCH agent ส่งกลับมาพร้อม verdict เช่น "หุ้นนี้ดี" → Master ต้อง ignore ส่วน opinion นั้น
2. **PARTIAL result ยังใช้ได้** — ข้อมูลบางส่วนดีกว่าไม่มีเลย; Master ต้องระบุส่วนที่ขาดใน report
3. **ไม่ block Phase 1 เพราะ FETCH เดียว fail** — ยกเว้น FETCH-D ล้มเหลวทั้งหมด (ไม่มี Database + ไม่มีข่าว)
4. **Log failures ทุกครั้ง** — ทุก FETCH failure ต้องปรากฏใน report section "Data Quality Notes"
5. **Credit tracking** — FETCH-B ต้องรายงาน credits used เสมอ เพื่อให้ Master รู้ว่าเหลือเท่าไหร่สำหรับ technical indicators ใน Phase 3
