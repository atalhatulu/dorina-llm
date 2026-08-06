Get-Process | Where-Object { $_.ProcessName -match 'uv|python|powershell' } | Select-Object Id, ProcessName, CPU, StartTime | Format-Table -AutoSize
Write-Host "---LOG---"
Get-Content C:\dorina-llm\setup.log -Tail 4
