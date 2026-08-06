$a = (Get-ChildItem C:\Users\Talha\AppData\Local\uv\cache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Start-Sleep 30
$b = (Get-ChildItem C:\Users\Talha\AppData\Local\uv\cache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$fark = $b - $a
$hiz = [math]::Round($fark/30/1MB, 2)
Write-Host "Cache: $([math]::Round($a/1MB,1)) MB -> $([math]::Round($b/1MB,1)) MB (fark: $([math]::Round($fark/1MB,1)) MB)"
Write-Host "GERCEK HIZ: $hiz MB/s"
