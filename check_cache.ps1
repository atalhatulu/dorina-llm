Get-ChildItem C:\Users\Talha\AppData\Local\uv\cache -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, Length, LastWriteTime | Format-Table -AutoSize
Write-Host "---TUM UV/PY PROCESSLER---"
Get-Process | Where-Object { $_.ProcessName -match 'uv|python' } | Select-Object Id, ProcessName, CPU | Format-Table -AutoSize
Write-Host "---BOS DISK---"
Get-PSDrive C | Select-Object Used, Free | Format-List
