$cmd = "powershell -ExecutionPolicy Bypass -File C:\dorina-llm\run_train.ps1"
$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
Write-Host "PID: $($result.ProcessId) - ReturnValue: $($result.ReturnValue)"
