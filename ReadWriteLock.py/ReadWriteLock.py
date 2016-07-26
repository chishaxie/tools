#!/usr/bin/env python
# -*- coding: utf8 -*-

import threading

class ReadWriteLock(object):

    def __init__(self):
        self.wl = threading.Lock()
        self.rc = threading.Lock()
        self.rl = threading.Lock()
        self.reader_count = 0

    def acquire_read(self):
        self.wl.acquire()
        self.rc.acquire()
        self.reader_count += 1
        if self.reader_count == 1:
            self.rl.acquire()
        self.rc.release()
        self.wl.release()

    def release_read(self):
        self.rc.acquire()
        self.reader_count -= 1
        if self.reader_count == 0:
            self.rl.release()
        self.rc.release()

    def acquire_write(self):
        self.wl.acquire()
        self.rl.acquire()

    def release_write(self):
        self.rl.release()
        self.wl.release()
