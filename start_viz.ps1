$cmd = "powershell -ExecutionPolicy Bypass -File C:\dorina-llm\run_viz.ps1"
$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd }
Write-Host "Viz PID: $($result.ProcessId) - ReturnValue: $($result.ReturnValue)"