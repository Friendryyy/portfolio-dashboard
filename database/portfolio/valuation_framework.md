# Financial Statement Adjustment & Valuation Framework
> **สร้าง:** 2026-05-21 | ใช้เป็นเกณฑ์มาตรฐานของ Fundamental AI Agent (Agent 02)
> **วัตถุประสงค์:** สูตรและตรรกะมาตรฐานสำหรับ AMZN, GOOGL, SOFI, RKLB, PLTR, NVDA, NVO, UNH

---

## มิติที่ 1 — SBC Dilution Adjustment

### สูตรหลัก

```
FCF After SBC = CFO - CapEx - SBC
             = Reported FCF - SBC

FCF Margin After SBC = FCF After SBC / Revenue × 100%
SBC Drag             = Reported FCF Margin - FCF Margin After SBC

Dilution Overhang = (Options + RSUs Outstanding) / Shares Outstanding × 100%
```

> **กฎ Agent 02:** เมื่อดึง FCF จาก filing ใดๆ → ต้องหัก SBC ออกจาก CFO เสมอ SBC อยู่ใน CFO Reconciliation section ของ Cash Flow Statement

### เกณฑ์วิเคราะห์ SBC

| SBC / Revenue | SBC / Reported FCF | Verdict |
|---|---|---|
| < 5% | < 20% | ✅ De minimis — ไม่ต้องกังวล |
| 5–10% | 20–40% | 🟡 ใช้ FCF After SBC ทุกการคำนวณ |
| 10–15% | 40–80% | 🔴 FCF รายงานทำให้เข้าใจผิด |
| > 15% | > 80% | 🚨 Red Flag — จ่ายพนักงานด้วยเงินผู้ถือหุ้น |

### การประยุกต์กับพอร์ต

| Ticker | Reported FCF Margin | FCF After SBC | SBC/Revenue | Verdict |
|---|---|---|---|---|
| PLTR | 33.5% | **18.2%** | ~15.3% | 🚨 Red Flag |
| RKLB | Negative | More negative | ~22% | 🚨 Pre-profit + SBC heavy |
| NVDA | ~60% | ~55% | ~5% | ✅ Scale absorbs SBC |
| SOFI | ~20% | ~15% | ~5-7% | 🟡 Monitor (+ MW claim) |
| GOOGL | ~25% | ~22% | ~3% | ✅ ยอมรับได้ |
| AMZN | ~12% | ~9% | ~3% | ✅ ยอมรับได้ |
| NVO | ~30% | ~29% | ~1% | ✅ Pharma SBC ต่ำมาก |
| UNH | ~10% | ~9% | ~1% | ✅ ยอมรับได้ |

---

## มิติที่ 2 — Maintenance CapEx vs Growth CapEx

### สูตรแยก CapEx

**วิธีที่ 1 — D&A Approximation (Buffett's shortcut)**
```
Maintenance CapEx ≈ D&A ของ PP&E (ไม่รวม amortization of intangibles)
Growth CapEx      = Total CapEx - Maintenance CapEx
                  = Total CapEx - D&A ของ PP&E
```

**วิธีที่ 2 — Revenue Ratio Method**
```
Maintenance CapEx = CapEx/Revenue ratio (long-run steady-state avg) × Revenue ปีนี้
Growth CapEx      = Total CapEx - Maintenance CapEx
```

**Owner Earnings (Buffett)**
```
Owner Earnings          = Net Income + D&A + Non-Cash Charges
                        - Maintenance CapEx - Required WC Changes
Owner Earnings Adjusted = Owner Earnings - SBC
```

### AI CapEx — Maintenance หรือ Growth?

```
IF incremental ROIC > WACC → Growth CapEx (value-creating) ✅
IF incremental ROIC < WACC → Maintenance CapEx (survival cost) ⚠️
IF ROIC ≈ WACC            → Neutral

Incremental ROIC = ΔNOPAT / ΔInvested Capital (YoY)
NOPAT            = EBIT × (1 - Tax Rate)
Invested Capital = Total Equity + Total Debt - Excess Cash
```

| สัญญาณ | Growth CapEx ✅ | Maintenance CapEx ⚠️ |
|---|---|---|
| Gross Margin | กำลังขยายตัว | ทรงตัวหรือลด |
| Pricing Power | ขึ้นราคาได้ | ลดราคาตลอด |
| หยุดลงทุนได้ไหม? | ได้ — ยัง earn ปกติ | ไม่ได้ — เสีย customer ทันที |
| Peer behavior | บาง player ไม่ตาม | ทุก player ต้องลงทุนเท่ากัน |

**GOOGL TPU/AI:** Growth CapEx — margin cloud expanding, ขาย TPU ให้ third party ✅
**AMZN Trainium/AWS:** Growth CapEx — AWS ROIC ~25-30% ชัดเจน ✅

---

## มิติที่ 3 — Valuation Multi-Engine

### แผนผังการเลือกเครื่องมือ

```
บริษัทมี FCF เป็นบวกและสม่ำเสมอไหม?

YES → มี moat ที่ยั่งยืนไหม?
      ├─ YES (mature moat) → EPV + DCF   (GOOGL Search, UNH, NVO)
      └─ MEDIUM (growing)  → DCF + PEG   (NVDA, AMZN AWS)

NO  → บริษัทโตเร็วและมี Revenue วัดได้?
      ├─ YES, high growth  → EV/S + Scenario  (RKLB)
      └─ YES, moderate     → P/FCF After SBC  (PLTR, SOFI)
```

### สูตรแต่ละเครื่องมือ

**DCF**
```
Intrinsic Value = Σ[FCFt / (1+WACC)^t] + Terminal Value / (1+WACC)^n
Terminal Value  = FCFn × (1+g) / (WACC - g)
g ต้อง < nominal GDP ≈ 3-4%

WACC ณ 2026-05-21 (30Y = 5.12%):
NVDA (β≈1.7): WACC ≈ 14.5%
RKLB (β≈2.0): WACC ≈ 16.1%
UNH  (β≈0.6): WACC ≈ 8.4%
NVO  (β≈0.5): WACC ≈ 7.9%
```

**PEG Ratio**
```
PEG = Forward P/E / EPS Growth Rate (%)

PEG < 1.0 → undervalued relative to growth
PEG = 1.0 → fairly valued (Lynch's rule)
PEG > 2.0 → expensive
PEG > 3.0 → speculation
```

**EV/Sales**
```
EV  = Market Cap + Total Debt - Cash
EV/S = EV / TTM Revenue

< 5x  → reasonable (gross margin > 60%)
5–15x → elevated, justify ด้วย growth > 30%
> 20x → priced for perfection
> 50x → extreme speculation (RKLB territory)

Rule of 40 + EV/S สำหรับ SaaS:
ถ้า Rule of 40 > 40% AND EV/S < (Rule of 40 / 8) → undervalued
```

**P/TBV (สำหรับธนาคาร — SOFI เท่านั้น)**
```
Tangible Book Value = Total Equity - Goodwill - Intangibles
P/TBV = Market Cap / TBV

< 1.0 → ซื้อสินทรัพย์ต่ำกว่ามูลค่าบัญชี
1–2x  → สมเหตุสมผลสำหรับ ROE 10–15%
> 3x  → ต้องการ ROE > 20%
```

**EPV (Earnings Power Value — Greenwald)**
```
EPV              = Normalized NOPAT / WACC
Franchise Value  = DCF Value - EPV

ถ้า DCF >> EPV → มูลค่ามาจาก growth assumption (risky)
ถ้า DCF ≈ EPV  → value supported ด้วย current earnings (ปลอดภัย)
MoS จริง        = (EPV - Market Price) / Market Price × 100%
```

### Valuation Engine Map — ทั้ง 8 ตัวในพอร์ต

| Ticker | Primary | Secondary | ห้ามใช้ | เหตุผล |
|---|---|---|---|---|
| NVDA | DCF + PEG | P/FCF After SBC | EPV | Growth คือหัวใจ thesis |
| RKLB | EV/S + Scenario | — | DCF, P/E, EPV | Pre-profit |
| GOOGL | DCF + EPV | EV/S (Cloud only) | PEG alone | Search = mature moat |
| AMZN | Sum-of-Parts DCF | EV/EBITDA | P/E หรือ P/S รวม | Retail+AWS margin ต่างกัน |
| SOFI | P/TBV | Forward P/E | EV/S, DCF | Banking model |
| UNH | EPV + DCF | P/E, P/FCF | EV/S | Insurance recurring |
| NVO | DCF | PEG | EV/S | Pharma FCF predictable |
| PLTR | P/FCF After SBC | EV/S | EPV | EPV ให้ค่าต่ำมาก |

### MoS Decision Gate

```
MoS ≥ 30%   → Aggressive DCA
MoS 15–30%  → Moderate DCA (monthly budget ปกติ)
MoS 0–15%   → Hold only — ห้ามเพิ่มไม้ใหม่
MoS < 0%    → ห้ามซื้อ

IF Valuation Confidence < 70% (FCF volatile, pre-profit)
→ ลด max position size ลง 50%
```

### Quick-Reference Formulas

```
FCF After SBC     = CFO - CapEx - SBC
Owner Earnings    = Net Income + D&A - Maintenance CapEx - ΔWWC - SBC
Maintenance CapEx ≈ D&A (PP&E only)
Growth CapEx      = Total CapEx - Maintenance CapEx
ROIC              = NOPAT / Invested Capital
NOPAT             = EBIT × (1 - Tax Rate)
Invested Capital  = Equity + Debt - Excess Cash
Incremental ROIC  = ΔNOPAT / ΔInvested Capital (YoY)
PEG               = Forward P/E / EPS Growth %
EV                = Market Cap + Debt - Cash
EV/S              = EV / TTM Revenue
P/TBV             = Market Cap / (Equity - Goodwill - Intangibles)
EPV               = Normalized NOPAT / WACC
MoS               = (Fair Value - Price) / Price × 100%
SBC Drag          = Reported FCF Margin - FCF After SBC Margin
Rule of 40        = Revenue Growth % + FCF Margin %
```

---

## Common Mistakes — Agent 02 ต้องระวัง

1. **AMZN:** ห้ามใช้ consolidated P/E — ต้องประเมิน AWS แยกก่อนเสมอ
2. **SOFI:** ห้ามใช้ EV/S เพราะ interest income ไม่ใช่ recurring SaaS revenue
3. **RKLB:** DCF terminal value capture Neutron upside → ต้องทำ base/bull/bear scenario แล้ว weight probability
4. **PLTR:** Reported FCF 33.5% ดูดีแต่ After SBC เหลือ 18.2% → valuation ที่ใช้ reported FCF จะ overvalue เสมอ
5. **NVO:** ระวัง Partner Revenue share กับ CVS/Walgreens → ใช้ Organic Revenue growth แทน headline
