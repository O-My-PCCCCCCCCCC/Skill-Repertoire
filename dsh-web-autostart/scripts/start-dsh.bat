@echo off
rem DSH Web launcher — 按需修改下面 4 个变量（或直接用 setup.ps1 自动生成）
set "NODE=C:\Program Files\nodejs\node.exe"
set "DSH_BIN=%APPDATA%\npm\node_modules\@deepseek-ai\dsh\lib\bin.js"
set "LOG=%USERPROFILE%\.dsh\web-autostart.log"
set "PORT=10101"
cd /d "%USERPROFILE%"

rem 端口占用守卫：已被占用则跳过（避免重复启动）
netstat -ano | findstr /c:":%PORT% " | findstr /c:"LISTENING" >nul 2>&1
if not errorlevel 1 (
  echo %date% %time% : port %PORT% already in use, skipping start >> "%LOG%"
  exit /b 0
)

rem 局域网信任地址（有默认网关的网卡 IP），配合 80 端口代理使用
set "LANIP="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null}).IPv4Address.IPAddress"`) do set "LANIP=%%i"

echo %date% %time% : starting dsh web on port %PORT% (LAN: %LANIP%) >> "%LOG%"
"%NODE%" "%DSH_BIN%" web --port %PORT% --trusted-host %LANIP% >> "%LOG%" 2>&1
