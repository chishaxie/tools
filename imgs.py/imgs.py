#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys

import os
import math
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

class ThreadMergedInfo(object):
    def __init__(self):
        self.succs = 0
        self.fails = 0
    def __add__(self, other):
        self.succs += other.succs
        self.fails += other.fails
        return self

def get_brightness(im):
    pixel, RMS, perceived, RMS_perceived = None, None, None, None
    if im.mode == "RGB":
        stat = ImageStat.Stat(im)
        r, g, b = stat.mean
        perceived = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
        r, g, b = stat.rms
        RMS_perceived = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
    if im.mode != "L":
        im = im.convert('L')
    stat = ImageStat.Stat(im)
    pixel = stat.mean[0]
    RMS = stat.rms[0]
    return pixel, RMS, perceived, RMS_perceived

def main():
    parser = argparse.ArgumentParser(description="Batch image processing")
    parser.add_argument("cmd",
        help='the command ("scan", "resize", "crop", "balance", "plugin")')
    parser.add_argument("-t", "--thread", type=int, default=1, help="thread number")
    parser.add_argument("-i", "--in_dir", help="input directory")
    parser.add_argument("-o", "--out_dir", help="output directory")
    parser.add_argument("--scan", nargs='+',
        help='extra scan ("brightness")')
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
    parser.add_argument("--width", type=int, help="output width")
    parser.add_argument("--height", type=int, help="output height")
    parser.add_argument("--brightness", type=float, help="balance pixel brightness")
    parser.add_argument("--plugin", help="plugin filename without '.py'")
    parser.add_argument("--function", help="plugin function name")
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
        if args.scan:
            for s in args.scan:
                if s == "brightness":
                    scan_brightness = True
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
                if scan_brightness:
                    bs = get_brightness(im)
                    if bs[0] is not None:
                        obj.brightnesses_pixel.append(bs[0])
                    if bs[1] is not None:
                        obj.brightnesses_RMS.append(bs[1])
                    if bs[2] is not None:
                        obj.brightnesses_perceived.append(bs[2])
                    if bs[3] is not None:
                        obj.brightnesses_RMS_perceived.append(bs[3])
                obj.succs += 1
            except Exception, e:
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
                im.save('%s/%s' % (args.out_dir, bfn))
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
                im.save('%s/%s' % (args.out_dir, bfn))
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

        if not args.brightness:
            print 'Missing balance setting'
            return

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        def handle_one(path, bfn, obj, task_id=0):
            fn = '%s/%s' % (path, bfn)
            try:
                im = Image.open(fn)
                if args.brightness:
                    if im.mode != "L":
                        im2 = im.convert('L')
                    else:
                        im2 = im
                    stat = ImageStat.Stat(im2)
                    pixel = stat.mean[0]
                    if pixel < 0.001:
                        pixel = 0.001
                    factor = args.brightness / pixel
                    im = ImageEnhance.Brightness(im).enhance(factor)
                im.save('%s/%s' % (args.out_dir, bfn))
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
