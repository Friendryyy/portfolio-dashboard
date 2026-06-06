# =============================================================================
# register_all_tasks.ps1 — Master Registration Script
# Run this ONCE as Administrator to install all 4 scheduled tasks
# Usage: Right-click → "Run with PowerShell" OR open Admin PowerShell and run:
#        .\scheduler\register_all_tasks.ps1
# =============================================================================

$WorkDir     = "c:\Users\LENOVO\OneDrive\文档\Second-Brain\Investment"
$SchedDir    = Join-Path $WorkDir "scheduler"
$PsExe       = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
$TaskPrefix  = "InvestmentOS"

function Register-InvestmentTask {
    param(
        [string]$TaskName,
        [string]$ScriptFile,
        [string]$TriggerDesc,
        [object]$Trigger,
        [string]$Description
    )
    $FullTaskName = "$TaskPrefix\$TaskName"
    $ScriptPath   = Join-Path $SchedDir $ScriptFile
    $Action = New-ScheduledTaskAction `
        -Execute $PsExe `
        -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$ScriptPath`"" `
        -WorkingDirectory $WorkDir

    $Settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -MultipleInstances IgnoreNew

    $Principal = New-ScheduledTaskPrincipal `
        -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
        -LogonType Interactive `
        -RunLevel Highest

    try {
        # Remove existing task if present (clean reinstall)
        if (Get-ScheduledTask -TaskName $TaskName -TaskPath "\$TaskPrefix\" -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $TaskName -TaskPath "\$TaskPrefix\" -Confirm:$false
            Write-Host "  [~] Removed existing task: $FullTaskName"
        }
        Register-ScheduledTask `
            -TaskName $TaskName `
            -TaskPath "\$TaskPrefix\" `
            -Action $Action `
            -Trigger $Trigger `
            -Settings $Settings `
            -Principal $Principal `
            -Description $Description | Out-Null
        Write-Host "  [OK] Registered: $FullTaskName  ($TriggerDesc)" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Failed to register $FullTaskName : $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Investment OS — Windows Task Scheduler Registration" -ForegroundColor Cyan
Write-Host "  Installing 4 automated tasks..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# ── Task 1: Daily Portfolio Machine — Every day at 12:00 ────────────────────
$trigger1 = New-ScheduledTaskTrigger -Daily -At "12:00"
Register-InvestmentTask `
    -TaskName  "DailyPortfolioCMO" `
    -ScriptFile "task_daily_portfolio.ps1" `
    -TriggerDesc "Daily at 12:00" `
    -Trigger   $trigger1 `
    -Description "Investment OS: Pull live portfolio + run Swarm full analysis. Output saved to /output/"

# ── Task 2: Sentiment Crisis Hunter — Mon-Fri at 09:00 ──────────────────────
$trigger2 = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
    -At "09:00"
Register-InvestmentTask `
    -TaskName  "SentimentCrisisHunter" `
    -ScriptFile "task_sentiment_hunter.ps1" `
    -TriggerDesc "Mon-Fri at 09:00" `
    -Trigger   $trigger2 `
    -Description "Investment OS: Scan Fear & Greed + price levels. Triggers Swarm if crisis detected."

# ── Task 3: Weekly DCA Shopping Assistant — Every Friday at 22:00 ───────────
$trigger3 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At "22:00"
Register-InvestmentTask `
    -TaskName  "WeeklyDCAShopping" `
    -ScriptFile "task_weekly_dca.ps1" `
    -TriggerDesc "Every Friday at 22:00" `
    -Trigger   $trigger3 `
    -Description "Investment OS: Weekly DCA Shopping List with RSI snapshot + Swarm DCA analysis."

# ── Task 4: CAIO Morning Briefing — Every day at 07:00 ──────────────────────
$trigger4 = New-ScheduledTaskTrigger -Daily -At "07:00"
Register-InvestmentTask `
    -TaskName  "CAIOMorningBriefing" `
    -ScriptFile "task_caio_innovation.ps1" `
    -TriggerDesc "Daily at 07:00" `
    -Trigger   $trigger4 `
    -Description "Investment OS: Morning briefing — summarizes log.md and innovation journal."

# ── Summary ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Registration Complete! Installed tasks:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Task Folder: \InvestmentOS\" -ForegroundColor Yellow
Get-ScheduledTask -TaskPath "\InvestmentOS\" -ErrorAction SilentlyContinue | ForEach-Object {
    $nextRun = ($_ | Get-ScheduledTaskInfo).NextRunTime
    Write-Host "  ✅ $($_.TaskName)" -ForegroundColor Green
    Write-Host "     Next run: $nextRun" -ForegroundColor Gray
}
Write-Host ""
Write-Host "  Open Task Scheduler (taskschd.msc) to view and manage." -ForegroundColor White
Write-Host "  Logs saved to: $SchedDir\logs\" -ForegroundColor White
Write-Host "  Output files in: $WorkDir\output\" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
