$cmd = "powershell -ExecutionPolicy Bypass -File C:\dorina-llm\watchdog.ps1"
$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
Write-Host "Watchdog PID: $($result.ProcessId) - ReturnValue: $($result.ReturnValue)"
