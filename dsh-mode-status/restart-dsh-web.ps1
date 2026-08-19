# 重启 DSH Web（默认 3080），使 client 插件变更生效
# 注意：会结束当前所有会话（agent 运行在 host 进程内），属正常现象
$ErrorActionPreference = 'Stop'
$node = 'C:\Users\Administrator\.dsh-runtime\node\node.exe'
$bin  = 'C:\Users\Administrator\.dsh-runtime\dsh\node_modules\@deepseek-ai\dsh\lib\bin.js'
$port = 3080

$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $conn | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object {
        Write-Host "停止 DSH Web PID $_ ..." -ForegroundColor Yellow
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

Write-Host "启动 DSH Web @ $port ..." -ForegroundColor Cyan
Start-Process -FilePath $node -ArgumentList $bin, 'web' -WorkingDirectory 'E:\Workspace' -WindowStyle Hidden

$ok = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 1000
    $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($c) { $ok = $true; break }
}
if ($ok) {
    Write-Host "DSH Web 已重启 ✓ http://127.0.0.1:$port" -ForegroundColor Green
} else {
    Write-Host "重启失败：$port 未监听" -ForegroundColor Red
    exit 1
}
