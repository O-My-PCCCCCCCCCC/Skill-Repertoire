# dsh-web-ui-plugin —— 给 DSH Web 写客户端插件 / 改 UI

沉淀自实战（dsh-mode-status 模式状态点插件）的开发流程 skill：
**不改 DSH 本体，用客户端插件给 DSH Web 注入自定义 UI，并正确适配主题。**

## 快速开始

```powershell
# 装现成插件（dsh-mode-status 示例）
cd E:\Workspace\skill\dsh-mode-status
powershell -ExecutionPolicy Bypass -File install.ps1
```

## 核心要点

1. **客户端插件机制**：npm 包声明 `dsh.client.platform: "web"` + `exports["./client"]`，
   即被自动注入浏览器 —— 无需改 DSH 本体
2. **注册**：`~/.dsh/profiles/web/package.json` 的 bundles + link 依赖
3. **样式必须用 DSW 变量**（`--dsw-alias-*`），否则与界面不搭
4. **性能**：别监听整个 body 子树、DOM 写入要值缓存

详见 `SKILL.md`（完整步骤 / DOM 锚点 / 变量速查 / 性能规范 / 调试方法）。

## 目录

```
├── SKILL.md          完整开发流程（AI 用）
├── README.md         本文件（人快速上手）
├── references/
│   └── 实战记录.md    本次开发全过程记录（含踩坑）
└── docs/
    └── 主题变量清单.md  DSW 变量整理
```

## 许可

MIT
