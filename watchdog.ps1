$ErrorActionPreference = "SilentlyContinue"
$log = "C:\dorina-llm\watchdog.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File $log -Append -Encoding utf8 }

while ($true) {
    # Eğitim bitmiş mi?
    $trainLog = Get-Content C:\dorina-llm\train.log -Raw -ErrorAction SilentlyContinue
    $bitti = $trainLog -match "EGITIM BITTI|EĞİTİM BİTTİ|train exit"

    if ($bitti) {
        Log "Egitim bitmis, watchdog duruyor."
        break
    }

    # python process var mi?
    $py = Get-Process python -ErrorAction SilentlyContinue
    if (-not $py) {
        Log "PYTHON PROCESS YOK! Yeniden baslatiliyor..."
        & powershell -ExecutionPolicy Bypass -File C:\dorina-llm\start_train.ps1
        Log "Yeniden baslatma komutu verildi."
    }
    Start-Sleep -Seconds 120
}
