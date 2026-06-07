# 📋 Slash Commands — Investment OS

> ไฟล์นี้รวบรวม custom slash commands ทั้งหมดของระบบ
> Command files จริงอยู่ที่ `.claude/commands/*.md`
> พิมพ์ใน Claude Code chat ได้เลย เช่น `/portfolio-analysis`

---

## รายการ Commands

| Command | สั้นๆ คืออะไร | เหมาะใช้เมื่อ |
|---|---|---|
| `/portfolio-analysis` | วิเคราะห์พอร์ตแบบ brief ทุกตัว | ต้องการ snapshot พอร์ตสด + ความคิดเห็น |
| `/portfolio-news-update` | วิเคราะห์เจาะลึกข่าวสารและผลกระทบ 10 สินทรัพย์เป้าหมาย | ต้องการอัปเดตข่าวสารสดใหม่รายหุ้น 50 ข่าวพร้อมแผนสภาพคล่อง CIO |
| `/youtube-analysis` | วิเคราะห์คอนเทนต์วิดีโอ & สื่อโซเชียลมีเดียด้วย AISWARM เชิงลึก | เมื่อได้รับ URL หรือวิดีโอและต้องการสกัดประเด็น วิจัยข้อมูลจริงเสริมภายนอก และเชื่อมเข้าพอร์ตจริง |
| `/daily-evolve` | Audit ระบบ 13-Agent + เขียน upgrade rules | ทุกวัน หลังทำ research เสร็จ เพื่ออัปเกรดระบบ |
| `/swarm-orchestrator` | วิเคราะห์เป้าหมายเชิงลึกด้วยกองทัพ Micro-Agents แบบคู่ขนาน | เมื่อต้องการประเมิน DCA, วิเคราะห์งบ หรือตอบเป้าหมายซับซ้อนอย่างละเอียดและรวดเร็ว |

---

## รายละเอียด

---

### `/portfolio-analysis`

**ทำอะไร:**
วิเคราะห์พอร์ตทั้งหมดแบบ brief — ไม่ deep dive ทุกตัว แต่ครอบคลุมทุกหุ้นในพอร์ต

**ขั้นตอนที่ระบบทำ (Parallel Architecture — ดู `workflows/portfolio_analysis_workflow.md`):**
1. PRE-STEP: Master Agent ดึง portfolio snapshot สด + อ่าน index.md + log.md
2. PARALLEL: spawn 1 sub-agent ต่อ 1 หุ้น — ทุกตัวรัน fetch + brief พร้อมกัน
   - แต่ละ Stock-Agent: อ่าน wiki → yfinance → twelvedata → news delta (ถ้า wiki_age > 3 วัน)
   - ส่งคืน stock_brief_pack มาที่ Master Agent
3. SYNTHESIS: Master Agent รวม packs ทั้งหมด → เขียนรายงานฉบับเดียว
4. Cross-portfolio analysis (Agent 10) + Behavioral check (Agent 13) โดย Master Agent
5. Save output + อัปเดต Obsidian + upload NotebookLM

**Output ที่ได้:**
- Portfolio health check (value, allocation, cash, concentration)
- Brief แต่ละหุ้น: ราคา / gain% / verdict / catalyst สำคัญ (เรียงตาม allocation)
- Cross-portfolio hidden correlations + sector exposure
- Action items สัปดาห์นี้ (🔴/🟡/🟢)
- Behavioral bias check + pre-mortem ถ้ามี action

**Agent ที่ใช้:** Stock sub-agents (fetch) + Master Agent (synthesis + Agent 10 + 13)

**บันทึกไปที่:**
- `output/YYYY-MM-DD_portfolio_analysis.md`
- `Database/index.md` + `Database/log.md`
- NotebookLM Master Hub

---

---

### `/daily-evolve`

**ทำอะไร:**
Audit ระบบ 13-Agent เทียบกับ Golden Standard ใน `workflows/AGENT_SYSTEM_AUDIT.md` หาจุดบกพร่อง วิเคราะห์สาเหตุ และเขียน Prompt/Rule ใหม่ที่ copy-paste ไปใส่ agent files ได้ทันที

**ขั้นตอนที่ระบบทำ:**
1. โหลด context: AGENT_SYSTEM_AUDIT.md + output วันนี้ + log.md + memory
2. **Step 1:** Gap & Friction Analysis — ตรวจ Agent ทั้ง 13 ตัวด้วย KPI เฉพาะของแต่ละตัว
3. **Step 2:** Root Cause Diagnosis — หาสาเหตุว่า friction เกิดจาก prompt/master agent/missing rule
4. **Step 3:** Actionable Evolution — เขียน fix จริงพร้อมระบุไฟล์ที่ต้องแก้ + prompt ที่ copy-paste ได้เลย
5. **Step 4:** Evolution Log — append บทเรียนวันนี้เข้า Database/log.md
6. Apply fixes จริงในไฟล์ workflows/ + save output + upload NotebookLM

**Output ที่ได้:**
- Audit report ทุก 13 agents (Pass/Friction)
- Root cause ของปัญหาที่พบ
- Code/Prompt upgrade ที่ใช้งานได้จริง (ไม่ใช่แค่คำแนะนำลอยๆ)
- Evolution Log 1-2 บรรทัด

**Agent ที่ใช้:** Chief AI Architect role — ประเมินทุก agent จากภายนอก

**บันทึกไปที่:**
- `output/YYYY-MM-DD_daily_evolve.md`
- `workflows/{agent_files ที่แก้ไข}`
- `Database/log.md`
- NotebookLM Master Hub

**Memory ที่สะสม:** `Database/EVOLUTION_LOG.md` — append-only log ทุก run พร้อม Retrospective "fix ใช้ได้จริงไหม"

**ควรรันเมื่อ:** ทุกวัน หลังจาก research session ใหญ่เสร็จ หรือเมื่อรู้สึกว่าระบบให้ผลลัพธ์ไม่ตรงมาตรฐาน

---

### `/swarm-orchestrator`

**ทำอะไร:**
วิเคราะห์และประเมินเป้าหมายการลงทุนที่ซับซ้อนแบบอัตโนมัติ (DCA assessment, macroeconomic analysis, sector impact, pricing metrics) โดยสลายเป้าหมายออกมาเป็น Micro-Tasks และเรียกใช้งานกองทัพ 4 Micro-Agents (Macro, Fundamental, Technical, Risk) ทำงานคู่ขนานกันด้วยสถาปัตยกรรม Multithreading เพื่อความรวดเร็วและแม่นยำ พร้อมทั้งทำ Agent 14 Compliance Audit ในตัว

**รูปแบบการใช้งาน (ผ่าน CLI):**
```bash
# รันวิเคราะห์แบบเต็มรูปแบบ (Live Run)
python tools/swarm_controller.py --goal "DCA assessment for RKLB and NVO"

# รันเพื่อทดสอบสัญญาณและตัวเลขโดยไม่บันทึกไฟล์ (Dry Run)
python tools/swarm_controller.py --goal "Evaluate NVDA and RKLB in high inflation" --dry-run
```

**ขั้นตอนที่ระบบทำ (Dynamic Swarm Architecture):**
1. **GoalDecomposition:** สกัด Ticker และบริบทจากโจทย์ผู้ใช้โดยอัตโนมัติ (เช่น ค้นพบ RKLB, NVDA, NVO)
2. **ParallelDataFetch:** ใช้ Thread Pool ดึงข้อมูลสด (yfinance price/info/financials, Twelve Data RSI, Google Sheets rules) ของทุก Ticker พร้อมๆ กัน
3. **SimulatedSpecialistReasoning:** โหลดระบบ Prompts จาก `workflows/subagents/` เพื่อให้ Micro-Agents ทั้ง 4 ประมวลผลเชิงลึกตามมิติของตนเอง:
   - **Macro Agent:** สแกนดัชนี Fear & Greed Index จาก API และตรวจสอบผลกระทบเชิงมหภาคและคู่แข่ง
   - **Fundamental Agent:** เจาะลึกงบการเงินคำนวณ OCF, CapEx, FCF after SBC, Accruals Ratio, และ Margin of Safety (MoS)
   - **Technical Agent:** เช็ค RSI(14) และหาโซนแนวรับ / DCA Entry Triggers (MA200, MA50)
   - **Risk Agent:** ดึงสัดส่วนจริงจาก Google Sheets เช็คความทับซ้อนและ Risk Ceilings (เช่น RKLB 30%, ตัวอื่น 20%)
4. **ConflictResolutionMatrix:** สังเคราะห์ตัวบ่งชี้ที่มีความขัดแย้งกัน (เช่น หุ้นมี MoS สูงมากแต่งบการเงินบอกว่าราคาถูก แต่กราฟกำลัง Overbought ระยะสั้น) ออกมาเป็น Stoic Verdict ที่เป็นระบบและปราศจากอารมณ์
5. **Agent 14 Compliance Audit:** ตรวจสอบความถูกต้องทางคณิตศาสตร์และความแม่นยำตามเกณฑ์ Agent 14 QA Refinement บังคับให้ได้คะแนน QA Score $\ge 95/100$
6. **SyncEngine:** บันทึกรายงาน Markdown ไปที่ `output/`, append ประวัติย่อลง Obsidian `log.md`, และอัปโหลดรายงานแบบ Dedup เข้าสู่ NotebookLM Master Hub ทันที

**Output ที่ได้:**
- ข้อมูลสภาพตลาดสด (CNN Fear & Greed, Cash Cushion %, RKLB Block Check)
- รายงานวิเคราะห์คู่ขนานเชิงลึกแยกหุ้นทีละตัวจาก Micro-Agents ทั้ง 4
- ตารางประเมินและคลี่คลายความขัดแย้งของตัวบ่งชี้ (Conflict Resolution Matrix)
- แผนปฏิบัติการลงทุน Stoic DCA Verdict (🟢 DCA ACCUMULATE / 🟡 HOLD / 🔴 TRIM)
- Deliverable QA Approved Sign-off block

**Agent ที่ใช้:** Subagent Macro, Fundamental, Technical, Risk + Agent 00 Orchestrator + Agent 14 Auditor

**บันทึกไปที่:**
- `output/YYYY-MM-DD_{GOAL_SLUG}_swarm_verdict.md`
- `Database/log.md` (Append 3-bullet summary)
- NotebookLM RAG Master Hub

---

### `/youtube-analysis`

**ทำอะไร:**
วิเคราะห์ข้อมูลวิดีโอ YouTube และเนื้อหาบนโซเชียลมีเดียเชิงลึก โดยผสานระบบ **AISWARM (กองทัพ 5 Subagents แบบคู่ขนาน)** และทำความสะอาดคลังความรู้พร้อมกับการสกัดประเด็นที่แปรผันตามระยะเวลาคลิป

**ขั้นตอนที่ระบบทำ (4-Phase Pipeline):**
1. **PHASE A — EXTRACT:** ดึงสคริปต์/คำบรรยายใต้คลิป (Transcript) และสกัดหัวข้อวิเคราะห์ระดับกลาง (Mid-level Topics) ที่จะแปรผันเพิ่มขึ้นตามความยาวจริงของคลิปวิดีโอ (Topic Duration Scaling Rule):
   - ความยาว < 20 นาที: 3-5 หัวข้อ
   - ความยาว 20-60 นาที: 5-8 หัวข้อ
   - ความยาว 1-2 ชั่วโมง: 8-12 หัวข้อ
   - ความยาว > 2 ชั่วโมง: 12-20 หัวข้อ
2. **PHASE B — CONFIRM (🔴 BLOCKING GATE):** พ่นหัวข้อวิเคราะห์ทั้งหมดและแสดงคำถามตัวเลือกบล็อกระบบแชท เพื่อรับการยืนยัน ("OK") จากผู้ใช้งานก่อนดำเนินการวิจัยต่อ
3. **PHASE C — SWARM RESEARCH:** รันกองทัพ Subagents (Macro, Fundamental, Technical, Risk, Insider, Media) โดยทำ **Extended Research ค้นคว้าข้อมูลภายนอกจริง (Live Web Search, yfinance, SEC, X)** เพื่อตรวจสอบ Claim และความเที่ยงตรง และทำ **Portfolio Impact Mapping** เชื่อมโยงเข้ากับพอร์ตจริง (NVDA, RKLB, GOOGL, AMZN, UNH, NVO, SOFI, TSM, BTC) เพื่อประเมินน้ำหนักการลงทุนและให้คำตัดสิน DCA/Trim/Hold เป็นรูปธรรม
4. **PHASE D — STORAGE & SYNC:** บันทึกรายงาน Markdown ไปที่ `/output/`, append ข้อมูลลิงก์ดิบและ research log เข้า Obsidian stocks wiki, and sync NotebookLM RAG (Dedup-Aware)

**Agent ที่ใช้:** subagent_media (กรองก่อน) + subagent_macro + subagent_fundamental + subagent_technical + subagent_risk + subagent_insider + Agent 14 (Compliance Auditor)

**บันทึกไปที่:**
- `output/YYYY-MM-DD_youtube_[ticker/topic_slug].md`
- `Database/stocks/{TICKER}.md` (Research Sources + Research Log)
- `Database/log.md` (Chronological summary)
- NotebookLM Stock Notebook & Master Hub

---

### `/research-stock`

**ทำอะไร:**
วิจัยและวิเคราะห์หุ้นเป้าหมายอย่างลึกซึ้ง 360 องศา ด้วยกระบวนการแบบ **Mode 6 (Full Analysis)** ผ่านกองทัพ Custom Sub-Agents Swarm โดยจัดทำรายงานวิเคราะห์เชิงคุณภาพขั้นสุดยอด (**ULTIMATE STRATEGIC BUSINESS MOAT MEGA-REPORT**) อิงตามมาตรฐาน [[16_ultimate_strategic_moat_report]] เป็นดีฟอลต์

**ขั้นตอนที่ระบบทำ (3-Phase Pipeline):**
1. **PHASE A — INITIALIZATION & DATA BRIDGES:**
   - รันคำสั่ง Python Bridges ทันทีเพื่อดึงข้อมูลสดของราคา งบการเงิน และข้อมูลเทคนิค:
     * `python tools/yfinance_bridge.py <TICKER> fundamentals`
     * `python tools/twelvedata_bridge.py <TICKER> price technical`
   - สปอว์น Sub-Agents Swarm (Macro, Fundamental, Technical, Risk)
2. **PHASE B — SWARM DEEP DIVE (6 เสาหลักเชิงคุณภาพ):**
   - รันวิจัยสกัดเชิงคุณภาพอย่างลึกซึ้ง: คูเมืองธุรกิจ 3 ปราการ (ASML, Yield Curve, CoWoS), พันธมิตรลูกค้าชั้นสูง (Apple flywheel, Nvidia, custom silicon), โมเดล Foundry สวิตเซอร์แลนด์, วิสัยทัศน์ CEO (C.C. Wei/Morris Chang), สเปกฮาร์ดแวร์เชิงประยุกต์ใช้งานจริง (N3, N2, A16), และ Silicon Shield ความมั่นคงระดับโลก
   - สกัดกระแสเงินสด FCF after SBC (CFO - CapEx - SBC) และยอดเงินสดสำรอง Net Cash Surplus (งบดุลป้อมปราการ) คลีนสูงสุด หลีกเลี่ยงโมเดล DCF/WACC 10 ปีที่ยุ่งเหยิงโดยไม่มีการร้องขอเพิ่มเติม (เน้นยืดหยุ่นตามผู้ใช้)
   - คัดแนวรับทางเทคนิค (MA200, RSI) และวางแผน DCA 3 ไม้ (Tranches 1, 2, 3) พร้อมตรวจสอบ Graham Margin of Safety (MoS) และออก Stoic DCA Verdict บนสัดส่วนพอร์ต 100% Equity base
   - ตรวจสอบ Geopolitical & Supply chain risks และตั้งค่า Thesis Breakers 3 ข้อ
3. **PHASE C — MULTI-LEVEL STORAGE & RAG SYNC:**
   - สร้างหน้า Obsidian Database/stocks/{TICKER}.md และ Database/sources/{TICKER}.md ตาม Schema มาตรฐาน 100%
   - เพิ่มชื่อหุ้นลงใน Watchlist และ File Index ใน index.md พร้อมบันทึกย่อ 1-3 bullets ลง log.md
   - แจ้งเตือนหรือสั่งสร้าง Stock Notebook ใหม่ใน NotebookLM:
     `python tools/notebooklm_bridge.py create "Stock Analysis: {TICKER}"`
     และอัปโหลดแหล่งอ้างอิง URL ผ่าน batch tools และอัปโหลดรายงาน final .md เข้า Master Hub (`d4268735-ab02-40c5-80a1-f1b9768befd9`)

**Output ที่ได้:**
- รายงาน Markdown `/output/YYYY-MM-DD_[TICKER]_ultimate_comprehensive_academic_mega_report.md` เชิงคุณภาพสุดหรู
- วิกิ Obsidian `database/stocks/{TICKER}.md` ได้รับการจัดตั้ง/อัปเดต
- บันทึก Chronological log ย่อใน `database/log.md`
- สมุด RAG ใน NotebookLM และ Master Hub ซิงค์ข้อมูลล่าสุด
- **Premium Dashboard News Card** แสดงผลในห้องแชท

**Agent ที่ใช้:** subagent_macro + subagent_fundamental + subagent_technical + subagent_risk + Agent 14 (Auditor) + Agent 15 (Compliance)

---

---

### `/portfolio-news-update`

**ทำอะไร:**
วิเคราะห์เจาะลึกข่าวสารล่าสุด 50 ข่าวสาร (10 สินทรัพย์เป้าหมาย สินทรัพย์ละ 5 ข่าว ได้แก่ NVDA, RKLB, GOOGL, AMZN, UNH, NVO, SOFI, PLTR, ASTS, BTC) และประเมินผลกระทบเชิงตัวเลขและยุทธศาสตร์ต่อพอร์ตลงทุน พร้อมแผนจัดสรรเงินสดตั้งรับ Limit Orders 

**ขั้นตอนที่ระบบทำ (5-Phase Workflow):**
1. **PHASE 0 — INITIALIZATION & SHEETS:** ดึงพอร์ตจริงผ่าน `sheets_bridge.py portfolio`
2. **PHASE 1 — LIVE NEWS SEARCH & VERIFICATION:** ทำ Web Search ดึงข่าวเดลต้าสดใหม่ 2-3 วัน ยืนยัน URL ตรงหัวข้อข่าวจริง 100% (ห้ามมี Hallucination ลิงก์หลอก)
3. **PHASE 2 — NARRATIVE & IMPACT DEPTH:** เขียนสรุปเนื้อหาข่าวอย่างละเอียดและอธิบายผลกระทบ (Corporate & Valuation Impact) อย่างลึกซึ้ง (ภาษาไทย)
4. **PHASE 3 — QUANTITATIVE LOGISTICS:** จัดทำแผนการเงิน (Funding Strategy) ตั้งรับคำสั่งซื้อ Limit Orders (เช่น TSM, BTC) เสนอการย้ายทุน (Capital Rotation) trim RKLB หรือใช้ DCA Deposits เพื่อไม่ให้ Cash Cushion ต่ำกว่า 10%
5. **PHASE 4 — STORAGE & RAG SYNC:** บันทึกรายงาน `output/YYYY-MM-DD_portfolio_news_deep_dive.md` (ห้ามใส่ Checklist/QA ในไฟล์), อัปเดต Obsidian wiki/sources และ log.md, อัปโหลด URL ลง NotebookLM stock notebooks (ข้ามการอัปโหลดรายงาน .md ลง Stock notebooks แต่ให้อัปโหลดเข้า Master Hub เสมอ)

**Output ที่ได้:**
- รายงาน Markdown `/output/YYYY-MM-DD_portfolio_news_deep_dive.md`
- Obsidian stocks และ sources ได้รับการซิงค์และ distill URL แหล่งอ้างอิง
- NotebookLM Stock Notebooks (URL เท่านั้น) และ Master Hub (ไฟล์รายงาน) ซิงค์ข้อมูลล่าสุด
- **Premium Dashboard News Card** แสดงผลในห้องแชท

**Agent ที่ใช้:** subagent_macro + subagent_fundamental + subagent_technical + subagent_risk + Agent 14 (Auditor) + Agent 15 (Compliance)


---

### `/macro-update`

**ทำอะไร:**
วิเคราะห์เจาะลึกสถานการณ์ภูมิรัฐศาสตร์มหภาคและสงครามของสหรัฐฯ ครอบคลุม 4 เสาหลักความขัดแย้งหลัก พร้อมประเมินกลไกการส่งผ่านมหภาคและการเงินเชิงสูตร CAPM/WACC, ทำข้อสอบทานราคาสมจริงป้องกัน Over-dramatization, วางแผนกระแสเงินสดรองรับ Limit Orders และจำลองฉากทัศน์ 3 ระดับ (Base / Worst / Best Case) พร้อมแผนปฏิบัติการ Action Plan ล่วงหน้า

**ขั้นตอนที่ระบบทำ (6-Phase Workflow):**
1. **PHASE 0 — INITIALIZATION & SHEETS:** ดึงพอร์ตจริงผ่าน `sheets_bridge.py portfolio`
2. **PHASE 1 — GEOPOLITICAL LIVE NEWS SWEEP:** ทำ Web Search ดึงข่าวเดลต้าสดใหม่ 2-3 วัน เสาหลักละ 5 ข่าว (รวม 20 ข่าว) ยืนยัน URL ข่าวจริง 100%
3. **PHASE 2 — FINANCIAL TRANSMISSION & WACC MODELING:** อธิบายและคำนวณการส่งผ่านทางนโยบายการเงินและการขาดดุลผ่าน Crowding-out effect ไปที่ Bond Yield, WACC และมูลค่า DCF ของหุ้น Long-duration
4. **PHASE 3 — MARKET PRICING GROUNDING:** ตรวจสอบความถูกต้องและประเมินราคาสมเหตุสมผลเชิงปริมาณ (เช่น Interception rates, oil infrastructure) เพื่อตรวจจับการ over-dramatization
5. **PHASE 4 — QUANTITATIVE LOGISTICS & SCENARIO ANALYSIS:** จัดทำ Funding Strategy คุม Cash Cushion > 10% ร่วมกับจำลอง 3 ฉากทัศน์ล่วงหน้าและ Action Plan ดักรอ
6. **PHASE 5 — STORAGE & RAG SYNC:** บันทึกรายงาน `output/YYYY-MM-DD_macro_us_conflict_geopolitics_report.md` (ห้ามมี Checklist/QA score), อัปเดต Obsidian index/log.md, อัปโหลดแหล่ง URL ลง NotebookLM Geopolitical Macro Notebook และอัปโหลดไฟล์รายงาน .md เข้า Master Hub (ลบไฟล์รุ่นเก่าใน RAG ก่อนเพื่อป้องกันข้อมูลซ้ำซ้อน)

**Output ที่ได้:**
- รายงาน Markdown `/output/YYYY-MM-DD_macro_us_conflict_geopolitics_report.md`
- Obsidian index และ chronological log.md ได้รับการอัปเดต
- NotebookLM Macro Notebook (URL) และ Master Hub (ไฟล์รายงาน) ซิงค์ข้อมูลล่าสุดอย่างเป็นระบบ
- **Premium Dashboard News Card** แสดงผลในห้องแชท

**Agent ที่ใช้:** subagent_macro + subagent_fundamental + subagent_technical + subagent_risk + Agent 14 (Auditor) + Agent 15 (Compliance)