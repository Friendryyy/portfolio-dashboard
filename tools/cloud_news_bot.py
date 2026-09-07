#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cloud Investment News Bot (LINE Messenger + Gemini AI)
Delivers full-depth, high-intelligence executive briefs to LINE without truncation.
"""

import sys
import os
import glob
import argparse
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output in Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / '.env'
load_dotenv(env_path)

LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_latest_report_context(max_chars=8000) -> str:
    """Read context from the latest portfolio news deep dive in output/"""
    output_dir = ROOT_DIR / 'output'
    files = sorted(glob.glob(str(output_dir / "*portfolio_news*.md")), reverse=True)
    if not files:
        files = sorted(glob.glob(str(output_dir / "*.md")), reverse=True)
    
    if files:
        try:
            with open(files[0], 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:max_chars]
        except Exception as e:
            print(f"[Warn] Could not read report file: {e}")
    return ""

def send_line_message(text: str):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("[Error] Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID")
        return False
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    # LINE text limit per message is 5,000 chars. Split smartly around 4,000 chars
    chunks = []
    curr = text
    while len(curr) > 4000:
        # Find newline near 4000
        split_idx = curr.rfind('\n', 0, 4000)
        if split_idx == -1 or split_idx < 2000:
            split_idx = 4000
        chunks.append(curr[:split_idx])
        curr = curr[split_idx:].strip()
    if curr:
        chunks.append(curr)
        
    print(f"[LINE] Sending {len(chunks)} message chunk(s)...")
    success = True
    for i, chunk in enumerate(chunks):
        payload = {
            "to": LINE_USER_ID,
            "messages": [{"type": "text", "text": chunk}]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                print(f"[Success] Pushed chunk {i+1}/{len(chunks)} to LINE successfully!")
            else:
                print(f"[Error] Failed chunk {i+1}: {res.status_code} - {res.text}")
                success = False
        except Exception as e:
            print(f"[Error] Exception sending chunk {i+1}: {e}")
            success = False
            
    return success

def query_gemini(prompt: str) -> str:
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY is not configured."
    
    candidate_models = [
        "gemini-3.5-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
    
    system_prompt = (
        "คุณคือ Chief Investment Officer (Agent 00) ของพอร์ตโฟลิโอ DCA ระยะยาว 30 ปี มุ่งสู่เป้าหมาย 100 ล้านบาท\n"
        "บุคลิก: มืออาชีพ, คมชัด, มีวินัย Stoic ปราศจากอารมณ์ร่วม, มองที่ปัจจัยพื้นฐาน (Fundamentals) และ Moat ทางธุรกิจ\n"
        "ข้อมูลพอร์ตปัจจุบัน: NAV ~$8,612.57 USD (฿283,525 THB), Cash Cushion 12.02% (ปลดล็อก Buy Lock 🟢), True Return +89.68%\n"
        "กฎเหล็ก: ห้ามสรุปสั้นแห้งๆ เด็ดขาด! ต้องมีเนื้อหาข่าวสารจริง ตัวเลขจริง บทวิเคราะห์ผลกระทบต่อมูลค่าหุ้น (Strategic Impact) "
        "และ Action คำแนะนำที่ชัดเจนจับต้องได้ จัดโครงสร้างด้วย Markdown และ Emoji ให้อ่านง่ายบนมือถือ LINE"
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nโจทย์ที่ต้องจัดทำรายงานเชิงลึก:\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 6000
        }
    }
    headers = {"Content-Type": "application/json"}
    
    last_error = ""
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=45)
            if res.status_code == 200:
                data = res.json()
                candidate = data['candidates'][0]
                text = candidate['content']['parts'][0]['text']
                print(f"[Gemini] Successfully generated deep brief using: {model_name} (Length: {len(text)} chars)")
                return text
            else:
                last_error = f"{model_name}: {res.status_code} - {res.text}"
                print(f"[Gemini Warn] {model_name} failed ({res.status_code}), trying next fallback...")
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            print(f"[Gemini Warn] {model_name} error: {e}, trying next fallback...")
            
    return f"Gemini API All Models Failed. Last Error: {last_error}"

def run_investment_command(command: str):
    cmd = command.lower().replace("_", "-").replace(" ", "-").strip()
    if cmd.startswith("/"):
        cmd = cmd[1:]
        
    print(f"[Running Command] {cmd}")
    context = get_latest_report_context(max_chars=6500)
    
    prompts = {
        "portfolio-news-update": f"""
จัดทำรายงานสรุป /portfolio-news-update ฉบับเต็มเจาะลึก สำหรับพอร์ต DCA 100 ล้านบาท:
1. 📈 **Executive Summary & Health Check:** รายงาน NAV ($8,612 USD), Cash Cushion (12.02%), True Return (+89.68%)
2. 🚀 **เจาะลึก 5 หุ้นที่มี Strategic Deltas สำคัญที่สุดในสัปดาห์นี้:**
   • **NVO (Novo Nordisk):** ข้อมูลและพัฒนาการยา Amycretin แซงหน้า CagriSema/Wegovy, การขยายกำลังการผลิต และผลต่อ Moat ยาลดน้ำหนัก
   • **UNH (UnitedHealth Group):** การขายธุรกิจ Amil ในบราซิล ล้างความเสี่ยงค่าเงิน FX และกระแสเงินสดฟื้นตัวพร้อมรองรับเงินปันผล
   • **SOFI (SoFi Technologies):** การเติบโตของ Tech Platform (Galileo/Technisys), การเตรียมขึ้นกล่าวงาน Goldman Sachs Communacopia และทิศทางธุรกิจในยุคดอกเบี้ยขาลง
   • **TSM (Taiwan Semiconductor):** ยอดจองผลิตชิป 2nm และ 3nm เต็ม 100% ถึงปี 2027 และการควบคุม Supply Chain ชิป AI โลก
   • **NVDA (NVIDIA):** ความคืบหน้าสถาปัตยกรรม Blackwell Ultra (B300), ตัวเลข AI Capex มหาศาลของกลุ่ม Hyperscalers
3. 🎯 **DCA Execution Matrix & Plan ประจำสัปดาห์นี้:**
   • 🥇 คิว 1: NVO (~$100 DCA)
   • 🥈 คิว 2: UNH (~$195 DCA)
   • 🥉 คิว 3: SOFI (~$119 DCA)
   • 🔹 GTC Limit โซนดักซื้อ: TSM ($405-$415)
   • 🚀 เงินสดล็อกสำรอง: SpaceX ($SPCX) $300 ห้ามแตะต้อง
   • 🛑 เพดานความเสี่ยง: NVDA (20.22% Cap) & RKLB (13.77% House Money) สั่ง HOLD
4. 📅 **Catalysts สำคัญในสัปดาห์นี้:** SoFi Keynote, Oracle Q1 Earnings, U.S. August CPI

ข้อมูลอ้างอิงล่าสุด:
{context}
""",
        "portfolio-analysis": f"""
จัดทำรายงาน /portfolio-analysis ตรวจสุขภาพพอร์ต 360 องศา:
1. 📊 **พอร์ตภาพรวม:** NAV $8,612.57 USD (~฿283,525 THB), Deployed Capital $4,540 USD, กำไรสุทธิ +$4,072 USD (+89.68%)
2. 🛡️ **การควบคุมความเสี่ยง (Risk & Concentration Audit):**
   - NVDA อยู่ที่ 20.22% (ชนเพดาน 20% Hard Cap สั่ง HOLD รันเทรนด์)
   - RKLB อยู่ที่ 13.77% (ต้นทุนฟรี 100% House Money ปล่อยรันเทรนด์ไปสู่ Neutron Launch 2026)
   - Cash Cushion 12.02% (ปลดล็อก Buy Lock 🟢 เหนือเกณฑ์ 10%)
3. 🎯 **การจัดสรรสินทรัพย์ 10 ตัว (Asset Breakdown & Verdicts):**
   แจกแจงสถานะของ NVDA, TSM, RKLB, GOOGL, AMZN, NVO, UNH, SOFI, BTC, SPCX
4. 🧭 **แผนการเดินทาง 30 ปีสู่ 100 ล้านบาท:** วินัยทางจิตวิทยาและการสะสมหุ้นแบบ Stoic

ข้อมูลอ้างอิง:
{context}
""",
        "dca-queue": f"""
จัดทำรายงานวิเคราะห์เจาะลึก 'DCA Queue & Capital Allocation Strategy':
1. 🟢 **สภาพคล่อง & อำนาจการซื้อ:** เงินสด $1,034.98 USD (12.02%) พร้อมกระจายเม็ดเงิน
2. 🥇 **ลำดับคิวการเข้าซื้อสะสมเรียงตาม Priority:**
   - คิว 1: NVO ($100 DCA) — ชี้แจง Valuation, PE, Moat และจุดคุ้มค่า
   - คิว 2: UNH ($195 DCA) — ชี้แจงกระแสเงินสด FCF และการฟื้นตัว
   - คิว 3: SOFI ($119 DCA) — ชี้แจง Growth Rate และโมเมนตัม
3. 🎯 **จุดรับ Limit และเงินสำรองพิเศษ:**
   - TSM: ตั้งรับที่ $405-$415
   - SpaceX ($SPCX): ล็อกเงินสด $300 เพื่อรอเข้าซื้อ Secondary Market
4. 📋 **สรุปตาราง Action Plan ที่ต้องทำในสัปดาห์นี้**

ข้อมูลอ้างอิง:
{context}
""",
        "market-pulse": f"""
จัดทำรายงานด่วน 'Pre-Market Pulse & Macro Radar':
1. 🌐 **ดัชนีและตลาด 24/7:** สถานะ Bitcoin ($79,500), ราคาน้ำมัน WTI ($90/bbl), US Treasury 10-Yr Yield
2. ⚠️ **ความเสี่ยงภูมิรัฐศาสตร์:** สถานการณ์ตะวันออกกลางและช่องแคบฮอร์มุซ
3. 📅 **Catalysts Roadmap ประจำสัปดาห์:**
   - 8 ก.ย.: Goldman Sachs Communacopia (Anthony Noto Keynote)
   - 10 ก.ย.: Oracle ($ORCL) Q1 FY27 Earnings
   - 11 ก.ย.: U.S. August CPI Inflation Print
4. 🛡️ **คำแนะนำทางกลยุทธ์สำหรับนักลงทุนวันนี้**

ข้อมูลอ้างอิง:
{context}
""",
        "macro-geopolitical": f"""
จัดทำรายงานวิเคราะห์ความเสี่ยงมหภาคและสงคราม 'Macro & Geopolitical Risk Assessment':
1. 💥 **วิกฤตพลังงานและช่องแคบฮอร์มุซ:** การปิดเส้นทางขนส่งน้ำมันและแรงกระแทกต่อราคาน้ำมันดิบ WTI แถว $90/บาร์เรล
2. 📈 **ผลกระทบลูกโซ่สู่เงินเฟ้อและดอกเบี้ย:** โอกาสที่เงินเฟ้อ CPI สหรัฐฯ จะพุ่งขึ้น และความท้าทายของ Fed ในการลดดอกเบี้ย 16 ก.ย.
3. 🛡️ **ภูมิคุ้มกันของพอร์ตเรา:** ทำไมหุ้นกลุ่ม AI Infrastructure (NVDA, TSM) และ Healthcare (NVO, UNH) จึงเป็นเกราะป้องกันที่ดี
4. 💡 **คำแนะนำการบริหารเงินสดและความเสี่ยง**

ข้อมูลอ้างอิง:
{context}
"""
    }
    
    prompt = prompts.get(cmd, prompts["portfolio-news-update"])
    analysis_text = query_gemini(prompt)
    
    send_line_message(analysis_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloud Investment News Bot")
    parser.add_argument(
        "--command", 
        type=str, 
        default="portfolio-news-update", 
        choices=["portfolio-news-update", "portfolio-analysis", "dca-queue", "market-pulse", "macro-geopolitical"], 
        help="Investment command keyword to execute"
    )
    args = parser.parse_args()
    
    run_investment_command(args.command)
