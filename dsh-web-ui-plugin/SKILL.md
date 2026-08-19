# dsh-web-ui-plugin —— 给 DeepSeek Harness Web 写客户端插件 / 改 UI

> 沉淀自 2026-08-19 的实战（dsh-mode-status 模式状态点插件）：
> 如何不改 DSH 本体，用"客户端插件"给 DSH Web 注入自定义 UI，并正确适配主题。
> 适用：在 DSH Web 界面加小部件 / 改样式 / 注入自定义元素。

## 核心结论（先记住）

1. **不用 clone dsh 源码、不用改编译产物**。DSH 有原生客户端插件机制：
   任何 npm 包声明 `dsh.client.platform: "web"` + `exports["./client"]`，
   就会被扫描注入浏览器（`/plugins/<id>/client.js`）。
2. **插件挂载**：通过 `~/.dsh/profiles/web/package.json` 的
   `dsh.profile.bundles` 注册 + dependencies `link:` 指向本地插件目录。
3. **UI 风格**：必须用 DSW 主题变量（`--dsw-alias-*` / `--dsw-font-*`），
   写死颜色会"不搭"；变量会自动跟随亮/暗主题与皮肤。
4. **性能铁律**：MutationObserver 别监听整个 body 子树；DOM 写入要加值缓存
   （内容未变化不写）。否则 React 高频重渲染下会把浏览器拖慢甚至卡死。

## 安装现有插件（dsh-mode-status 示例）

```powershell
# 见 skill/dsh-mode-status/install.ps1（一键：复制+注册+pnpm+重启提示）
powershell -ExecutionPolicy Bypass -File install.ps1
```

## 开发一个自定义 client 插件（步骤）

### 1. 建插件包（放在 `C:\Users\Administrator\DSH-Plugin\<name>`）

```
<name>/
├── package.json        # 声明 dsh.client + exports
├── cordis.patch.yml    # 插入入口
└── lib/
    ├── index.js        # host 侧空入口（export { apply }）
    └── client.js       # 浏览器侧（__ModuleLoader__.load 格式）
```

### 2. package.json 关键字段

```json
{
  "name": "@dsh-external/<name>",
  "type": "module",
  "main": "lib/index.js",
  "exports": { ".": "./lib/index.js", "./client": "./lib/client.js" },
  "dsh": { "bundle": { "patch": "./cordis.patch.yml" },
           "client": { "inject": [], "platform": "web" } }
}
```

### 3. cordis.patch.yml（插入入口）

```yaml
- insert:
    - id: <entry-id>
      name: '@dsh-external/<name>'
```

### 4. lib/index.js（host 侧）

```js
function apply() {}
export { apply };
```

### 5. lib/client.js（浏览器侧，核心）

```js
window.__ModuleLoader__.load({
  id: "@dsh-external/<name>",
  factory: (require) => {
    var module = { exports: {} };
    var exports = module.exports;
    // ... 组件逻辑 ...
    function apply(ctx) {
      ctx.effect(function () {
        // 1) 注入 <style>（CSS 用 DSW 变量）
        // 2) 挂载自定义元素（找 DOM 锚点）
        // 3) 轻量 MutationObserver 守护
        // 4) setInterval 刷新（带值缓存）
        return function () { /* 清理 */ };
      }, "label");
    }
    exports.apply = apply;
    return module.exports;
  }
});
```

### 6. 注册进 profile

编辑 `~/.dsh/profiles/web/package.json`：
- `dependencies` 加 `"@dsh-external/<name>": "link:C:/Users/Administrator/DSH-Plugin/<name>"`
- `dsh.profile.bundles` 数组追加 `"@dsh-external/<name>"`

然后 `cd ~/.dsh/profiles/web && pnpm install`，重启 DSH Web。

## 常用 DOM 锚点（rc.6 实测）

| 目标 | 选择器 |
|---|---|
| 侧栏设置区（底部锚点） | `[data-slot='sidebar.settings']` |
| 对话流容器 | `[data-chat-flow]` |
| 侧栏列 | `[data-pane='sidebar'], [class*='sidebarCol']` |
| 会话激活区 | `[data-phase='active']` |
| 主题（亮/暗） | `body[data-ds-dark-theme]` |
| 侧栏折叠 | `body[data-dsh-sidebar-collapsed]` |

> 注入位置建议：找语义化 `data-slot` 锚点插入，比猜 hash 类名稳。

## DSW 主题变量速查（样式必用）

| 用途 | 变量 |
|---|---|
| 页面背景 | `--dsw-alias-bg-base` / `--dsw-alias-bg-layer-1/2/3` |
| 边框 | `--dsw-alias-border-l1/2/3/4` |
| 文字 | `--dsw-alias-label-primary/secondary/tertiary/caption` |
| 品牌色 | `--dsw-alias-brand-primary` |
| 成功/警告/错误 | `--dsw-alias-state-success-primary` / `state-warn-primary` / `state-error-primary` |
| hover 底色 | `--dsw-alias-interactive-bg-hover` |
| 遮罩/阴影 | `--dsw-alias-bg-mask-3` |
| 字体 | `--dsw-font-base-16-font-family`（可作 font-family 兜底） |

完整 351 个变量：`dsh-web-frontend/dist/assets/index-*.css` 里提取。

## 性能规范（重要）

1. MutationObserver **不要** `subtree: true` 监听整个 body —— 只监听必要范围
2. DOM 写入加**值缓存**：`if (el._key === newKey) return;` 再更新
3. 定时刷新用 `setInterval(1000)` 足够，别用 requestAnimationFrame 逐帧
4. 自定义元素加自己的 id/data 属性，React 重渲染时用 MutationObserver 兜底恢复

## 调试

- 语法检查：`node --check lib/client.js`
- 加载验证：临时起一个实例（用 >=15000 的合规端口，如 16555）：
  `node <dsh>/lib/bin.js web --port 16555` 然后访问
  `/plugins/@dsh-external/<name>/client.js` 应返回 200
- 生效需**重启 DSH Web**（会结束当前会话，属正常现象）

## 参考

- 实战成品：`skill/dsh-mode-status/`（完整可安装插件）
- 皮肤参考：`C:\Users\Administrator\DSH-Plugin\dsh-deep-whale\maid-atelier`
- 规范文档：`E:\Workspace\开发环境规范.txt`（端口/目录/UI 规则）

## 许可

MIT
