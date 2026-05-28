# 📊 Financial Statement Adjustment & Valuation Framework

> **เอกสารข้อกำหนดระดับสถาบัน (Institutional Master Standard):** คู่มือมาตรฐานทางคณิตศาสตร์และการประมวลผลข้อมูลการเงินเชิงลึก สำหรับ Fundamental AI Agent (Agent 02) เพื่อหามูลค่าที่แท้จริง (Intrinsic Value / Fair Value) ของบริษัทเทคโนโลยีขนาดใหญ่และหุ้นเติบโตสูง

---

## 🧩 มิติที่ 1 — การปรับปรุงผลกระทบจาก Stock-Based Compensation (SBC Dilution)

### 1.1 สูตรคณิตศาสตร์การปรับปรุง FCF
การแสดงงบกระแสเงินสดที่รายงานตามมาตรฐานบัญชีทั่วไป มักจะจัดประเภท **Stock-Based Compensation (SBC)** เป็นรายการ Add-back ที่ไม่ใช่เงินสด (Non-cash Add-back) ในกระแสเงินสดจากการดำเนินงาน (CFO) ส่งผลให้ Free Cash Flow (FCF) สูงเกินจริง ซึ่งเป็นการบิดเบือนเนื่องจาก SBC คือภาระต้นทุนสิทธิพนักงานที่สร้างผลกระทบเจือจางหุ้น (Dilution) ต่อผู้ถือหุ้นรายย่อยอย่างชัดเจน

$$\text{FCF}_{Reported} = \text{CFO} - \text{CapEx}$$

$$\text{FCF}_{After\ SBC} = \text{CFO} - \text{CapEx} - \text{SBC}$$

$$\text{FCF Margin}_{Reported} = \frac{\text{FCF}_{Reported}}{\text{Revenue}} \times 100\%$$

$$\text{FCF Margin}_{After\ SBC} = \frac{\text{FCF}_{After\ SBC}}{\text{Revenue}} \times 100\%$$

$$\text{SBC Drag} = \text{FCF Margin}_{Reported} - \text{FCF Margin}_{After\ SBC}$$

### 1.2 การวิเคราะห์ความเสี่ยงการเจือจางสิทธิ์ (Dilution Overhang)
เพื่อประเมินภาระผูกพันสิทธิประโยชน์พนักงานที่กำลังรอแปลงสภาพและสร้างผลกระทบต่อสัดส่วนความเป็นเจ้าของ:

$$\text{Dilution Overhang} = \frac{\text{Stock Options} + \text{RSUs Outstanding}}{\text{Total Shares Outstanding}} \times 100\%$$

* **ระดับยอมรับสิทธิ์เบื้องต้น (Overhang):**
  - **ต่ำกว่า 5%:** ยอมรับได้ (ไม่มีนัยสำคัญเชิงทำลายมูลค่า)
  - **5% - 10%:** เริ่มมีนัยสำคัญ เจือจางความเป็นเจ้าของอย่างช้าๆ
  - **มากกว่า 10%:** เจือจางความเป็นเจ้าของอย่างรุนแรง (ผู้ถือหุ้นรายย่อยเสียเปรียบสูง)

### 1.3 เกณฑ์คัดกรองความเสี่ยงจากระดับ SBC ต่อโครงสร้างธุรกิจ

| อัตราส่วน SBC / Revenue | สัดส่วน SBC / Reported FCF | ระดับความเสี่ยง | แนวทางปฏิบัติการ (Actionable Guidance) |
| :---: | :---: | :---: | :--- |
| **< 5%** | **< 20%** | ✅ **ยอมรับได้ (Safe)** | ไม่ต้องกังวล ดำเนินการวิเคราะห์ตามข้อมูลปกติได้ |
| **5% – 10%** | **20% – 40%** | 🟡 **เฝ้าระวัง (Monitor)** | บังคับใช้ค่า $FCF_{After\ SBC}$ ในการคำนวณ Fair Value และ DCF ทุกกรณี |
| **10% – 15%** | **40% – 80%** | 🔴 **อันตราย (Severe)** | FCF รายงานบิดเบือนอย่างรุนแรง ห้ามใช้ประเมินมูลค่าตรงๆ |
| **> 15%** | **> 80%** | 🚨 **วิกฤต (Red Flag)** | FCF เป็นเพียงภาพลวงตา จ่ายค่าจ้างพนักงานด้วยมูลค่าสัดส่วนความเป็นเจ้าของของนักลงทุน |

### 1.4 การประเมินผลกระทบ SBC ต่อหุ้นกลุ่มเทคโนโลยีในพอร์ตโฟลิโอ

* **PLTR (Palantir):** 🚨 **Red Flag**
  - **SBC/Revenue:** ~15.3% | **SBC Drag:** 15.3 ppt
  - **คำแนะนำ:** FCF ที่รายงานสูง 33.5% แท้จริงแล้วหลังปรับปรุง SBC เหลือเพียง 18.2% การประเมินมูลค่าต้องระวังอย่างมาก
* **RKLB (Rocket Lab):** 🚨 **Pre-profit + High SBC**
  - **SBC/Revenue:** ~22.0% (est.)
  - **คำแนะนำ:** สัญญาณความเสี่ยงสูงเนื่องจากอยู่ในระยะขาดทุนและมีการอัดฉีดหุ้นเพื่อดึง talent
* **NVDA (NVIDIA):** ✅ **ยอมรับได้**
  - **SBC/Revenue:** ~5.0%
  - **คำแนะนำ:** รายได้มหาศาลขยายตัวเร็วสะกดระดับ SBC ให้เจือจางต่ำ
* **SOFI (SoFi):** 🟡 **เฝ้าระวัง**
  - **SBC/Revenue:** ~5% - 7%
  - **คำแนะนำ:** ติดตามข้อแฉการซ่อน SBC เพื่อทำตัวเลข EBITDA ให้ดูดีตามรายงาน Muddy Waters
* **GOOGL, AMZN, NVO, UNH:** ✅ **ยอมรับได้ทั้งหมด (< 3% of revenue)**

---

## 🛠️ มิติที่ 2 — การแยกแยะ Maintenance CapEx vs Growth CapEx

### 2.1 สูตรคำนวณหาส่วนรักษาและส่วนขยายธุรกิจ (CapEx Splitting)
เพื่อประเมินค่า **Owner Earnings** (กำไรที่แท้จริงของผู้ประกอบการ) ต้องแยก **Maintenance CapEx** (รายจ่ายทุนเพื่อประคองให้คูเมืองทางธุรกิจเท่าเดิม) ออกจาก **Growth CapEx** (รายจ่ายทุนเพื่อขยายกำลังการผลิต/ครอง TAM ใหม่)

#### วิธีที่ 1 — เครื่องมืออ้างอิงค่าเสื่อมราคา (D&A Approximation - Buffett Shortcut)
ในธุรกิจ steady-state ทั่วไป ค่าเสื่อมราคาและค่าตัดจำหน่ายมักสะท้อนค่าเฉลี่ยในการซ่อมบำรุงรักษาสินทรัพย์ถาวร:

$$\text{Maintenance CapEx} \approx \text{Depreciation \& Amortization (D\&A) of PP\&E}$$

$$\text{Growth CapEx} = \text{Total CapEx} - \text{D\&A of PP\&E}$$

#### วิธีที่ 2 — การหาอัตราส่วนต่อรายได้ (Revenue Ratio Method)
สำหรับธุรกิจที่มีความผันผวนของรอบอุตสาหกรรม (Cyclical):

$$\text{Maintenance CapEx} = \text{Long-run Steady-State CapEx/Revenue Ratio} \times \text{Current Revenue}$$

$$\text{Growth CapEx} = \text{Total CapEx} - \text{Maintenance CapEx}$$

### 2.2 สูตรคำนวณกำไรของผู้ถือหุ้นที่แท้จริง (Owner Earnings)

$$\text{Owner Earnings} = \text{Net Income} + \text{D\&A} + \text{Other Non-Cash Charges} - \text{Maintenance CapEx} \pm \text{Changes in Working Capital}$$

$$\text{Owner Earnings}_{Adjusted} = \text{Owner Earnings} - \text{SBC}$$

---

### 2.3 การประเมินคุณภาพงบลงทุน AI CapEx ของบริษัท Big Tech (เช่น GOOGL, AMZN)
เพื่อวิเคราะห์ว่าการลงทุนคลาวด์/ศูนย์ข้อมูล AI (AI CapEx) ยักษ์ใหญ่เป็นการลงทุนสร้างศักยภาพเพื่อเติบโต (Value-creating Growth CapEx) หรือเป็นเพียงรายจ่ายเพื่อความอยู่รอดให้เท่าทันคู่แข่ง (Competitive Survival Spending / Maintenance CapEx):

$$\text{Incremental ROIC} = \frac{\Delta\text{NOPAT}}{\Delta\text{Invested Capital}}$$

$$\text{NOPAT} = \text{EBIT} \times (1 - \text{Effective Tax Rate})$$

$$\text{Invested Capital} = \text{Total Equity} + \text{Total Debt} - \text{Excess Cash}$$

$$\text{Incremental ROIC} = \frac{\text{NOPAT}_{t} - \text{NOPAT}_{t-1}}{\text{Invested Capital}_{t-1} - \text{Invested Capital}_{t-2}}$$

#### 📡 ตารางสัญญาณแยกประเภทกระแส AI CapEx:

| สัญญาณตรวจสอบคุณภาพการลงทุน | 🟢 Growth CapEx (Value-Creating) | ⚠️ Maintenance CapEx (Survival Cost) |
| :--- | :--- | :--- |
| **มาร์จิ้นขั้นต้น (Gross Margin)** | แนวโน้มขยายตัว (Cloud margin ปรับสูงขึ้น) | ทรงตัวหรือลดลง (จากการแข่งขันตัดราคา) |
| **อัตราได้มาซึ่งลูกค้าใหม่** | เพิ่มขึ้นเร็วกว่าอัตราส่วนเฉลี่ยคู่แข่ง | เพิ่มขึ้นเท่ากันทั้งอุตสาหกรรม |
| **อำนาจกำหนดราคา (Pricing Power)** | สามารถปรับเพิ่มค่าบริการได้ง่าย | ต้องหั่นราคาแข่งขันเพื่อรักษาลูกค้าเก่า |
| **หากเลือกที่จะหยุดลงทุนตอนนี้** | ยอดขายและส่วนแบ่งการตลาดคงเดิม | สูญเสียลูกค้าและเทคโนโลยีล้าสมัยทันที |
| **พฤติกรรมในระดับคู่แข่ง** | ลงทุนด้วยเทคโนโลยีที่คู่แข่งสร้างตามได้ยาก | ทุกรายถูกบังคับลงทุนในปริมาณที่เท่าๆ กัน |

* **กรณีประยุกต์ใช้กับ GOOGL & AMZN:**
  - **GOOGL (TPU & AI Infrastructure):** จัดเป็น **Growth CapEx** เนื่องจากพัฒนาชิป TPU v8 ใช้ภายใน ลดการพึ่งพิง NVIDIA และมีการขายสิทธิ์การประมวลผลต่อให้บริษัทภายนอก
  - **AMZN (AWS Cloud Scaling):** จัดเป็น **Growth CapEx** เนื่องจาก AWS มีระดับ ROIC ปานกลาง-สูง (~25-30%) สามารถสร้างมาร์จิ้นการดำเนินงานได้แกร่ง

---

## 🚀 มิติที่ 3 — การเลือกเครื่องมือประเมินมูลค่า (Valuation Multi-Engine Protocol)

เพื่อความถูกต้องในการหามูลค่าที่แท้จริง ห้ามใช้เครื่องมือประเมินแบบเดียวกับทุกบริษัทในพอร์ตโฟลิโอ ให้เลือกใช้งานตามเกณฑ์ตรรกะดังนี้:

```
[START: บริษัทมีกระแสเงินสด FCF สม่ำเสมอและเป็นบวก?]
  ├── YES ── [มีคูเมืองทางธุรกิจมั่นคง (Moat)?]
  │           ├── YES (Mature Moat) ───────→ EPV + DCF (GOOGL, NVO, UNH)
  │           └── NO/MEDIUM (Growing Moat) → DCF + PEG (NVDA, AMZN)
  │
  └── NO ─── [อัตราการเติบโตสูงและวัด Revenue ได้?]
              ├── YES (High Growth, Pre-Profit) ──→ EV/S + Scenario Analysis (RKLB)
              └── YES (Moderate Growth, Profitable) → P/FCF After SBC + EV/EBITDA (PLTR, SOFI)
```

### 3.1 รายละเอียดชุดเครื่องมือประเมินมูลค่า (Valuation Engine Specifications)

#### 1. DCF (Discounted Cash Flow Model)
ใช้สำหรับบริษัทที่เป็นผู้นำตลาด มีกระแสเงินสดชัดเจน มั่นคง และคาดเดาได้ง่าย

$$\text{Intrinsic Value} = \sum_{t=1}^{n} \frac{\text{FCF}_{After\ SBC, t}}{(1 + \text{WACC})^t} + \frac{\text{Terminal Value}}{(1 + \text{WACC})^n}$$

$$\text{Terminal Value} = \frac{\text{FCF}_{After\ SBC, n} \times (1 + g)}{\text{WACC} - g}$$

$$\text{WACC} = R_f + (\beta \times \text{ERP})$$

* WACC baseline ในปี 2026 (บนพื้นฐาน Bond Yield 30Y ที่ 5.12% และ ERP 5.5%):
  - **UNH (Beta 0.6):** WACC $\approx 8.4\%$
  - **NVO (Beta 0.5):** WACC $\approx 7.9\%$
  - **GOOGL (Beta 1.1):** WACC $\approx 11.2\%$
  - **NVDA (Beta 1.7):** WACC $\approx 14.5\%$
  - **RKLB (Beta 2.0):** WACC $\approx 16.1\%$

#### 2. PEG Ratio (Price/Earnings-to-Growth)
ประเมินระดับความถูกแพงเมื่อเทียบอัตราการเติบโตของกำไรต่อหุ้น:

$$\text{PEG} = \frac{\text{Forward P/E}}{\text{Expected EPS Growth Rate (\%) } (3-5\text{ years average})}$$

* **ระดับเกณฑ์ตัดสินใจ (Valuation Signal):**
  - **PEG < 1.0:** ต่ำกว่ามูลค่าการเติบโตที่คาดหวัง (Undervalued - **Strong Buy Zone**)
  - **PEG = 1.0 - 2.0:** มูลค่าตลาดสะท้อนอัตราเติบโตตามเป้าหมาย (Fair Value)
  - **PEG > 2.0:** คาดหวังการเติบโตล่วงหน้าในราคาค่อนข้างสูง (Overvalued)
  - **PEG > 3.0:** ราคาหุ้นตั้งอยู่บนการคาดการณ์ที่ห้ามผิดพลาดแม้แต่ข้อเดียว (Speculative)

#### 3. EV/Sales (Enterprise Value to Revenue)
ใช้สำหรับบริษัทเติบโตสูงที่ยังมี FCF ขาดทุน หรือเริ่มเข้าสู่ระยะเริ่มมีกำไร:

$$\text{EV} = \text{Market Cap} + \text{Total Debt} - \text{Cash \& Equivalents}$$

$$\text{EV/Sales} = \frac{\text{EV}}{\text{Revenue (TTM)}}$$

* **Rule of 40 for SaaS/Software:**  
  หากบริษัทมีการเติบโตสูงและมีมาร์จิ้นดี ยอดบวกของอัตราเติบโตรายได้และอัตรากำไร FCF ต้องเกิน 40%

#### 4. P/TBV (Price to Tangible Book Value)
ใช้สำหรับหุ้นกลุ่มสถาบันการเงินและธนาคารที่สินทรัพย์จับต้องได้เป็นหลัก (เช่น SOFI):

$$\text{Tangible Book Value (TBV)} = \text{Total Equity} - \text{Goodwill} - \text{Intangible Assets}$$

$$\text{P/TBV} = \frac{\text{Market Cap}}{\text{Tangible Book Value}}$$

* **เกณฑ์คัดกรอง:** ระดับ P/TBV < 1.0 (ถูกมาก ซื้อหุ้นราคาต่ำกว่าสินทรัพย์จริง), P/TBV 1.0 - 2.0x (สมเหตุสมผลสำหรับ ROE > 12%)

#### 5. EPV (Earnings Power Value — Greenwald Model)
ประเมินมูลค่าบริษัทหากอัตราการเติบโตในอนาคตเป็นศูนย์ (Zero Growth Intrinsic Value) เพื่อหาจุดแข็งของคูเมืองปัจจุบัน:

$$\text{Normalized EBIT} = \text{Operating Income} + \text{SBC} - \text{Maintenance CapEx}$$

$$\text{EPV} = \frac{\text{Normalized EBIT} \times (1 - \text{Tax Rate})}{\text{WACC}}$$

$$\text{Franchise Value} = \text{DCF Value} - \text{EPV}$$

> 💡 **ความลับเชิงเปรียบเทียบ:** หากมูลค่าของ DCF สูงกว่า EPV มหาศาล แสดงว่ามูลค่าหุ้นที่ประเมินพึ่งพา "ความหวังอัตราการเติบโตในอนาคต" สูงมาก หากการเติบโตชะลอตัว หุ้นจะลงรุนแรง แต่หาก DCF ใกล้เคียง EPV หุ้นตัวนั้นจะมี Margin of Safety สูงสุดแม้อัตราการเติบโตจะเป็นศูนย์

---

## 🎯 สรุปการจับคู่ Valuation Engine ต่อพอร์ต 8 หุ้น

| Ticker | เครื่องมือหลัก (Primary) | เครื่องมือรอง (Secondary) | 🚫 ข้อห้ามใช้ประเมิน | เหตุผลเชิงวิชาชีพ |
| :--- | :--- | :--- | :--- | :--- |
| **NVDA** | **DCF (FCF After SBC)** | **PEG (Forward)** | EPV | อัตราการขยายตัวและ optionality สูงเกินกว่า EPV จะประเมินได้ครอบคลุม |
| **RKLB** | **EV/S + Scenario Analysis** | **TAM Probability** | DCF, P/E | ธุรกิจระยะเริ่มต้นที่ขาดทุนงวดเงินสด ประเมินได้ด้วยยอดขายและโอกาส Neutron เท่านั้น |
| **GOOGL** | **DCF + EPV** | **EV/S (Cloud Division)** | PEG Alone | Search Engine คือกระแสเงินสด Mature Moat ประเมิน EPV เพื่อหาพื้นหลังความปลอดภัยได้ดี |
| **AMZN** | **DCF (FCF After SBC)** | **SOTP (Sum of the Parts)** | P/E TTM | ธุรกิจมีความซับซ้อน คลาวด์แยกตัวกับค้าปลีก ต้องวิเคราะห์ FCF แบบปรับปรุง SBC เท่านั้น |
| **SOFI** | **P/TBV** | **P/FCF After SBC** | DCF, EPV | ต้องกำกับดูแลสัดส่วนการเงินสไตล์ธนาคาร ดูความแข็งแกร่งของ Tangible Book |
| **UNH** | **EPV** | **DCF** | EV/Sales | ธุรกิจประกันมีความสม่ำเสมอของเบี้ยรับ สามารถ Normalized หา Earnings Power ได้นิ่ง |
| **NVO** | **DCF** | **EPV** | PEG | ยามีสิทธิบัตรคุ้มครองและกระแสเงินสดชัดเจนมาก เหมาะกับ EPV และ DCF |
| **PLTR** | **P/FCF After SBC** | **EV/EBITDA** | DCF | ระดับ SBC เจือจางสิทธิ์พนักงานสูงมาก หากใช้ DCF ปกติจะไม่สะท้อนค่าที่ผู้ถือหุ้นจริงได้ |
