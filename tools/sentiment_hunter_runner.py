#!/usr/bin/env python3
import sys
import os
import urllib.request
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Base paths
TOOLS_DIR = Path(__file__).parent
WORKSPACE_DIR = TOOLS_DIR.parent
LOG_DIR = WORKSPACE_DIR / "scheduler" / "logs"
OUTPUT_DIR = WORKSPACE_DIR / "output"
LOG_DIR.mkdir(exist_ok=True)

today_str = datetime.now().strftime("%Y-%m-%d")
log_file_path = LOG_DIR / f"sentiment_hunter_{today_str}.log"

def write_log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

write_log("==============================================")
write_log("  INVESTMENT OS — Sentiment Crisis Hunter (Python)")
write_log(f"  Date: {today_str}")
write_log("==============================================")

# Step 1: Fetch CNN Fear & Greed Index
write_log("[1/3] Fetching CNN Fear & Greed Index...")
crisis_detected = False
fng_value = 50
fng_class = "Neutral (fallback)"

try:
    req = urllib.request.Request(
        "https://api.alternative.me/fng/",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
        if "data" in data and len(data["data"]) > 0:
            fng_value = int(data["data"][0]["value"])
            fng_class = data["data"][0]["value_classification"]
            write_log(f"      FNG: {fng_value} — {fng_class}")
            
            if fng_value <= 25:
                write_log(f"      [ALERT] EXTREME FEAR detected ({fng_value})! Crisis trigger activated.")
                crisis_detected = True
            elif fng_value <= 40:
                write_log(f"      [WARN] Fear zone ({fng_value}). Monitoring closely.")
            else:
                write_log(f"      [OK] Market sentiment normal ({fng_value}).")
        else:
            write_log("      [WARN] Unexpected FNG structure, using fallback.")
except Exception as e:
    write_log(f"      [WARN] FNG fetch failed: {e}. Proceeding with caution.")

# Step 2: Check price levels
write_log("[2/3] Checking price levels for holdings...")
watch_tickers = ["RKLB", "NVDA", "GOOGL", "NVO", "SOFI", "UNH", "AMZN"]

for ticker in watch_tickers:
    try:
        # Run yfinance_bridge.py
        bridge_path = TOOLS_DIR / "yfinance_bridge.py"
        cmd = [sys.executable, str(bridge_path), "price", ticker]
        res = subprocess.run(cmd, cwd=str(WORKSPACE_DIR), capture_output=True, text=True, encoding="utf-8")
        if res.returncode == 0:
            try:
                out_data = json.loads(res.stdout)
                price = out_data.get("price", 0.0)
                write_log(f"      {ticker} price: ${price:,.2f}")
            except Exception:
                # Fallback parse
                match = re.search(r'"price":\s*([\d.]+)', res.stdout)
                if match:
                    write_log(f"      {ticker} price: ${float(match.group(1)):,.2f}")
                else:
                    write_log(f"      [WARN] Could not parse price output for {ticker}")
        else:
            write_log(f"      [WARN] Bridge returned error code {res.returncode} for {ticker}")
    except Exception as e:
        write_log(f"      [WARN] Price check failed for {ticker}: {e}")

# Step 3: Action or daily sentiment summary
if crisis_detected:
    write_log("[3/3] CRISIS MODE — Launching Swarm Crisis Analysis...")
    goal = f"CRISIS ALERT FNG={fng_value} ({fng_class}): Analyze all portfolio holdings RKLB NVDA GOOGL NVO SOFI UNH AMZN, identify DCA buying zones and risk flags immediately"
    try:
        swarm_path = TOOLS_DIR / "swarm_controller.py"
        cmd = [sys.executable, str(swarm_path), "--goal", goal]
        write_log(f"      Running swarm controller: {' '.join(cmd)}")
        
        # Run and stream swarm output in real-time
        proc = subprocess.Popen(
            cmd,
            cwd=str(WORKSPACE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        for line in proc.stdout:
            line_str = line.rstrip()
            if line_str:
                write_log(f"      [Swarm] {line_str}")
        proc.wait()
        
        if proc.returncode == 0:
            write_log("      [OK] Crisis Swarm analysis completed and saved to output/")
        else:
            write_log(f"      [WARN] Swarm exited with code {proc.returncode}")
    except Exception as e:
        write_log(f"      [ERROR] Crisis Swarm failed: {e}")
else:
    write_log("[3/3] No crisis detected. Writing daily sentiment summary...")
    summary_file = OUTPUT_DIR / f"{today_str}_sentiment_daily_summary.md"
    
    summary_content = (
        f"# 📡 Daily Sentiment Check — {today_str}\n\n"
        f"**Fear & Greed Index:** {fng_value} — {fng_class}\n"
        f"**Status:** ✅ No Crisis Detected — Market within normal range\n"
        f"**Action:** Hold positions. Continue DCA plan as scheduled.\n\n"
        f"---\n"
        f"*Generated by Sentiment Crisis Hunter at {datetime.now().strftime('%H:%M')} Thai time*\n"
    )
    
    with open(summary_file, "w", encoding="utf-8") as sf:
        sf.write(summary_content)
    write_log(f"      Summary saved: {summary_file}")

write_log("==============================================")
write_log("  Sentiment Crisis Hunter — COMPLETE")
write_log("==============================================")
