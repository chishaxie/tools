#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys

from PIL import Image

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'Usage: python img_resize.py <width> <height> <src> <dst>'
        sys.exit()

    width = int(sys.argv[1])
    height = int(sys.argv[2])
    src = sys.argv[3]
    dst = sys.argv[4]

    assert width > 0
    assert height > 0

    im = Image.open(src)
    nim = Image.new(im.mode, (width, height))
    sw, sh = im.size

    if sw * 1.0 / width > sh * 1.0 / height:
        dw = width
        dh = int(sh * 1.0 * width / sw)
    else:
        dh = height
        dw = int(sw * 1.0 * height / sh)

    assert dw <= width
    assert dh <= height

    im = im.resize((dw, dh), Image.BICUBIC)

    bx = (width - dw) / 2
    by = (height - dh) / 2

    nim.paste(im, (bx, by))
    nim.save(dst)
