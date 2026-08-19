# kei-skin-dev —— 凯伊（天童柯伊）主题皮肤开发

> ⚠️ **仅供学习使用 · 禁止商用 · 禁止二次售卖 · 禁止未经授权再分发（含修改版）**

> 用户级 skill：记录"凯伊主题 DSH Web 皮肤"的完整开发流程与产物，
> 供后续修改皮肤（换图/换色/调布局）时复用。

## 皮肤现状

- **插件位置**：`C:\Users\Administrator\DSH-Plugin\dsh-kei-skin\`
- **包名**：`@dsh-external/dsh-client-ui-skin-kei`
- **注册**：`~/.dsh/profiles/web/package.json`（bundles 已含，与 maid-atelier 皮肤并存）
- **生效**：重启 DSH Web（3080）；刷新页面
- **主题**：亮「银白×绯红」（白毛红瞳）/ 暗「深蓝黑×红瞳发光」，跟随 DSH `data-ds-dark-theme` 自动切换

## 架构（基于 maid-atelier 模板改造）

| 部分 | 文件 | 说明 |
|---|---|---|
| 主逻辑 | `src/client/index.ts` | 立绘舞台、背景切换、侧栏装饰、主题投影、MutationObserver 守卫、性能保护 |
| 样式 | `src/client/kei.module.css` | 亮/暗双主题 DSW 变量覆盖 + 装饰设计 |
| 图片数据 | `src/client/kei-art.generated.ts` | base64 内嵌（背景 2 + 表情包 3），由脚本生成 |
| 宿主入口 | `lib/index.js` | 空 apply |
| 皮肤元数据 | `skin.json` | 皮肤名/标签/主色 |

## 修改皮肤（常用操作）

### 换背景/换图

1. 放图到 `assets\`（背景 jpg / 表情包 png）
2. 重新生成图片数据：
   ```powershell
   # 改 src/client/kei-art.generated.ts：手动替换 base64 或重跑生成逻辑
   ```
3. 更新 `src/client/index.ts` 中的引用（KEI_BG_LIGHT / KEI_BG_DARK / KEI_EMO_*）
4. 构建：`cd C:\Users\Administrator\DSH-Plugin\dsh-kei-skin && pnpm build`
5. 重启 DSH Web 生效

### 改配色

改 `src/client/kei.module.css` 顶部两段主题变量：
- 亮色：`--kei-red-*`（绯红系）+ `--dsw-alias-*` 覆盖
- 暗色：`[data-ds-dark-theme]` 段

## 构建链

```powershell
cd C:\Users\Administrator\DSH-Plugin\dsh-kei-skin
pnpm install    # 首次（tsdown/lightningcss/vitest）
pnpm build      # 产物 lib/client.js（含图片 base64 + CSS）
```

## 素材来源

- 背景/立绘：`F:\图片\静态\kei`（用户凯伊图库，340 张）
- 表情包：`F:\图片\静态\kei\表情包`（550×550 方形）
- 当前选图：
  - 亮背景 `e3d48c1489a8d87c04eb4760bcb62096.png`（4000×3541 白底立绘）
  - 暗背景 `fbe0f000149c52ad3af9072313619852.png`（1600×2429 深色）

## 角色设定（配色依据）

- 天童柯伊（Tendo Kei），《蔚蓝档案》角色
- **银白长发 + 红瞳**（白毛红瞳）→ 皮肤用银白×绯红
- 千年科学学园 / AI 机械设定 → 暗色主题用深蓝黑 + 红瞳发光
