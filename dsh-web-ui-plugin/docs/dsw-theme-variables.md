# DSW 主题变量速查

来源：`dsh-web-frontend/dist/assets/index-*.css`（共 351 个 `--dsw-*` 变量）。
以下为常用分组；切主题（亮/暗/皮肤）时变量值自动变化。

## 背景层

| 变量 | 用途 |
|---|---|
| `--dsw-alias-bg-base` | 页面根背景 |
| `--dsw-alias-bg-layer-1` | 浮层/面板背景 |
| `--dsw-alias-bg-layer-2` | 卡片/行背景 |
| `--dsw-alias-bg-layer-3` | 更深一层 |
| `--dsw-alias-bg-overlay` | 覆盖层 |
| `--dsw-alias-bg-mask-1/2/3` | 遮罩（3 常用作阴影/模糊底） |
| `--dsw-alias-bg-skeleton` | 骨架屏 |

## 边框

| 变量 | 用途 |
|---|---|
| `--dsw-alias-border-l1` | 最弱边框（卡片内） |
| `--dsw-alias-border-l2` | 常规边框（面板） |
| `--dsw-alias-border-l3` | 强调边框 |
| `--dsw-alias-border-l4` | 最强边框 |
| `--dsw-alias-border-inverted` | 反色边框 |

## 文字

| 变量 | 用途 |
|---|---|
| `--dsw-alias-label-primary` | 主文字 |
| `--dsw-alias-label-secondary` | 次要文字 |
| `--dsw-alias-label-tertiary` | 弱化文字 |
| `--dsw-alias-label-caption` | 说明/标注 |
| `--dsw-alias-label-primary-inverted` | 反色主文字 |
| `--dsw-alias-label-primary-foreground` | 前景文字 |

## 品牌与状态

| 变量 | 用途 |
|---|---|
| `--dsw-alias-brand-primary` | 品牌主色（按钮/链接/高亮） |
| `--dsw-alias-brand-primary-invert` | 品牌反色 |
| `--dsw-alias-state-success-primary` | 成功（绿） |
| `--dsw-alias-state-success-secondary/tertiary` | 成功弱化 |
| `--dsw-alias-state-warn-primary` | 警告（黄/橙） |
| `--dsw-alias-state-warn-secondary/tertiary` | 警告弱化 |
| `--dsw-alias-state-error-primary` | 错误（红） |
| `--dsw-alias-state-error-secondary` | 错误弱化 |
| `--dsw-alias-state-business-primary` | 业务色 |

## 交互反馈

| 变量 | 用途 |
|---|---|
| `--dsw-alias-interactive-bg-hover` | hover 底色 |
| `--dsw-alias-interactive-bg-active` | active 底色 |
| `--dsw-alias-interactive-bg-hover-accent` | hover 强调色底 |
| `--dsw-alias-interactive-bg-hover-danger` | hover 危险色底 |
| `--dsw-alias-button-primary-fill` | 主按钮填充 |
| `--dsw-alias-button-primary-hover` | 主按钮 hover |
| `--dsw-alias-button-floating-fill` | 悬浮按钮 |
| `--dsw-alias-tooltip-bg` | 提示背景 |
| `--dsw-alias-toast-bg` | toast 背景 |

## 字体

| 变量 | 用途 |
|---|---|
| `--dsw-font-base-16` | 基础字号 |
| `--dsw-font-base-16-font-family` | **字体族（自定义元素 font-family 用它）** |

## 用法示例

```css
.my-widget {
  background: var(--dsw-alias-bg-layer-2);
  border: 1px solid var(--dsw-alias-border-l2);
  color: var(--dsw-alias-label-primary);
  font: 600 12px/1.3 var(--dsw-font-base-16-font-family, sans-serif);
}
.my-widget:hover { background: var(--dsw-alias-interactive-bg-hover); }
.mode-green { color: var(--dsw-alias-state-success-primary); }
.mode-brand { color: var(--dsw-alias-brand-primary); }
.mode-warn  { color: var(--dsw-alias-state-warn-primary); }
```
