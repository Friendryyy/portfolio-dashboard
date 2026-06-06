# Agent System Audit — 2026-05-08

## Executive Summary

ระบบเดิมมีจุดแข็งมากในงาน **single-stock analysis**: ข่าว, fundamental, technical, portfolio risk, macro, moat, smart money และ ESG ครอบคลุมแกนหลักของนักวิเคราะห์หุ้นแล้ว แต่ยังมีช่องว่างระดับ "investment operating system" ที่มืออาชีพต้องมีเพิ่ม:

1. ตรวจคุณภาพหลักฐานก่อนเชื่อรายงาน
2. ประเมินว่าหุ้นนั้นเหมาะกับพอร์ตจริงหรือไม่
3. คุม tax/FX/execution friction
4. ติดตาม thesis หลังซื้อด้วย KPI
5. กัน bias ก่อนตัดสินใจจริง

จึงเพิ่ม Agent 09-13 เพื่อเปลี่ยนระบบจากรายงาน 8-Agent เป็นระบบ 13-Agent ที่ครบวงจรขึ้น

---

## Gap Analysis Matrix

| ช่องว่างเดิม | ความเสี่ยงถ้าไม่แก้ | Agent ที่เพิ่ม | สิ่งที่เติมเต็ม |
|---|---|---|---|
| Source quality ยังขึ้นกับ agent แต่ละตัว | รายงานอาจมั่นใจสูงจากข้อมูลเก่า/ผิด/source อ่อน | 09 Research Integrity | ตรวจ evidence map, freshness, unsupported claims, confidence |
| Portfolio Agent เดิมเน้น position รายตัว | หุ้นดีอาจยิ่งเพิ่ม concentration ในพอร์ตจริง | 10 Portfolio Construction | ตรวจ factor exposure, cash policy, rebalance, portfolio fit |
| คำแนะนำยังไม่ครบโลกจริง | ซื้อ/ขายจริงอาจเสียจาก FX, tax, fee, slippage | 11 Tax/FX/Execution | แปลง verdict เป็น order plan, FX/tax awareness, tranche execution |
| รายงานจบแล้วไม่มีระบบติดตาม | ถือหุ้นเพราะจำ thesis ไม่ได้ หรือพลาด catalyst สำคัญ | 12 Thesis Monitoring | KPI tracker, thesis breakers, review calendar |
| Bias ยังเป็น implicit rule | FOMO/anchoring/overconfidence ทำให้ position sizing เพี้ยน | 13 Behavioral Journal | pre-mortem, decision journal, emotional clearance |

---

## Why These Agents Matter

### 09 — Research Integrity Agent

**เหตุผลที่เพิ่ม:** ระบบวิเคราะห์ที่ดีต้องรู้ว่าข้อมูลของตัวเองน่าเชื่อถือแค่ไหน ไม่ใช่แค่สรุปได้สวย

**มืออาชีพใช้สิ่งนี้อย่างไร:** Investment committee มักมีชั้นตรวจ source, assumption และ data freshness ก่อนตัดสินใจลงเงินจริง

**ผลลัพธ์ที่คาดหวัง:** ลด hallucination, ลด unsupported precision, บังคับใช้ URL+date, จำกัด conviction ถ้าหลักฐานอ่อน

### 10 — Portfolio Construction Agent

**เหตุผลที่เพิ่ม:** พอร์ตจริงตอนนี้มี RKLB 38.51%, NVDA 22.09%, Cash ~0% ดังนั้นคำถามสำคัญไม่ใช่แค่หุ้นไหนดี แต่คือ "พอร์ตควรรับความเสี่ยงเพิ่มตรงไหน"

**มืออาชีพใช้สิ่งนี้อย่างไร:** Fund manager แยก stock selection ออกจาก portfolio construction เพราะ alpha ที่ดีอาจถูกทำลายโดย sizing ที่ผิด

**ผลลัพธ์ที่คาดหวัง:** เห็น hidden concentration, factor exposure, cash discipline และ rebalance policy ชัดขึ้น

### 11 — Tax/FX/Execution Agent

**เหตุผลที่เพิ่ม:** นักลงทุนไทยถือหุ้น US ต้องคิดเป็น USD และ THB พร้อมกัน และ execution ที่ผิดทำให้ expected return จริงลดลง

**มืออาชีพใช้สิ่งนี้อย่างไร:** Trading desk / execution desk แปลง investment decision เป็น order strategy ที่คุม slippage และ liquidity

**ผลลัพธ์ที่คาดหวัง:** มี limit zone, staged buy/trim, FX note, tax awareness และ order discipline ทุกครั้ง

### 12 — Thesis Monitoring Agent

**เหตุผลที่เพิ่ม:** การลงทุน 30 ปีต้องมีระบบเฝ้าดู thesis ไม่ใช่แค่เขียนรายงานแล้วจบ

**มืออาชีพใช้สิ่งนี้อย่างไร:** Analyst ทุกคนมี coverage calendar, KPI dashboard, earnings checklist และ thesis breaker

**ผลลัพธ์ที่คาดหวัง:** รู้ว่าหุ้น On Track / Watch / Broken / VETO และรู้วันที่ต้อง review ถัดไป

### 13 — Behavioral Journal Agent

**เหตุผลที่เพิ่ม:** จุดอ่อนใหญ่ของนักลงทุนเก่งคืออารมณ์ที่ปลอมตัวเป็นเหตุผล เช่น FOMO ตอนหุ้นวิ่ง หรือไม่ยอมขายเพราะขาดทุน

**มืออาชีพใช้สิ่งนี้อย่างไร:** นักลงทุนระดับสูงใช้ pre-mortem, decision journal และ post-mortem เพื่อแยก skill ออกจาก luck

**ผลลัพธ์ที่คาดหวัง:** ทุก trade สำคัญมีเหตุผลก่อนทำ มี pre-mortem และมี checkpoint กลับมาทบทวน decision quality

---

## New Professional Standard

หลังปรับระบบแล้ว รายงานที่ดีต้องตอบครบ:

| คำถาม | Agent หลัก |
|---|---|
| ข้อมูลเชื่อถือได้ไหม? | 09 |
| ธุรกิจดีและถูกพอไหม? | 02 + 06 |
| มี risk ที่ฆ่า thesis ได้ไหม? | 04 + 08 |
| เหมาะกับพอร์ตตอนนี้ไหม? | 10 |
| ซื้อ/ขายอย่างไรในโลกจริง? | 11 |
| หลังซื้อจะติดตามอะไร? | 12 |
| เรากำลังโดน bias หลอกไหม? | 13 |

---

## Recommended Use

- **Full stock analysis:** ใช้ Master 13-Agent flow
- **หุ้นในพอร์ตที่ overweight:** เรียก Agent 10 และ 13 ทุกครั้ง
- **หุ้น speculative/pre-profit:** เพิ่มความเข้มของ Agent 04, 08, 09, 12
- **ก่อนซื้อจริง:** Agent 11 + 13 ต้องผ่าน
- **หลัง earnings:** Agent 12 ทำ monitoring update และส่งกลับ Agent 02 ถ้า KPI เปลี่ยนแรง

---

## Bottom Line

ระบบใหม่ไม่ได้เพิ่ม agent เพื่อให้ดูใหญ่ขึ้น แต่เพิ่มเพื่อปิดช่องว่างจาก "นักวิเคราะห์หุ้นรายตัว" ไปเป็น "คณะกรรมการลงทุนจำลอง" ที่มีทั้ง analyst, risk manager, evidence auditor, portfolio architect, execution desk และ behavioral coach อยู่ในระบบเดียวกัน
