#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cloud Investment News Bot (LINE Messenger + Gemini AI)
Designed to run standalone or on GitHub Actions without requiring local PC on.
"""

import sys
import os
import argparse
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output in Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def send_line_message(text: str):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("[Error] Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID")
        return False
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    # LINE text limit per message is 5000 chars. Split if needed.
    chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
    messages = [{"type": "text", "text": chunk} for chunk in chunks[:5]]
    
    payload = {
        "to": LINE_USER_ID,
        "messages": messages
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            print("[Success] Pushed message to LINE successfully!")
            return True
        else:
            print(f"[Error] Failed to send LINE message: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"[Error] Exception sending to LINE: {e}")
        return False

def query_gemini(prompt: str) -> str:
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY is not configured."
    
    # Model fallback hierarchy
    candidate_models = [
        "gemini-3.5-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
    
    system_prompt = (
        "คุณคือ Chief Investment Officer (Agent 00) ของพอร์ตโฟลิโอ DCA ระยะยาว 30 ปี มุ่งสู่เป้าหมาย 100 ล้านบาท\n"
        "บุคลิก: มืออาชีพ, คมชัด, มีวินัย Stoic, โฟกัสพื้นฐานและ Moat ทางธุรกิจ\n"
        "รูปแบบการตอบ: ภาษาไทยวิเคราะห์การเงินระดับสูง ใช้ศัพท์เทคนิคภาษาอังกฤษกำกับ ฟอร์แมตด้วย Emoji และ Bullet Points ชัดเจน อ่านง่ายบนหน้าจอมือถือ LINE\n"
        "โครงสร้างข้อความบังคับ:\n"
        "1. 🚨 [หัวข้ออีเวนต์ / หัวข้อข่าว]\n"
        "2. 🔍 สรุปประเด็นสำคัญ (3-4 bullets สั้นกระชับได้เนื้อหา)\n"
        "3. 🎯 ผลกระทบต่อพอร์ตโฟลิโอ & คำแนะนำ DCA (เช่น ลำดับคิว DCA, จุดรับ Limit, เพดานความเสี่ยง)\n"
        "4. 📅 Catalyst ถัดไปที่ต้องจับตา\n"
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nโจทย์ที่ต้องสรุป:\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }
    headers = {"Content-Type": "application/json"}
    
    last_error = ""
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=25)
            if res.status_code == 200:
                data = res.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                print(f"[Gemini] Successfully generated using model: {model_name}")
                return text
            else:
                last_error = f"{model_name}: {res.status_code} - {res.text}"
                print(f"[Gemini Warn] {model_name} failed ({res.status_code}), trying next fallback...")
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            print(f"[Gemini Warn] {model_name} error: {e}, trying next fallback...")
            
    return f"Gemini API All Models Failed. Last Error: {last_error}"

def run_event_brief(event_type: str):
    print(f"[Running] Generating brief for event: {event_type}")
    
    prompts = {
        "test": (
            "ช่วยแนะนำตัวและทดสอบระบบ Investment Alert ประจำพอร์ตโฟลิโอ DCA 30 ปี ให้ผู้ใช้ทราบว่า "
            "ขณะนี้ระบบคลาวด์อัตโนมัติ (Gemini AI + LINE Bot) เชื่อมต่อสมบูรณ์ 100% แล้ว พร้อมระบุสถานะพอร์ตคร่าวๆ "
            "(NAV $8,612 USD / Cash 12.02% ปลดล็อก Buy Lock พร้อมเข้าซื้อ NVO, UNH, SOFI ตามลำดับ)"
        ),
        "sofi": (
            "สรุปงานสัมมนา Goldman Sachs Communacopia Conference: ถ้อยแถลงสำคัญของ Anthony Noto (CEO SoFi) "
            "โดยเน้นไปที่: การเติบโตของ Tech Platform (Galileo/Technisys), การขยายตัวของ Loan Origination, "
            "การรับมือช่วงดอกเบี้ยขาลง และกลยุทธ์ของพอร์ตโฟลิโอเราในการสะสมคิว 3 ($119 DCA)"
        ),
        "oracle": (
            "สรุปงบการเงินไตรมาส 1 FY2027 ของ Oracle ($ORCL) หลังปิดตลาด: ตรวจสอบยอด AI Cloud Infrastructure Revenue, "
            "RPO (Remaining Performance Obligations) Backlog ที่เติบโตอย่างร้อนแรง, และการจัดสรรงบ CapEx เพื่อซื้อชิปประมวลผล "
            "พร้อมวิเคราะห์ผลบวกทางตรงต่อ NVIDIA ($NVDA) และ TSMC ($TSM) ในพอร์ตโฟลิโอ"
        ),
        "cpi": (
            "สรุปรายงานตัวเลขเงินเฟ้อสหรัฐฯ U.S. August 2026 CPI Release: วิเคราะห์ตัวเลข Headline CPI และ Core CPI (MoM/YoY) "
            "เทียบกับ Consensus ของตลาด ผลกระทบต่อ US 10-Yr Treasury Yield, การคาดการณ์มติการประชุม Fed FOMC วันที่ 16 ก.ย. "
            "และผลกระทบต่อสินทรัพย์เสี่ยง (Tech Equities & Bitcoin)"
        ),
        "daily": (
            "สรุปภาพรวมตลาดประจำวัน (Daily Market Wrap) และความพร้อมของพอร์ตโฟลิโอ: ตรวจสอบสถานะดัชนีหลัก, ราคาน้ำมัน WTI, "
            "Bitcoin และทบทวนความพร้อมของเงินสดสำรอง 12.02% กับคิว DCA (NVO, UNH, SOFI) และคำสั่ง GTC Limit ของ TSM ($405-$415)"
        )
    }
    
    prompt = prompts.get(event_type.lower(), prompts["daily"])
    analysis_text = query_gemini(prompt)
    print("\n--- Generated Analysis ---")
    try:
        print(analysis_text)
    except Exception:
        print(analysis_text.encode('utf-8', errors='ignore').decode('utf-8'))
    print("--------------------------\n")
    
    send_line_message(analysis_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloud Investment News Bot")
    parser.add_argument("--event", type=str, default="test", choices=["test", "sofi", "oracle", "cpi", "daily"], help="Event type to analyze")
    args = parser.parse_args()
    
    run_event_brief(args.event)
