# 💼 Portfolio Overview

**Stocks:** [[RKLB]] | [[NVDA]] | [[GOOGL]] | [[AMZN]] | [[UNH]] | [[SOFI]] | [[NVO]] | [[PLTR]]
**Frameworks:** [[dca_rules]] | [[pre_mortem_matrix]] | [[valuation_framework]] | **Decisions:** [[decision_log]] | **Index:** [[index]]

> **Live data always:** `python tools/sheets_bridge.py portfolio`
> **ข้อมูลในไฟล์นี้** = static context + rules; ราคา/allocation ต้องดึงจาก sheets_bridge เสมอ

---

## Static Holdings (shares + avg cost — เปลี่ยนแปลงเมื่อซื้อ/ขายเท่านั้น)

| Ticker | Shares | Avg Cost | Sector | Wiki Page |
|---|---|---|---|---|
| RKLB | 19.00 | $22.86 | Space/Defense | [[RKLB]] |
| NVDA | 7.56 | $127.01 | AI/Semi | [[NVDA]] |
| GOOGL | 2.43 | $190.35 | AI/Cloud | [[GOOGL]] |
| AMZN | 1.92 | $215.96 | E-comm/Cloud | [[AMZN]] |
| UNH | 1.27 | $326.85 | Healthcare | [[UNH]] |
| SOFI | 34.04 | $15.88 | Fintech | [[SOFI]] |
| NVO | 13.99 | $47.76 | Pharma | [[NVO]] |
| TSM | 1.11 | $404.52 | AI/Semi | [[TSM]] (DCA Active) |
| BTC | 0.0059 | $76,658.44 | Digital Gold | [[BTC]] (DCA Active) |
| SPCX | — | — | Space Economy | [[SPCX]] (Pre-IPO) |
| PLTR | 0.00 | $0.00 | AI/Defense | [[PLTR]] (Liquidated 2026-05-24) |

---

## Portfolio Rules & Constraints

### Concentration Limits (อัปเดต 2026-05-24)
| Rule | Limit | Current Status |
|---|---|---|
| Single stock max | 15% | RKLB ~28.47% ⚠️ (เกินเป้า 15% หลัง Active Micro-Trim แต่ปลอดภัยใต้ 30% ceiling) |
| Single sector max | 35% | Space ~28.47% ✅ (RKLB+SPCX อยู่ใต้เพดาน 35.00% ตามกฎ Joint Space Ceiling) |
| Cash target | 0.00% | 17.11% (DCA Active deployment สภาพคล่องสำรองในบัญชี เพื่อโอนสลับ TSM/BTC/NVO) |

### Position Sizing Guidelines
- **Core holding** (high conviction, proven fundamentals): 5-10%
- **Growth position** (high conviction, high growth): 3-8%
- **Speculation bucket** (binary catalyst, pre-profit): max 2-3%
- **Watchlist** (attractive but not yet entry): 0% — just watch

### DCA Protocol
- **คู่มือปฏิบัติการ:** ดูรายละเอียดเต็มรูปแบบที่ [[dca_rules]]
- DCA ทุกเดือน ไม่ว่าตลาดจะเป็นอย่างไร โดยเน้นการจัดสรรตามระบบไร้อารมณ์ (De-emotionalized DCA)
- ระงับการซื้อ RKLB เพิ่มชั่วคราว (Buy Block) เนื่องจากสัดส่วนเกิน 30% (มีสัดส่วน 31.68% ณ ปัจจุบัน)
- Deploy เงินสดสำรอง (Cash 17.04%) ตามเกณฑ์ Market Correction Tiers
- จัดลำดับความสำคัญตาม Priority Order สะสม (Priority 1: NVO, Priority 2: NVDA, Priority 3: AMZN)

---

## Correlation Matrix (approximate)

| — | RKLB | NVDA | GOOGL | AMZN | UNH | SOFI | NVO | PLTR |
|---|---|---|---|---|---|---|---|---|
| RKLB | 1.0 | 0.4 | 0.3 | 0.3 | 0.1 | 0.3 | 0.1 | 0.5 |
| NVDA | — | 1.0 | 0.7 | 0.6 | 0.1 | 0.3 | 0.1 | 0.7 |
| GOOGL | — | — | 1.0 | 0.6 | 0.2 | 0.2 | 0.1 | 0.5 |
| AMZN | — | — | — | 1.0 | 0.2 | 0.3 | 0.1 | 0.4 |
| UNH | — | — | — | — | 1.0 | 0.2 | 0.4 | 0.1 |
| SOFI | — | — | — | — | — | 1.0 | 0.1 | 0.3 |
| NVO | — | — | — | — | — | — | 1.0 | 0.1 |
| PLTR | — | — | — | — | — | — | — | 1.0 |

> ⚠️ High AI cluster correlation: NVDA + GOOGL + AMZN + PLTR — ถ้า AI sentiment ร่วง = ทั้งกลุ่มพัง

---

## Rebalance Roadmap

### Phase 1 — ✅ COMPLETE (2026-05-14)
1. ~~TRIM RKLB จาก ~45% → 30%~~ ✅ DONE — ขาย 14 หุ้น (Phase 1+2) เหลือ 21.46 shares
2. ~~สะสม cash~~ ✅ DONE — Cash 18.83% ✅
3. ~~Analyze GOOGL~~ ✅ DONE — Full analysis 2026-05-14, conviction 7/10

### Phase 2 — ✅ COMPLETE (2026-05-24)
1. ~~PLTR Full Analysis & Exit~~ ✅ DONE — Full analysis 2026-05-21, 100% liquidated 2026-05-24 (+$120.70)
2. ~~RKLB Active Micro-Trim~~ ✅ DONE — ขาย RKLB 2.46 หุ้น @ $135.76 (+$334.22) ลดสัดส่วนเหลือ 28.47% คุมความเสี่ยงเรียบร้อย
3. ~~DCA Deployments~~ ✅ DONE — ช้อนสะสม NVO (13.99 หุ้น), เริ่ม Tranche 1 TSM (1.11 หุ้น) และ BTC (0.0059 หุ้น) สำเร็จ
4. ~~UNH Thesis Resolved~~ ✅ DONE — Confirmed Lifetime Hold ยกเว้นโดน DOJ สั่งฟ้องอาญา

### Phase 3 — Active & Long-term (H2 2026)
1. SOFI เพิ่ม — รอ Muddy Waters resolve + H2 2026
2. Review PLTR exit ถ้า conviction < 4/10 หลัง analysis
3. พิจารณา new position ถ้า conviction ≥ 7/10 และ Cash > 20%

---

## Worst-Case & Systemic Scenarios
> **คู่มือเฝ้ารงระวังภัยพิบัติ:** ดูรายละเอียดแบบสมบูรณ์และ Early Warning Signals ที่ [[pre_mortem_matrix]]

| Scenario | Portfolio Impact | อัปเดต |
|---|---|---|
| RKLB Neutron Failure (-90% drop) | พอร์ตสูญเสียถาวร ~28% (SPOF critical) | 2026-05-21 |
| AI Capex Bust (NVDA+GOOGL+AMZN) | กลุ่ม AI / Cloud ทรุด กระทบพอร์ต ~36% | 2026-05-21 |
| Tech Antitrust Breakup Wave | บังคับแยกส่วนธุรกิจ กระทบพอร์ต ~34% | 2026-05-21 |
| Bond Yield Spike 6%+ (Rate Shock 2.0) | กระทบหุ้นมูลค่า DCF สูง (RKLB, PLTR, SOFI) ~43% | 2026-05-21 |
| UNH DOJ Criminal Indictment | UNH ดิ่งหนักและผู้บริหารว่างเว้น ~2% | 2026-05-21 |

> **กฎ:** ห้ามใช้ leverage ไม่ว่ากรณีใดทั้งสิ้น — DCA ต่อเนื่องช่วยให้ average down ได้เสมอ
