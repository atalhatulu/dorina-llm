$ErrorActionPreference = "Continue"
Set-Location C:\dorina-llm
$log = "C:\dorina-llm\train.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File $log -Append -Encoding utf8 }
Log "=== EĞİTİM BAŞLADI ==="
& C:\dorina-llm\.venv\Scripts\python.exe C:\dorina-llm\train_laptop.py *>&1 | ForEach-Object { Log $_ }
Log "train exit: $LASTEXITCODE"
Log "=== EĞİTİM BİTTİ ==="
