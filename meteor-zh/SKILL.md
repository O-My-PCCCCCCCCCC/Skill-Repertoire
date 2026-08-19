---
name: meteor-zh
description: >-
  Localize a Minecraft Fabric mod jar (Meteor Client or its addons/plugins) to
  Simplified Chinese by safely rewriting the compiled bytecode strings, and make
  the Chinese actually render by injecting an on-demand CJK glyph renderer.
  Use this whenever the user wants a Chinese/汉化 version of Meteor Client or any
  Meteor addon/mod jar ("汉化 meteor", "给这个 mod 出中文版", "translate meteor
  client to chinese", "localize this fabric mod"), even if they don't say the
  word "translate". Works on any Fabric mod jar: Meteor Client jar = full treatment,
  addon/plugin jar = translate-only.
---

# Meteor Client / Fabric Mod 汉化 (Chinese localization)

> ⚠️ **仅供学习使用 · 禁止商用 · 禁止二次售卖 · 禁止未经授权再分发（含修改版）**

Turn any Fabric mod jar into a Simplified-Chinese version by safely rewriting the
compiled bytecode, then make the Chinese render with a bundled on-demand CJK
renderer (needed because Meteor's own custom font renderer only rasterizes ASCII).

## How it works (why it's non-trivial)

Minecraft mods hardcode UI strings in English inside `.class` bytecode. A naive
string replace breaks the game. The important rules that keep the result stable:

- **Translate only "pure literals"** — a constant-pool string entry is only
  translated if it is used as a display string (`ldc`) AND not also used as a
  field/method name. javac merges identical strings, so an enum constant name and
  its display literal often share one entry; translating it corrupts identifiers.
- **Enum options need force-translation with collision safety** — dropdown option
  names like `Always`/`None` are enum constant field names. To translate them you
  must translate the field name AND every reference consistently. Two constants
  mapping to the same Chinese = duplicate field name = `ClassFormatError`, so a
  global collision pre-pass removes those values (they stay English).
- **Never translate directly-serialized enums** — enums stored in config and
  loaded back via `Enum.valueOf(name)` (e.g. `XAnchor`, `YAnchor`, `ShapeMode`,
  `AccountType`, `FontInfo$Type`) must stay English, or loading an existing config
  throws `IllegalArgumentException: No enum constant`.
- **Never translate functional identifiers** — mod-id (`meteor-client`), resource
  Identifier paths (`storage-blocks`), HTTP header names (`Accept`), command names.
  These live outside the dictionaries so they are untouched.
- **Chinese display needs a CJK renderer** — Meteor's `Font`/`CustomTextRenderer`
  only pack glyphs for chars 0x20–0x7F. Even with a CJK font, Chinese renders
  blank. The fix is replacing `CustomTextRenderer` with the bundled `FontFix`
  renderer (on-demand glyph loading), plus setting a CJK font as the default.

## Inputs

| Input | Mode | What happens |
|-------|------|--------------|
| Meteor Client jar (`meteor-client-*.jar`) | `client` | translate + inject CJK renderer + set CJK font |
| Meteor addon / plugin jar | `addon` | translate only (client already renders CJK) |
| Any other Fabric mod jar | `addon` | translate only |

## Workflow

### Step 0 — Determine mode

If the jar's `fabric.mod.json` `id` is `meteor-client`, it is **client** mode.
Anything else (an addon that `depends` on `meteor-client`) is **addon** mode.

### Step 1 — Extract strings

```bash
python scripts/extract_strings.py --input <mod.jar> --output strings.json
```

This lists every translatable string literal per class. Compare against
`references/translations/` (the bundled 4300-entry dictionary from the
Meteor 26.1 client) to see what's already covered.

### Step 2 — Translate the uncovered strings

The bundled dictionary covers the Meteor 26.1 strings. For strings not in it
(new version, addon, mod):

1. Group them by class/context (module names, settings, descriptions, GUI labels,
   chat messages).
2. Translate the user-visible ones to natural Simplified Chinese. Keep `%s`, `%d`,
   `(highlight)/(default)` formatting placeholders, and `\x01` control chars.
3. Do NOT translate: regexes, URLs, file paths, JSON/NBT/starscript examples,
   class/method names, packet class names, command syntax.
4. Merge the new entries into a working dictionary JSON `{en: zh}`.

### Step 3 — Build the force map (client jar only)

The bundled `references/force_map.json` has the known enum-option force
translations. For a new version, add translated enum options the same way: short
words that are enum constants. The patcher already drops collision values and
serialized-enum constants automatically.

### Step 4 — Patch

```bash
# client mode (Meteor Client jar)
python scripts/patch_jar.py \
  --input <meteor.jar> --output <meteor-zh.jar> \
  --translations <merged.json> --force-map references/force_map.json \
  --mode client \
  --font <cjk-font.ttf> \
  --fontfix-dir scripts/renderer/classes

# addon mode (any other jar)
python scripts/patch_jar.py \
  --input <addon.jar> --output <addon-zh.jar> \
  --translations <merged.json> --force-map references/force_map.json \
  --mode addon
```

The client jar additionally gets the `CustomTextRenderer` replaced with the
FontFix on-demand renderer and (if `--font` given) the default font swapped for
the CJK font.

### Step 5 — CJK font (client mode)

The renderer draws whatever font face is selected; the default is `Comfortaa`.
Pick a CJK font:

- Prefer a system font: `C:\Windows\Fonts\msyh.ttc` (Microsoft YaHei, Windows),
  `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` (Linux),
  `/System/Library/Fonts/PingFang.ttc` (macOS).
- Or ask the user for a `.ttf`/`.ttc` they want to use.
- The patcher replaces the mod's default font resource (the file named
  `Comfortaa.ttf` under the font resources folder) with the chosen font.

If no font is available, tell the user the translation is done but Chinese needs a
CJK font selected (they can put one in and rerun, or pick a system font in the
client's font setting).

### Step 6 — Verify

```bash
python scripts/verify_jar.py --input <output.jar>
```

Must report `failures: 0`. If failures, the patching hit something unexpected —
re-inspect that class rather than disabling the safety checks.

### Step 7 — Deliver

Copy the output jar into the user's `mods/` folder, replacing the original
meteor jar (only ONE meteor jar allowed). Tell them:

- Module/setting configs reset once (identifiers changed to Chinese).
- Commands now use Chinese module names (`.toggle 杀戮光环`).
- Addon text is translated but the addon must load against the same meteor version.

## Tips

- A fresh test is a good idea after any version bump: run `verify_jar.py`, then
  have the user launch and report any crash. Crash classes to recognize:
  `NoSuchFieldError` = a translated reference didn't match its field (force-map
  collision/serialization exclusion issue); `IllegalArgumentException: No enum
  constant` = a serialized enum got translated; `ClassFormatError` = duplicate
  field names.
- For a Meteor **addon**, skip the font/renderer entirely (mode `addon`) — the
  client jar already renders CJK; translating the addon's strings is enough.
- Recompile the renderer (see `scripts/renderer/compile_font.py`) if targeting a
  meteor version whose `CustomTextRenderer` API changed. Requires a JDK and the
  meteor jar + MC classes on the classpath.
