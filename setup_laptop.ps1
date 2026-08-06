$ErrorActionPreference = "Continue"
Set-Location C:\dorina-llm
$log = "C:\dorina-llm\setup.log"
$py = "C:\dorina-llm\.venv\Scripts\python.exe"

function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File $log -Append -Encoding utf8 }

Log "=== SETUP BASLADI ==="

Log "--- torch kuruluyor (cu126) ---"
uv pip install --python $py torch --index-url https://download.pytorch.org/whl/cu126 *>&1 | ForEach-Object { Log $_ }
Log "torch exit: $LASTEXITCODE"

Log "--- diger kutuphaneler ---"
uv pip install --python $py transformers datasets peft trl accelerate sentencepiece protobuf bitsandbytes huggingface_hub *>&1 | ForEach-Object { Log $_ }
Log "libs exit: $LASTEXITCODE"

Log "--- torch test ---"
& $py -c "import torch; print('TORCH', torch.__version__, 'CUDA', torch.cuda.is_available())" *>&1 | ForEach-Object { Log $_ }
Log "test exit: $LASTEXITCODE"

Log "=== SETUP BITTI ==="
