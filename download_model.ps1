$ErrorActionPreference = "Continue"
Set-Location C:\dorina-llm
$log = "C:\dorina-llm\model_download.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File $log -Append -Encoding utf8 }
$env:HF_HUB_DISABLE_PROGRESS_BARS = "1"
Log "=== MODEL INDIRME BASLADI (progress barsiz) ==="
& C:\dorina-llm\.venv\Scripts\hf.exe download Qwen/Qwen2.5-1.5B-Instruct --local-dir C:\dorina-llm\base_model *>&1 | ForEach-Object { Log $_ }
Log "model exit: $LASTEXITCODE"
Log "=== BITTI ==="
