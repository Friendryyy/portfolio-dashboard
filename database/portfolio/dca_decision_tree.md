# Dynamic DCA & Rebalancing Decision Tree
> **อัปเดต:** 2026-05-24 | พอร์ต $9,058.75 | Cash Live: 17.11% ($1,549.88) / Target: 0.00% (Zero Cash Target) | Horizon: 30 ปี | เป้าหมาย: ฿100M
> **วัตถุประสงค์:** คู่มือสั่งการ Execution รายเดือน — ไร้อารมณ์ ใช้ตรรกะเดียว

---

## Target Allocation Model (ฐานอ้างอิงของทุกการตัดสินใจ)

| Ticker | สัดส่วนปัจจุบัน (Live) | Target | Drift | สถานะและข้อเสนอการลงทุน |
| :--- | :---: | :---: | :---: | :--- |
| **NVDA** | 19.53% | **20.00%** | -0.47% | 🟡 **Core AI Compounder (ถือครองน้ำหนักคงที่บน GPU)** |
| **RKLB** | 32.41% | **15.00%** | +17.41% | 🔴 **Buy Blocked (ถือครอง 19.00 หุ้นเดิม คุมความเสี่ยง Space ceiling <35%)** |
| **GOOGL** | 11.33% | **10.00%** | +1.33% | 🟡 **Core AI/Software (ถือครองน้ำหนักคงที่บน Cloud)** |
| **UNH** | 7.76% | **8.00%** | -0.24% | 🟢 **DCA Active (สะสมเพิ่มตามเป้าหมายน้ำหนัก 8% ใหม่)** |
| **NVO** | 7.81% | **8.00%** | -0.19% | 🟢 **DCA Active (DCA Priority #2 - ตั้ง GTC Limit Order สะสม $250 ในโซน < $44.55)** |
| **SOFI** | 7.59% | **8.00%** | -0.41% | ⏸️ **Hold Only (ปรับเพิ่มเป้าหมายเป็น 8.00% ตามความต้องการจัดพอร์ตสะสมค้างรับผลบวก Stablecoin / ปลดล็อกเงินสดแล้ว)** |
| **TSM** | 1.86% | **8.00%** | -6.14% | 🟢 **DCA Active (DCA Priority #1 - ตั้ง GTC Limit Order สะสม $450 ในโซน $385-$415)** |
| **AMZN** | 6.35% | **5.00%** | +1.35% | 🟡 **Core Cloud/Retail (เป้าหมายปรับเป็น 5.00% / ถือครองเพื่อรองรับการเจือจาง)** |
| **SPCX** | 0.00% | **13.00%** | -13.00% | 🟢 **SpaceX Target (จัดตั้ง SpaceX Reserve $300 ใน Cash Buffer ห้ามซื้อ Day 1 Pop)** |
| **BTC** | 5.36% | **5.00%** | +0.36% | 🟢 **DCA Active (สะสมต่อเพื่อป้องกัน Dollar Debasement)** |
| **PLTR** | 0.00% | **0.00%** | 0.00% | 🔴 **Closed (ปิดพอร์ตโฟลิโอ 100% โยกย้ายทุนหมุนเวียนสะสม TSM/NVO เรียบร้อย)** |

> *หมายเหตุ: การคำนวณสัดส่วนและเป้าหมายข้างต้นอยู่บนฐาน **ตราสารทุนและคริปโต 100% (ไม่รวมเงินสด)** เพื่อความแม่นยำในการคุมน้ำหนักพอร์ต*  
> 💵 **Cash Cushion:** มีเงินสดสำรองรวม **11.84% ของพอร์ตรวม** ($1,097.91 USD) โดยมีเงินสด **$300.00 USD** ล็อกเป้าเป็น SpaceX IPO Reserve



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

กระแสเงินสดรวมในพอร์ต (Cash Buffer) ทั้งหมด **$1,097.91 USD** ได้รับการจัดสรรจัดระเบียบตามแผนยุทธศาสตร์ Capital Rotation ใหม่ดังนี้:

```
[กระแสเงินสดรวมพอร์ต $1,097.91 USD (11.84% Live)]
  ├── SpaceX IPO Reserve (ล็อกสำรองเชิงรุก): $300.00 USD (สำรองพร้อมจองซื้อ SPCX วันที่ 12 มิ.ย. 2026)
  ├── SOFI Reserve Lock (ปลดล็อกเรียบร้อย): $0.00 USD (ยกเลิกการแช่แข็งทุน โอนย้ายกลับเข้าสู่เงินสดใช้งานหลัก)
  └── Free Cash Cushion (เงินสดคงเหลือเพื่อ DCA): $797.91 USD
       ├── GTC Limit Order สะสม TSM (DCA Priority #1): $450.00 USD (ตั้งซื้อในโซน $385 - $415)
       └── GTC Limit Order สะสม NVO (DCA Priority #2): $250.00 USD (ตั้งซื้อในโซน < $44.55)
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
   Drift: +0.69% | Risk Flag: MW Cloud (Target Slashed to 6.00%)
   → ยกเลิกการล็อกเงินสะสม $374.00 USD และคงสถานะ HOLD เท่านั้น ห้ามสะสมเพิ่ม หมุนเวียนเม็ดเงินสำรองไป DCA สินทรัพย์หลัก (เช่น TSM, NVO)


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
1. RKLB > 30% → ห้ามซื้อเพิ่มเด็ดขาด และถ้าร่วมกับ SPCX แล้ว กลุ่มอวกาศรวม (Space Ceiling) ห้ามเกิน 35.00% (Hard Space Cap)
2. TSM, NVO, UNH, NVDA, BTC คือเป้าหมาย DCA Active ปัจจุบันเพื่อกระชับน้ำหนักพอร์ตตามเป้าปรับปรุงใหม่
3. Cash Target คือ 10.66% เพื่อบริหารกระแสเงินสดสภาพคล่องสำหรับการสะสมสะท้อน TSM/NVO และล็อกสำรอง SpaceX IPO $300.00
4. ห้ามไล่ราคา SPCX (SpaceX) ในวันแรก (Day 1 Pop) ล็อกสำรอง $300.00 ใน Cash Buffer เพื่อรอจังหวะสะสมช่วง Lock-up Expiry Dump ($70-80) ปลายปี 2026
5. Risk Flag (SEC/DOJ/MW) และกติกา VETO → ขาย 100% ทันทีหาก DOJ สั่งฟ้องอาญา UNH หรือ SOFI มี SEC Formal Order

```
