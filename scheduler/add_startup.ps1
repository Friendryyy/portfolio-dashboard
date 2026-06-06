# Script to register Investment OS Daemon to Windows Startup folder
$batPath = "c:\Users\LENOVO\OneDrive\文档\Second-Brain\Investment\scheduler\start_daemon.bat"
$startupPath = [Environment]::GetFolderPath("Startup")
$lnkPath = Join-Path $startupPath "InvestmentOS_Daemon.lnk"

Write-Host "Creating startup shortcut..."
Write-Host "Target: $batPath"
Write-Host "Shortcut: $lnkPath"

try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($lnkPath)
    $shortcut.TargetPath = $batPath
    $shortcut.WorkingDirectory = "c:\Users\LENOVO\OneDrive\文档\Second-Brain\Investment"
    $shortcut.WindowStyle = 7 # Minimized
    $shortcut.Save()
    Write-Host "Successfully registered in Startup! Daemon will auto-start next time you log in." -ForegroundColor Green
} catch {
    Write-Error "Failed to create startup shortcut: $_"
}
