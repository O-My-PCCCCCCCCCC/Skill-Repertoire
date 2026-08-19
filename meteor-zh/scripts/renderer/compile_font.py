#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compile FontFix + CustomTextRenderer against a given Minecraft + meteor setup.

The bundled pre-compiled classes in ./classes work for the Meteor 26.1.x client.
Recompile only if the target meteor version's renderer API changed.

Usage:
  python compile_font.py --javac <javac.exe> \
      --minecraft <mc-client.jar> --meteor <meteor.jar> \
      --libraries <minecraft-libraries-dir> --output <out-dir>
"""
import argparse, os, subprocess


def build_classpath(mc_jar, meteor_jar, libs_dir):
    parts = [mc_jar, meteor_jar]
    if os.path.isdir(libs_dir):
        for root, dirs, files in os.walk(libs_dir):
            for f in files:
                if f.endswith('.jar'):
                    parts.append(os.path.join(root, f))
    return ';'.join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--javac', required=True)
    ap.add_argument('--minecraft', required=True, help='MC client jar (official/unobfuscated)')
    ap.add_argument('--meteor', required=True, help='meteor client jar')
    ap.add_argument('--libraries', default='', help='MC libraries dir (for LWJGL, fastutil, ...)')
    ap.add_argument('--output', default='classes')
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    src = [os.path.join(here, 'FontFix.java'), os.path.join(here, 'CustomTextRenderer.java')]
    os.makedirs(args.output, exist_ok=True)

    env = dict(os.environ)
    env['CLASSPATH'] = build_classpath(args.minecraft, args.meteor, args.libraries)
    cmd = [args.javac, '-encoding', 'UTF-8', '-d', os.path.abspath(args.output)] + src
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(r.stdout)
    print(r.stderr)
    print('exit:', r.returncode)
    if r.returncode == 0:
        print('classes written to', args.output)


if __name__ == '__main__':
    main()
