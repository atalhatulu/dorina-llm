[Console]::OutputEncoding = [Text.Encoding]::UTF8
$lines = powercfg /query SCHEME_CURRENT SUB_BUTTONS LIDACTION
foreach ($l in $lines) {
    if ($l -match "Index") { Write-Host $l.Trim() }
}
