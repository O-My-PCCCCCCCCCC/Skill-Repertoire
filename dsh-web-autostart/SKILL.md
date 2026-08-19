---
name: dsh-web-autostart
description: >-
  Set up DeepSeek Harness Web (dsh web) to auto-start on Windows at logon,
  running fully hidden in the background (zero console windows), with a desktop
  shortcut, optional LAN access, and a configurable port. Use whenever the user
  wants "dsh 开机自启"、"后台静默运行不弹窗"、"任务栏/桌面快捷方式打开 web"、
  "局域网手机访问 dsh" or similar.
---

# DSH Web 开机自启（Windows 全后台静默运行）

把 `dsh web` 服务做成：**开机登录后自动启动、完全后台无窗口、随时一键打开**，
可选**局域网访问**（手机在同一 WiFi 下也能用），端口按规范可配置。

## 效果

| 能力 | 说明 |
|---|---|
| 开机自启 | 登录 Windows 后约 10~15 秒，服务自动在后台就绪 |
| 零窗口 | 全程无任何 cmd/黑色窗口弹出 |
| 一键打开 | 桌面快捷方式双击即开界面 |
| 局域网（可选） | 手机连同一 WiFi 访问 `http://<电脑IP>/` |
| 端口可配 | 默认 `10101`（规范：<10000 禁用、≥15000 留给其他项目） |

## 原理（为什么这样设计）

```
计划任务（登录触发）
  └─> wscript.exe           ← 图形程序，天生不创建控制台窗口
        └─> start-dsh-web.vbs   ← 以隐藏方式(SW_HIDE)调用 bat
              └─> start-dsh.bat ← 端口占用检测 + 日志 + 启动 node
                    └─> node bin.js web --port 10101   ← 服务本体
```

三个关键设计决策（都有踩坑依据）：

1. **隐藏窗口用 `wscript` 而不是 `cmd /k` / 计划任务直接跑 bat**：`wscript` 是
   GUI 子系统程序，任何情况下都不会弹控制台；bat 里的 node 共享那个隐形控制台，
   同样不会开新窗口。
2. **端口占用守卫**：bat 启动前先检查端口，已被占用就直接跳过（幂等，避免
   重复启动两个实例打架）。
3. **不要用 netsh 端口代理转发到服务同端口**：`0.0.0.0:3080 → 127.0.0.1:3080`
   这类规则在重启后由系统服务**先于应用绑定**，会导致应用绑 `127.0.0.1` 时
   `EACCES: permission denied`（Windows 特性：通配绑定在前会挡住具体地址绑定）。
   局域网要用代理，就选一个**服务不用的端口**（如 80），或者直接绑具体 IP。

## 前置条件

- Windows 10 / 11
- Node.js（建议 20+）
- dsh 已安装：`npm i -g @deepseek-ai/dsh`
- 浏览器访问过 `dsh web` 确认能跑

## 快速安装（推荐）

以**管理员身份**打开 PowerShell，执行：

```powershell
cd <解压目录>\dsh-web-autostart
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

脚本会自动：
1. 检测 `node.exe` 和 `dsh` 的 `bin.js` 路径；
2. 生成 `start-dsh.bat`（含端口守卫 + 日志）和 `start-dsh-web.vbs`（隐藏启动器）；
3. 注册计划任务 **DSH Web Autostart**（登录触发 → wscript 隐藏运行）。

常用参数：

```powershell
# 自定义端口 / 工作目录 / 安装位置 / 开启局域网
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Port 10101 -WorkDir "E:\Workspace" -InstallDir "D:\tools\dsh" -EnableLan
```

## 手动安装（想自己动手时）

1. 把 `scripts\start-dsh.bat` 和 `scripts\start-dsh-web.vbs` 放到任意目录
   （建议放在自己规划的高危/工具目录里）；
2. 编辑 bat 顶部变量：`NODE`（node 路径）、`DSH_BIN`（dsh 的 bin.js 路径）、
   `LOG`（日志文件）、`PORT`（端口）、`cd /d` 后的工作目录；
3. 注册计划任务（PowerShell）：

   ```powershell
   $action = New-ScheduledTaskAction -Execute "wscript.exe" `
     -Argument '"<你的目录>\start-dsh-web.vbs"'
   $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
   $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME `
     -LogonType Interactive -RunLevel Limited
   $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
     -ExecutionTimeLimit ([TimeSpan]::Zero)
   Register-ScheduledTask -TaskName "DSH Web Autostart" -Action $action `
     -Trigger $trigger -Principal $principal -Settings $settings -Force
   ```

## 桌面快捷方式

1. 在桌面新建快捷方式，目标填：

   ```
   C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Process 'http://127.0.0.1:10101'"
   ```

   （端口按实际修改；`-WindowStyle Hidden` 保证双击不闪黑窗）

2. 图标：右键快捷方式 → 属性 → 更改图标 → 选自己的图标（.ico 文件）；
3. **固定到任务栏只能手动**（Windows 11 限制）：右键快捷方式 → 「固定到任务栏」。
   程序化固定（`InvokeVerb("Pin to taskbar")`、直接往
   `User Pinned\TaskBar` 丢文件）在 Win11 上**均无效**，别浪费时间。

> 更精致的做法：`scripts\dsh-web-launcher.cs` 是一个 C# 启动器源码，
> 编译成 exe 后桌面快捷方式直接指向它（图标可内嵌）。编译：
> `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /target:winexe /win32icon:你的图标.ico /out:dsh-web-launcher.exe dsh-web-launcher.cs`

## 局域网访问（可选）

服务默认只绑 `127.0.0.1`（本机）。要让手机访问：

1. **给服务加 `--trusted-host <局域网IP>`**（bat 里已内置动态检测：取有默认网关的
   网卡 IP）。**必须加，否则手机打开页面但所有数据接口返回 403**——dsh 的
   `/api` 有浏览器信任围栏：非回环 Host 必须在 `trustedHosts` 里才放行。
2. **端口代理走 80**（或其他非服务端口），**不要用服务同端口**（见"原理"第 3 条）：

   ```cmd
   netsh interface portproxy set v4tov4 listenaddress=0.0.0.0 listenport=80 connectaddress=127.0.0.1 connectport=10101
   ```
3. 防火墙放行（仅专用/域网络，别开公用）：

   ```cmd
   netsh advfirewall firewall add rule name="DSH Web LAN 80" dir=in action=allow protocol=TCP localport=80 profile=private,domain
   ```
4. 把电脑的 WiFi 网络设为「专用网络」（设置 → 网络和 Internet → WLAN →
   当前网络 → 专用），否则 Windows 防火墙默认拦公用网络入站。
5. 手机连同一 WiFi → 打开 `http://<电脑IP>/`。

⚠️ **安全提醒**：这个界面无登录验证且能执行任意代码。局域网访问=同网络内任何人
都能控制这台电脑。只在可信网络开启，用完删除规则。

## 验证

- 看日志：`type %USERPROFILE%\.dsh\web-autostart.log`
- 本机访问：浏览器开 `http://127.0.0.1:<端口>`
- 重启电脑后：登录 → 等 15 秒 → 直接访问，全程无窗口

## 卸载

```powershell
Unregister-ScheduledTask -TaskName "DSH Web Autostart" -Confirm:$false
# 可选：删除生成的 bat/vbs、删除局域网代理和防火墙规则
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=80
netsh advfirewall firewall delete rule name="DSH Web LAN 80"
```

## 故障排查

| 现象 | 原因与解决 |
|---|---|
| 启动报 `EACCES: permission denied 127.0.0.1:<port>` | 端口被系统代理/其他进程通配绑定占先。查 `netstat -ano | findstr :<port>`；若 `0.0.0.0:<port>` 被 iphlpsvc 占用，删对应 `netsh interface portproxy` 规则 |
| 手机能开页面但没数据（/api 403） | 缺 `--trusted-host`。重启服务带上即可 |
| 局域网连不上 | ①手机没连同一 WiFi ②路由器开了 AP 隔离（关闭）③Windows 网络是"公用"（改专用）④防火墙没放行 |
| 登录后没自动启动 | 查计划任务状态与日志；确认是"登录触发"而非"开机触发"（开机触发跑在 SYSTEM 会话，会读错配置目录） |
| 任务栏图标没出现 | Win11 只认手动固定，右键快捷方式 → 固定到任务栏 |

## 端口规范（建议）

- `<10000`：禁用（留给系统/低端口惯例）
- `10101`：DSH Web
- `>=15000`：后续项目
