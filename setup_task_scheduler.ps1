# 註冊「台股市場廣度儀表板」每日自動更新工作排程
# 用法：以一般使用者身分在 PowerShell 執行： .\setup_task_scheduler.ps1

$TaskName    = "TW-MarketBreadthDashboard-DailyUpdate"
$PythonExe   = "C:\Users\George\AppData\Local\Programs\Python\Python311\python.exe"
$ProjectDir  = $PSScriptRoot
$ScriptPath  = Join-Path $ProjectDir "daily_update.py"
$LogPath     = Join-Path $ProjectDir "data\daily_update.log"

if (-not (Test-Path $PythonExe)) {
    Write-Error "找不到 Python：$PythonExe"
    exit 1
}

# cmd.exe /c 負責把 stdout/stderr 導向 log 檔（排程工作沒有主控台可看輸出）
$CmdLine = "/c `"`"$PythonExe`" `"$ScriptPath`" >> `"$LogPath`" 2>&1`""

$Action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $CmdLine -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 21:45
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings `
    -Description "每天平日 21:45（TWSE融資資料約21:00更新後）自動抓取並重算台股市場廣度儀表板" `
    -RunLevel Limited

Write-Host "已註冊排程工作：$TaskName（平日 21:45 執行）"
Write-Host "log 檔位置：$LogPath"
Write-Host "可用「工作排程器」(taskschd.msc) 圖形介面查看，或執行：Get-ScheduledTask -TaskName '$TaskName'"
