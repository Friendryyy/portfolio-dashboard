#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cloud Investment News Bot (LINE Messenger + Gemini AI)
Supports familiar investment keywords:
- portfolio-news-update
- portfolio-analysis
- dca-queue
- market-pulse
- macro-geopolitical
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
        "บุคลิก: มืออาชีพ, คมชัด, มีวินัย Stoic ปราศจากอารมณ์ร่วม, มองที่ปัจจัยพื้นฐาน (Fundamentals) และ Moat ทางธุรกิจ\n"
        "สินทรัพย์ในพอร์ต: NVDA (20% cap), TSM, RKLB (House Money), GOOGL, AMZN, NVO, UNH, SOFI, BTC, SpaceX ($SPCX $300 cash reserve)\n"
        "สถานะปัจจุบัน: NAV ~$8,612 USD, Cash Cushion 12.02% (ปลดล็อก Buy Lock พร้อมซื้อ)\n"
        "รูปแบบการตอบ: ภาษาไทยวิเคราะห์การเงินระดับสูง ใช้ศัพท์เทคนิคภาษาอังกฤษกำกับ ฟอร์แมตด้วย Emoji และ Bullet Points ชัดเจน อ่านง่ายบนหน้าจอมือถือ LINE\n"
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nโจทย์ที่ต้องวิเคราะห์และสรุป:\n{prompt}"}
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

def run_investment_command(command: str):
    # Normalize command keyword
    cmd = command.lower().replace("_", "-").replace(" ", "-").strip()
    if cmd.startswith("/"):
        cmd = cmd[1:]
        
    print(f"[Running Command] {cmd}")
    
    prompts = {
        "portfolio-news-update": (
            "รันคำสั่ง /portfolio-news-update:\n"
            "สรุปเจาะลึกข่าวสารและ Strategic Deltas ล่าสุดของ 10 สินทรัพย์ในพอร์ต (NVDA, TSM, RKLB, GOOGL, AMZN, NVO, UNH, SOFI, BTC, SPCX)\n"
            "คัดเฉพาะ 3-5 ข่าวสำคัญระดับ Game-Changer ที่กระทบต่อมูลค่าพื้นฐาน (เช่น ยา Amycretin ของ NVO, งาน Goldman Sachs ของ SOFI, AI Backlog ของ Big Tech, ความคืบหน้า Neutron ของ RKLB)\n"
            "พร้อมระบุ 'วิเคราะห์ผลกระทบเชิงกลยุทธ์ & มูลค่าหุ้น' และข้อสรุปว่าส่งผลต่อแผน DCA ประจำสัปดาห์นี้อย่างไร"
        ),
        "portfolio-analysis": (
            "รันคำสั่ง /portfolio-analysis:\n"
            "ตรวจสุขภาพพอร์ตโฟลิโอภาพรวม (Portfolio Health Check) สำหรับเป้าหมาย 30 ปี 100 ล้านบาท:\n"
            "1. สภาพคล่อง & สัดส่วนเงินสด (Cash Cushion 12.02% ปลดล็อก Buy Lock)\n"
            "2. การควบคุมเพดานความเสี่ยง (NVDA ติดเพดาน 20% Hard Sizing Cap ห้ามซื้อเพิ่ม, RKLB ถือรันเทรนด์แบบ House Money)\n"
            "3. ผลตอบแทน True Return (+89.68%) และ NAV ปัจจุบัน (~$8,612 USD)\n"
            "4. แผนปฏิบัติการสัปดาห์นี้ (Action Items 🔴/🟡/🟢)"
        ),
        "dca-queue": (
            "รันคำสั่ง DCA Queue & Capital Allocation Review:\n"
            "ประเมินลำดับคิวการเข้าซื้อสะสมหุ้นในพอร์ตโฟลิโอตามวินัยการเงิน:\n"
            "• คิว 1 (Top Priority): NVO (~$100 DCA) เหตุผลเชิงคุณค่าและ Moat ยาลดน้ำหนัก\n"
            "• คิว 2: UNH (~$195 DCA) เหตุผลการปลดล็อกความเสี่ยงค่าเงินและการฟื้นตัวของ Cash Flow\n"
            "• คิว 3: SOFI (~$119 DCA) เหตุผลการขยาย Tech Platform Galileo & สัมมนา Goldman Sachs\n"
            "• โซนดักซื้อ GTC Limit: TSM ($405-$415)\n"
            "• เงินสดล็อกสำรอง: SpaceX ($SPCX) $300 ห้ามแตะต้องเพื่อรอ Private Entry ($80-$90)\n"
            "สรุปแผนการจัดสรรเงินแบบคมชัด Stoic และระเบียบวินัยเหล็ก"
        ),
        "market-pulse": (
            "รันคำสั่ง Market Pulse & Pre-Market Briefing:\n"
            "สรุปชีพจรตลาดด่วนก่อนเปิดทำการ:\n"
            "1. ทิศทาง US Stock Futures และดัชนีหลัก (S&P 500, Nasdaq)\n"
            "2. ราคาน้ำมัน WTI และความเสี่ยงภูมิรัฐศาสตร์\n"
            "3. ความเคลื่อนไหวของ Bitcoin ($BTC) ในกรอบ $79k-$81k\n"
            "4. ปฏิทิน Catalyst สำคัญที่ตลาดจับตาในสัปดาห์นี้ (SoFi Keynote, Oracle Earnings, U.S. CPI Inflation)\n"
            "5. สรุปความพร้อมของนักลงทุน: จุดสังเกตและกลยุทธ์ตั้งรับวันนี้"
        ),
        "macro-geopolitical": (
            "รันคำสั่ง Macro & Geopolitical Risk Assessment:\n"
            "วิเคราะห์สถานการณ์ความตึงเครียดในตะวันออกกลาง (ช่องแคบฮอร์มุซ) และผลกระทบต่อราคาน้ำมันดิบ WTI แถว $90/บาร์เรล\n"
            "ผลกระทบต่อเงินเฟ้อสหรัฐฯ (CPI) และแนวโน้มดอกเบี้ยของ Fed FOMC ในการประชุม 16 ก.ย.\n"
            "พร้อมวิเคราะห์ว่าพอร์ตของเรา (ซึ่งเน้น Secular Growth & Health Care) มีภูมิคุ้มกันอย่างไร และจุดใดที่เป็นความเสี่ยงเชิงระบบ"
        )
    }
    
    prompt = prompts.get(cmd, prompts["portfolio-news-update"])
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
    parser.add_argument(
        "--command", 
        type=str, 
        default="portfolio-news-update", 
        choices=["portfolio-news-update", "portfolio-analysis", "dca-queue", "market-pulse", "macro-geopolitical"], 
        help="Investment command keyword to execute"
    )
    args = parser.parse_args()
    
    run_investment_command(args.command)
