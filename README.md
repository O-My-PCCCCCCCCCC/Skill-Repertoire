# Skill-Repertoire · Skill 仓库

个人 skill 收藏与发布仓库。

> ⚠️ **重要声明**
>
> 本仓库内所有 skill **仅供学习使用**。
> **禁止商用、禁止二次售卖、禁止未经授权再分发**（含修改版）。
> 使用本仓库内容产生的任何问题，作者不承担任何责任。
>
> —— 追寻光的影

## 仓库内容

| Skill | 说明 | 许可 |
|---|---|---|
| `meteor-zh` | Minecraft Meteor Client / addon jar 安全汉化工具（字节码字符串改写 + 中文渲染器注入 + 中文字体） | GPL-3.0（个人学习用，遵守原项目许可） |
| `dsh-web-autostart` | DSH Web 开机自启方案（计划任务 + 脚本模板） | 见包内说明 |
| `dsh-mode-status` | DSH Web 客户端插件：侧栏底部显示"梁文谷/梁文峰"时间分段模式状态点，点击弹详情 | MIT |
| `dsh-web-ui-plugin` | 给 DSH Web 写客户端插件 / 改 UI 的完整流程 skill（DOM 锚点 / 主题变量 / 性能规范） | MIT |
| `beijing-mode` | AI 按北京时间自动切换回复风格（梁文谷 = 正常 / 梁文峰 = 极简）的用户级 skill | MIT |

## 目录结构

```
Skill-Repertoire/
├── README.md                本文件（含使用声明）
├── LICENSE                  仓库许可（学习用途声明）
├── <skill-name>/            每个 skill 一个目录（含 SKILL.md 与素材）
└── <skill-name>.skill       每个 skill 的打包压缩包（zip 格式，UTF-8 文件名）
```

## 获取方式

- **源码**：直接 clone 本仓库
- **压缩包**：在 [Releases](../../releases) 页面下载每个 skill 的独立压缩包（`<name>.skill`）

## 使用说明

1. 解压对应 skill 包（`.skill` 本质是 zip，可改后缀解压或直接解压）
2. 阅读包内 `README.md` / `SKILL.md` 了解用法
3. 部分 skill 是 DSH（DeepSeek Harness）专用，需 DSH 环境

## 免责声明

本仓库内容为个人学习产物，与任何组织无关。引用第三方内容请遵守各自许可证。
