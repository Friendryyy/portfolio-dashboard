# 📺 YouTube Research Report: NVIDIA Earnings 2026 — Price Action LIVE TRADING
> **วันที่:** 2026-05-21 | **Source:** https://www.youtube.com/live/liRsG-3Jiu8 | **Topics:** 8

---

## 📺 ที่มา
- **วิดีโอ:** Nvidia Earnings 2026: Price Action LIVE TRADING | Stock Market Today
- **Channel:** Stock Market Today (live trading session)
- **URL:** https://www.youtube.com/live/liRsG-3Jiu8
- **Context:** Live trading reaction หลัง NVDA Q1 FY2027 earnings รายงาน 2026-05-20

---

## 📊 NVDA Q1 FY2027 — Scorecard

| Metric | Q1 FY27 Actual | Estimate | Beat |
|---|---|---|---|
| Revenue | **$81.6B** | $78.8-80.4B | ✅ +3-4% |
| EPS (non-GAAP) | **$2.39** | $1.75-1.79 | ✅ +33% |
| Gross Margin GAAP | **74.9%** | 74.5% | ✅ |
| Data Center | **$75.2B** | ~$65-70B | ✅ +92% YoY |
| Networking | **$14.8B** | — | ✅ +199% YoY |
| Free Cash Flow | **$49B** | — | 🟢 record |
| Q2 FY27 Guidance | **$91B ±2%** | $86B | ✅ +5.8% |

**Post-earnings price action:** หุ้นเปิด **-0.5%** แม้ beat ทุก metric — classic "sell the news"

---

## 📑 Topic 1: Jensen Huang ที่ Trump-Xi Summit + China H200 ยัง Stalled

### สรุปจากวิดีโอ
Live trading session นี้ trade price action ที่ NVDA CFO ประกาศชัดว่า **"We are not including any China data center compute revenue in our outlook"** — zero China revenue assumption ใน Q2 $91B guidance

### Research เพิ่มเติม
**ที่มาของ Trump-Xi Summit:**
- Jensen Huang ถูกเพิ่มเข้ากลุ่ม delegation กะทันหัน หลัง Trump โทรหาโดยตรง ("President Trump asked me to come") — ขึ้นเครื่อง Air Force One ระหว่าง refueling ที่ Alaska [CNBC, 2026-05-14]
- Summit outcome: **"Warm Rhetoric, H200 Deliveries Remain Stalled"** [TechTimes, 2026-05-15]

**สถานะ H200 China:**
- US อนุมัติให้ Alibaba, Tencent, ByteDance, JD.com, Lenovo ซื้อ H200 ได้ ภายใต้ revenue-share 25% กับรัฐบาลสหรัฐฯ
- **Beijing สั่งให้บริษัทจีนหยุดรับสินค้า** — กดดันทางการเมืองให้ block การซื้อ
- ผล: **$0 China DC revenue ใน Q1** + ไม่รวมใน Q2 guidance

**Upside Optionality:**
- Q2 $91B = 100% ex-China → China reopening = **pure upside optionality** ที่ยังไม่ถูก price in
- หาก H200 เริ่มส่งมอบ → potential $8B+ incremental revenue ต่อปี

### ผลต่อพอร์ต
- **NVDA (avg $127.01, ~19%):** ไม่ว่า China จะ reopen หรือไม่ → Q2 $91B guidance ยืนอยู่; China upside = free optionality

### Key Sources
- [CNBC: Jensen "Trump asked me to come"](https://www.cnbc.com/2026/05/14/nvidias-jensen-huang-on-china-trip-trump.html)
- [TechTimes: Trump-Xi Summit H200 Stalled](https://www.techtimes.com/articles/316674/20260515/trump-xi-close-beijing-summit-warm-rhetoric-nvidia-h200-deliveries-remain-stalled-rare-earth.htm)
- [AI News: H200 Deal Analysis](https://www.artificialintelligence-news.com/news/nvidia-h200-china-deal-stalled-trump-xi-summit-2026/)

---

## 📑 Topic 2: SBC ~$2B + True FCF After SBC — Mandatory Valuation Check

### สรุปจากวิดีโอ
NVDA เปลี่ยนนโยบาย non-GAAP ตั้งแต่ Q1 FY27: รวม SBC เข้าใน non-GAAP แล้ว (ไม่ exclude อีก) → non-GAAP EPS $2.39 ตอนนี้ "cleaner" กว่าก่อน

### Research เพิ่มเติม
**ตัวเลขยืนยัน Q1 FY27:**
- Cash from Operations (CFO): **$50.3B**
- Free Cash Flow (reported): **$49.0B** (record, up from $35B ใน Q4 FY26)
- CapEx (estimate): $50.3B - $49.0B = **~$1.3B** (fabless model = CapEx ต่ำ)
- SBC (opex portion): **~$1.9B** (ยืนยันจาก NVDA Q1 FY27 guidance)
- SBC total (incl. COGS): **~$2.0-2.2B** (estimate)
- GAAP Operating Expenses: **$7.621B** (รวม SBC $1.9B)

**FCF After SBC Calculation (SBC Zero-Trust Rule — CLAUDE.md):**
```
FCF After SBC = FCF - SBC total
              = $49.0B - $2.1B
              = ~$46.9B

FCF After SBC Margin = $46.9B / $81.6B = 57.5%
```

**เปรียบเทียบกับ PLTR Q1 FY26:**
| Metric | NVDA Q1 FY27 | PLTR Q1 FY26 |
|---|---|---|
| SBC % Revenue | ~2.6% | 12.3% |
| FCF After SBC Margin | **~57.5%** | 18.2% |

NVDA SBC drag = minimal (2.6%) vs revenue base $81.6B — ไม่เป็น concern

### ผลต่อพอร์ต
- **NVDA:** FCF After SBC 57.5% = หนึ่งในสูงสุดใน semiconductor history; valuation floor แกร่งมาก
- **DCA Decision:** รัน `twelvedata_bridge.py quote NVDA` เพื่อ verify live price ก่อน DCA

### Key Sources
- [SEC 8-K Q1 FY27 CFO Commentary](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000051/q1fy27cfocommentary.htm)
- [Quiver Quant: NVDA EPS Beat Breakdown](https://www.quiverquant.com/news/NVIDIA+Corporation+(NVDA)+Releases+Q1+2027+Earnings:+Blockbuster+Revenue,+Profit+and+EPS+Beat)

---

## 📑 Topic 3: "Sell the News" -0.5% + DCA Timing

### สรุปจากวิดีโอ
Core ของ live trading session — trader navigate price action ที่หุ้นลงแม้ beat ทุก metric

### Research เพิ่มเติม
**ทำไม -0.5% แม้ beat ครั้งประวัติศาสตร์?**
- NVDA ขึ้น **+20% ในเดือนก่อน earnings** (จาก ~$110 → ~$132) → expectations ถูก price in ล่วงหน้า
- Analyst: "garden variety beat — better than expected top/bottom + guidance above Street" — ไม่มี shock factor
- Historical: May 2024 NVDA +32% หลัง earnings (AI cycle ต้น), ตอนนี้ market efficient มากขึ้น

**DCA Timing:**
- Post-earnings -0.5% ถึง -2% = ปกติสำหรับ priced-in growth stocks
- ประวัติ NVDA: ฟื้นใน 2-4 สัปดาห์หลัง earnings ถ้า thesis intact
- สำหรับ DCA 30 ปี: soft spot post-earnings = opportunity ไม่ใช่ warning

### ผลต่อพอร์ต
- **NVDA (avg $127.01):** ราคา ~$131-135 = ใกล้ avg cost เล็กน้อย; **DCA เพิ่มได้ถ้า pullback $120-125** ตาม DCA Decision Tree Priority 2

### Key Sources
- [Al Jazeera: NVDA record profit + price reaction](https://www.aljazeera.com/economy/2026/5/21/nvidia-posts-record-profit-and-revenue-amid-ai-chip-boom)
- [247 Wall St: NVDA +20% pre-earnings](https://247wallst.com/investing/2026/05/14/nvidia-is-up-20-in-a-month-could-the-may-20-earnings-report-knock-it-right-back-down/)

---

## 📑 Topic 4: Gross Margin 74.9% + AMD MI350 — Pricing Power ยังอยู่

### สรุปจากวิดีโอ
Gross margin เป็น metric traders ดู real-time

### Research เพิ่มเติม
**NVDA Gross Margin Q1 FY27:**
- GAAP: **74.9%** | Non-GAAP: **75.0%** (-0.1pt QoQ, +14.4pt YoY)
- Q2 FY27 guidance: 74.9% / 75.0% ±50bps — flat sequential
- ต่ำกว่า 73% = signal pricing pressure → **74.9% ผ่าน** ✅

**AMD MI350 Competitive Reality:**
- AMD claims "40% more tokens-per-dollar" ใน inference vs Blackwell B200
- Hyperscalers ใช้ mixed fleet: **NVDA training** + **AMD inference cost optimization**
- NVDA Spectrum-X ใหญ่กว่า all Ethernet peers combined → AMD ไม่มี full-stack networking equivalent ยังคง

**CFO Quote:** "GAAP gross margin was 74.9%...largely flat sequentially as Blackwell Systems continued to account for most shipments."

### ผลต่อพอร์ต
- **NVDA:** AMD threat จริงใน inference แต่ CUDA lock-in + networking moat ยังแข็งแกร่ง 2-3 ปีข้างหน้า — **Moat intact, thesis valid**

### Key Sources
- [Shacknews: NVDA 75% gross margin](https://www.shacknews.com/article/149225/nvidia-nvda-reports-75-q1-fy27-gross-margin)
- [Tech-Insider: Blackwell vs AMD MI350](https://tech-insider.org/nvidia-blackwell-vs-amd-mi350-2026/)

---

## 📑 Topic 5: Inference Boom + Anthropic + CoreWeave

### สรุปจากวิดีโอ
Jensen: "Demand has gone parabolic. Agentic AI has arrived." — inference demand กำลัง sustain supercycle

### Research เพิ่มเติม
**Key Data:**
- Anthropic ใช้ NVDA GPU ผ่าน CoreWeave สำหรับ production inference; training ผ่าน AWS Trainium (Project Rainier)
- CoreWeave เซ็น multi-year deal กับ Anthropic — NVDA GB200 NVL72 = primary inference hardware
- Meta ให้ commitment $21B กับ CoreWeave สำหรับ AI infrastructure
- CoreWeave = first NVDA Exemplar Cloud สำหรับ inference on GB200 NVL72

**Training vs Inference:**
- Inference = persistent GPU demand ตลอดเวลา → demand curve flatter but longer vs training batch jobs
- Agentic AI = chains of inference calls → 10-100x more compute per user action
- Jensen: Grace Blackwell = "lowest token generation cost at inference" → NVDA ตั้งใจ dominate inference

### ผลต่อพอร์ต
- **NVDA:** Inference = demand layer ใหม่ต่อจาก training **thesis extender** ✅
- **GOOGL:** GCP ต้องใช้ NVDA GPU ด้วยสำหรับ third-party inference workloads

### Key Sources
- [The Next Web: CoreWeave x Anthropic](https://thenextweb.com/news/coreweave-has-agreed-a-multi-year-gpu-cloud-deal-with-anthropic-to-power-claude-at-production-scale-its-second-major-ai-infrastructure-announcement-in-48-hours)
- [CoreWeave Press: NVDA HGX B300](https://www.coreweave.com/news/coreweave-advances-ai-native-cloud-platform-for-the-next-phase-of-production-scale-ai)

---

## 📑 Topic 6: Networking Revenue $14.8B (+199% YoY) — Hidden Revenue Monster

### สรุปจากวิดีโอ
Segment ที่ทุกคนมองข้ามเพราะโฟกัส GPU — แต่กำลัง triple ทุกปี

### Research เพิ่มเติม
**Q1 FY27 Networking Breakdown:**
| Segment | Q1 FY27 | Growth |
|---|---|---|
| Spectrum-X (Ethernet) | >$10B annualized | double-digit sequential + YoY |
| InfiniBand (XDR) | — | **+400%+ YoY** |
| **รวม Networking** | **$14.8B** | **+199% YoY** |

**CFO Kress:** "Spectrum-X...is now larger than all Ethernet network peers combined. InfiniBand...growing more than 4x year over year."

**ทำไม Networking Margin สูงกว่า GPU:**
- Software/firmware licensing → high gross margin
- Switching cost สูง — ย้าย ecosystem ยาก
- AMD ไม่มี full-stack networking equivalent

### ผลต่อพอร์ต
- **NVDA:** Networking = **second major moat** ที่ AMD ยังตามไม่ทัน → protect margin long-term แม้ GPU competition เพิ่ม

### Key Sources
- [NVDA Earnings Transcript (Motley Fool)](https://www.fool.com/earnings/call-transcripts/2026/05/20/nvidia-nvda-q1-2027-earnings-transcript/)
- [Network World: NVDA networking roadmap](https://www.networkworld.com/article/4050881/nvidia-networking-roadmap-ethernet-infiniband-co-packaged-optics-will-shape-data-center-of-the-future.html)

---

## 📑 Topic 7: $80B Buyback + Dividend 25x — Transition เป็น Dividend Compounder

### สรุปจากวิดีโอ
Capital return program เป็นข่าวสำคัญสำหรับนักลงทุน DCA ระยะยาว

### Research เพิ่มเติม
**Capital Return Q1 FY27:**
- Q1 returned: **$20B** (record quarterly return)
- New buyback authorization: **$80B** (เพิ่มเติม)
- Dividend: **$0.01 → $0.25/share/quarter** (+2,400%)
- Dividend yield ที่ราคา ~$132: **~0.76%** — เล็กน้อยแต่ growing fast

**ที่ avg cost $127.01:**
- Yield-on-cost = $1.00 ÷ $127.01 = **0.79%**
- ถ้า dividend grow 20%/year × 10 ปี → yield-on-cost สูงขึ้นสู่ 4-5% โดยไม่ต้องทำอะไร

**Impact ต่อ Investor Profile:**
- Pension funds, income ETFs เริ่ม qualify NVDA เข้า portfolio → institutional demand เพิ่ม
- $80B buyback ลด dilution จาก SBC + ลด share count → EPS accretive multi-year

### ผลต่อพอร์ต
- **NVDA:** Transition จาก pure growth → **Dividend Growth Compounder** สอดคล้องกับ DCA 30-year thesis ✅

### Key Sources
- [StockTitan: NVDA $81.6B + buyback $80B](https://www.stocktitan.net/news/NVDA/nvidia-announces-financial-results-for-first-quarter-fiscal-fq78amc9h84m.html)
- [IndMoney: Dividend 25x analysis](https://www.indmoney.com/blog/us-stocks/nvidia-stock-q1-fy27-earnings-81b-revenue-25x-dividend)

---

## 📑 Topic 8: Sovereign AI +80% YoY + 40 Countries — TAM ที่ยังไม่ถูก Price In

### สรุปจากวิดีโอ
Jensen "Demand has gone parabolic" — sovereign AI คือ demand driver นอกเหนือ hyperscalers

### Research เพิ่มเติม
**CFO Kress:** "Sovereign revenue increased more than 80% year over year...deployed across nearly 40 countries."

**Major Sovereign AI Deals (2026):**
| ประเทศ | Deal | Scale |
|---|---|---|
| South Korea | Sovereign cloud + AI factories | >250,000 NVDA GPUs |
| France | Mistral AI deployment | 18,000 Grace Blackwell systems |
| UAE | DGX Vera Rubin early delivery | 8,640 → 16,000 Blackwell Ultra |
| Germany | Deutsche Telekom industrial AI cloud | World's first |
| Canada | Toronto-Waterloo corridor | 320 MW power pathway |
| UK | AI research compute | £1B by 2030 |
| India | AI factories (L&T, Yotta, Netweb) | National scale |

**Revenue Structure:**
- Hyperscalers >50% ของ DC revenue = >$38B (CFO ยืนยัน)
- Sovereign = growing fast, ~$10-15B estimate + 80% YoY
- ลด customer concentration risk ระยะยาว

### ผลต่อพอร์ต
- **NVDA:** Sovereign AI = demand buffer ถ้า hyperscaler CapEx ชะลอ + government contracts = multi-year revenue visibility
- **MACRO:** AI infrastructure กลายเป็น national security asset → geopolitical demand ไม่หายง่าย

### Key Sources
- [Yahoo Finance: NVDA Sovereign AI](https://finance.yahoo.com/news/nvidia-deepens-role-global-ai-031845840.html)
- [The National: UAE mega-deal](https://www.thenationalnews.com/business/2026/03/27/what-the-uaes-mega-deal-with-nvidia-means-for-its-ai-sovereignty/)
- [Futurum: NVDA European AI Sovereignty](https://futurumgroup.com/press-release/nvidias-european-ai-sovereignty-push-infrastructure-partnerships-and-policy-report-summary/)

---

## 🎯 Investment Implications สรุป

| Topic | กระทบ | Action |
|---|---|---|
| China H200 Stalled | NVDA | Hold — $0 China ใน Q2 guidance; upside optionality ถ้าเปิด |
| FCF After SBC ~57.5% | NVDA | Valuation แข็งแกร่งมาก; DCA ถ้า pullback $120-125 |
| "Sell the News" -0.5% | NVDA | Pattern ปกติ; รอ 2-4 สัปดาห์ settle; ไม่ใช่ thesis break |
| Gross Margin 74.9% | NVDA | Pricing power intact; AMD threat ใน inference เท่านั้น |
| Inference + Anthropic | NVDA + GOOGL | Demand layer ใหม่; thesis extender ✅ |
| Networking $14.8B (+199%) | NVDA | Hidden moat; AMD ตามไม่ทัน → protect long-term margin |
| $80B Buyback + Dividend 25x | NVDA | Dividend Compounder; attract institutional; DCA 30yr aligned ✅ |
| Sovereign AI 40 Countries | NVDA + MACRO | TAM expansion + customer diversification; sticky demand |

**Overall NVDA Thesis Assessment:**
> NVDA Q1 FY2027 = thesis **ยิ่งแข็งแกร่งขึ้น** หลัง earnings นี้ FCF monster ($49B), Networking moat emerging, Sovereign AI diversifying customer base, $91B Q2 guide = 100% ex-China
> ใน DCA Decision Tree: NVDA ยัง **Priority 2** (รองจาก NVO ที่ Active Zone 1) — DCA เพิ่มได้ถ้า pullback $120-125

---

## 🔗 All Sources

| URL | สรุป | Tags |
|---|---|---|
| https://www.youtube.com/live/liRsG-3Jiu8 | Source วิดีโอหลัก | #youtube #earnings |
| https://www.cnbc.com/2026/05/14/nvidias-jensen-huang-on-china-trip-trump.html | Jensen at Trump-Xi Summit | #news #macro |
| https://www.techtimes.com/articles/316674/20260515/trump-xi-close-beijing-summit-warm-rhetoric-nvidia-h200-deliveries-remain-stalled-rare-earth.htm | H200 stalled outcome | #macro #risk |
| https://www.artificialintelligence-news.com/news/nvidia-h200-china-deal-stalled-trump-xi-summit-2026/ | H200 deal analysis | #risk |
| https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000051/q1fy27cfocommentary.htm | SEC CFO Commentary Q1 FY27 | #IR #sec |
| https://www.fool.com/earnings/call-transcripts/2026/05/20/nvidia-nvda-q1-2027-earnings-transcript/ | Earnings call transcript | #earnings #IR |
| https://www.quiverquant.com/news/NVIDIA+Corporation+(NVDA)+Releases+Q1+2027+Earnings:+Blockbuster+Revenue,+Profit+and+EPS+Beat | EPS $2.39 beat | #earnings #valuation |
| https://www.aljazeera.com/economy/2026/5/21/nvidia-posts-record-profit-and-revenue-amid-ai-chip-boom | Record profit + price action | #news |
| https://www.stocktitan.net/news/NVDA/nvidia-announces-financial-results-for-first-quarter-fiscal-fq78amc9h84m.html | Full financials + buyback | #earnings #IR |
| https://www.shacknews.com/article/149225/nvidia-nvda-reports-75-q1-fy27-gross-margin | Gross margin 75% | #earnings |
| https://tech-insider.org/nvidia-blackwell-vs-amd-mi350-2026/ | Blackwell vs AMD MI350 | #moat #sector |
| https://thenextweb.com/news/coreweave-has-agreed-a-multi-year-gpu-cloud-deal-with-anthropic | CoreWeave x Anthropic deal | #product #catalyst |
| https://www.coreweave.com/news/coreweave-advances-ai-native-cloud-platform-for-the-next-phase-of-production-scale-ai | CoreWeave HGX B300 | #product |
| https://finance.yahoo.com/news/nvidia-deepens-role-global-ai-031845840.html | Sovereign AI global | #macro #catalyst |
| https://www.thenationalnews.com/business/2026/03/27/what-the-uaes-mega-deal-with-nvidia-means-for-its-ai-sovereignty/ | UAE sovereign AI deal | #macro |
| https://futurumgroup.com/press-release/nvidias-european-ai-sovereignty-push-infrastructure-partnerships-and-policy-report-summary/ | Europe AI sovereignty | #macro |
| https://www.heygotrade.com/en/blog/nvidia-q1-fy27-earnings-preview-may-20-2026/ | Pre-earnings preview | #analyst |
| https://www.gurufocus.com/news/8872854/nvidia-nvda-q1-fy2027-eps-239-beats-175-est | GF Score 96/100, 31.9% undervalued | #valuation #analyst |
| https://247wallst.com/investing/2026/05/14/nvidia-is-up-20-in-a-month-could-the-may-20-earnings-report-knock-it-right-back-down/ | +20% pre-earnings context | #technicals |
| https://www.kiplinger.com/investing/live/nvidia-earnings-live-updates-and-commentary-may-2026 | Kiplinger live earnings coverage | #news #earnings |
| https://www.cnbc.com/2026/05/20/nvidia-nvda-earnings-report-q1-2027.html | CNBC live earnings updates | #news #earnings |
