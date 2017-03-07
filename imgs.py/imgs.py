#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys

import os
import argparse
import threading

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

class ThreadMergedInfo(object):
    def __init__(self):
        self.succs = 0
        self.fails = 0
    def __add__(self, other):
        self.succs += other.succs
        self.fails += other.fails
        return self

def main():
    parser = argparse.ArgumentParser(description="Batch image processing")
    parser.add_argument("cmd", help='the command ("scan", "resize", "plugin")')
    parser.add_argument("-t", "--thread", type=int, default=1, help="thread number")
    parser.add_argument("-i", "--in_dir", help="input directory")
    parser.add_argument("-o", "--out_dir", help="output directory")
    parser.add_argument("--width", type=int, help="output width")
    parser.add_argument("--height", type=int, help="output height")
    parser.add_argument("-m", "--mode", help=u'''resize mode
        ==>
        free:   自由缩放图片至目标尺寸,
        scale:  等比例缩放图片至目标尺寸(补黑边|Alpha通道),
        reduce: 等比例缩小图片至目标尺寸以内(保持原始比例),
''')
    parser.add_argument("--plugin", help="plugin filename without '.py'")
    parser.add_argument("--function", help="plugin function name")
    args = parser.parse_args()

    if args.cmd not in ("scan", "resize", "plugin"):
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

        class ScanInfo(ThreadMergedInfo):
            def __init__(self):
                super(ScanInfo, self).__init__()
                self.sizes = {}
                self.ratios = {}
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
                    print '[%s] [Fail]: %s' % (task_id, bfn)
                else:
                    print '[Fail]: %s' % bfn
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
