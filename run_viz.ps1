$ErrorActionPreference = "Continue"
Set-Location C:\dorina-llm
$log = "C:\dorina-llm\viz.log"
& C:\dorina-llm\.venv\Scripts\python.exe C:\dorina-llm\viz.py *>&1 | ForEach-Object { "$(Get-Date -Format 'HH:mm:ss') $_" | Out-File $log -Append -Encoding utf8 }