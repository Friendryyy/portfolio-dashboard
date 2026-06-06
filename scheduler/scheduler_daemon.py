#!/usr/bin/env python3
"""
Investment OS — Scheduler Daemon
รันอยู่เบื้องหลัง เช็คเวลาทุก 60 วินาที แล้วสั่งงานอัตโนมัติตามเวลาที่กำหนด
ไม่ต้องการสิทธิ์ Administrator

เริ่มใช้งาน:
    python scheduler/scheduler_daemon.py

เพิ่มใน Windows Startup (รันอัตโนมัติทุกครั้งที่เปิดคอม):
    1. กด Win+R → พิมพ์ shell:startup → Enter
    2. สร้าง Shortcut ชี้ไปที่ start_daemon.bat ในโฟลเดอร์นั้น
"""

import subprocess
import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Fix encoding on Windows — handles Chinese characters in OneDrive path (文档)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
SCHED_DIR  = Path(__file__).parent
LOG_DIR    = SCHED_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

PYTHON_EXE = sys.executable  # ใช้ Python interpreter ที่รัน daemon นี้เอง
PS_EXE     = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"daemon_{datetime.now().strftime('%Y-%m-%d')}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("InvestmentOS-Daemon")

# ── Task State Tracking (ป้องกันรัน 2 ครั้ง/วัน) ──────────────────────────
STATE_FILE = SCHED_DIR / ".daemon_state.json"

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def already_ran_today(task_name: str) -> bool:
    state = load_state()
    last_ran = state.get(task_name, "")
    today = datetime.now().strftime("%Y-%m-%d")
    return last_ran == today

def mark_ran_today(task_name: str):
    state = load_state()
    state[task_name] = datetime.now().strftime("%Y-%m-%d")
    save_state(state)

# ── Task Runner ──────────────────────────────────────────────────────────────
def run_ps1(script_name: str):
    """Run a PowerShell script from the scheduler/ directory."""
    script_path = SCHED_DIR / script_name
    if not script_path.exists():
        log.error(f"Script not found: {script_path}")
        return
    log.info(f"Launching: {script_name}")
    try:
        proc = subprocess.Popen(
            [PS_EXE, "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        # Stream output to daemon log
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                log.info(f"  [{script_name}] {line}")
        proc.wait()
        if proc.returncode == 0:
            log.info(f"[OK] {script_name} completed successfully.")
        else:
            log.warning(f"[WARN] {script_name} exited with code {proc.returncode}")
    except Exception as e:
        log.error(f"[ERROR] Failed to run {script_name}: {e}")

# ── Schedule Definitions ────────────────────────────────────────────────────
# แต่ละ task: (task_name, script_file, run_hour, run_minute, weekdays_only, friday_only)
TASKS = [
    {
        "name":         "SentimentCrisisHunter",
        "script":       "task_sentiment_hunter.ps1",
        "hour":         12,
        "minute":       0,
        "weekdays_only": True,   # จันทร์-ศุกร์เท่านั้น
        "friday_only":  False,
    },
    {
        "name":         "DailyPortfolioCMO",
        "script":       "task_daily_portfolio.ps1",
        "hour":         12,
        "minute":       0,
        "weekdays_only": False,
        "friday_only":  False,
    },
    {
        "name":         "WeeklyDCAShopping",
        "script":       "task_weekly_dca.ps1",
        "hour":         22,
        "minute":       0,
        "weekdays_only": False,
        "friday_only":  True,    # ศุกร์เท่านั้น
    },
]

# ── Main Loop ────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("  Investment OS — Scheduler Daemon STARTED")
    log.info(f"  Python: {PYTHON_EXE}")
    log.info(f"  Base Dir: {BASE_DIR}")
    log.info(f"  Tasks configured: {len(TASKS)}")
    for t in TASKS:
        weekday_info = ""
        if t["friday_only"]:
            weekday_info = " [Friday only]"
        elif t["weekdays_only"]:
            weekday_info = " [Mon-Fri only]"
        log.info(f"    • {t['name']}: {t['hour']:02d}:{t['minute']:02d}{weekday_info}")
    log.info("  Checking every 60 seconds...")
    log.info("=" * 60)

    while True:
        now = datetime.now()
        weekday = now.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun

        for task in TASKS:
            # ตรวจสอบเวลา (ยืดหยุ่น ±2 นาที เผื่อ daemon ถูก pause ชั่วคราว)
            is_correct_time = (
                now.hour == task["hour"] and
                abs(now.minute - task["minute"]) <= 2
            )
            if not is_correct_time:
                continue

            # ตรวจสอบวัน
            if task["friday_only"] and weekday != 4:  # ไม่ใช่ศุกร์
                continue
            if task["weekdays_only"] and weekday >= 5:  # เสาร์/อาทิตย์
                continue

            # ป้องกันรัน 2 ครั้งใน session เดียวกัน
            state_key = f"{task['name']}_{now.strftime('%Y-%m-%d_%H%M')}"
            if already_ran_today(state_key):
                continue

            # ✅ เงื่อนไขผ่านทั้งหมด → รัน Task
            log.info(f"⏰ TIME TRIGGER: {task['name']} → {task['script']}")
            mark_ran_today(state_key)
            run_ps1(task["script"])

        # นอนหลับ 60 วินาทีก่อนเช็ครอบใหม่
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Scheduler Daemon stopped by user (Ctrl+C).")
    except Exception as e:
        log.critical(f"Daemon crashed: {e}", exc_info=True)
