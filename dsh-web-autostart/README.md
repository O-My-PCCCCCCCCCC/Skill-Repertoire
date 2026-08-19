# dsh-web-autostart

**DSH Web 开机自启（Windows 全后台静默运行）** — 分享给朋友的 skill 包。

## 目录

```
dsh-web-autostart/
├── SKILL.md                 # 完整说明文档（原理/安装/排障/局域网）
├── README.md                # 本文件（快速上手）
└── scripts/
    ├── setup.ps1            # ★ 一键安装脚本（自动检测路径、注册计划任务）
    ├── start-dsh.bat        # 启动脚本模板（端口守卫 + 日志 + 局域网检测）
    ├── start-dsh-web.vbs    # 隐藏窗口启动器
    └── dsh-web-launcher.cs  # 桌面快捷方式启动器源码（可选，编译成 exe）
```

## 30 秒上手

1. 确认已安装：`npm i -g @deepseek-ai/dsh`（Node.js 20+）；
2. 右键 `scripts\setup.ps1` → 「使用 PowerShell 运行」（会自动请求管理员权限）；
3. 重启电脑，浏览器打开 `http://127.0.0.1:10101`，全程无窗口。

## 它做了什么

- 计划任务（登录触发）→ `wscript`（图形程序，永不弹窗）→ 隐藏启动 bat → 服务
- 端口守卫：已占用则跳过，不会重复启动
- 端口规范：默认 10101（<10000 禁用，≥15000 留给其他项目）
- 可选：局域网访问（手机同 WiFi 访问），详见 SKILL.md

## 常见坑（都踩过，文档里写了）

- Win11 任务栏只能手动固定（程序化固定无效）
- 局域网必须加 `--trusted-host`，否则手机看到页面但没数据（/api 403）
- 端口代理别用服务同端口（重启后会 EACCES 冲突）

详细文档见 **SKILL.md**。
