# 📊 Portfolio Analysis Workflow — Parallel Per-Stock Architecture
> **Command:** `/portfolio-analysis`
> **หลักการ:** spawn 1 sub-agent ต่อ 1 หุ้น → วิ่งพร้อมกันทั้งพอร์ต → Master Agent รับผลทั้งหมด → สังเคราะห์เป็นรายงานฉบับเดียว

---

## สถาปัตยกรรมภาพรวม

```
/portfolio-analysis
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  PRE-STEP — Portfolio Snapshot (Master Agent เท่านั้น)│
│  python tools/sheets_bridge.py portfolio             │
│  → ได้ list หุ้นทุกตัว + allocation live            │
└─────────────────────────────────────────────────────┘
        │
        ▼  spawn N sub-agents พร้อมกันใน 1 message
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ STOCK-   │ │ STOCK-   │ │ STOCK-   │ │ STOCK-   │ │ STOCK-   │
│ AGENT    │ │ AGENT    │ │ AGENT    │ │ AGENT    │ │ AGENT    │
│ RKLB     │ │ NVDA     │ │ GOOGL    │ │ NVO      │ │ SOFI     │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
     ↓ (parallel — ทุกตัวทำงานพร้อมกัน)
┌──────────┐ ┌──────────┐ ┌──────────┐ ...
│ STOCK-   │ │ STOCK-   │ │ STOCK-   │
│ AGENT    │ │ AGENT    │ │ AGENT    │
│ AMZN     │ │ UNH      │ │ PLTR     │
└──────────┘ └──────────┘ └──────────┘
        │
        ▼  รวมผล stock_brief_packs ทั้งหมด
┌─────────────────────────────────────────────────────┐
│  MASTER SYNTHESIS — เขียนรายงานฉบับเดียว            │
│  Portfolio Health → Brief รายตัว → Action Items      │
│  Agent 10 (Portfolio Construction) รัน cross-check  │
│  Agent 13 (Behavioral) รัน bias + pre-mortem         │
└─────────────────────────────────────────────────────┘
        │
        ▼
   Output รายงาน + Storage Protocol
```

---

## PRE-STEP — Master Agent ทำก่อน Spawn

```bash
# 1. ดึง portfolio snapshot สด — เพื่อรู้ว่าต้อง spawn กี่ตัว
python tools/sheets_bridge.py portfolio

# 2. อ่าน Database/index.md — active alerts ปัจจุบัน
# 3. อ่าน Database/log.md (3 entries ล่าสุด) — context งานที่ผ่านมา
```

**ผลลัพธ์:** Master Agent รู้ว่ามีหุ้น N ตัว → เตรียม prompt สำหรับ N sub-agents

---

## STOCK-AGENT — Template (ใช้กับทุกหุ้น แทน {TICKER} ด้วยชื่อจริง)

> **หมายเหตุ:** Sub-agent แต่ละตัวรับ prompt ต่อไปนี้ — ทำหน้าที่ fetch + brief เท่านั้น ไม่ออก portfolio-level verdict

### Prompt Template สำหรับแต่ละ STOCK-AGENT:

```
คุณคือ Stock Research Sub-Agent สำหรับ {TICKER}
หน้าที่: รวบรวมข้อมูลสดและสรุป brief สำหรับ {TICKER} เท่านั้น
ห้าม: วิเคราะห์ portfolio รวม, ห้ามเปรียบเทียบข้ามหุ้น, ห้ามออก portfolio-level recommendation

ทำตามลำดับ:

STEP 1 — อ่าน Static Knowledge (ไม่ต้อง WebSearch):
- อ่าน Database/stocks/{TICKER}.md → thesis, conviction, last verdict, thesis breakers
- อ่าน Database/sources/{TICKER}.md (ถ้ามี) → topics ที่ research แล้ว
- บันทึก wiki_age = วันนี้ - last_updated

STEP 2 — ดึงข้อมูล Live (รันพร้อมกัน):
a) python tools/yfinance_bridge.py price {TICKER}     ← ราคา + P/L
b) python tools/yfinance_bridge.py info {TICKER}      ← P/E, analyst PT, short float
c) python tools/twelvedata_bridge.py technicals {TICKER}  ← RSI, MACD, BB

⚠️ TwelveData Rate Limit Warning (8 credits/minute):
  - technicals ใช้ 5 credits ต่อหุ้น (4 indicators + 1 price)
  - ถ้า spawn 8 STOCK-AGENTS พร้อมกัน = 40 credits ซึ่งเกิน 8/min limit
  - แต่ละ STOCK-AGENT รัน twelvedata_bridge.py ด้วย internal delay 8s ระหว่าง indicator
  - ผลคือ: parallel spawn ปลอดภัย เพราะ API calls กระจายตัวตาม time — ไม่ burst พร้อมกัน
  - ถ้าได้ 429 error → STOCK-AGENT นั้น fallback: ใช้ yfinance_bridge.py price แทน (ไม่มี technicals)

STEP 3 — 📰 Live Multi-Channel News Search (บังคับรัน 100% ไม่มีข้อยกเว้นเรื่อง wiki_age):
- **ห้ามข้ามเด็ดขาด:** ข่าวสารและอัปเดตคือหัวใจหลักของการทบทวนพอร์ตโฟลิโอ!
- **การดึงข้อมูลสดใหม่ (Freshness Principle):** รัน WebSearch ค้นหาข่าวล่าสุด 2-3 วัน (ห้ามเก่าเกิน 1 สัปดาห์) จาก Web, X/Twitter, YouTube และแหล่งอื่นๆ
- **การคัดกรองข้อมูลซ้ำ (Delta-Aware Deduplication):** ห้ามนำเสนอข่าวเก่าที่ปรากฏใน Database/log.md หรือ sources page แล้ว หรือเคยรายงานไปแล้วในวันเดียวกัน ให้หาข่าวเด่น/ข่าวลึกใหม่ๆ ที่สะท้อนมุมมองที่คนทั่วไปยังไม่รู้
- **จำนวนเป้าหมาย:** สกัดข่าวสดใหม่ให้ได้ **อย่างน้อย 5 ข่าวสาร/เหตุการณ์สัญญาน่าสนใจ** ต่อหุ้นหลักในพอร์ต! พร้อมระบุวันที่ (DD/MM/YYYY) และแหล่งข้อมูลอ้างอิงชัดเจน

STEP 4 — Behavioral Quick Check (Agent 13 — Lightweight) [บังคับทุกหุ้น]:
ตอบ 3 คำถามนี้จากข้อมูลที่หามาใน STEP 1-3:
  Q1. ราคาขึ้น > 30% จาก avg cost → FOMO risk? (อย่า chase momentum)
  Q2. ราคาลง > 25% จาก avg cost → Loss aversion risk? (thesis ยังอยู่ไหม vs แค่ป้องกันเจ็บ)
  Q3. Last verdict ≠ verdict ครั้งนี้ → Anchoring risk? (เปลี่ยนใจเพราะข้อมูลหรือเพราะราคา?)
  Behavioral flag: CLEAR / WATCH / CAUTION (ถ้า CAUTION ต้องอธิบาย 1 บรรทัด)

STEP 4.5 — 🔮 การวิเคราะห์มูลค่าและคาดการณ์ราคา (subagent_forecast integration) [บังคับทุกหุ้น]:
- เรียกใช้กรอบประเมินมูลค่าและคาดการณ์ตามกฎของ `workflows/subagents/subagent_forecast.md`
- คำนวณแบบจำลอง 3 ฉากทัศน์ ครอบคลุม 3 ช่วงเวลา: ระยะสั้น 3 ปี (3-Year), ระยะกลาง 5 ปี (5-Year), และระยะยาว 10 ปี (10-Year) โดยตั้งสมมติฐานหลัก:
  * กำหนดความน่าจะเป็น: Bear Case 30%, Base Case 50%, Bull Case 20%
  * สมมติฐาน: Revenue CAGR, FCF Margin (SBC Adjusted), Terminal Multiple (P/FCF), และ Annual Dilution/Buyback Rate
- คำนวณเป้าหมายราคาหุ้นปีที่ 3, 5, และ 10 ของแต่ละฉากทัศน์ และอัตราผลตอบแทนทบต้นเฉลี่ย (Expected CAGR %) ตามหลักเกณฑ์และสมการทางการเงิน
- คำนวณราคาเป้าหมายถ่วงน้ำหนักความน่าจะเป็น (Expected Probability-Weighted Price) ของทั้ง 3 ช่วงเวลา (3Y, 5Y, 10Y) เพื่อประกอบคำวินิจฉัย (Verdict)

STEP 5 — สร้าง stock_brief_pack และส่งคืน:

STOCK_BRIEF_PACK: {TICKER}
├── Price: $X.XX (±X.XX% วันนี้)
├── Allocation: X.XX% | Shares: X.XX | Avg Cost: $X.XX
├── Gain/Loss: +/-$X.XX (+/-X.XX%)
├── Analyst PT: $XXX (mean, X analysts)
├── RSI: XX.X → [Overbought/Neutral/Oversold]
├── MACD: [Bullish/Bearish]
├── 🔮 การคาดการณ์ราคา 3 ปี, 5 ปี และ 10 ปี (Price Forecast - ตามกฎ subagent_forecast):
│   ├── Valuation Assumptions:
│   │   ├── Base Revenue CAGR: [ CAGR% ]
│   │   ├── FCF Margin (SBC Adjusted) [Bear/Base/Bull]: [ % / % / % ]
│   │   ├── Terminal P/FCF Multiple [Bear/Base/Bull]: [ Xx / Xx / Xx ]
│   │   └── Annual Dilution/Buyback Rate: [ +X% Dilution หรือ -X% Buyback ต่อปี ]
│   ├── 1) ฉากทัศน์ระยะสั้น 3 ปี (3-Year Projection):
│   │   ├── Bear Case (30% Prob): $[Price] | expected CAGR: [+/-]%
│   │   ├── Base Case (50% Prob): $[Price] | expected CAGR: [+/-]%
│   │   ├── Bull Case (20% Prob): $[Price] | expected CAGR: [+/-]%
│   │   └── Expected Probability-Weighted Price (3Y): $[Price]
│   ├── 2) ฉากทัศน์ระยะกลาง 5 ปี (5-Year Projection):
│   │   ├── Bear Case (30% Prob): $[Price] | expected CAGR: [+/-]%
│   │   ├── Base Case (50% Prob): $[Price] | expected CAGR: [+/-]%
│   │   ├── Bull Case (20% Prob): $[Price] | expected CAGR: [+/-]%
│   │   └── Expected Probability-Weighted Price (5Y): $[Price]
│   ├── 3) ฉากทัศน์ระยะยาว 10 ปี (10-Year Projection):
│   │   ├── Bear Case (30% Prob): $[Price] | expected CAGR: [+/-]%
│   │   ├── Base Case (50% Prob): $[Price] | expected CAGR: [+/-]%
│   │   ├── Bull Case (20% Prob): $[Price] | expected CAGR: [+/-]%
│   │   └── Expected Probability-Weighted Price (10Y): $[Price]
├── Key Catalyst (ถ้ามี): [event + วันที่]
├── 📰 ข่าวเดลต้าสดใหม่ 5 ข่าวล่าสุด (ภายใน 2-3 วัน) [บังคับมีขั้นต่ำ 5 ข่าว]:
│   1. [DD/MM/YYYY] [หัวข้อข่าว/เหตุการณ์] | แหล่งอ้างอิง: [Link/Source]
│   2. [DD/MM/YYYY] [หัวข้อข่าว/เหตุการณ์] | แหล่งอ้างอิง: [Link/Source]
│   3. [DD/MM/YYYY] [หัวข้อข่าว/เหตุการณ์] | แหล่งอ้างอิง: [Link/Source]
│   4. [DD/MM/YYYY] [หัวข้อข่าว/เหตุการณ์] | แหล่งอ้างอิง: [Link/Source]
│   5. [DD/MM/YYYY] [หัวข้อข่าว/เหตุการณ์] | แหล่งอ้างอิง: [Link/Source]
├── Conviction: X/10
├── Verdict: HOLD/DCA/TRIM/WATCH/SELL
├── Action: [1 ประโยคว่าต้องทำอะไร ถ้ามี]
├── Thesis Breaker Watch: [เหตุการณ์ที่ต้องระวัง]
└── Behavioral Flag: CLEAR / WATCH / CAUTION — [เหตุผลถ้าไม่ CLEAR]
```

---

## MASTER SYNTHESIS — หลัง Sub-agents ทั้งหมด Complete

Master Agent รับ stock_brief_packs ทุกตัว แล้วสังเคราะห์เป็นรายงานเดียว:

### 1. Portfolio Health Check

```
คำนวณจาก sheets_bridge.py + brief packs รวม:
- Total value + gain/loss รวม
- Allocation breakdown (ใช้ข้อมูลจาก sheets — live)
- Cash level + สถานะ
- Concentration risk (ตัวไหนเกิน 30%?)
- Sector exposure (AI/Tech, Space, Healthcare, etc.)
```

### 2. Brief รายตัว (เรียงตาม allocation สูงสุด → ต่ำสุด)

```
สำหรับแต่ละหุ้น → แปลง stock_brief_pack เป็น section ในรายงาน:

### {EMOJI} {TICKER} — {Company} | {allocation}% | {gain%} | ${price}

**Verdict: {HOLD/DCA/TRIM/WATCH}**

- [bullet 1: thesis status]
- [bullet 2: technical status + key level]
- [bullet 3: catalyst หรือ risk สำคัญ]
- **🔮 คาดการณ์ราคาล่วงหน้า 3 ปี, 5 ปี และ 10 ปี (ตามกฎ subagent_forecast):**
  * **Valuation Assumptions:** Revenue CAGR: X% (Yr 1-5) / Y% (Yr 6-10) | FCF Margin (SBC Adj): [Bear: X% / Base: X% / Bull: X%] | Terminal P/FCF: [Bear: Xx / Base: Xx / Bull: Xx] | Dilution/Buyback: X%
  * **1) ฉากทัศน์ระยะสั้น 3 ปี (3-Year Projection):**
    - Bear Case (30% Prob): **$X.XX** (expected CAGR: X%)
    - Base Case (50% Prob): **$X.XX** (expected CAGR: X%)
    - Bull Case (20% Prob): **$X.XX** (expected CAGR: X%)
    - **Expected Probability-Weighted Price (3Y):** **$X.XX**
  * **2) ฉากทัศน์ระยะกลาง 5 ปี (5-Year Projection):**
    - Bear Case (30% Prob): **$X.XX** (expected CAGR: X%)
    - Base Case (50% Prob): **$X.XX** (expected CAGR: X%)
    - Bull Case (20% Prob): **$X.XX** (expected CAGR: X%)
    - **Expected Probability-Weighted Price (5Y):** **$X.XX**
  * **3) ฉากทัศน์ระยะยาว 10 ปี (10-Year Projection):**
    - Bear Case (30% Prob): **$X.XX** (expected CAGR: X%)
    - Base Case (50% Prob): **$X.XX** (expected CAGR: X%)
    - Bull Case (20% Prob): **$X.XX** (expected CAGR: X%)
    - **Expected Probability-Weighted Price (10Y):** **$X.XX**
- **📰 ข่าวสารเดลต้าสดใหม่ 5 ข่าวล่าสุด (2-3 วัน) [บังคับมี 5 ข่าว]:**
  1. [DD/MM/YYYY] [หัวข้อข่าว/ความเคลื่อนไหว] | [แชลแนล/แหล่งอ้างอิง]
  2. [DD/MM/YYYY] [หัวข้อข่าว/ความเคลื่อนไหว] | [แชลแนล/แหล่งอ้างอิง]
  3. [DD/MM/YYYY] [หัวข้อข่าว/ความเคลื่อนไหว] | [แชลแนล/แหล่งอ้างอิง]
  4. [DD/MM/YYYY] [หัวข้อข่าว/ความเคลื่อนไหว] | [แชลแนล/แหล่งอ้างอิง]
  5. [DD/MM/YYYY] [หัวข้อข่าว/ความเคลื่อนไหว] | [แชลแนล/แหล่งอ้างอิง]
- **Thesis Breaker:** {event}
```

### 3. Cross-Portfolio Analysis (Agent 10 — Master Agent เท่านั้น)

```
ดูภาพรวมที่ sub-agents ไม่เห็น:
- Hidden correlations ระหว่างหุ้น (NVDA+GOOGL+AMZN+PLTR = AI cluster)
- Sector overweight/underweight
- Cash deployment priority
- Factor exposure (growth heavy? defensive ขาด?)
```

### 4. Action Items สัปดาห์นี้

```
รวบรวมจาก verdict ของทุก sub-agent:
🔴 ด่วน: [actions ที่ต้องทำวันนี้/พรุ่งนี้]
🟡 Watch: [events ที่ต้องจับตา]
🟢 ระยะกลาง: [actions ก่อน earnings ถัดไป]
```

### 5. Behavioral Check (Agent 13)

```
มองภาพรวม — biases ที่อาจเกิดใน portfolio context:
- FOMO bias: มีหุ้นตัวไหนที่กำลัง chase momentum?
- Anchoring: มีหุ้นที่ถือเพราะ avg cost มากกว่าเพราะ thesis?
- Inaction bias: มี action ที่ค้างอยู่นานเกินควร?
- Emotional Clearance: Clear/Wait

⚠️ Pre-Mortem บังคับถ้ามีการแนะนำ BUY/DCA/TRIM ใดๆ
```

---

## ตัวอย่าง Spawn Message (Master Agent ส่ง 1 message นี้)

```
ส่ง Agent tool calls พร้อมกัน [ในข้อความเดียว]:

Agent 1 → prompt: STOCK-AGENT template สำหรับ RKLB
Agent 2 → prompt: STOCK-AGENT template สำหรับ NVDA
Agent 3 → prompt: STOCK-AGENT template สำหรับ GOOGL
Agent 4 → prompt: STOCK-AGENT template สำหรับ NVO
Agent 5 → prompt: STOCK-AGENT template สำหรับ SOFI
Agent 6 → prompt: STOCK-AGENT template สำหรับ AMZN
Agent 7 → prompt: STOCK-AGENT template สำหรับ UNH
Agent 8 → prompt: STOCK-AGENT template สำหรับ PLTR

→ รอทุกตัว complete → นำผลมา MASTER SYNTHESIS
```

---

## Mode Exceptions

| Mode | Parallel Stocks? | ความแตกต่าง |
|---|---|---|
| Brief (ปกติ) | ✅ ทุกตัว | Bypasses wiki_age constraints completely. Runs multi-channel News search (P-WEB + P-X + P-YOUTUBE) for all stocks to guarantee at least 5 fresh news items (2-3 days old). |
| Quick snapshot | ✅ ทุกตัว | ข้าม STEP 3 ทั้งหมด — live price only |
| Deep (มี red flag) | ✅ ทุกตัว + escalate | ตัวที่มี red flag → spawn Full Analysis agent แยก |

---

## Storage Protocol (Master Agent ทำหลัง Synthesis เสร็จ)

```bash
# 1. บันทึก output
output/YYYY-MM-DD_portfolio_analysis.md

# 2. อัปเดต Obsidian
# → Database/index.md (allocation table ใหม่, active alerts)
# → Database/log.md (1-3 bullet summary)
# → Database/stocks/{TICKER}.md เฉพาะตัวที่มีข้อมูล/verdict เปลี่ยน

# 3. Upload NotebookLM Master Hub
python tools/notebooklm_bridge.py add-report "d4268735-ab02-40c5-80a1-f1b9768befd9" "output/YYYY-MM-DD_portfolio_analysis.md"
```

แจ้งสถานะ:
```
✅ Output: output/YYYY-MM-DD_portfolio_analysis.md
✅ NotebookLM Master Hub: uploaded
✅ Obsidian: Database/index.md + log.md updated
⚡ Parallel fetch: {N} stocks researched simultaneously
```

---

## ผลลัพธ์ที่คาดหวัง vs เดิม

| | เดิม (Sequential) | ใหม่ (Parallel Per-Stock) |
|---|---|---|
| Fetch + Brief time | ~15-20 นาที | ~3-5 นาที |
| รายงาน | 1 ฉบับ | 1 ฉบับ ✅ (ตามที่ต้องการ) |
| Coverage | ครบ | ครบ |
| Cross-portfolio analysis | ✅ | ✅ (Master Agent เท่านั้น) |
| News freshness | ทุกตัว WebSearch | เฉพาะตัวที่ wiki_age > 3 วัน |
