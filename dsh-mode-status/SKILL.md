# dsh-mode-status —— DSH Web 模式状态点插件

> ⚠️ **仅供学习使用 · 禁止商用 · 禁止二次售卖 · 禁止未经授权再分发（含修改版）**

> 在 DeepSeek Harness Web 界面的**侧栏底部**显示"梁文谷 / 梁文峰"时间分段模式状态点：
> 模式色圆点 + 模式名 + 北京时间 + 距下次切换，点击弹出详情面板。
> 纯前端实现，全部使用 DSW 主题变量，自动适配亮/暗主题与皮肤。

## 适用场景

任何使用 DeepSeek Harness Web（`dsh web`）且希望界面常驻显示"按北京时间分段切换回复模式"状态的用户。

## 快速使用

```powershell
# 一键安装（复制插件 + 注册 profile + pnpm install）
powershell -ExecutionPolicy Bypass -File install.ps1

# 重启 DSH Web 生效（或手动重启）
powershell -ExecutionPolicy Bypass -File restart-dsh-web.ps1
```

安装后刷新浏览器页面，侧栏底部（设置按钮上方）即出现模式状态点。

## 目录结构

```
dsh-mode-status/
├── SKILL.md               # 本文件（AI 用完整说明）
├── README.md              # 人快速上手
├── install.ps1            # 一键安装脚本（复制+注册+pnpm）
├── restart-dsh-web.ps1    # 重启 DSH Web 脚本（安装后需重启生效）
├── plugin/                # 插件本体（DSH-Plugin 结构）
│   ├── package.json       # 声明 dsh.client.platform=web + exports ./client
│   ├── cordis.patch.yml   # 插入 ui-mode-status 入口
│   └── lib/
│       ├── index.js       # host 侧空入口
│       └── client.js      # 浏览器侧：状态点 + 详情面板
└── docs/
    └── rules.md           # 模式规则与修改说明（三处同步）
```

## 插件工作机制

- **client 插件**：`lib/client.js` 通过 `window.__ModuleLoader__.load({id, factory})` 注册，
  由 DSH 的 `dsh-client-modules` 扫描 `package.json` 的 `dsh.client.platform: "web"` 声明
  后注入浏览器（`/plugins/<id>/client.js`）
- **注入位置**：找到侧栏的 `[data-slot='sidebar.settings']`（设置区），状态点插到它前面
- **纯前端**：用 `Date.now() + 8h` 计算北京时间（与服务器时区无关），每秒刷新，
  值缓存（内容未变化不写 DOM），性能开销极小
- **样式**：全部 DSW 主题变量（`--dsw-alias-*` / `--dsw-font-*`），主题/皮肤自动跟随

## 修改模式规则（重要）

规则定义在三处，**必须同步修改**：

1. 本插件：`plugin/lib/client.js` 顶部的 `SEGMENTS` 与 `WARNINGS`
2. 独立看板：`E:\Workspace\Project\mode-status\server.js` 与 `public\app.js`
3. AI 行为 skill：`~/.dsh/skills/beijing-mode/SKILL.md`

### 当前规则（北京时间）

| 时段 | 模式 | 行为 |
|---|---|---|
| 00:00-09:00 | 梁文谷 | 正常回复 |
| 09:00-12:00 | 梁文峰 | 极简回复 |
| 12:00-14:00 | 梁文谷 | 正常回复 |
| 14:00-18:00 | 梁文峰 | 极简回复 |
| 18:00-24:00 | 梁文谷 | 正常回复 |
| 08:50-09:00 / 13:50-14:00 | — | 提醒"快到梁文峰时间了" |

### 颜色映射

| 状态 | DSW 变量 | 含义 |
|---|---|---|
| 绿 | `--dsw-alias-state-success-primary` | 梁文谷模式 |
| 品牌色 | `--dsw-alias-brand-primary` | 梁文峰模式 |
| 黄+闪烁 | `--dsw-alias-state-warn-primary` | 提醒时段 |

## 卸载

```powershell
# 从 ~/.dsh/profiles/web/package.json 移除依赖与 bundles 条目
# 删除 C:\Users\Administrator\DSH-Plugin\dsh-mode-status
# 重启 DSH Web
```

## 许可

MIT —— 可自由使用、修改、分发（含商业），保留版权声明即可。

## 作者

追寻光的影（2026-08-19）
