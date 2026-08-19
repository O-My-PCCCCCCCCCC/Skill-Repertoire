#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract translatable string literals from a mod jar.

Usage:
  python extract_strings.py --input <mod.jar> [--output <strings.json>]

Output: { "<string>": [ "class/path", ... ] } — the strings that are safe to
translate (pure literals, not shared with field/method names), plus a human
readable summary. Combine with references/translations.json to see what's
already covered.
"""
import argparse, os, sys, json, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cp_patch import ClassFile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', default=None)
    ap.add_argument('--min-length', type=int, default=3)
    args = ap.parse_args()

    usage = {}
    with zipfile.ZipFile(args.input) as z:
        for n in z.namelist():
            if not n.endswith('.class') or n.startswith('META-INF/jars/'):
                continue
            try:
                cf = ClassFile(z.read(n))
            except Exception:
                continue
            for s in cf.string_literals():
                if len(s) >= args.min_length and s.isprintable():
                    usage.setdefault(s, []).append(n)

    print(f'classes scanned, unique printable string literals: {len(usage)}')
    # simple heuristic buckets
    import re
    kebab = sum(1 for s in usage if re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)+', s))
    print(f'  kebab identifiers: {kebab}, remaining: {len(usage)-kebab}')

    if args.output:
        json.dump(usage, open(args.output, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('saved', args.output)


if __name__ == '__main__':
    main()
