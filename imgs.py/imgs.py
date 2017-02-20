#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys

import os
import argparse

from PIL import Image

def gcd(a, b):
    if a < b:
        a, b = b, a
    y = a % b
    if y == 0:
        return b
    else:
        a, b = b, y
        return gcd(a, b)

def main():
    parser = argparse.ArgumentParser(description="Batch image processing")
    parser.add_argument("cmd", help='the command ("scan", "resize")')
    parser.add_argument("-i", "--in_dir", help="input directory")
    parser.add_argument("-o", "--out_dir", help="output directory")
    parser.add_argument("--width", type=int, help="output width")
    parser.add_argument("--height", type=int, help="output height")
    args = parser.parse_args()

    if args.cmd not in ("scan", "resize"):
        print 'Unknown command "%s"' % args.cmd
        return

    if not args.in_dir:
        print 'Missing "--in_dir"'
        return

    if args.cmd == "scan":
        succs = 0
        fails = 0
        sizes = {}
        ratios = {}
        for path, dirs, files in os.walk(args.in_dir):
            for bfn in files:
                fn = '%s/%s' % (path, bfn)
                try:
                    im = Image.open(fn)
                    if im.size not in sizes:
                        sizes[im.size] = 0
                    sizes[im.size] += 1
                    v = gcd(im.size[0], im.size[1])
                    ratio = (im.size[0] // v, im.size[1] // v)
                    if ratio not in ratios:
                        ratios[ratio] = 0
                    ratios[ratio] += 1
                    succs += 1
                except Exception, e:
                    fails += 1

        o_sizes = []
        for k, v in sizes.items():
            o_sizes.append((k, v))
        o_sizes.sort(key=lambda x: -x[1])
        print 'Sizes: [%s]' % len(o_sizes)
        for k, v in o_sizes:
            print '  %s: %s' % (k, v)

        o_ratios = []
        for k, v in ratios.items():
            o_ratios.append((k, v))
        o_ratios.sort(key=lambda x: -x[1])
        print 'Ratios: [%s]' % len(o_ratios)
        for k, v in o_ratios:
            print '  %s: %s' % (k, v)

        print 'succs: %s' % succs
        if fails:
            print 'fails: %s' % fails

    elif args.cmd == "resize":
        if not args.out_dir:
            print 'Missing "--out_dir"'
            return
        if not args.width:
            print 'Missing "--width"'
            return
        if not args.height:
            print 'Missing "--height"'
            return

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        succs = 0
        fails = 0
        for path, dirs, files in os.walk(args.in_dir):
            for bfn in files:
                fn = '%s/%s' % (path, bfn)
                try:
                    im = Image.open(fn)
                    im = im.resize((args.width, args.height), Image.BICUBIC)
                    im.save('%s/%s' % (args.out_dir, bfn))
                    print bfn
                    succs += 1
                except Exception, e:
                    print '[Fail]: %s' % bfn
                    fails += 1

        print 'succs: %s' % succs
        if fails:
            print 'fails: %s' % fails

if __name__ == '__main__':
    main()
