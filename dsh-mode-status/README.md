# dsh-mode-status —— 模式状态点插件（DSH Web）

> ⚠️ **仅供学习使用 · 禁止商用 · 禁止二次售卖 · 禁止未经授权再分发（含修改版）**

在 DeepSeek Harness Web 侧栏底部显示"梁文谷 / 梁文峰"时间分段模式的实时状态：
模式色圆点 + 模式名 + 北京时间 + 距下次切换，点击弹出详情面板。

## 安装

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

脚本会：
1. 把 `plugin/` 复制到 `C:\Users\Administrator\DSH-Plugin\dsh-mode-status`
2. 在 `~/.dsh/profiles/web/package.json` 注册依赖与 bundles
3. 在 profile 目录执行 `pnpm install`

然后重启 DSH Web：

```powershell
powershell -ExecutionPolicy Bypass -File restart-dsh-web.ps1
```

刷新浏览器 → 侧栏底部出现状态点（● 梁文峰 15:42:31 → 18:00:00）。

## 界面

- 圆点颜色：绿=梁文谷 / 品牌色=梁文峰 / 黄+闪烁=提醒时段（08:50-09:00、13:50-14:00）
- 无边框无背景（GitHub 状态点风格），hover 浅色反馈，点击弹详情
- 侧栏折叠成窄条时只显示圆点
- 全部 DSW 主题变量，亮/暗主题与皮肤自动适配

## 改规则

模式分段定义在 `plugin/lib/client.js` 顶部 `SEGMENTS` / `WARNINGS`。
注意与 AI 行为 skill（`~/.dsh/skills/beijing-mode/SKILL.md`）及独立看板
（`Project\mode-status`）三处同步，详见 `docs/rules.md`。

## 目录

```
├── SKILL.md / README.md   说明
├── install.ps1            一键安装
├── restart-dsh-web.ps1    重启 DSH Web
├── plugin/                插件本体（复制到 DSH-Plugin 用）
└── docs/rules.md          模式规则与同步说明
```

## 许可

MIT，可自由使用/修改/分发。
