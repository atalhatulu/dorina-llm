$cmd = "powershell -ExecutionPolicy Bypass -File C:\dorina-llm\run_server.ps1"
$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
Write-Host "Server PID: $($result.ProcessId) - ReturnValue: $($result.ReturnValue)"