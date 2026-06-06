# =============================================================================
# Task 3: Weekly DCA Shopping Assistant
# Schedule: Every Friday at 22:00 (Thai time)
# Purpose: Generate weekly DCA shopping list with RSI + Swarm analysis
# =============================================================================

$PythonExe  = "C:\Users\LENOVO\AppData\Local\Programs\Python\Python314\python.exe"
# Resolve path dynamically using PSScriptRoot to prevent Unicode corruption of Chinese characters (文档)
$WorkDir    = Split-Path $PSScriptRoot -Parent
$LogDir     = Join-Path $WorkDir "scheduler\logs"
$OutputDir  = Join-Path $WorkDir "output"
$Today      = (Get-Date -Format "yyyy-MM-dd")
$LogFile    = Join-Path $LogDir "weekly_dca_$Today.log"

function Write-Log {
    param([string]$Msg)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $Msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Write-Log "=============================================="
Write-Log "  INVESTMENT OS — Weekly DCA Shopping Assistant"
Write-Log "  Week Ending: $Today"
Write-Log "=============================================="
Set-Location $WorkDir

# ── Step 1: Fetch RSI snapshot for all holdings ──────────────────────────────
Write-Log "[1/3] Fetching RSI signals for all holdings..."
$Holdings = @("RKLB", "NVDA", "GOOGL", "UNH", "AMZN", "NVO", "SOFI", "PLTR")
$RsiData = @{}

foreach ($ticker in $Holdings) {
    try {
        $rsiOut = & $PythonExe "tools\twelvedata_bridge.py" "indicator" $ticker "--type" "RSI" 2>&1 | Out-String
        if ($rsiOut -match '"rsi":\s*"?([\d.]+)"?') {
            $rsi = [float]$Matches[1]
            $RsiData[$ticker] = $rsi
            $signal = if ($rsi -lt 30) { "🟢 OVERSOLD" } elseif ($rsi -gt 70) { "🔴 OVERBOUGHT" } else { "🟡 NEUTRAL" }
            Write-Log "      $ticker RSI: $rsi — $signal"
        } else {
            Write-Log "      [WARN] Could not get RSI for $ticker"
        }
    } catch {
        Write-Log "      [WARN] RSI fetch failed for $ticker: $_"
    }
}

# ── Step 2: Run full Swarm DCA Assessment ───────────────────────────────────
Write-Log "[2/3] Launching Weekly DCA Swarm Analysis..."
$OversoldTickers = ($RsiData.GetEnumerator() | Where-Object { $_.Value -lt 40 } | Select-Object -ExpandProperty Key) -join " "
$AllTickers = $Holdings -join " "
$goal = "Weekly DCA assessment for the weekend: analyze $AllTickers — identify top 3 DCA priority picks with entry zones, position sizing based on 500 USD budget, and 1-year price targets"

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
    
    Write-Log "      [OK] Weekly DCA Swarm report generated."
} catch {
    Write-Log "      [ERROR] Swarm failed: $_"
}

# ── Step 3: Log completion ───────────────────────────────────────────────────
Write-Log "[3/3] Weekly DCA Shopping Assistant complete."
Write-Log "      Check output/ folder for this week's DCA Shopping List 📋"
Write-Log "      Have a great weekend! ☕"
Write-Log "=============================================="
