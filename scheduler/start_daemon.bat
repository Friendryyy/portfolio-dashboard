@echo off
chcp 65001 > nul
title Investment OS — Scheduler Daemon
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║   Investment OS — Scheduler Daemon           ║
echo  ║   กำลังเริ่มต้นระบบงานอัตโนมัติ...         ║
echo  ╚══════════════════════════════════════════════╝
echo.
cd /d "c:\Users\LENOVO\OneDrive\文档\Second-Brain\Investment"
python scheduler\scheduler_daemon.py
pause
