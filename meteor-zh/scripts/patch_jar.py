#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Localize a Minecraft Fabric mod jar (Meteor Client or an addon) to Chinese.

Usage:
  python patch_jar.py --input <mod.jar> --output <zh.jar> \
      [--translations translations.json] [--force-map force_map.json] \
      [--mode client|addon] [--font <cjk.ttf>] [--fontfix-dir <classes-dir>]

Modes:
  client — full treatment: translate strings + inject the CJK on-demand glyph
           renderer (FontFix-based CustomTextRenderer) + set a CJK default font.
           Use for the Meteor Client jar itself.
  addon  — translate strings only (the client already renders CJK). Use for
           Meteor addons / plugins.

Safety built in (each one was a real crash fixed during development):
  * Only pure string literals are translated; entries shared with field/method
    names are skipped (translating them corrupts identifiers -> ClassFormatError).
  * Force-translation of enum option identifiers runs a GLOBAL collision pre-pass:
    if two enum constants in the same enum would map to the same Chinese, both are
    left English (duplicate field names -> crash).
  * Enum constants of directly-serialized enums (XAnchor, YAnchor, ShapeMode,
    AccountType, FontInfo$Type) are excluded — translating them breaks loading
    existing configs (IllegalArgumentException: No enum constant).
  * Resource identifiers / mod-id / HTTP-header / command-name strings are never
    touched (they are not in the dictionaries).
"""
import argparse, os, sys, json, zipfile, glob, struct
from collections import defaultdict

# -- imports ---------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cp_patch import ClassFile

# -- class-file low level helpers (self-contained) -------------------------

def parse_cp(data):
    idx = 10
    count = struct.unpack('>H', data[8:10])[0]
    cp = {}
    i = 1
    while i < count:
        tag = data[idx]
        if tag == 1:
            ln = struct.unpack('>H', data[idx+1:idx+3])[0]
            cp[i] = data[idx+3:idx+3+ln].decode('utf-8', 'replace')
            idx += 3 + ln
        elif tag in (7, 8, 16, 19, 20):
            idx += 3
        elif tag == 15:
            idx += 4
        elif tag in (9, 10, 11, 12, 17, 18):
            idx += 5
        elif tag in (3, 4):
            idx += 5
        elif tag in (5, 6):
            idx += 9
            i += 1
        else:
            raise ValueError(tag)
        i += 1
    return cp, idx


def class_fields(data):
    """Return [(field_name, field_desc)] for a class."""
    cp, cpend = parse_cp(data)
    idx = cpend + 6
    ifc = struct.unpack('>H', data[idx:idx+2])[0]; idx += 2 + 2*ifc
    fc = struct.unpack('>H', data[idx:idx+2])[0]; idx += 2
    out = []
    for _ in range(fc):
        _, ni, di = struct.unpack('>HHH', data[idx:idx+6]); idx += 6
        out.append((cp.get(ni, ''), cp.get(di, '')))
        ac = struct.unpack('>H', data[idx:idx+2])[0]; idx += 2
        for _ in range(ac):
            idx += 2
            alen = struct.unpack('>I', data[idx:idx+4])[0]
            idx += 4 + alen
    return out


# -- safety pre-passes -----------------------------------------------------

def compute_collision_values(fm, class_glob):
    """Return force values that would create duplicate field names in some enum."""
    coll = set()
    for f in glob.glob(class_glob, recursive=True):
        try:
            fs = class_fields(open(f, 'rb').read())
        except Exception:
            continue
        names = [n for n, _ in fs]
        if '$VALUES' not in names:
            continue
        binname = f.replace('.class', '').replace(os.sep, '/')
        self_desc = 'L' + binname + ';'
        by_tr = defaultdict(list)
        for name, desc in fs:
            if name == '$VALUES':
                continue
            if desc == self_desc and name in fm:
                by_tr[fm[name]].append(name)
        for names2 in by_tr.values():
            if len(names2) > 1:
                for nm in names2:
                    coll.add(nm)
    return coll


def compute_serialized_constants(fm, class_glob, serialized_enums):
    """Return force values that belong to directly-serialized enums."""
    ser = set()
    for f in glob.glob(class_glob, recursive=True):
        base = os.path.basename(f)[:-6]
        if base not in serialized_enums:
            continue
        try:
            fs = class_fields(open(f, 'rb').read())
        except Exception:
            continue
        for name, _ in fs:
            if name in fm:
                ser.add(name)
    return ser


# -- main ----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='Localize a Fabric mod jar to Chinese')
    ap.add_argument('--input', required=True, help='input mod jar')
    ap.add_argument('--output', required=True, help='output localized jar')
    ap.add_argument('--translations', default=None, help='translations JSON (en->zh)')
    ap.add_argument('--force-map', default=None, help='force translation map JSON (enum options)')
    ap.add_argument('--mode', default='client', choices=['client', 'addon'],
                    help='client = full (renderer+font); addon = translate only')
    ap.add_argument('--font', default=None, help='CJK ttf to use as the default font (client mode)')
    ap.add_argument('--fontfix-dir', default=None,
                    help='dir containing compiled FontFix.class + CustomTextRenderer.class (client mode)')
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))

    def merge_dict_dir(path):
        merged = {}
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('.json'):
                    try:
                        d = json.load(open(os.path.join(root, f), encoding='utf-8'))
                        for k, v in d.items():
                            merged.setdefault(k, v)
                    except Exception:
                        pass
        return merged

    translations = {}
    if args.translations and os.path.isdir(args.translations):
        translations = merge_dict_dir(args.translations)
    elif args.translations and os.path.exists(args.translations):
        translations = json.load(open(args.translations, encoding='utf-8'))
    elif os.path.isdir(os.path.join(here, '..', 'references', 'translations')):
        translations = merge_dict_dir(os.path.join(here, '..', 'references', 'translations'))
    elif os.path.exists(os.path.join(here, '..', 'references', 'translations.json')):
        translations = json.load(open(os.path.join(here, '..', 'references', 'translations.json'), encoding='utf-8'))
    translations = {k: v for k, v in translations.items() if k != v}

    force_map = {}
    if args.force_map and os.path.exists(args.force_map):
        force_map = json.load(open(args.force_map, encoding='utf-8'))
    elif os.path.exists(os.path.join(here, '..', 'references', 'force_map.json')):
        force_map = json.load(open(os.path.join(here, '..', 'references', 'force_map.json'), encoding='utf-8'))

    class_glob = os.path.join(os.path.dirname(args.input), '**', '*.class') if False else None
    # We operate on the zip directly; compute collisions over the extracted classes
    # is expensive, so rely on the pre-filtered force_map.json + a local check on the
    # input jar's own classes.
    if not os.path.exists(args.input):
        print('input jar not found:', args.input)
        sys.exit(1)

    # Safety pass 1: collisions within the input jar's enums
    temp = {}
    with zipfile.ZipFile(args.input) as zin:
        for n in zin.namelist():
            if n.endswith('.class') and not n.startswith('META-INF/jars/'):
                try:
                    fs = class_fields(zin.read(n))
                except Exception:
                    continue
                names = [x for x, _ in fs]
                if '$VALUES' not in names:
                    continue
                binname = n[:-6].replace('/', '/')
                self_desc = 'L' + binname + ';'
                by_tr = defaultdict(list)
                for name, desc in fs:
                    if name == '$VALUES':
                        continue
                    if desc == self_desc and name in force_map:
                        by_tr[force_map[name]].append(name)
                for n2 in by_tr.values():
                    if len(n2) > 1:
                        for nm in n2:
                            temp[nm] = True
    if temp:
        print(f'  * dropped collision force values: {sorted(temp)}')
        force_map = {k: v for k, v in force_map.items() if k not in temp}

    # Safety pass 2: serialized enums
    SERIALIZED = {'XAnchor', 'YAnchor', 'ShapeMode', 'AccountType', 'FontInfo$Type'}
    ser = set()
    with zipfile.ZipFile(args.input) as zin:
        for n in zin.namelist():
            if not n.endswith('.class') or n.startswith('META-INF/jars/'):
                continue
            base = os.path.basename(n)[:-6]
            if base not in SERIALIZED:
                continue
            try:
                fs = class_fields(zin.read(n))
            except Exception:
                continue
            for name, _ in fs:
                if name in force_map:
                    ser.add(name)
    if ser:
        print(f'  * excluded serialized enum constants: {sorted(ser)}')
        force_map = {k: v for k, v in force_map.items() if k not in ser}

    # Read FontFix renderer classes (client mode)
    ff = {}
    if args.mode == 'client':
        ffdir = args.fontfix_dir or os.path.join(here, 'renderer', 'classes')
        for cls in ['CustomTextRenderer.class', 'FontFix.class', 'FontFix$CharData.class']:
            p = os.path.join(ffdir, cls)
            if os.path.exists(p):
                with open(p, 'rb') as f:
                    ff['meteordevelopment/meteorclient/renderer/text/' + cls] = f.read()

    # CJK font (client mode)
    cjk_font = None
    if args.mode == 'client' and args.font and os.path.exists(args.font):
        with open(args.font, 'rb') as f:
            cjk_font = f.read()

    zin = zipfile.ZipFile(args.input)
    names = zin.namelist()
    zout = zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED)

    used = set()
    patched = 0
    total_repl = 0
    for n in names:
        data = zin.read(n)
        if n == 'assets/meteor-client/fonts/Comfortaa.ttf' and cjk_font is not None:
            data = cjk_font
        elif n == 'meteordevelopment/meteorclient/renderer/text/CustomTextRenderer.class' and ff:
            data = ff.pop('meteordevelopment/meteorclient/renderer/text/CustomTextRenderer.class')
        elif n.endswith('.class') and not n.startswith('META-INF/jars/'):
            try:
                cf = ClassFile(data)
            except Exception:
                zout.writestr(n, data)
                continue
            n_repl = 0
            for old, new in translations.items():
                c = cf.literal_counts().get(old, 0)
                if c:
                    used.add(old)
                    n_repl += c
            present = {val for _, _, val in cf.utf8.values()} & set(force_map)
            if n_repl or present:
                nb = cf.to_bytes_force(translations, force_map)
                if nb != data:
                    data = nb
                    patched += 1
                    total_repl += n_repl
                    used |= present
        zout.writestr(n, data)
    zin.close()

    # Add renderer classes not already present
    for path, content in ff.items():
        zout.writestr(path, content)
        print(f'  * added {os.path.basename(path)}')
    zout.close()

    unused = set(translations) - used
    print(f'classes patched: {patched}, string-uses replaced: {total_repl}')
    print(f'translations used: {len(used)}, unused: {len(unused)}')
    print(f'wrote {args.output} ({os.path.getsize(args.output)} bytes)')


if __name__ == '__main__':
    main()
