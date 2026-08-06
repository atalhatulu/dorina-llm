$a = (Get-ChildItem C:\Users\Talha\AppData\Local\uv\cache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Start-Sleep 10
$b = (Get-ChildItem C:\Users\Talha\AppData\Local\uv\cache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$mb1 = [math]::Round($a/1MB, 1)
$mb2 = [math]::Round($b/1MB, 1)
$hiz = [math]::Round(($b-$a)/10/1MB, 2)
Write-Host "Cache: $mb1 MB -> $mb2 MB"
Write-Host "HIZ: $hiz MB/s"
