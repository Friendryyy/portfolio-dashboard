# 🔮 Blueprints for Feature Fusion — 13-Agent Investment OS

> **"ความอัจฉริยะไม่ได้อยู่ที่ความสามารถของเครื่องมือแต่ละตัว แต่อยู่ที่การเชื่อมโยงข้อมูลอย่างสอดประสานไร้รอยต่อ เพื่อให้การตัดสินใจลงทุนระยะยาวปราศจากอารมณ์และมีความเสี่ยงต่ำที่สุด"**
> พิมพ์เขียวสถาปัตยกรรมเชิงโครงสร้างเพื่อผสานฟีเจอร์ระดับสูง (Custom Subagents, Browser, Schedule Engine, Local Python Bridges) สำหรับพอร์ตเป้าหมาย ฿100M ใน 30 ปี

---

## 🎯 พิมพ์เขียวที่ 1: The Fear-Arbitrage Sniper (ยิงส่วนต่างราคาจากความหวาดกลัว)

ระบบล่าโอกาส DCA ช้อนซื้อสินทรัพย์พรีเมียมราคาลดกระหน่ำในสภาวะ Extreme Fear ทำงานเชิงรุกโดยเชื่อมต่อสัญญาณอารมณ์ตลาดมหาชนเข้ากับกลไกวินัยพอร์ตโฟลิโอของคุณ

```
[🕒 Schedule Engine ปลุกระบบ] (พุธ/ศุกร์ 22:30 น.)
       │
       ▼
[🌐 Browser Scraper] ──► Scrape CNN Fear & Greed Index (ดักค่า < 20)
       │
       ▼
[📊 Sheets Bridge] ──► เช็ค Cash Cushion >= 10% & RKLB Ceiling < 30%
       │
       ▼
[📡 Parallel Subagents] ──► subagent_technical (RSI < 30, MA200) + subagent_fundamental (MoS >= 20%)
       │
       ▼
[🔴 Enforced QA Audit] ──► workflows/14_qa_refinement_agent.md (ตรวจสูตรคณิตศาสตร์ทางการเงิน คะแนน >= 95)
       │
       ▼
[💾 Output & Delivery] ──► บันทึก output/ + อัปเดต Obsidian dca_decision_tree.md + ส่งสัญญาณ Shopping List
```

### 📋 ขั้นตอนการทำงานเชิงโครงสร้าง (Step-by-Step Data Flow)

#### STEP 1: Trigger Phase (Schedule Engine)
* **กลไก:** ตั้งค่าระบบตั้งเวลาของ AntiGravity รันอัตโนมัติทุกวันพุธและวันศุกร์ เวลา **22:30 น.** (ตามเวลาไทย — ซึ่งเป็นเวลา 1 ชั่วโมงหลังจากตลาดหุ้นสหรัฐฯ เปิดทำการ เพื่อให้ราคาและปริมาณการซื้อขายเริ่มสะท้อนทิศทางที่แท้จริงของวัน)
* **คำสั่งรันระบบเบื้องหลัง:**
  ```text
  /schedule "30 22 * * 3,5" "รันระบบวิจัย Fear-Arbitrage Sniper สแกนดัชนีช้อนซื้อประจำวัน"
  ```

#### STEP 2: Sentiment Scanning (Browser Scraper)
* **กลไก:** เรียกใช้เครื่องมือ `Browser` สแกนหน้าเว็บ **CNN Business - Fear & Greed Index** ที่ URL: `https://edition.cnn.com/markets/fear-and-greed`
* **Logic:** 
  * ระบบดึงตัวเลขค่าดัชนี (0-100)
  * **Gate 1 Check:** หากค่า **$\ge 20$** (ไม่ใช่สภาวะ Extreme Fear) ให้ทำการ **STOP** และสลายตัวทันที เพื่อประหยัด Token และอัตรา API Quota
  * หากค่า **$< 20$** (Extreme Fear) สัญญาณไฟเขียวสว่างขึ้น ส่งต่อราคาไปยัง Phase ถัดไป

#### STEP 3: Portfolio Rules Compliance (sheets_bridge.py)
* **กลไก:** เรียกใช้ `python tools/sheets_bridge.py portfolio` ดึงข้อมูลการจัดสรรพอร์ต (Asset Allocation) ล่าสุดจาก Google Sheets สดๆ
* **Logic (Gate 2 Check - Strict Rules):**
  * **กฎ Cash Cushion (ความปลอดภัยทางการเงิน):** เงินสดสำรองต้อง $\ge 10\%$ เท่านั้น (ดึงจาก `Cash (9%)` หรือสัดส่วนปัจจุบันจริง หากต่ำกว่าเกณฑ์ ห้าม DCA)
  * **กฎ RKLB Ceiling (วินัยการกระจุกตัว):** สัดส่วน RKLB ในพอร์ตต้อง $< 30\%$ หาก RKLB เติบโตจนแตะ $30\%-35\%$ ของพอร์ต ระบบจะสั่ง `Hard Buy Block` กับ RKLB ทันที และโยกสัญญาณการสะสมไปยังหุ้นพรีเมียมตัวถัดไปในลำดับความสำคัญ (เช่น NVO, NVDA, AMZN)

#### STEP 4: Parallel Deep-Dive Analysis (Custom Subagents)
เมื่อผ่านการอนุมัติวินัยพอร์ตโฟลิโอ ระบบจะสั่งสปอว์น Subagents ขึ้นมาประมวลผลคู่ขนานเพื่อวิเคราะห์ทางเลือกที่ดีที่สุด:
1. **[subagent_technical.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/workflows/subagents/subagent_technical.md):** 
   * ดึงราคาปิดและ Time-Series ผ่าน `twelvedata_bridge.py` 
   * คำนวณ RSI (14) เพื่อคัดกรองตัวที่เข้าข่าย Oversold ($< 30$) หรือทดสอบแนวรับสำคัญระดับ MA200 (200-day Moving Average)
2. **[subagent_fundamental.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/workflows/subagents/subagent_fundamental.md):** 
   * ตรวจสอบมูลค่าเหมาะสม (Fair Value Base) และคำนวณ Margin of Safety (MoS) ล่าสุด:
     $$\text{Margin of Safety (MoS)} = \frac{\text{Fair Value Base} - \text{Current Price}}{\text{Current Price}} \times 100\%$$
   * คัดเลือกเฉพาะหุ้นที่มี **MoS $\ge 20\%$**

#### STEP 5: Verification & Quality Gate (Agent 14 Enforced Audit)
* **กลไก:** ส่งชุดคำนวณและดราฟต์รายงานเข้าสู่ [14_qa_refinement_agent.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/workflows/14_qa_refinement_agent.md) เพื่อรันการตรวจประเมินคณิตศาสตร์และการเงินอย่างเข้มงวด:
  * ตรวจสอบว่าสูตร FCF Reconciliation ถูกต้องตามมาตรฐานของ `AGENTS.md`
  * สอบทานตัวเลขและ Citation (ดักจับคำกล่าวอ้างลอยๆ หรือค่า unverified)
  * ต้องได้รับคะแนน **QA Score $\ge 95/100$** เท่านั้น จึงจะปลดล็อกระบบบันทึก หากไม่ถึงเกณฑ์ ระบบจะทำการแก้ไขและคำนวณคะแนนใหม่โดยไม่บันทึกงานที่บกพร่อง

#### STEP 6: Vault Logging & Actionable Delivery
* **ผลลัพธ์:**
  * บันทึกรายงานวิจัยไว้ที่ `output/YYYY-MM-DD_fear_arbitrage_sniper.md`
  * อัปเดตข้อมูลความเสี่ยงลง Obsidian [dca_decision_tree.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/Database/portfolio/dca_decision_tree.md) และลงบันทึก 1-3 bullet summary ใน [log.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/Database/log.md)
  * ส่งแจ้งเตือน **"🟢 DCA Extreme Fear Opportunity"** พร้อมแนบ Shopping List แสดงหุ้นที่มีส่วนลดดีที่สุด และตาราง Tranche DCA สดๆ ทันที!

---

## 🌐 พิมพ์เขียวที่ 2: Geopolitical Thesis Breaker (เกราะรับแรงกระแทกภูมิรัฐศาสตร์)

ระบบเฝ้าระวัง ตรวจจับ และทำ Stress-Test พอร์ตเชิงรุกเมื่อเกิดวิกฤตความตึงเครียดทางภูมิรัฐศาสตร์ (เช่น ความขัดแย้งในช่องแคบไต้หวัน หรือการปิดช่องแคบฮอร์มุซ) เพื่อประเมินความเสถียรของสมมติฐานการลงทุน (DCA Thesis)

```
[🕒 Daily Scan / News Alert Trigger]
       │
       ▼
[🌐 Browser Scraper] ──► ดักจับพาดหัวข่าวด่วน (Reuters / Bloomberg / Al Jazeera)
       │
       ▼
[📡 subagent_macro] ──► ประเมิน Supply Chain (TSMC Blockade) & Energy Drag (Brent Oil > $100)
       │
       ▼
[📡 subagent_risk] ──► รัน Stress-Test พอร์ต RKLB, NVDA และประเมิน SPOF ใน pre_mortem_matrix.md
       │
       ▼
[🔴 Enforced QA Audit] ──► workflows/14_qa_refinement_agent.md (ดักข่าวปลอม ต้องมี [Source / Date] ยืนยัน)
       │
       ▼
[💾 NotebookLM & Vault Sync] ──► add-urls-batch (notebooklm_bridge.py) + อัปโหลดรายงาน + อัปเดต Obsidian
```

### 📋 ขั้นตอนการทำงานเชิงโครงสร้าง (Step-by-Step Data Flow)

#### STEP 1: Crisis Monitoring & Trigger (Browser Scraper)
* **กลไก:** ตั้งค่าให้ `Schedule Engine` วิ่งตรวจจับข่าวเด่นทุกวันเวลา **12:00 น.** (หรือเปิดระบบทำงานทันทีเมื่อตลาดมีการเคลื่อนไหวผิดปกติ)
* **การดักจับข้อมูล:** ใช้ `Browser` เข้าถึงเว็บไซต์ข่าวกรองการเงินต่างประเทศ เช่น Reuters, Bloomberg, หรือ Al Jazeera
* **คีย์เวิร์ดตรวจจับวิกฤต (Crisis Keywords):** 
  * `"Taiwan blockade"`, `"Hormuz strait closed"`, `"Tech sanctions China"`, `"Pakistan-Iran ceasefire broken"`
  * หากพบข่าวสารสำคัญที่มีแรงกดดันสูง ระบบจะเริ่มทำงานวิจัยทันทีโดยอัตโนมัติ

#### STEP 2: Macro Supply Chain & Valuation Assessment (subagent_macro)
* **กลไก:** สปอว์น [subagent_macro.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/workflows/subagents/subagent_macro.md) ประเมินความเสียหายเชิงมหภาค:
  1. **Supply Chain Disruption (ไต้หวัน chokepoint):** 
     * คำนวณผลกระทบต่อ TSMC (ซึ่งผลิตชิป Advanced 92% ของโลก) 
     * ประเมินผลกระทบเป็นลูกโซ่ต่อ GPU Blackwell/Vera Rubin ของ NVDA ในพอร์ตโฟลิโอของคุณ
  2. **Energy & Inflation Overhang (ช่องแคบฮอร์มุซปิดตัว):**
     * เช็กราคา Brent Crude Oil ล่าสุด หากราคาน้ำมันยืนเหนือ **$100-$110/barrel** จะทำให้เกิดภาวะ Stagflation Risk ส่งผลกดดันต่อหุ้น High-Multiple Growth ในพอร์ตทันที

#### STEP 3: Active Portfolio Stress-Testing (subagent_risk)
* **กลไก:** สปอว์น [subagent_risk.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/workflows/subagents/subagent_risk.md) ดึงข้อมูลความเสี่ยงในระบบมาทดสอบความต้านทาน:
  * **SPOF (Single Point of Failure) Analysis:** ระบุหุ้นที่จะเจ็บหนักที่สุดในกรณีที่เกิดวิกฤตภูมิรัฐศาสตร์ (เช่น NVDA โดนประเด็น Supply chain เต็มๆ, ส่วน UNH โดนประเด็นเศรษฐกิจถดถอยและ DOJ probe)
  * **Defense Tailwind Valuation:** ประเมินแรงบวกเชิงโครงสร้างที่พอร์ตจะได้รับชดเชย เช่น **RKLB** (ระบบอัญมณีฟ้าทองคำ Golden Dome / ดาวเทียมลาดตระเวน HASTE / Anduril Backlog) และ **PLTR** (ระบบ Maven AI ที่ผ่านสมรภูมิรบจริง) ที่ได้อานิสงส์จากงบกลาโหมสหรัฐฯ ที่พุ่งสูงขึ้น 
  * ระบบทำการบันทึกและอัปเดตสัดส่วนความต้านทานพอร์ตลงใน [pre_mortem_matrix.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/Database/portfolio/pre_mortem_matrix.md)

#### STEP 4: Integrity & Proof Audit (Agent 14 & 09 Enforced QA)
* **กลไก:** เพื่อป้องกันการตื่นตระหนกจากข่าวปลอม (FUD หรือ Speculative News) รายงานนี้ต้องรันผ่าน [09_research_integrity_agent.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/workflows/09_research_integrity_agent.md) และ **Agent 14 Enforced QA Audit**
  * คัดกรองแหล่งข่าวที่เชื่อถือไม่ได้
  * ข้อเท็จจริง ข่าวลือ และประเด็นผลกระทบทางการเงินทุกประโยคต้องถูกกำกับด้วย tag **`[Source / Date]`** เสมอ หากไม่มีที่มาจะถูกแบนออกจากรายงานทันที
  * คะแนนประเมินความโปร่งใสทางการเงินและขจัด Hallucination ต้องได้คะแนน **$\ge 95/100$**

#### STEP 5: NotebookLM Integration (notebooklm_bridge.py)
* **กลไก:** เมื่อรายงานผ่าน QA แล้ว ระบบจะจัดการด้านความรู้อย่างเป็นระเบียบ:
  1. ดึง URL อ้างอิงจากข่าวทั้งหมดเขียนใส่ `tools/{TICKER}_sources.txt`
  2. รันคำสั่งเพิ่มความรู้เข้า Stock Notebook ของหุ้นนั้นๆ (เช่น NVDA):
     ```bash
     python tools/notebooklm_bridge.py add-urls-batch {STOCK_NOTEBOOK_ID} "tools/{TICKER}_sources.txt"
     ```
  3. อัปโหลดรายงาน Geopolitical Crisis Analysis ตัวเต็มเข้าระบบ RAG Master Hub เพื่อบันทึกฐานความรู้การประเมินวิกฤตของพอร์ตอย่างถาวร:
     ```bash
     python tools/notebooklm_bridge.py add-report "d4268735-ab02-40c5-80a1-f1b9768befd9" "output/YYYY-MM-DD_{TICKER}_geopolitical_crisis.md"
     ```

#### STEP 6: Vault Update & Mitigation Advice
* **ผลลัพธ์:**
  * อัปเดต Risk Indicator สีไฟสัญญาณเตือนภัย (🔴/🟡/🟢) ในไฟล์รายหุ้น [stocks/{TICKER}.md](file:///c:/Users/LENOVO/OneDrive/文档/Second-Brain/Investment/Database/stocks/)
  * ให้คำแนะนำประกอบการจัดสรรพอร์ตเชิงป้องกัน (Mitigation Strategy) เช่น การยกเลิก DCA ชั่วคราวในหุ้นที่เสี่ยงสูง และโยกไปพักใน Cash Cushion (ปืนแก๊ปแห้ง) หรือตราสารปลอดภัยจนกว่าสถานการณ์จะคลี่คลาย

---

## 🛠️ รหัสตัวอย่างและแนวทางการนำไปพัฒนาจริง (Core Python Integration Prototype)

นี่คือโครงร่างแนวคิดโค้ดสำหรับการพัฒนา Python Script ใน `tools/` เพื่อคุมการทำงานของสถาปัตยกรรมทั้ง 2 ตัวนี้ร่วมกับ CLI ของเรา:

```python
# tools/feature_fusion_controller.py
import subprocess
import json
import sys

def run_fear_arbitrage_sniper():
    print("[+] Starting Fear-Arbitrage Sniper Execution...")
    
    # 1. Scrape CNN Fear & Greed Index
    # (จำลองการรัน Browser CLI หรือ Python Scraper ดึงค่าดัชนี)
    fear_greed_score = scrape_cnn_fear_greed() 
    if fear_greed_score >= 20:
        print(f"[-] Market Fear Greed Index at {fear_greed_score}. Not extreme enough. Exiting...")
        return
        
    print(f"[!] Active Signal! Fear & Greed at {fear_greed_score} (Extreme Fear). Checking Portfolio...")
    
    # 2. เรียก sheets_bridge ตรวจสอบกระสุน Cash Cushion & Target Allocation
    portfolio_data = subprocess.run(["python", "tools/sheets_bridge.py", "summary"], capture_output=True, text=True)
    
    # 3. โหลด Subagents (Technical + Fundamental) รันคู่ขนาน
    # (ส่ง raw data ไปยัง Master Orchestrator เพื่อรัน Subagents ใน workflows/subagents/)
    print("[+] Invoking subagent_technical & subagent_fundamental...")
    
    # 4. ส่งประเมิน Agent 14 QA
    # 5. บันทึกผลและแจ้งเตือน Shopping List

def run_geopolitical_thesis_breaker():
    print("[+] Starting Geopolitical Thesis Breaker Scan...")
    # 1. ค้นหาดึงข่าวด่วนผ่าน Browser tool
    # 2. หากพบคีย์เวิร์ดอันตราย สั่งสปอว์น subagent_macro & subagent_risk ประเมินผลกระทบพอร์ต
    # 3. ตรวจสอบ Integrity ผ่าน Agent 09 & 14
    # 4. อัปโหลด RAG ผ่าน notebooklm_bridge
```

---

## 📅 การบันทึกสิทธิ์และวินัยการปฏิบัติงาน (Governance Plan)

การผสานฟีเจอร์ระดับสูงทั้ง 2 รูปแบบนี้ จะทำให้ Second Brain ใน Obsidian ของคุณกลายเป็น **"ศูนย์รับมือวิกฤตและการสร้างโอกาสการลงทุนแบบอัจฉริยะ"** ที่ไม่ได้คิดเองลอยๆ แต่ขับเคลื่อนด้วย:
1. **พยานหลักฐานประจักษ์ (Data-driven evidence)** จากการ scrape สัญญาณสดของเว็บต่างประเทศ
2. **วินัยพอร์ตโฟลิโอแบบเครื่องจักรอัตโนมัติ (Automated Control)** ผ่านการดึงยอดเงินสดจริงจาก Google Sheets
3. **การประมวลผลที่มีเหตุผลและรัดกุมรอบคอบ (Radical Truth & Graham's Margin of Safety)** ผ่านการระดมสมองของ Subagents และการกรองความถูกต้องอย่างมีจรรยาบรรณวิชาชีพของ Agent 14
