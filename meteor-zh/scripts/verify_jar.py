#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify a localized mod jar: every class re-parses, count CJK coverage.

Usage:
  python verify_jar.py --input <jar>
"""
import argparse, sys, os, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cp_patch import ClassFile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    args = ap.parse_args()

    z = zipfile.ZipFile(args.input)
    bad = 0
    classes = 0
    cjk_classes = 0
    total_literals = 0
    cjk_literals = 0
    for n in z.namelist():
        if not n.endswith('.class') or n.startswith('META-INF/jars/'):
            continue
        classes += 1
        try:
            cf = ClassFile(z.read(n))
        except Exception as e:
            bad += 1
            print('  PARSE FAIL', n, e)
            continue
        lits = cf.string_literals()
        has_cjk = False
        for s in lits:
            total_literals += 1
            if any('一' <= c <= '鿿' for c in s):
                cjk_literals += 1
                has_cjk = True
        if has_cjk:
            cjk_classes += 1

    print(f'classes parsed: {classes}, failures: {bad}')
    print(f'classes with CJK literals: {cjk_classes}')
    if total_literals:
        print(f'string literals: {total_literals}, CJK: {cjk_literals} ({100*cjk_literals/total_literals:.1f}%)')
    print('OK' if bad == 0 else 'FAILURES FOUND')


if __name__ == '__main__':
    main()
