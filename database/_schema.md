# 📐 Investment Wiki — Schema & Update Protocol

> **อ่านไฟล์นี้ก่อนทุกครั้งที่จะเขียนหรืออัปเดต wiki** — นี่คือ "กฎของระบบ"

---

## หลักการ (Immutable Rules)

1. **Database = สมองหลัก (PRIMARY)** — ทุก research output, analysis, สรุป, insight ต้องเข้าที่นี่ก่อนเสมอ
   - NotebookLM = SECONDARY — เฉพาะ 10-K/10-Q/PDF ต้นทางขนาดใหญ่เท่านั้น
2. **One page per entity** — หุ้น 1 ตัว = 1 ไฟล์ ห้ามสร้างซ้ำ
3. **Incremental update only** — อัปเดตของเดิม ไม่ใช่สร้างใหม่ เว้นแต่เป็น entity ใหม่จริงๆ
4. **Append to log, never delete** — `log.md` เป็น append-only เสมอ ห้ามลบ
5. **Date-stamp everything** — ทุก metric ต้องมีวันที่กำกับ ข้อมูลไม่มีวันที่ = ไม่มีค่า
6. **Contradiction = escalate** — ถ้าข้อมูลใหม่ขัดกับของเดิม ให้ระบุ `⚡ CONFLICT:` และอธิบายทั้งสองฝั่ง ไม่ใช่ overwrite โดยไม่บอก

---

## โครงสร้าง Vault

```
Database/
├── _schema.md          ← ไฟล์นี้ (กฎระบบ)
├── index.md            ← Catalog ทุก entity + สถานะ
├── log.md              ← Append-only research log
├── stocks/             ← Wiki pages ทีละหุ้น
│   ├── RKLB.md
│   ├── NVDA.md
│   └── ...
├── sectors/            ← Sector-level analysis
│   └── space.md
├── decisions/
│   └── decision_log.md ← Timeline BUY/HOLD/TRIM/SELL
└── portfolio/
    └── overview.md     ← Live pointer + allocation rules
```

---

## Stock Page Format (บังคับทุกหน้า)

```markdown
---
ticker: XXXX
company: Company Name
sector: Technology / Healthcare / etc.
tags: [in-portfolio, conviction/high, space, growth]
last_updated: YYYY-MM-DD
conviction: 7/10
thesis_status: ACTIVE | WATCH | BROKEN
---

# XXXX — Company Name

## 🎯 Investment Thesis
[2-4 ประโยคสรุปว่าทำไมถือหุ้นตัวนี้ — เน้น WHY ไม่ใช่ WHAT]

## 📊 Key Metrics Snapshot
| Metric | Value | Date |
|---|---|---|
| Price | $X.XX | YYYY-MM-DD |
| Market Cap | $XB | YYYY-MM-DD |
| Revenue (TTM) | $XB | YYYY-MM-DD |
| ... | ... | ... |

## 🏰 Moat Analysis
[ข้อได้เปรียบทางการแข่งขันที่ยั่งยืน]

## ⚠️ Risk Factors & Thesis Breakers
- **[Risk Name]:** รายละเอียด (date)
- **Thesis breaks if:** [เงื่อนไขที่ thesis จะพัง]

## 💼 Portfolio Position
| Item | Value |
|---|---|
| Shares | X.XX |
| Avg Cost | $X.XX |
| Current Price | $X.XX (YYYY-MM-DD) |
| Gain/Loss | +X% |
| Allocation | X% of portfolio |

## 🎬 Decision History
| Date | Action | Price | Rationale |
|---|---|---|---|
| YYYY-MM-DD | BUY/HOLD/TRIM/SELL | $X | ... |

## 📡 KPI Watchlist (Next Review)
- [ ] KPI หนึ่ง — ดูตอน [เหตุการณ์/วันที่]
- [ ] KPI สอง — threshold: [เงื่อนไข]

## 🔗 Key Sources
- [Source Name](URL) — YYYY-MM-DD

---

## 📝 Research Log
> Append each update here. Never delete old entries.

### [YYYY-MM-DD] — [Event/Research Type]
[สรุปสั้นๆ ไม่เกิน 5 bullet]
```

---

## Update Protocol (ทำตามลำดับนี้ทุกครั้ง)

### ก่อน Research ใหม่
```
1. อ่าน Database/stocks/{TICKER}.md ก่อนเสมอ
2. ถ้ายังไม่มีไฟล์ → สร้างตาม Stock Page Format ด้านบน
3. อ่าน Database/log.md เพื่อดู research ล่าสุด
4. ถ้ามีข้อมูลครอบคลุมอยู่แล้ว (< 14 วัน) → ใช้ของเดิม, research แค่ delta ที่ขาด
```

### หลัง Research เสร็จ
```
1. อัปเดต stocks/{TICKER}.md:
   - อัปเดต frontmatter: last_updated, conviction
   - อัปเดต Key Metrics Snapshot (date-stamp ใหม่)
   - อัปเดต Risk Factors ถ้ามีเพิ่ม/เปลี่ยน
   - เพิ่ม entry ใน Decision History ถ้ามีการตัดสินใจ
   - อัปเดต KPI Watchlist (check off ที่ทำแล้ว, เพิ่มอันใหม่)
   - APPEND ใน Research Log section (ห้าม overwrite เดิม)
   
2. APPEND ใน Database/log.md (1-3 bullet summary)
    
3. อัปเดต Database/index.md ถ้าเพิ่ม entity ใหม่
4. APPEND หรืออัปเดตสรุปแหล่งข้อมูลใน `Database/sources/{TICKER}.md` ตามรูปแบบด้านล่าง
```

---

## Sources Page Format (Database/sources/{TICKER}.md)

หน้านี้สร้างขึ้นเพื่อบันทึกและสกัดความรู้จากแหล่งอ้างอิงทั้งหมดแบบเบ็ดเสร็จ เพื่อประหยัด Tokens และลดความจำเป็นในการ Fetch ลิงก์ออนไลน์ซ้ำซาก โดยมีโครงสร้างดังนี้:

```markdown
# 📎 {TICKER} — Research Sources
> **Company:** [Company Name]  
> **Thesis:** [สรุปสมมติฐานการลงทุนสั้นๆ 1 ประโยค]  
> **Research Sessions:** [YYYY-MM-DD] | **Updated:** [YYYY-MM-DD]  
> **Total Sources:** [จำนวนแหล่งข้อมูลรวม]

> 💡 **วิธีใช้:** อ่านหน้านี้แทนการเปิด URL — summary บอกว่าแต่ละ source พูดถึงอะไรและเกี่ยวกับ thesis ยังไง

---

## [ชื่อหมวดหมู่ เช่น 📊 Earnings & Financial Data / 🎯 Analyst Coverage]

### [ชื่อบทความ / แหล่งอ้างอิง / หัวข้อวิดีโอ]
**Tags:** #tag1 #tag2 ... (เช่น #earnings #valuation #risk #youtube)
**สรุป:** [สรุปย่อประเด็นสำคัญและเหตุผลว่าทำไมแหล่งข้อมูลนี้สนับสนุนหรือสั่นคลอน Thesis การลงทุน 1-2 ประโยค]
**Key Stats/Data:** [ตัวเลขจริง, สถิติ, หรือ Core Metric ที่สกัดออกมากำหนดเป็นจุดยืนยันความจริง หรือระบุ N/A]
**URL:** [ลิงก์ URL ปลายทางที่เข้าถึงได้จริง]
```

---

## Sector Page Format

```markdown
---
sector: Space / AI / Healthcare / etc.
tags: [sector-analysis]
last_updated: YYYY-MM-DD
---

# Sector: [Name]

## 📡 Key Catalysts
[อะไรขับเคลื่อน sector นี้ใน 12-24 เดือนข้างหน้า]

## 🏆 Peer Ranking
| Ticker | P/S | Revenue | Moat | Rank |
|---|---|---|---|---|

## ⚡ Risks
[ความเสี่ยงระดับ sector]

## 📝 Research Log
[Append-only]
```

---

## Decision Log Format (decisions/decision_log.md)

```
| Date | Ticker | Action | Price | Conviction | Rationale | Next Review |
```

---

## Tags ที่ใช้ใน Obsidian

| Tag | ความหมาย |
|---|---|
| `#in-portfolio` | ถืออยู่จริง |
| `#watchlist` | ติดตาม ยังไม่ซื้อ |
| `#conviction/high` | Conviction 7-10/10 |
| `#conviction/medium` | Conviction 4-6/10 |
| `#conviction/low` | Conviction 1-3/10 |
| `#thesis/active` | Thesis ยังใช้ได้ |
| `#thesis/watch` | Thesis มีความเสี่ยง |
| `#thesis/broken` | Thesis พังแล้ว — review ด่วน |
| `#sector/space` | Space industry |
| `#sector/ai` | AI / Semiconductor |
| `#sector/fintech` | Fintech |
| `#sector/healthcare` | Healthcare |
| `#sector/ecommerce` | E-commerce / Cloud |
| `#growth` | Growth stock |
| `#speculation` | Speculation bucket (ระวัง) |
| `#concentration-risk` | Allocation สูงผิดปกติ |
