# setup_notebooklm.ps1
# ติดตั้ง notebooklm-py และทำ authentication สำหรับ Windows
# รัน: powershell -ExecutionPolicy Bypass -File tools\setup_notebooklm.ps1

Write-Host "=== NotebookLM Bridge Setup ===" -ForegroundColor Cyan
Write-Host ""

# 1. ตรวจสอบ Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: $pythonVersion" -ForegroundColor Green

# 2. ติดตั้ง notebooklm-py
Write-Host ""
Write-Host "[2/4] Installing notebooklm-py..." -ForegroundColor Yellow
pip install "notebooklm-py[browser]" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Try: pip install --upgrade pip first" -ForegroundColor Red
    exit 1
}
Write-Host "  notebooklm-py installed OK" -ForegroundColor Green

# 3. ติดตั้ง Playwright + Chromium
Write-Host ""
Write-Host "[3/4] Installing Playwright Chromium browser..." -ForegroundColor Yellow
Write-Host "  (This downloads ~150MB, may take a minute)" -ForegroundColor Gray
playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: playwright install failed." -ForegroundColor Red
    exit 1
}
Write-Host "  Chromium installed OK" -ForegroundColor Green

# 4. Login to NotebookLM
Write-Host ""
Write-Host "[4/4] Authenticating with Google NotebookLM..." -ForegroundColor Yellow
Write-Host "  A browser window will open. Log in with your Google account." -ForegroundColor Gray
Write-Host "  After login, close the browser and return here." -ForegroundColor Gray
Write-Host ""
notebooklm login
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Login may have failed. Try running 'notebooklm login' manually." -ForegroundColor Yellow
} else {
    Write-Host "  Authentication saved OK" -ForegroundColor Green
}

# ทดสอบ
Write-Host ""
Write-Host "=== Testing bridge ===" -ForegroundColor Cyan
python tools\notebooklm_bridge.py list
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! NotebookLM bridge is ready." -ForegroundColor Green
    Write-Host "Usage examples:" -ForegroundColor Cyan
    Write-Host "  python tools\notebooklm_bridge.py list"
    Write-Host "  python tools\notebooklm_bridge.py find `"ASTS`""
    Write-Host "  python tools\notebooklm_bridge.py create `"Stock Analysis: NVDA`""
    Write-Host "  python tools\notebooklm_bridge.py query <id> `"What is the moat?`""
    Write-Host "  python tools\notebooklm_bridge.py add-url <id> <url>"
    Write-Host "  python tools\notebooklm_bridge.py add-report <id> output\2026-05-07_ASTS_analysis.md"
} else {
    Write-Host ""
    Write-Host "Bridge test failed. Check errors above." -ForegroundColor Red
    Write-Host "If auth is the issue, run: notebooklm login" -ForegroundColor Yellow
}
