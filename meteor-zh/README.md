# meteor-zh · Minecraft 汉化 skill

> ⚠️ **仅供学习使用 · 禁止商用 · 禁止二次售卖 · 禁止未经授权再分发（含修改版）**

把 Minecraft 的 Meteor Client（或它的任何插件/addon 的 jar）安全地改成简体中文版。

- **Meteor Client jar** → 全量处理：翻译界面文字 + 注入按需加载的中文渲染器 + 换中文字体
- **插件 / addon jar** → 只翻译（客户端已能显示中文）

## 快速使用

```bash
# 汉化 Meteor Client
python scripts/patch_jar.py \
  --input <meteor.jar> --output <汉化.jar> \
  --mode client --font "C:\Windows\Fonts\msyh.ttc"

# 汉化一个插件
python scripts/patch_jar.py \
  --input <addon.jar> --output <addon-汉化.jar> --mode addon
```

输出 jar 替换 mods 文件夹里的原 jar（mods 里只能有一个 meteor jar）。

## 目录结构

```
├── SKILL.md                # Claude 用的完整工作流说明
├── README.md               # 本文件（人快速上手）
├── scripts/
│   ├── cp_patch.py         # 常量池安全改写引擎（核心）
│   ├── patch_jar.py        # 主打包脚本（客户端/插件双模式）
│   ├── extract_strings.py  # 从 jar 提取待翻译字符串
│   ├── verify_jar.py       # 校验：重解析所有类 + 中文覆盖率
│   └── renderer/           # 中文渲染器（源码 + 编译产物 + 编译脚本）
├── references/
│   ├── translations/       # 4314 条翻译词典（按模块分文件，脚本自动合并）
│   ├── force_map.json      # 枚举选项强制翻译映射
│   ├── force_enum.json     # 辅助：可翻译的枚举常量
│   ├── serialized_enums.json # 辅助：不能翻译的序列化枚举
│   └── meteor-guide.md     # 内部机制和踩过的坑
├── docs/usage.md           # 详细用法
└── assets/zh_cn.json       # 按键绑定汉化
```

## 为什么"安全"很重要

Minecraft mod 的界面文字硬编码在字节码里，直接改字符串会崩。这个工具内置了
防崩溃机制（详见 `references/meteor-guide.md`）：

- 只翻纯字面量，不碰字段/方法名
- 枚举选项翻译带冲突预检（避免重复字段名崩溃）
- 序列化枚举自动排除（避免读配置崩溃）
- mod-id / 资源路径 / 命令名等功能串天然不碰

## 中文为什么能显示

Meteor 的自定义字体渲染器只支持 ASCII，中文字符会渲染成空白。工具内置了
`renderer/` 里的 **FontFix** 渲染器（按需加载中文字形），替换掉原来的渲染器，
再配上中文字体，中文就能正常显示。

## 许可证说明

本工具基于开源 Meteor Client 做汉化，仅供个人学习使用，请遵守原项目的
GPL-3.0 许可证。
