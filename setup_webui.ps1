$ErrorActionPreference = "Continue"
Set-Location C:\dorina-llm
$log = "C:\dorina-llm\webui_setup.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File $log -Append -Encoding utf8 }
Log "=== WEBUI KURULUYOR ==="
$py = "C:\dorina-llm\.venv\Scripts\python.exe"
& $py -c "import fastapi, uvicorn" *>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Log "fastapi yok, kuruluyor..."
    & C:\Users\Talha\.local\bin\uv.exe pip install --python $py fastapi uvicorn pydantic *>&1 | ForEach-Object { Log $_ }
    Log "fastapi exit: $LASTEXITCODE"
} else {
    Log "fastapi zaten var"
}
& $py -c "import fastapi, uvicorn; print('FASTAPI', fastapi.__version__)" *>&1 | ForEach-Object { Log $_ }
Log "=== BITTI ==="