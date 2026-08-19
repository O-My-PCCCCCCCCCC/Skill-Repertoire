# 详细用法

## 完整工作流

### 1. 判断模式

- `fabric.mod.json` 的 `id` 是 `meteor-client` → **client** 模式
- 其他（依赖 meteor-client 的 addon/插件）→ **addon** 模式

### 2. 提取字符串

```bash
python scripts/extract_strings.py --input <mod.jar> --output strings.json
```

列出所有可安全翻译的字符串。对照 `references/translations/` 看哪些还没覆盖。

### 3. 翻译未覆盖的字符串

把新增的 `{英文: 中文}` 合并进词典。注意：

- 保留 `%s` `%d` `(highlight)/(default)` `\x01` 等占位符
- 不翻译：正则、URL、路径、JSON/NBT/starscript 示例、类名/方法名、命令语法
- 模块名/设置名必须唯一（撞名会导致模块被覆盖）

### 4. 打补丁

```bash
# client 模式（Meteor Client）
python scripts/patch_jar.py \
  --input <meteor.jar> --output <汉化.jar> \
  --translations references/translations/ \
  --force-map references/force_map.json \
  --mode client --font <中文字体.ttf> \
  --fontfix-dir scripts/renderer/classes

# addon 模式
python scripts/patch_jar.py \
  --input <addon.jar> --output <汉化.jar> \
  --translations references/translations/ \
  --force-map references/force_map.json \
  --mode addon
```

参数说明：

| 参数 | 说明 |
|------|------|
| `--input` | 输入的 mod jar |
| `--output` | 输出的汉化 jar |
| `--translations` | 翻译词典（单个 json 或目录，目录会递归合并所有 json） |
| `--force-map` | 枚举选项强制翻译映射 |
| `--mode` | `client` 或 `addon` |
| `--font` | 中文字体文件（client 模式用，替换默认字体） |
| `--fontfix-dir` | 中文渲染器编译产物目录（默认 scripts/renderer/classes） |

### 5. 中文字体

client 模式需要中文字体。推荐系统字体：

- Windows：`C:\Windows\Fonts\msyh.ttc`（微软雅黑）
- Linux：`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`
- macOS：`/System/Library/Fonts/PingFang.ttc`

或者让用户提供。

### 6. 校验

```bash
python scripts/verify_jar.py --input <汉化.jar>
```

必须 `failures: 0`。

### 7. 交付

输出 jar 放进 mods 文件夹，替换原 jar。提醒用户：

- 模块/设置配置会重置一次（标识符变成中文）
- 命令里用中文模块名（`.toggle 杀戮光环`）
- 插件文字已汉化，但需和对应 meteor 版本一起用

## 遇到崩溃时

| 崩溃 | 含义 | 处理 |
|------|------|------|
| `ClassFormatError: Duplicate field name` | 枚举翻译撞名 | 从 force_map 移除撞名的值 |
| `NoSuchFieldError` | 字段/引用不一致 | 检查冲突预检和序列化排除 |
| `IllegalArgumentException: No enum constant` | 序列化枚举被翻译 | 把该枚举加进序列化排除列表 |
| `NoSuchElementException` at `<clinit>` | mod-id/元数据键被翻 | 检查词典里是否有 `meteor-client` 等 |
| `IdentifierException` | 资源路径被翻 | 检查词典里是否有 `storage-blocks` 等 |
| NPE at `Modules.get()` | 模块名撞名 | 修正模块翻译的唯一性 |

详见 `references/meteor-guide.md`。

## 重新编译渲染器

如果目标 meteor 版本的渲染器 API 变了（`CustomTextRenderer` 方法签名不同），
用 `scripts/renderer/compile_font.py` 重新编译：

```bash
python scripts/renderer/compile_font.py \
  --javac <javac.exe> --minecraft <mc.jar> --meteor <meteor.jar> \
  --libraries <minecraft-libraries目录> --output scripts/renderer/classes
```

需要 JDK 25+，且 MC 客户端 jar 是官方未混淆版。
