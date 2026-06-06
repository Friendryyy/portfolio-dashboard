# =============================================================================
# Task 2: Sentiment Crisis Hunter
# Schedule: Monday-Friday at 12:00 (Thai time)
# Purpose: Scan Fear & Greed + check for portfolio drop > 5% from key levels
# =============================================================================

# Resolve path dynamically using PSScriptRoot to prevent Unicode corruption of Chinese characters
$WorkDir = Split-Path $PSScriptRoot -Parent
Set-Location $WorkDir
$PythonExe = "python"
& $PythonExe tools/sentiment_hunter_runner.py
