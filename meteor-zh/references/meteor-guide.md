# Meteor Client 汉化：内部机制与坑

这是做字节码级汉化时踩过的真实坑和对应解法。任何版本升级或遇到新崩溃时先查这里。

## 常量池与"共享字符串"

JVM 常量池会**合并相同的 UTF-8 字符串**。所以一个枚举常量名（`Always` 字段）
和它的显示字面量（`"Always"`）经常是**同一个条目**。改它 = 同时改字段名和显示。
后果：

- 两个枚举常量映射到同一中文 → **两个字段同名** → `ClassFormatError: Duplicate field name`
- 字段名改了但别的类里的 Fieldref 没改 → **NoSuchFieldError**

解法：只翻"纯字面量"（被 `ldc` 引用、且不被任何字段/方法名引用）。枚举选项走
"强制翻译"，但加**全局冲突预检**：任何枚举里两个常量撞同名的值，整个从 force_map
移除（字段和引用都保持英文）。

## 序列化枚举

配置存枚举用的是 `Enum.valueOf(name)`。这些枚举的值**绝对不能翻译**，否则旧配置
一加载就 `IllegalArgumentException: No enum constant X`：

```
XAnchor, YAnchor, ShapeMode, AccountType, FontInfo$Type
```

（模块设置里的枚举是安全的——设置键也翻译了，旧配置的键对不上，值不会被加载。）

## 功能性字符串（绝不翻译）

- mod-id：`meteor-client`（`getModContainer("meteor-client")` 崩溃）
- 资源 Identifier 路径：`storage-blocks`（`IdentifierException: Non [a-z0-9/._-]`）
- HTTP 头名：`Accept`（`invalid header name`）
- 命令名：`name-history`, `save-map`, `fake-player` 等
- 附魔注册表 ID：`fire-aspect`, `breach`, `wind-burst` 等
- 名称本身是字段的枚举常量（`Offhand$Item` 的 `EGap`/`Gap`）

这些都在词典之外，天然不会被翻。

## 模块名翻译的坑

`Modules.add()` 有去重：同名的两个模块会互相覆盖。翻译模块名时若两个模块撞名
（如 Freecam/FreeLook 都叫"自由视角"，ESP/WallHack 都叫"透视"），后注册的会
把先注册的从注册表移除 → `get(ModuleClass)` 返回 null → NPE。翻译模块名必须
保证唯一。

## 中文字体渲染（核心）

Meteor 的自定义字体渲染器 `Font`/`CustomTextRenderer` 用 STB 打包字形时只覆盖
**0x20–0x7F**（纯 ASCII）。所以不管用啥字体，中文都渲染成空白。这也是"汉化后
文字变空气"的根因。

解法：用 **FontFix**（scripts/fontfix/）替换 `CustomTextRenderer`：

- 按需加载字形：中文字符第一次出现时实时用 STB 打包进字形表
- 一次加载全部缺失字形（避免每 100ms 只加载 7 个导致的卡顿）
- 复用纹理、缩放对齐原版（不要沿用旧版加 `/1.5` 的系数——那是 Meteor 0.6 的约定）

FontFix 渲染的是所选字体面（默认 `Comfortaa`）。要把默认字体换成中文字体：
替换 mod jar 内"字体资源文件夹下名为 Comfortaa.ttf 的那个条目"的字节（这是 jar
内的资源，不是本 skill 目录里的文件），或让用户在客户端字体设置里选系统中文字体。
FontFix 的字体缓冲来自 `FontFace.readToDirectByteBuffer()`。

## 判断崩溃

| 崩溃 | 含义 |
|------|------|
| `ClassFormatError: Duplicate field name` | force 翻译撞名，漏了冲突预检 |
| `NoSuchFieldError` | 字段名/引用不一致（冲突或序列化排除没生效） |
| `IllegalArgumentException: No enum constant` | 序列化枚举被翻译了 |
| `NoSuchElementException` at `<clinit>` | mod-id 或元数据键被翻译 |
| `IdentifierException` | 资源路径被翻译 |
| NPE at `Modules.get().get(X.class)` | 模块名撞名，模块被覆盖 |
