# =============================================================================
# Task 1: Daily Portfolio Machine
# Schedule: Every day at 12:00 (Thai time)
# Purpose: Pull live portfolio from Google Sheets + run full Swarm analysis
# =============================================================================

$PythonExe  = "C:\Users\LENOVO\AppData\Local\Programs\Python\Python314\python.exe"
# Resolve path dynamically using PSScriptRoot to prevent Unicode corruption of Chinese characters (文档)
$WorkDir    = Split-Path $PSScriptRoot -Parent
$LogDir     = Join-Path $WorkDir "scheduler\logs"
$OutputDir  = Join-Path $WorkDir "output"
$Today      = (Get-Date -Format "yyyy-MM-dd")
$LogFile    = Join-Path $LogDir "daily_portfolio_$Today.log"

function Write-Log {
    param([string]$Msg)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $Msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

# ── Startup ─────────────────────────────────────────────────────────────────
Write-Log "=============================================="
Write-Log "  INVESTMENT OS — Daily Portfolio Machine"
Write-Log "  Date: $Today"
Write-Log "=============================================="
Set-Location $WorkDir

# ── Step 1: Verify Google Sheets connection ──────────────────────────────────
Write-Log "[1/3] Verifying Google Sheets connection..."
try {
    $sheetsResult = & $PythonExe "tools\sheets_bridge.py" "summary" 2>&1
    Write-Log "      Sheets OK: $($sheetsResult | Select-String 'Total Equity' | Select-Object -First 1)"
} catch {
    Write-Log "      [WARN] Sheets check failed: $_"
}

# ── Step 2: Run Swarm full portfolio analysis ────────────────────────────────
Write-Log "[2/3] Launching Swarm Orchestrator — Full Portfolio Review..."
$goal = "Daily portfolio review: analyze all holdings RKLB NVDA GOOGL UNH AMZN NVO SOFI PLTR and give DCA recommendations"
try {
    $swarmOutput = & $PythonExe "tools\swarm_controller.py" "--goal" $goal 2>&1
    # Print to console/host instantly so daemon can stream it
    $swarmOutput | ForEach-Object { Write-Host "      $_" }
    
    # Save the entire swarm output to the log file in a single write operation to prevent OneDrive lock collision
    $timestamp = Get-Date -Format "HH:mm:ss"
    $swarmLog = $swarmOutput | ForEach-Object { "[$timestamp]       $_" }
    if ($swarmLog) {
        $swarmLog | Add-Content -Path $LogFile -Encoding UTF8
    }
    
    Write-Log "      [OK] Swarm completed."
} catch {
    Write-Log "      [ERROR] Swarm failed: $_"
}

# ── Step 3: Log completion ───────────────────────────────────────────────────
Write-Log "[3/3] Daily Portfolio Machine complete."
Write-Log "      Output files saved to: $OutputDir"
Write-Log "      Log saved to: $LogFile"
Write-Log "=============================================="
