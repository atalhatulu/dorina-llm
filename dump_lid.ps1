$raw = powercfg /query SCHEME_CURRENT SUB_BUTTONS LIDACTION 2>&1 | Out-String
$utf8 = [System.Text.Encoding]::UTF8.GetBytes($raw)
[System.IO.File]::WriteAllBytes("C:\dorina-llm\lid_result.txt", $utf8)
Write-Host "yazildi"
