# Pre-Mortem Failure Matrix — Portfolio 2030
> **สร้าง:** 2026-05-21 | **สมมติฐาน:** ปี 2030 พอร์ตพังถาวร — ไม่ใช่ขาดทุนชั่วคราว แต่ thesis สลายไม่กลับมา
> **วัตถุประสงค์:** ระบุ Single Point of Failure ล่วงหน้า เพื่อใช้เป็นคู่มือเฝ้าระวังภัยพิบัติ

---

## รายหุ้น — Single Point of Failure

### 🚀 RKLB (28.47%) — ความเสี่ยงสูงสุดของพอร์ต (หลัง Micro-Trim)

**Failure Narrative (2030):**
Neutron ทำการบินครั้งแรกปี 2027 แต่เครื่องยนต์ Archimedes ระเบิดที่ Max-Q ครั้งที่สอง payload capacity ต่ำกว่าสเปค ปี 2028 Starship commercial launch ครั้งที่ 40+ ราคา $15M/flight ถูกกว่า Neutron target $40M รัฐบาลตัดงบ Golden Dome หลัง debt ceiling crisis SDA contracts ถูก rescale 60% RKLB rerates จาก P/S 100x → 8x หุ้นลง **~90%** พอร์ตสูญ ~28%

**Single Point of Failure:** Neutron ล้มเหลวทางเทคนิค + SpaceX Starship commoditize medium-heavy launch

**Early Warning Signals:**
- Neutron delay เกิน Q4 2027 โดยไม่มี technical rationale
- Starship commercial cadence เกิน 15 flights/ปี
- Revenue growth < 30% YoY ติดต่อ 2 ไตรมาส
- Backlog หยุดโต หรือ defense contract ถูก cancel

---

### 🖥️ NVDA (18.57%)

**Failure Narrative (2030):**
Microsoft Maia 200, Google TPU v8, Amazon Trainium 3 รวมกินส่วนแบ่ง AI training compute 35% AMD ROCm 6.0 achieve 85% CUDA compatibility ปี 2028 "AI ROI Crisis" มาถึง — hyperscalers ตัด capex AI จาก $250B → $140B/ปี NVDA revenue drop จาก $200B → $120B EPS revision รุนแรง หุ้นจาก $270 → $70-90

**Single Point of Failure:** Hyperscaler vertical integration (in-house silicon) + AI capex cycle bust เกิดพร้อมกัน

**Early Warning Signals:**
- Microsoft/Google/Amazon capex allocation ย้ายจาก NVDA → custom silicon > 20%
- AMD market share AI training เกิน 15%
- LLM benchmark improvement rate แบน (scaling law หมด)
- NVDA data center revenue growth < 30% YoY

---

### 🔍 GOOGL (10.40%)

**Failure Narrative (2030):**
AI-native search กิน 25-30% ของ informational queries Google search ad revenue $200B/ปีเริ่มลด 6%/ปี DOJ antitrust บังคับ divest Chrome และ Android — data flywheel ขาดสะบั้น advertiser CPCs ลด ที่ P/E 10x บน declining revenue หุ้นลงหนัก

**Single Point of Failure:** AI search ทำลาย click-based ad model + antitrust forced divestiture เกิดพร้อมกัน

**Early Warning Signals:**
- Search click-through rate (CTR) ลดต่อกว่า 3 ไตรมาส
- Google Search market share ต่ำกว่า 85% (ปัจจุบัน ~91%)
- DOJ antitrust ruling เกิดขึ้นจริง
- YouTube/Cloud ไม่ offset search revenue decline ได้

---

### 💳 SOFI (5.87%) — ⚠️ ความเสี่ยงที่ใกล้ที่สุดในปัจจุบัน

**Failure Narrative (2030):**
SEC เปิด formal investigation จาก Muddy Waters 11 allegations EBITDA restatement ตามมา ลด earnings 40% Block & Leviton settle $600M 2027 recession hits unsecured personal loans charge-off rate 3% → 7.5% Net interest margin ถูก squeeze จาก provision สูง หุ้นจาก $16 → $2-3

**Single Point of Failure:** Accounting irregularities จริง (Muddy Waters) + credit cycle bust กดทับพร้อมกัน

**Early Warning Signals (เฝ้าระวังทันที):**
- SEC formal investigation order ออก → **SELL ทันที ไม่รอ**
- Charge-off rate > 4.5% (จาก 3.03% ปัจจุบัน)
- SOFI ไม่ตอบ MW 11 คำถามอย่างเป็นทางการภายใน Q2 2026
- Revenue growth < 20% YoY

---

### 📦 AMZN (5.58%)

**Failure Narrative (2030):**
AWS pricing war ทำให้ gross margin ลดจาก 38% → 22% Retail margin หยุดจาก labor cost + unions FTC บังคับ structural separation AWS-retail ทำลาย cross-subsidization flywheel แยก entity แต่ละตัวถูก value ต่ำกว่า combined เดิม

**Single Point of Failure:** AWS margin compression + antitrust-forced separation

**ระดับความเสี่ยง: ปานกลาง** — AMZN มี diversification จริง ไม่ easy fail เหมือน RKLB/SOFI

---

### 🏥 UNH (5.36%) — ⚠️ DOJ เป็น existential risk จริง

**Failure Narrative (2030):**
DOJ criminal indictment ออกต่อ C-suite executives — criminal conviction ไม่ใช่แค่ civil settlement CMS ตัด Medicare Advantage reimbursement 6-8%/ปี ติดต่อ 3 ปี Medical Loss Ratio พุ่งเกิน 92% สูญเสีย government contracts รายใหญ่ หุ้นจาก $350+ → $60-80

**Single Point of Failure:** Criminal conviction (ไม่ใช่ civil settlement) + CEO murder governance vacuum

**Early Warning Signals:**
- Criminal indictment ออก (ต่างจาก investigation ที่ยังเปิดอยู่)
- CMS rate cut เกิน 5% consecutive years
- หลุด Fortune 50 government health contract รายใหญ่

---

### 💊 NVO (4.17%)

**Failure Narrative (2030):**
FDA อนุมัติ oral GLP-1 ของ Eli Lilly (orforglipron) หรือ Pfizer ที่มี efficacy ใกล้เคียง Ozempic แต่เป็นยาเม็ด ผู้ป่วย migrate จากการฉีดรายสัปดาห์ manufacturing moat ของ NVO กลายเป็นไร้ความหมาย 2031 Ozempic patent cliff + biosimilar P/E compress จาก 30x → 10x ราคาลง 60-70%

**Single Point of Failure:** FDA approval ของ oral GLP-1 จากคู่แข่งที่มี comparable efficacy

**Early Warning Signals:**
- Phase 3 trial data ของ orforglipron (LLY) แสดง non-inferiority vs semaglutide
- Pfizer/Roche oral GLP-1 เข้า FDA review
- Biosimilar semaglutide application filed (post-2029)

---

### 🔴 PLTR (0.00% — LIQUIDATED)

**Status:** ปิดสถานะขาย 100% แล้วเมื่อ 2026-05-24 ยุติความเสี่ยงเศษหุ้น zombie position เพื่อโอนย้ายทุน DCA สินทรัพย์หลัก

---

### 🖥️ TSM (4.97% — DCA Active)

**Failure Narrative (2030):**
ความตึงเครียดช่องแคบไต้หวันบานปลาย (Invasion / Navy Blockade) ทำลายหรือปิดกั้นการเดินเรือขนชิป advanced nodes ทำให้ supply chain เทคโนโลยีโลกหยุดชะงัก หรือโครงการ Fab นอกเกาะไต้หวัน (Arizona) เผชิญค่าใช้จ่ายบานปลาย ประสิทธิภาพผลิตต่ำกว่าคาด ดัน PE compress จาก 20.7x -> 10x

**Single Point of Failure:** Geopolitical Conflict (Taiwan Strait) + Chokehold fabrication node dependency

**Early Warning Signals:**
- ความตึงเครียดช่องแคบไต้หวันเพิ่มระดับอย่างเป็นทางการหรือการซ้อมรบปิดช่องแคบ
- อัตราผลิต (Yield rate) โรงงาน Arizona ต่ำกว่า 50% ต่อเนื่อง 2 ไตรมาส
- สหรัฐฯ ยกเลิกสิทธิเงินอุดหนุนชิป CHIPS Act

---

### 🪙 BTC (4.97% — DCA Active)

**Failure Narrative (2030):**
การโจมตีกำลังขุด 51% Attack สำเร็จเชิงทฤษฎี หรือการเปิดเผยจุดบกพร่องทางคณิตศาสตร์ในโค้ดทำให้ระบบล่มสลาย หรือกฎหมายแบนกระเป๋าเงินดิจิทัลไร้ KYC อย่างเป็นทางการในกลุ่ม G7 บีบจำกัดการเข้าถึง และการพัฒนาคอมพิวเตอร์ควอนตัมถอดรหัส ECDSA สำเร็จโดยไม่มีการอัปเกรด Post-Quantum Cryptography ได้ทันเวลา

**Single Point of Failure:** Quantum decryption + Severe global regulatory ban

**Early Warning Signals:**
- สหรัฐฯ หรือ G7 ออกกฎหมายแบน non-custodial wallets
- ความก้าวหน้าควอนตัมคอมพิวเตอร์แตะระดับถอดรหัสกุญแจลับเชิงพาณิชย์
- Hash rate เครือข่ายร่วงดิ่งเกิน 50% ต่อเนื่อง 1 เดือน

---

### 🚀 SPCX (0.00% — Pre-IPO Reserve)

**Failure Narrative (2030):**
งบ xAI บวมขึ้นเผาผลาญกำไร Starlink จนกระแสเงินสดติดลบต่อเนื่อง หรือ Starlink เผชิญปัญหาวงโคจรชนกันทำลายกลุ่มดาวเทียม หรือการ IPO ที่ราคาสูงเกินไปโดน index inclusion exit liquidity เทขายอย่างหนักช่วงหมดอายุ Lock-up

**Single Point of Failure:** xAI cash drain + Starlink collision cascade (Kessler Syndrome) + Lock-up expiry dump

**Early Warning Signals:**
- งบ xAI ขาดทุนบวมเกิน $20B/ปี
- SpaceX กู้เงินสดฉุกเฉินเพิ่มเติมเกิน $15B
- อัตราความล้มเหลวการปล่อยดาวเทียม Starlink สูงเกิน 10%

---

## Systemic Risks — ระเบิดพร้อมกันหลายตำแหน่ง

| Systemic Scenario | Positions กระทบ | % พอร์ต |
|---|---|---|
| **AI Capex Bust** | NVDA + GOOGL Cloud + AMZN AWS + TSM | **~38%** |
| **Rate Shock 2.0** (10Y 6%+) | RKLB DCF + SOFI credit + TSM + NVO | **~46%** |
| **Tech Antitrust Wave** | GOOGL + AMZN + (NVDA monopoly probe) | **~34%** |
| **AI Search Disruption** | GOOGL revenue + AMZN ad revenue | **~16%** |
| **Government Spending Cuts** | RKLB + SPCX + UNH Medicare | **~54%** |
| **Consumer Credit Bust** | SOFI + AMZN retail | **~11%** |
| **Geopolitical Strait Conflict** | TSM (Taiwan) + NVDA supply + SOFI macro | **~28%** |

**Correlation ที่น่ากลัวที่สุด:**
RKLB ลง 50% (Neutron failure) **พร้อมกับ** NVDA ลง 40% (AI capex bust) = พอร์ตหายทันที **~23%** ในสถานการณ์เดียว

---

## KPI Monitoring Dashboard — Review ทุกไตรมาส

```
RKLB (CRITICAL):
[ ] Neutron on schedule (launch Q4 2026)
[ ] Revenue growth > 30% YoY
[ ] Defense contract backlog ยังโต
[ ] Starship commercial cadence < 15 flights/year

SOFI (HIGH — ตรวจทุก earnings):
[ ] SEC investigation = ไม่มี formal order
[ ] Charge-off rate < 4.5%
[ ] MW 11 questions ตอบแล้วหรือยัง?

UNH (HIGH — DOJ status):
[ ] Criminal indictment = ไม่มี
[ ] CMS rate cut < 5%
[ ] MLR < 88%

NVDA (MEDIUM):
[ ] Hyperscaler in-house silicon < 15% market share
[ ] AMD market share < 15%
[ ] Data center revenue growth > 40%

GOOGL (MEDIUM):
[ ] Search market share > 87%
[ ] Antitrust ruling = ไม่มี forced divestiture

NVO (MEDIUM):
[ ] Oral GLP-1 Phase 3 competitor = ไม่มี non-inferiority data

Portfolio-Level:
[ ] AI capex ไม่ลดเกิน 20% YoY
[ ] 10Y yield < 5.5%
[ ] ไม่มี antitrust breakup ruling ต่อ GOOGL/AMZN
```

---

## Radical Truth Summary

3 จุดอ่อนเชิงโครงสร้างจริงที่ต้องเฝ้าระวังมากกว่าส่วนอื่น:
1. **RKLB concentration + Neutron dependency** — ถ้า Neutron ล้มเหลว พอร์ตหายหนักที่สุด
2. **SOFI accounting cloud** — Muddy Waters ยังไม่ resolve คือ live bomb
3. **AI Bubble Correlation** — NVDA + GOOGL + AMZN + RKLB = ถ้า AI spend หดตัวจะโดนพร้อมกัน > 36% พอร์ต

### [Geopolitical Stress Audit — 2026-05-22]
* **Detected Catalyst:** Taiwan & Hormuz Strait premium pressure.
* **Stress Indicators:** NVDA Supply Chain Risk flagged to High | RKLB & PLTR Defense buffer intact.
