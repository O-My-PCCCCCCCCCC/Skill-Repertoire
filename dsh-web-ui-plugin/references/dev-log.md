# 实战记录：dsh-mode-status 开发全过程（2026-08-19）

## 需求演变

1. 初始：25565 端口独立看板（纯 Node 服务，显示模式/时间/倒计时/时间表，带 /api/status）
2. 用户要求：移植进 DSH Web 对话框最上方
3. 第一版：注入 `[data-chat-flow]` 容器顶部（sticky）—— 位置不对，用户要"最最最上面"
4. 第二版：`position:fixed` 顶部悬浮胶囊 —— 用户反馈访问变慢/无响应（性能问题）
5. 第三版：胶囊样式改用 DSW 主题变量 —— 用户反馈 UI 诡异不搭
6. 第四版（最终）：**侧栏底部状态点**（圆点+文字，无边框无背景）—— 用户满意

## 关键技术结论

### 客户端插件机制（@deepseek-ai/dsh-client-modules）

- 扫描 host Loader entries 中声明 `dsh.client.platform: "web"` 的包
- 通过 `exports["./client"]` 找到浏览器 bundle，注入 `window.__DSH_BOOT__` 图
- 浏览器端格式：`window.__ModuleLoader__.load({id, factory})`
- host 侧 `lib/index.js` 只需空 `apply()`

### 注册链路（~/.dsh/profiles/web/package.json）

```json
{
  "dependencies": {
    "@dsh-external/<name>": "link:C:/Users/Administrator/DSH-Plugin/<name>"
  },
  "dsh": {
    "profile": { "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-web-app", "@dsh-external/<name>"] }
  }
}
```

### 性能踩坑（重要教训）

- **症状**：用户反馈"访问变慢、没有响应"
- **根因**：MutationObserver 监听整个 body 子树（`subtree: true`），
  React 页面 DOM 高频变动 → 每帧触发回调；且每秒无差别写 DOM（textContent/dataset）
- **修复**：
  - observer 只监听必要范围；回调里只做"元素在不在"的幂等检查
  - `updatePill` 加值缓存：`if (el._msKey === key) return;`
  - 兜底补挂放在 setInterval 里（每秒一次）

### DOM 锚点（rc.6 实测）

- 侧栏底部：`[data-slot='sidebar.settings']` → 状态点插到它前面（parentElement.insertBefore）
- 侧栏折叠状态：`body[data-dsh-sidebar-collapsed]` → CSS 隐藏文字只留圆点
- 对话流：`[data-chat-flow]`

### 主题适配

- 全部用 `--dsw-alias-*` / `--dsw-font-*` 变量，无任何写死颜色
- 模式色：梁文谷=`--dsw-alias-state-success-primary`，
  梁文峰=`--dsw-alias-brand-primary`，提醒=`--dsw-alias-state-warn-primary`

### 时间计算

- 北京时间 = `new Date(Date.now() + 8*3600*1000)`，用 getUTC* 读取
  （与浏览器/服务器时区无关）
- 规则用"分钟数"表示：00:00=0, 09:00=540, 12:00=720, 14:00=840, 18:00=1080, 24:00=1440

### 验证方法

- `node --check lib/client.js` 语法
- 合规临时端口（>=15000，如 16555）起实例验证 `/plugins/@dsh-external/<name>/client.js` 返回 200
- 重启 DSH Web 生效

## 相关产物

- 插件：`C:\Users\Administrator\DSH-Plugin\dsh-mode-status\`
- 独立看板：`E:\Workspace\Project\mode-status\`（25565）
- AI 行为 skill：`~/.dsh/skills/beijing-mode/SKILL.md`
- 规范登记：`E:\Workspace\开发环境规范.txt`（端口 25565、项目、插件、skill 记录）
