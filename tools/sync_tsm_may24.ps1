# tools/sync_tsm_may24.ps1
# Sync script for TSMC research report and sources to NotebookLM notebooks

$tsm_nb = "120452e3-54ed-496b-af74-0ebca59b2e85"
$googl_nb = "f524cf09-7a96-4944-9af6-fe52d7476b34"
$amzn_nb = "f380cc6e-a937-4bea-b00a-e62455ca8bd7"
$spcx_nb = "abe3ade8-c8f2-4764-8033-6585d061c091"
$master_nb = "d4268735-ab02-40c5-80a1-f1b9768befd9"

$sources_file = "tools/TSM_sources.txt"
$report_file = "output/2026-05-24_TSM_fundamental_AI_deep_dive.md"
$report_title = "2026 05 24 TSM advanced semiconductor foundry monopoly - Mega Report"

Write-Host "=== 🟢 STEP 1: Syncing Source URLs to Stocks ===" -ForegroundColor Green
Write-Host "Syncing URLs to TSM notebook..."
python tools/notebooklm_bridge.py add-urls-batch $tsm_nb $sources_file

Write-Host "Syncing URLs to GOOGL notebook..."
python tools/notebooklm_bridge.py add-urls-batch $googl_nb $sources_file

Write-Host "Syncing URLs to AMZN notebook..."
python tools/notebooklm_bridge.py add-urls-batch $amzn_nb $sources_file

Write-Host "Syncing URLs to SPCX notebook..."
python tools/notebooklm_bridge.py add-urls-batch $spcx_nb $sources_file


Write-Host "`n=== 🟢 STEP 2: Uploading TSM Mega-Report ===" -ForegroundColor Green
Write-Host "Uploading Report to TSM notebook..."
python tools/notebooklm_bridge.py add-text $tsm_nb --title $report_title --file $report_file

Write-Host "Uploading Report to GOOGL notebook..."
python tools/notebooklm_bridge.py add-text $googl_nb --title $report_title --file $report_file

Write-Host "Uploading Report to AMZN notebook..."
python tools/notebooklm_bridge.py add-text $amzn_nb --title $report_title --file $report_file

Write-Host "Uploading Report to SPCX notebook..."
python tools/notebooklm_bridge.py add-text $spcx_nb --title $report_title --file $report_file

Write-Host "Uploading Report to Master Hub notebook..."
python tools/notebooklm_bridge.py add-text $master_nb --title $report_title --file $report_file

Write-Host "`n=== 🎉 Sync Complete! ===" -ForegroundColor Green
