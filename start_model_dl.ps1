$cmd = "powershell -ExecutionPolicy Bypass -File C:\dorina-llm\download_model.ps1"
$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
Write-Host "PID: $($result.ProcessId) - ReturnValue: $($result.ReturnValue)"
