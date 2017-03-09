#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys

import os
import math
import operator
import argparse
import threading

from PIL import Image
from PIL import ImageStat
from PIL import ImageEnhance

import numpy as np

def gcd(a, b):
    if a < b:
        a, b = b, a
    y = a % b
    if y == 0:
        return b
    else:
        a, b = b, y
        return gcd(a, b)

def rgb_to_hsv(rgb):
    # Translated from source of colorsys.rgb_to_hsv
    # r,g,b should be a numpy arrays with values between 0 and 255
    # rgb_to_hsv returns an array of floats between 0.0 and 1.0.
    rgb = rgb.astype('float')
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select(
        [r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc)
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv

def hsv_to_rgb(hsv):
    # Translated from source of colorsys.hsv_to_rgb
    # h,s should be a numpy arrays with values between 0.0 and 1.0
    # v should be a numpy array with values between 0.0 and 255.0
    # hsv_to_rgb returns an array of uints between 0 and 255.
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype('uint8')
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 0] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 1] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype('uint8')

def hueChange(img, hue):
    # arr = np.array(img)
    # hsv = rgb_to_hsv(arr)
    # hsv[..., 0] = hue / 2.0 / np.pi
    # rgb = hsv_to_rgb(hsv)
    # return Image.fromarray(rgb, 'RGB')
    im_HSV = img.convert('HSV')
    hsv = np.asarray(im_HSV)
    hsv = hsv.copy()
    nh = int(hue / 2.0 / np.pi * 255)
    # oh = hsv[..., 0]
    # oh = oh.reshape(-1)
    # oh = oh * 2.0 * np.pi / 255.0
    # avg_hue = np.arctan2(np.mean(np.sin(oh)), np.mean(np.cos(oh)))
    # oh = int(avg_hue / 2.0 / np.pi * 255)
    # dh = nh - oh
    # if dh > 128:
    #     dh -= 256
    # elif dh < -128:
    #     dh += 256
    # if dh > 0:
    #     hsv[..., 0] += dh
    # else:
    #     hsv[..., 0] -= -dh
    hsv[..., 0] = nh
    im = Image.fromarray(hsv, 'HSV')
    return im.convert('RGB')

class ThreadMergedInfo(object):
    def __init__(self):
        self.succs = 0
        self.fails = 0
    def __add__(self, other):
        self.succs += other.succs
        self.fails += other.fails
        return self

def im_pkg_get(im_pkg, name):
    if name == "o":
        return im_pkg["o"]
    elif name == "L":
        if im_pkg["L"] is None:
            im_pkg["L"] = im_pkg["o"].convert('L')
        return im_pkg["L"]
    elif name == "RGB":
        if im_pkg["RGB"] is None:
            im_pkg["RGB"] = im_pkg["o"].convert('RGB')
        return im_pkg["RGB"]
    else:
        assert 0

def get_brightness(im_pkg):
    pixel, RMS, perceived, RMS_perceived = None, None, None, None
    stat = ImageStat.Stat(im_pkg_get(im_pkg, "L"))
    pixel = stat.mean[0]
    RMS = stat.rms[0]
    stat = ImageStat.Stat(im_pkg_get(im_pkg, "RGB"))
    r, g, b = stat.mean
    perceived = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    r, g, b = stat.rms
    RMS_perceived = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    return pixel, RMS, perceived, RMS_perceived

def get_contrast(im_pkg):
    Weber, Michelson, RMS = None, None, None
    im = im_pkg_get(im_pkg, "RGB")
    im_np = np.asarray(im)
    w, h = im.size
    assert im_np.shape == (h, w, 3)
    # for x in xrange(w):
    #     for y in xrange(h):
    #         r, g, b = im_np[y][x]
    #         lum = 0.2126*r + 0.7152*g + 0.0722*b
    lums = np.dot(im_np, [0.2126, 0.7152, 0.0722])
    lums = lums.reshape(h * w)
    max_lum, min_lum = np.max(lums), np.min(lums)
    if max_lum <= 1.0:
        max_lum = 1.0
    Michelson = (max_lum - min_lum) / (max_lum + min_lum)
    RMS = math.sqrt(np.var(lums))
    return Weber, Michelson, RMS

def get_hue(im_pkg):
    im = im_pkg_get(im_pkg, "RGB")
    w, h = im.size
    # arr = np.array(im)
    # hsv = rgb_to_hsv(arr)
    im_HSV = im.convert('HSV')
    hsv = np.asarray(im_HSV)
    assert hsv.shape == (h, w, 3)
    # hue = np.delete(hsv, [1, 2], axis=2) # remove SV
    hue = hsv[..., 0]
    hue = hue.reshape(h * w)
    hue = hue * 2.0 * np.pi / 255.0
    # hue = hue * 2.0 * np.pi
    avg_hue = np.arctan2(np.mean(np.sin(hue)), np.mean(np.cos(hue)))
    return avg_hue

def main():
    parser = argparse.ArgumentParser(description="Batch image processing")
    parser.add_argument("cmd",
        help='the command ("scan", "resize", "crop", "balance", "plugin")')
    parser.add_argument("-t", "--thread", type=int, default=1, help="thread number")
    parser.add_argument("-i", "--in_dir", help="input directory")
    parser.add_argument("-o", "--out_dir", help="output directory")
    parser.add_argument("-q", "--quality", type=int, default=90,
        help="quality for save")
    parser.add_argument("--scan", action='append',
        help='extra scan ("brightness", "contrast", "hue")')
    parser.add_argument("-m", "--mode", help=u'''
    resize mode
        ==>
        free:   自由缩放图片至目标尺寸,
        scale:  等比例缩放图片至目标尺寸(补黑边|Alpha通道),
        reduce: 等比例缩小图片至目标尺寸以内(保持原始比例),
    crop mode
        ==>
        border: 裁剪掉四周的纯色边框,
        center: 以--width和--height的比例生成居中的边界裁剪,
''')
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--brightness", type=float, help="balance pixel brightness")
    parser.add_argument("--contrast", type=float, help="balance RMS contrast")
    parser.add_argument("--hue", type=float, help=u"balance hue (radian: 0 ~ 2π)")
    parser.add_argument("--histogram_equalization", action='store_true',
        help="(experimental) histogram equalization")
    parser.add_argument("--plugin", help="plugin filename without '.py'")
    parser.add_argument("--function", help="plugin function name")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args = parser.parse_args()

    if args.cmd not in ("scan", "resize", "crop", "balance", "plugin"):
        print 'Unknown command "%s"' % args.cmd
        return

    if not args.in_dir:
        print 'Missing "--in_dir"'
        return

    def threading_process_path(ThreadMergedInfo_obj, ThreadMergedInfo_cls,
        handle_one_func):
        path_bfn_list = []
        for path, dirs, files in os.walk(args.in_dir):
            for bfn in files:
                path_bfn_list.append((path, bfn))

        thread_len = len(path_bfn_list) // args.thread
        assert thread_len > 0

        path_bfn_lists = []
        objs = []
        for i in xrange(args.thread):
            if i != args.thread - 1:
                path_bfn_lists.append(
                    path_bfn_list[i*thread_len : (i+1)*thread_len])
            else:
                path_bfn_lists.append(path_bfn_list[i*thread_len : ])
            objs.append(ThreadMergedInfo_cls())

        def thread_task(path_bfn_list, obj, task_id):
            for path, bfn in path_bfn_list:
                handle_one_func(path, bfn, obj, task_id)

        ts = []
        for i in xrange(args.thread):
            t = threading.Thread(target=thread_task,
                args=(path_bfn_lists[i], objs[i], i+1))
            t.setDaemon(True)
            t.start()
            ts.append(t)

        for t in ts:
            t.join()

        for o in objs:
            ThreadMergedInfo_obj += o

    if args.cmd == "scan":

        scan_brightness = False
        scan_contrast = False
        scan_hue = False
        if args.scan:
            for s in args.scan:
                if s == "brightness":
                    scan_brightness = True
                elif s == "contrast":
                    scan_contrast = True
                elif s == "hue":
                    scan_hue = True
                else:
                    print 'Unknown scan "%s" for scan' % s
                    return

        class ScanInfo(ThreadMergedInfo):
            def __init__(self):
                super(ScanInfo, self).__init__()
                self.sizes = {}
                self.ratios = {}
                self.brightnesses_pixel = []
                self.brightnesses_RMS = []
                self.brightnesses_perceived = []
                self.brightnesses_RMS_perceived = []
                self.contrasts_Weber = []
                self.contrasts_Michelson = []
                self.contrasts_RMS = []
                self.hues = []
            def __add__(self, other):
                super(ScanInfo, self).__add__(other)
                for k, v in other.sizes.items():
                    if k not in self.sizes:
                        self.sizes[k] = v
                    else:
                        self.sizes[k] += v
                for k, v in other.ratios.items():
                    if k not in self.ratios:
                        self.ratios[k] = v
                    else:
                        self.ratios[k] += v
                self.brightnesses_pixel += other.brightnesses_pixel
                self.brightnesses_RMS += other.brightnesses_RMS
                self.brightnesses_perceived += other.brightnesses_perceived
                self.brightnesses_RMS_perceived += other.brightnesses_RMS_perceived
                self.contrasts_Weber += other.contrasts_Weber
                self.contrasts_Michelson += other.contrasts_Michelson
                self.contrasts_RMS += other.contrasts_RMS
                self.hues += other.hues
                return self

        def handle_one(path, bfn, obj, task_id=0):
            fn = '%s/%s' % (path, bfn)
            try:
                im = Image.open(fn)
                if im.size not in obj.sizes:
                    obj.sizes[im.size] = 1
                else:
                    obj.sizes[im.size] += 1
                v = gcd(im.size[0], im.size[1])
                ratio = (im.size[0] // v, im.size[1] // v)
                if ratio not in obj.ratios:
                    obj.ratios[ratio] = 0
                obj.ratios[ratio] += 1
                im_pkg = {
                    "o": im,
                    "L": im if im.mode == "L" else None,
                    "RGB": im if im.mode == "RGB" else None,
                }
                if scan_brightness:
                    bs = get_brightness(im_pkg)
                    if bs[0] is not None:
                        obj.brightnesses_pixel.append(bs[0])
                    if bs[1] is not None:
                        obj.brightnesses_RMS.append(bs[1])
                    if bs[2] is not None:
                        obj.brightnesses_perceived.append(bs[2])
                    if bs[3] is not None:
                        obj.brightnesses_RMS_perceived.append(bs[3])
                    if args.verbose >= 2:
                        print '%s brightness: %s' % (bfn, bs)
                if scan_contrast:
                    cs = get_contrast(im_pkg)
                    if cs[0] is not None:
                        obj.contrasts_Weber.append(cs[0])
                    if cs[1] is not None:
                        obj.contrasts_Michelson.append(cs[1])
                    if cs[2] is not None:
                        obj.contrasts_RMS.append(cs[2])
                    if args.verbose >= 2:
                        print '%s contrast: %s' % (bfn, cs)
                if scan_hue:
                    hue = get_hue(im_pkg)
                    obj.hues.append(hue)
                    if args.verbose >= 2:
                        print '%s hue: %s' % (bfn, hue)
                obj.succs += 1
            except Exception, e:
                print '[Fail]: %s\n  %s' % (bfn, e)
                obj.fails += 1

        obj = ScanInfo()

        if args.thread == 1:
            for path, dirs, files in os.walk(args.in_dir):
                for bfn in files:
                    handle_one(path, bfn, obj)

        else:
            threading_process_path(obj, ScanInfo, handle_one)

        o_sizes = []
        for k, v in obj.sizes.items():
            o_sizes.append((k, v))
        o_sizes.sort(key=lambda x: -x[1])
        print 'Sizes: [%s]' % len(o_sizes)
        for k, v in o_sizes:
            print '  %s: %s' % (k, v)

        o_ratios = []
        for k, v in obj.ratios.items():
            o_ratios.append((k, v))
        o_ratios.sort(key=lambda x: -x[1])
        print 'Ratios: [%s]' % len(o_ratios)
        for k, v in o_ratios:
            print '  %s: %s' % (k, v)

        def avg(_list):
            return float(sum(_list)) / len(_list)

        if obj.brightnesses_pixel:
            print 'Brightness:'
            print '  %s by %s images (pixel)' % (
                avg(obj.brightnesses_pixel),
                len(obj.brightnesses_pixel))
            print '  %s by %s images (RMS)' % (
                avg(obj.brightnesses_RMS),
                len(obj.brightnesses_RMS))
            if obj.brightnesses_perceived:
                print '  %s by %s images (pixel perceived)' % (
                    avg(obj.brightnesses_perceived),
                    len(obj.brightnesses_perceived))
                print '  %s by %s images (RMS perceived)' % (
                avg(obj.brightnesses_RMS_perceived),
                len(obj.brightnesses_RMS_perceived))

        if scan_contrast:
            print 'Contrast:'
            if obj.contrasts_Weber:
                print '  %s by %s images (Weber)' % (
                    avg(obj.contrasts_Weber),
                    len(obj.contrasts_Weber))
            if obj.contrasts_Michelson:
                print '  %s by %s images (Michelson)' % (
                    avg(obj.contrasts_Michelson),
                    len(obj.contrasts_Michelson))
            if obj.contrasts_RMS:
                print '  %s by %s images (RMS)' % (
                    avg(obj.contrasts_RMS),
                    len(obj.contrasts_RMS))

        if obj.hues:
            print 'Hue: %s' % (
                np.arctan2(np.mean(np.sin(obj.hues)), np.mean(np.cos(obj.hues))))

        print 'succs: %s' % obj.succs
        if obj.fails:
            print 'fails: %s' % obj.fails

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
        if not args.mode:
            print 'Missing "--mode"'
            return

        if args.mode not in ("free", "scale", "reduce"):
            print 'Unknown mode "%s" for resize' % args.mode
            return

        assert args.width > 0
        assert args.height > 0

        width = args.width
        height = args.height

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        def handle_one(path, bfn, obj, task_id=0):
            fn = '%s/%s' % (path, bfn)
            try:
                im = Image.open(fn)
                if args.mode == "free":
                    im = im.resize((width, height), Image.BICUBIC)
                elif args.mode == "scale":
                    sw, sh = im.size
                    nim = Image.new(im.mode, (width, height))
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
                    im = nim
                elif args.mode == "reduce":
                    sw, sh = im.size
                    if sw > width or sh > height:
                        if sw * 1.0 / width > sh * 1.0 / height:
                            dw = width
                            dh = int(sh * 1.0 * width / sw)
                        else:
                            dh = height
                            dw = int(sw * 1.0 * height / sh)
                        assert dw <= width
                        assert dh <= height
                        im = im.resize((dw, dh), Image.BICUBIC)
                else:
                    assert 0
                im.save('%s/%s' % (args.out_dir, bfn), quality=args.quality)
                if task_id:
                    print '[%s] %s' % (task_id, bfn)
                else:
                    print bfn
                obj.succs += 1
            except Exception, e:
                if task_id:
                    print '[%s] [Fail]: %s\n  %s' % (task_id, bfn, e)
                else:
                    print '[Fail]: %s\n  %s' % (bfn, e)
                obj.fails += 1

        obj = ThreadMergedInfo()

        if args.thread == 1:
            for path, dirs, files in os.walk(args.in_dir):
                for bfn in files:
                    handle_one(path, bfn, obj)

        else:
            threading_process_path(obj, ThreadMergedInfo, handle_one)

        print 'succs: %s' % obj.succs
        if obj.fails:
            print 'fails: %s' % obj.fails

    elif args.cmd == "crop":
        if not args.out_dir:
            print 'Missing "--out_dir"'
            return
        if not args.mode:
            print 'Missing "--mode"'
            return

        if args.mode not in ("border", "center"):
            print 'Unknown mode "%s" for crop' % args.mode
            return

        if args.mode == "center":
            if not args.width:
                print 'Missing "--width"'
                return
            if not args.height:
                print 'Missing "--height"'
                return

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        def h_pixels(im, y):
            pixels = []
            width = im.size[0]
            for x in xrange(width):
                pixels.append(im.getpixel((x, y)))
            return pixels

        def v_pixels(im, x):
            pixels = []
            height = im.size[1]
            for y in xrange(height):
                pixels.append(im.getpixel((x, y)))
            return pixels

        def h_pixels_v2(im_np, y):
            return im_np[y,:]

        def v_pixels_v2(im_np, x):
            return im_np[:,x]

        def handle_one(path, bfn, obj, task_id=0):
            fn = '%s/%s' % (path, bfn)
            try:
                im = Image.open(fn)
                if args.mode == "border":
                    if im.mode != "L":
                        im2 = im.convert('L')
                    else:
                        im2 = im
                    w, h = im2.size
                    im_np = np.asarray(im2)
                    # top -> bottom
                    top = 0
                    while top < h - 2:
                        # pixels = h_pixels(im2, top)
                        # pixels = np.array(pixels)
                        pixels = h_pixels_v2(im_np, top)
                        if np.var(pixels) > 4.0:
                            break
                        top += 1
                    # bottom -> top
                    bottom = h - 1
                    while bottom > top + 1:
                        # pixels = h_pixels(im2, bottom)
                        # pixels = np.array(pixels)
                        pixels = h_pixels_v2(im_np, bottom)
                        if np.var(pixels) > 4.0:
                            break
                        bottom -= 1
                    # left -> right
                    left = 0
                    while left < w - 2:
                        # pixels = v_pixels(im2, left)
                        # pixels = np.array(pixels)
                        pixels = v_pixels_v2(im_np, left)
                        if np.var(pixels) > 4.0:
                            break
                        left += 1
                    # right -> left
                    right = w - 1
                    while right > left + 1:
                        # pixels = v_pixels(im2, right)
                        # pixels = np.array(pixels)
                        pixels = v_pixels_v2(im_np, right)
                        if np.var(pixels) > 4.0:
                            break
                        right -= 1
                    #print top, bottom, left, right
                    assert top < bottom
                    assert left < right
                    assert top >= 0
                    assert bottom < h
                    assert left >= 0
                    assert right < w
                    im = im.crop((left, top, right + 1, bottom + 1))
                elif args.mode == "center":
                    width, height = args.width, args.height
                    sw, sh = im.size
                    if sw * 1.0 / width > sh * 1.0 / height:
                        dh = sh
                        dw = int(width * 1.0 * sh / height)
                    else:
                        dw = sw
                        dh = int(height * 1.0 * sw / width)
                    assert dw <= sw
                    assert dh <= sh
                    bx = (sw - dw) / 2
                    by = (sh - dh) / 2
                    im = im.crop((bx, by, bx + dw, by + dh))
                else:
                    assert 0
                im.save('%s/%s' % (args.out_dir, bfn), quality=args.quality)
                if task_id:
                    print '[%s] %s' % (task_id, bfn)
                else:
                    print bfn
                obj.succs += 1
            except Exception, e:
                if task_id:
                    print '[%s] [Fail]: %s\n  %s' % (task_id, bfn, e)
                else:
                    print '[Fail]: %s\n  %s' % (bfn, e)
                obj.fails += 1

        obj = ThreadMergedInfo()

        if args.thread == 1:
            for path, dirs, files in os.walk(args.in_dir):
                for bfn in files:
                    handle_one(path, bfn, obj)

        else:
            threading_process_path(obj, ThreadMergedInfo, handle_one)

        print 'succs: %s' % obj.succs
        if obj.fails:
            print 'fails: %s' % obj.fails

    elif args.cmd == "balance":
        if not args.out_dir:
            print 'Missing "--out_dir"'
            return

        if not args.brightness and \
            not args.contrast and \
            not args.hue and \
            not args.histogram_equalization:
            print 'Missing balance setting'
            return

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        def handle_one(path, bfn, obj, task_id=0):
            fn = '%s/%s' % (path, bfn)
            try:
                im = Image.open(fn)
                im_pkg = {
                    "o": im,
                    "L": im if im.mode == "L" else None,
                    "RGB": im if im.mode == "RGB" else None,
                }
                if args.brightness:
                    stat = ImageStat.Stat(im_pkg_get(im_pkg, "L"))
                    pixel = stat.mean[0]
                    if pixel < 0.001:
                        pixel = 0.001
                    factor = args.brightness / pixel
                    im = ImageEnhance.Brightness(im).enhance(factor)
                if args.contrast:
                    Weber, Michelson, RMS = get_contrast(im_pkg)
                    if RMS < 0.001:
                        RMS = 0.001
                    factor = args.contrast / RMS
                    im = ImageEnhance.Contrast(im).enhance(factor)
                if args.hue:
                    im = hueChange(im_pkg_get(im_pkg, "RGB"), args.hue)
                if args.histogram_equalization:
                    h = im_pkg_get(im_pkg, "L").histogram()
                    lut = [] # equalization lookup table
                    for b in range(0, len(h), 256):
                        step = reduce(operator.add, h[b:b+256]) / 255
                        n = 0
                        for i in range(256):
                            lut.append(n / step)
                            n = n + h[i+b]
                    im = im.point(lut * im.layers)
                im.save('%s/%s' % (args.out_dir, bfn), quality=args.quality)
                if task_id:
                    print '[%s] %s' % (task_id, bfn)
                else:
                    print bfn
                obj.succs += 1
            except Exception, e:
                if task_id:
                    print '[%s] [Fail]: %s\n  %s' % (task_id, bfn, e)
                else:
                    print '[Fail]: %s\n  %s' % (bfn, e)
                obj.fails += 1

        obj = ThreadMergedInfo()

        if args.thread == 1:
            for path, dirs, files in os.walk(args.in_dir):
                for bfn in files:
                    handle_one(path, bfn, obj)

        else:
            threading_process_path(obj, ThreadMergedInfo, handle_one)

        print 'succs: %s' % obj.succs
        if obj.fails:
            print 'fails: %s' % obj.fails

    elif args.cmd == "plugin":
        if not args.plugin:
            print 'Missing "--plugin"'
            return
        if not args.function:
            print 'Missing "--function"'
            return

        plugin = __import__(args.plugin)
        func = getattr(plugin, args.function)

        if args.out_dir and not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        def handle_one(path, bfn, obj, task_id=0):
            fn = '%s/%s' % (path, bfn)
            try:
                func(path, bfn, args.out_dir)
                if task_id:
                    print '[%s] %s' % (task_id, bfn)
                else:
                    print bfn
                obj.succs += 1
            except Exception, e:
                if task_id:
                    print '[%s] [Fail]: %s\n  %s' % (task_id, bfn, e)
                else:
                    print '[Fail]: %s\n  %s' % (bfn, e)
                obj.fails += 1

        obj = ThreadMergedInfo()

        if args.thread == 1:
            for path, dirs, files in os.walk(args.in_dir):
                for bfn in files:
                    handle_one(path, bfn, obj)

        else:
            threading_process_path(obj, ThreadMergedInfo, handle_one)

        print 'succs: %s' % obj.succs
        if obj.fails:
            print 'fails: %s' % obj.fails

if __name__ == '__main__':
    main()
