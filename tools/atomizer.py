#!/usr/bin/env python3
"""
atomizer.py — Knowledge Atomization Engine
Segments massive texts, transcripts, or PDF documents into highly-focused 2-3 sentence "Atoms"
supporting both heuristic NLP parsing and direct Gemini API integration.

Usage:
    python tools/atomizer.py --file scratch/McfYY3vktg0_transcript.txt --ticker SYSTEM --output scratch/atoms.md
"""

import os
import sys
import re
import json
import argparse
import hashlib
from datetime import datetime

# Ensure UTF-8 Console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def calculate_hash(text: str) -> str:
    """Generate a stable 6-character hex hash of the text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:6]

def heuristic_atomize(text: str, ticker: str, source_url: str = "https://youtube.com") -> list[dict]:
    """
    Slices raw text into logical sentence-level chunks, searches for key triggers,
    and constructs clean 2-3 sentence Atoms with relevant tags.
    """
    # Clean text and split into sentences
    cleaned = re.sub(r'\s+', ' ', text).strip()
    # Split by standard Thai ending spaces or English periods/question marks
    sentences = re.split(r'(?<=[.!?])\s+|\s{2,}', cleaned)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if len(sentences) <= 3:
        # Fallback for contiguous Thai transcripts with single spaces
        words = [w.strip() for w in cleaned.split(" ") if w.strip()]
        sentences = []
        # Group every 30-40 words into a readable phrase
        for i in range(0, len(words), 35):
            phrase = " ".join(words[i:i+35]).strip()
            if len(phrase) > 15:
                sentences.append(phrase)

    atoms = []
    chunk_size = 2  # Group every 2-3 sentences into an Atom
    
    for i in range(0, len(sentences), chunk_size):
        group = sentences[i:i+chunk_size]
        atom_content = " ".join(group).strip()
        if len(atom_content) < 40:
            continue
            
        # Classify tags based on keywords
        tag = "#macro-catalyst"  # Default
        lower_content = atom_content.lower()
        
        # Financial metric triggers
        if any(w in lower_content for w in ["fcf", "revenue", "capex", "sbc", "cfo", "กำไร", "ขาดทุน", "รายได้", "งบการเงิน"]):
            tag = "#financial-metric"
        # Thesis threat & bear triggers
        elif any(w in lower_content for w in ["risk", "threat", "competitor", "downside", "ล้มละลาย", "คู่แข่ง", "ความเสี่ยง", "หั่นราคา"]):
            tag = "#thesis-threat"
        # Bull case & strengthen triggers
        elif any(w in lower_content for w in ["moat", "growth", "buy", "dca", "สะสม", "ได้ประโยชน์", "แข็งแกร่ง", "ผู้นำ"]):
            tag = "#thesis-strengthen"
        elif any(w in lower_content for w in ["bear", "short", "panic", "ขาย", "ฟองสบู่"]):
            tag = "#bear-case"
            
        date_str = datetime.now().strftime("%Y%m%d")
        atom_id = f"ATM_{date_str}_{ticker.upper()}_{calculate_hash(atom_content)}"
        
        atoms.append({
            "id": atom_id,
            "source": f"{ticker} Research / Source",
            "url": source_url,
            "tag": tag,
            "content": atom_content
        })
        
    return atoms

def gemini_atomize(text: str, ticker: str, source_url: str, api_key: str) -> list[dict]:
    """Uses Google's generative AI client to cleanly extract exact, high-signal Atoms."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        prompt = f"""
        คุณคือ Subagent Indy ผู้เชี่ยวชาญด้าน Knowledge Atomization
        หน้าที่ของคุณคืออ่านข้อความนี้และสกัด "Atoms" (ความรู้อะตอมเดี่ยว) ขนาดเล็กยาวไม่เกิน 2-3 ประโยคต่อชิ้น 
        โดยตัด Noise และข้อความเกริ่นนำทิ้งทั้งหมด เน้นเฉพาะข้อเท็จจริงทางการเงิน (Financial Facts), สมมติฐาน (Thesis), ความเสี่ยง (Risks), และคู่แข่ง ของหุ้น {ticker}

        ข้อกำหนดผลลัพธ์:
        ตอบกลับในรูปแบบ JSON Array เท่านั้น ห้ามเขียนเกริ่นนำหรืออธิบายเพิ่มเติมใดๆ นอกเหนือจาก JSON
        ห้ามขัดกฎความกระชับ 2-3 ประโยคเด็ดขาด

        รูปแบบ JSON Schema:
        [
          {{
            "tag": "#thesis-strengthen" (เลือกจาก: #thesis-strengthen, #thesis-threat, #financial-metric, #bear-case, #macro-catalyst),
            "content": "เนื้อหาภาษาไทยสั้นๆ 2-3 ประโยค ไม่มีน้ำ"
          }}
        ]

        เนื้อหาดิบที่ต้องอ่าน:
        {text[:12000]}
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Clean JSON block
        clean_json = response.text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        raw_atoms = json.loads(clean_json)
        atoms = []
        date_str = datetime.now().strftime("%Y%m%d")
        
        for index, item in enumerate(raw_atoms):
            content = item.get("content", "").strip()
            if not content:
                continue
            tag = item.get("tag", "#macro-catalyst")
            atom_id = f"ATM_{date_str}_{ticker.upper()}_{calculate_hash(content)}"
            atoms.append({
                "id": atom_id,
                "source": f"{ticker} Research / Source",
                "url": source_url,
                "tag": tag,
                "content": content
            })
            
        return atoms
    except Exception as e:
        print(f"[!] Gemini API atomization failed: {e}. Falling back to NLP heuristics...", file=sys.stderr)
        return heuristic_atomize(text, ticker, source_url)

def main():
    parser = argparse.ArgumentParser(description="Knowledge Atomization Engine (Subagent Indy)")
    parser.add_argument("--file", required=True, help="Path to raw text or transcript file")
    parser.add_argument("--ticker", required=True, help="Stock ticker context, e.g. RKLB or SYSTEM")
    parser.add_argument("--url", default="https://youtube.com", help="Source URL reference")
    parser.add_argument("--output", required=True, help="Path to write distilled markdown atoms")
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"[-] Error: File not found -> {args.file}")
        sys.exit(1)
        
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            text_content = f.read()
    except Exception as e:
        print(f"[-] Error reading file: {e}")
        sys.exit(1)
        
    print(f"[*] Subagent Indy: Processing {args.file} ({len(text_content)} characters)...")
    
    # Check for API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("[+] API Key detected! Running Dynamic AI Atomizer via Gemini API...")
        atoms = gemini_atomize(text_content, args.ticker, args.url, api_key)
    else:
        print("[*] No API Key found. Running Advanced Heuristics-based sentence slice...")
        atoms = heuristic_atomize(text_content, args.ticker, args.url)
        
    # Write distilled MD
    try:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as out:
            out.write(f"### 🗃️ Distilled Atoms List — {args.ticker.upper()}\n\n")
            out.write(f"> **Source:** [{args.ticker} video/document]({args.url}) | **Distilled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for a in atoms:
                out.write(f"- **ID:** {a['id']}\n")
                out.write(f"  - **Source:** [{a['source']}]({a['url']})\n")
                out.write(f"  - **Tag:** {a['tag']}\n")
                out.write(f"  - **Content:** {a['content']}\n\n")
                
        print(f"[+] Distillation Successful! {len(atoms)} atoms saved to -> {args.output}")
    except Exception as e:
        print(f"[-] Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
