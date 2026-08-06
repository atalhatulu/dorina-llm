$out = powercfg /query SCHEME_CURRENT SUB_BUTTONS LIDACTION 2>&1
$out | Out-String | Write-Host
Write-Host "=== AYAR DEGISTIRILIYOR: kapak kapatma = hicbir sey yapma (AC) ==="
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setactive SCHEME_CURRENT
Write-Host "=== YENI DURUM ==="
$out2 = powercfg /query SCHEME_CURRENT SUB_BUTTONS LIDACTION 2>&1
$out2 | Out-String | Write-Host
