# Dynamic DCA & Rebalancing Decision Tree
> **อัปเดต:** 2026-05-24 | พอร์ต $9,058.75 | Cash Live: 17.11% ($1,549.88) / Target: 0.00% (Zero Cash Target) | Horizon: 30 ปี | เป้าหมาย: ฿100M
> **วัตถุประสงค์:** คู่มือสั่งการ Execution รายเดือน — ไร้อารมณ์ ใช้ตรรกะเดียว

---

## Target Allocation Model (ฐานอ้างอิงของทุกการตัดสินใจ)

| Ticker | สัดส่วนปัจจุบัน (Live) | Target | Drift | สถานะและข้อเสนอการลงทุน |
| :--- | :---: | :---: | :---: | :--- |
| **SPCX** | 0.00% | **20.00%** | -20.00% | 🟢 **Core Space Commander (แม่ทัพอวกาศหลัก - รอช้อน Lock-up Expiry Dump)** |
| **RKLB** | 28.47% | **15.00%** | +13.47% | 🔴 **Micro-Trimmed & Buy Block (ถือครอง 19.00 หุ้นเดิม ห้ามเติมเงินใหม่ รอเจือจาง)** |
| **NVDA** | 17.97% | **18.00%** | -0.03% | 🟡 **Core AI Compounder (ถือครองน้ำหนักคงที่บน GPU)** |
| **GOOGL** | 10.29% | **10.00%** | +0.29% | 🟡 **Core AI/Software (ถือครองน้ำหนักคงที่บน Cloud)** |
| **SOFI** | 5.87% | **10.00%** | -4.13% | ⏸️ **Hold Only (ล็อคเงินสดสำรอง $374.17 USD เตรียมสะสมเมื่อคลี่คลายคดี)** |
| **TSM** | 4.97% | **6.00%** | -1.03% | 🟢 **DCA Active (เริ่มสะสม Tranche 1 แล้ว $450.00 USD @ Bollinger Middle)** |
| **AMZN** | 5.64% | **5.00%** | +0.64% | 🟡 **Core Cloud/Retail (ถือสะสมรายไตรมาส)** |
| **NVO** | 6.94% | **6.00%** | +0.94% | 🟡 **Core Pharma (สะสมเพิ่มด่วน $250.00 USD เรียบร้อย)** |
| **BTC** | 4.97% | **5.00%** | -0.03% | 🟢 **DCA Active (เริ่มสะสม Tranche 1 แล้ว $450.00 USD ป้องกันเงินเฟ้อ)** |
| **UNH** | 5.45% | **5.00%** | +0.45% | 🟢 **DCA Active (สะสมบนแรงย่อตัว ในโซนสะสม $350-385)** |
| **PLTR** | 0.00% | **0.00%** | 0.00% | 🔴 **Closed (ปิดพอร์ตโฟลิโอ 100% เรียบร้อย)** |
| **Cash** | 0.00% | **0.00%** | 0.00% | ✅ **Zero Cash Target (จัดสรรเงินสดในบัญชีสะสมหุ้นใช้งานทั้งหมด)** |

---

## ส่วนที่ 1 — RKLB Risk Ceiling Protocol

```
1. IF RKLB allocation > 35%
   └── MANDATORY TRIM ทันที (ไร้เงื่อนไข ไม่สนใจราคาตลาดและกำไร)
   └── ดำเนินการขายเพื่อปรับสัดส่วนเป้าหมายกลับคืนระดับ 27% เสมอ
   └── เงินสดที่ได้จากการ Trim: นำไปสะสมต่อใน Priority List (ส่วนที่ 3)

2. IF RKLB allocation 30% – 35%
   └── HARD BUY BLOCK — สั่งระงับการซื้อเพิ่มเด็ดขาด!
   └── แม้ว่าราคาจะร่วงลง 20% - 30% ก็ห้ามเพิ่มความเสี่ยง RKLB ในพอร์ต
   └── ดำเนินการ: HOLD และรอให้สัดส่วนพอร์ตตัวอื่นเติบโตขึ้นเพื่อ Rebalance เองตามกลไก

3. IF RKLB allocation 25% – 30% (สถานะปัจจุบันหลัง Micro-Trim: 28.47%)
   └── HOLD STATUS — ไม่ซื้อเพิ่ม รักษาปริมาณหุ้นให้คงที่ที่ 19.00 หุ้น
   └── รอให้ขนาดธุรกิจของ RKLB หรือหุ้นตัวอื่นๆ โตมาทดแทนเชิงออร์แกนิก

4. IF RKLB allocation < 25%
   └── เข้าสู่ WATCH ZONE — ป้องกันความเสี่ยง ห้ามซื้อสะสมทั่วไป
   └── อนุญาตให้ทำ DCA ได้ ภายใต้เงื่อนไข A AND B AND C ครบถ้วนเท่านั้น:
        (A) โครงการ Neutron คืบหน้าในตารางเวลา (ไม่ล่าช้าเกิน Q4/2026)
        (B) ไม่มีสัญญาจัดหาโครงการความมั่นคงด้านอวกาศถูกยกเลิก
        (C) อัตราเติบโตรายได้ (Revenue Growth) คงระดับ > 30% YoY
   └── หากขาดข้อใดข้อหนึ่ง → สั่งการ HOLD ห้ามสะสมเด็ดขาด
```

**เหตุผลเชิงคณิตศาสตร์:**
* RKLB -90% × 30% allocation = พอร์ตสูญ 27% → ต้องใช้เวลา 4-5 ปีดึงทุนคืน
* RKLB -90% × 28.47% allocation = พอร์ตสูญ 25.6% → ควบคุมได้ดีกว่า และการ Micro-Trim ออกบางส่วนช่วยปลดปล่อยทุนไปเพิ่มผลตอบแทนทบต้นใน NVO/TSM/BTC ที่ปลอดภัย

---

## ส่วนที่ 2 — Cash Deployment Protocol

กระแสเงินสดดำเนินการสะสมทั้งหมด **$2,004.80 USD** หลังจากการทำธุรกรรมสลับทุน (Micro-Trim RKLB + Exit PLTR) ได้รับการจัดสรรกระจาย 100% สู่การลงทุน:

```
[เงินสดดำเนินการสะสม $2,004.80 USD]
  ├── NVO Buy Execution (เข้าช้อนซื้อลดต้นทุน): $250.00 USD
  ├── TSM Tranche 1 Buy (สะสมชิปแม่ทัพเทคโนโลยี): $450.00 USD
  ├── BTC Tranche 1 Buy (สะสมประกันภัยเงินเฟ้อ): $450.00 USD
  └── SOFI & SPCX Capital Preservation Reserve (ล็อคสำรองเชิงรับ): $854.80 USD
       ├── SOFI Reserve (เตรียมสะสมเมื่อเคลียร์งบ): $374.17 USD
       └── SPCX IPO Reserve (เตรียมช้อน SpaceX IPO): $480.63 USD
```

---

## ส่วนที่ 3 — DCA Priority Order

**Scoring:** `Priority = (Allocation Drift × 0.4) + (MoS Score × 0.4) + (Conviction × 0.2)`

```
══════════════════════════════════════════════════════
           DCA PRIORITY ORDER — 2026-05-24
══════════════════════════════════════════════════════

🥇 PRIORITY 1 — 💊 NVO (Novo Nordisk)
   Drift: +0.94% | MoS: HIGH (P/E 9.6x ถูกสุด 10 ปี) | Conviction: 7/10
   → จัดสรรสะสมไม้ใหญ่ $250.00 USD เรียบร้อย ทยอยสะสมต่อรายเดือนรักษาความแข็งแกร่ง

🥈 PRIORITY 2 — 🖥️ NVDA (NVIDIA)
   Drift: -0.03% | MoS: MEDIUM-HIGH (Forward P/E 19x, PEG 0.71x) | Conviction: 8/10
   → ถือครองสถานะหลัก 7.56 หุ้น รอสะสมเพิ่มเมื่อราคาย่อแตะ $205-215

🥉 PRIORITY 3 — 🖥️ TSM (TSMC)
   Drift: -1.03% | MoS: HIGH (PE 20.7x, MoS +5.59%) | Conviction: 8.5/10
   → เริ่มสะสม Tranche 1 แล้ว $450.00 USD @ Bollinger Middle

4️⃣ PRIORITY 4 — 🪙 BTC (Bitcoin)
   Drift: -0.03% | MoS: HIGH (Drawdown -39.3% from ATH) | Conviction: 8/10
   → เริ่มสะสม Tranche 1 แล้ว $450.00 USD เพื่อป้องกัน Dollar Debasement

5️⃣ PRIORITY 5 — 📦 AMZN (Amazon)
   Drift: +0.64% | MoS: MEDIUM | Conviction: 6/10
   → DCA รายไตรมาส หรือเบิกจ่ายซื้อช่วงตลาดหดตัว Tier C, D

6️⃣ PRIORITY 6 — 🔍 GOOGL (Alphabet)
   Drift: +0.29% | MoS: MEDIUM | Conviction: 7/10
   → DCA รายไตรมาส

7️⃣ PRIORITY 7 — 🏥 UNH (UnitedHealth Group)
   Drift: +0.45% | Risk Flag: ⚠️ DOJ Investigation
   → อนุมัติ DCA ซื้อสะสมบนแรงย่อตัว ในโซนสะสม $350 - $385
   → VETO Line: สั่งยกเลิก DCA และปิดโพซิชั่น 100% หาก DOJ สั่งยื่นฟ้องคดีอาญา

⏸️ HOLD ONLY — 💳 SOFI (SoFi Technologies)
   Drift: -4.13% | Risk Flag: MW Cloud
   → ล็อคเงินสดสะสมสำรอง $374.17 USD รอ SEC ปิดคดีประเด็นบัญชีฉ้อโกง

🔴 BUY BLOCK — 🚀 RKLB (Rocket Lab)
   Drift: +13.47% | Concentration Defense (28.47% > 15% target)
   → ล็อคสถานะ HOLD ห้ามสั่งซื้อเพิ่มเด็ดขาด เพื่อรอเจือจางออร์แกนิก

🔴 CLOSED — 🔐 PLTR (Palantir)
   Drift: 0.00% | Conviction: 0.0/10
   → ปิดโพซิชั่นขายทิ้ง 100% เรียบร้อยแล้ว

══════════════════════════════════════════════════════
```

---

## Monthly DCA Execution Template

```
════════════════════════════════════════════════
   MONTHLY DCA CHECKLIST — [YYYY-MM]
════════════════════════════════════════════════

STEP 1 — RKLB & Space Ceiling Check
[ ] รัน sheets_bridge.py → ดู RKLB allocation และ SPCX
    > 35% Space Ceiling (RKLB + SPCX) → Trim ก่อน DCA
    30–35% RKLB → Buy Block (งดสะสม)
    < 30% RKLB → ดำเนินการต่อ

STEP 2 — Risk Flag Scan
[ ] SOFI: SEC investigation formal order เปิดหรือยัง? (ถ้าใช่ → SELL ทันที)
[ ] UNH: Criminal indictment ออกต่อ C-suite หรือยัง? (ถ้าใช่ → SELL ทันที)
[ ] RKLB: Neutron delay เกิน Q4 2026? (ถ้าใช่ → ลด ceiling เหลือ 20%)

STEP 3 — Market Condition
[ ] S&P500 vs ATH ล่าสุด = -X%
    < 10%  → Condition A
    10–20% → Condition B
    20–30% → Condition C
    > 30%  → Condition D

STEP 4 — Allocate Budget
[ ] งบ DCA เดือนนี้รวม: $________________ USD
    NVO:   40–50% = $______
    NVDA:  30–40% = $______
    TSM:   10–15% = $______
    BTC:   5–10%  = $______
    UNH:   0% (DCA only on dip zones $350-385)

STEP 5 — Execute + Record
[ ] กดซื้อตามแผนจริงผ่านโบรกเกอร์
[ ] Update sheets_bridge portfolio
[ ] Append log.md

════════════════════════════════════════════════
```

---

## กฎเหล็ก 5 ข้อ

```
1. RKLB > 30% → ห้ามซื้อเพิ่มเด็ดขาด และถ้าร่วมกับ SPCX แล้ว กลุ่มอวกาศรวม (Space Ceiling) ห้ามเกิน 35.00%
2. NVO, NVDA, TSM, BTC คือเป้าหมาย DCA Active ปัจจุบันเพื่อกระชับน้ำหนักพอร์ต
3. Cash Target คือ 0.00% (Zero Cash) จัดสรรเงินสะสม DCA ฿4,000/เดือน สู่สินทรัพย์คุณภาพทันที
4. ห้ามไล่ราคา SPCX (SpaceX) ในวันแรก (Day 1 Pop) รอช้อนซื้อช่วง Lock-up Expiry Dump ($70-80) ปลายปี 2026
5. Risk Flag (SEC/DOJ/MW) และกติกา VETO → ขาย 100% ทันทีหาก DOJ สั่งฟ้องอาญา UNH หรือ SOFI มี SEC Formal Order
```
