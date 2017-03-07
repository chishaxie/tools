#!/usr/bin/env python
# -*- coding: utf8 -*-

import struct

import sysv_ipc

MAGIC_BGN = 0x20170306
MAGIC_END = 0x20170307
HEAD_LEN = 20

class IPC_MsgQ(object):
    def __init__(self, shm_key, lock_key, msg_size, queue_len):
        self.msg_size = msg_size
        self.queue_len = queue_len
        self.mem_size = HEAD_LEN + msg_size * queue_len
        self.mem = sysv_ipc.SharedMemory(shm_key,
            flags=sysv_ipc.IPC_CREAT, mode=0600, size=self.mem_size)
        assert self.mem_size == self.mem.size
        self.lock = sysv_ipc.Semaphore(lock_key,
            flags=sysv_ipc.IPC_CREAT, mode=0600, initial_value=1)
        self.lock.acquire()
        head_buff = self.mem.read(HEAD_LEN, offset=0)
        _mb, msg_bgn, msg_end, msg_cnt, _me = struct.unpack('!5I', head_buff)
        if (_mb, msg_bgn, msg_end, msg_cnt, _me) == (0, 0, 0, 0, 0):
            _mb = MAGIC_BGN
            _me = MAGIC_END
            head_buff = struct.pack('!5I', _mb, msg_bgn, msg_end, msg_cnt, _me)
            self.mem.write(head_buff, offset=0)
            print 'IPC_MsgQ: init bytes=%s' % self.mem_size
        self.lock.release()
        assert _mb == MAGIC_BGN
        assert _me == MAGIC_END

    def put(self, buff):
        ret = True
        assert len(buff) == self.msg_size
        self.lock.acquire()
        head_buff = self.mem.read(HEAD_LEN, offset=0)
        _mb, msg_bgn, msg_end, msg_cnt, _me = struct.unpack('!5I', head_buff)
        # print msg_bgn, msg_end, msg_cnt
        if msg_cnt < self.queue_len:
            msg_cnt += 1
            self.mem.write(buff, offset=HEAD_LEN+msg_end*self.msg_size)
            msg_end = (msg_end + 1) % self.queue_len
            head_buff = struct.pack('!5I', _mb, msg_bgn, msg_end, msg_cnt, _me)
            self.mem.write(head_buff, offset=0)
        else:
            ret = False
        self.lock.release()
        return ret

    def get(self):
        ret = None
        self.lock.acquire()
        head_buff = self.mem.read(HEAD_LEN, offset=0)
        _mb, msg_bgn, msg_end, msg_cnt, _me = struct.unpack('!5I', head_buff)
        # print msg_bgn, msg_end, msg_cnt
        if msg_cnt > 0:
            msg_cnt -= 1
            ret = self.mem.read(self.msg_size, offset=HEAD_LEN+msg_bgn*self.msg_size)
            msg_bgn = (msg_bgn + 1) % self.queue_len
            head_buff = struct.pack('!5I', _mb, msg_bgn, msg_end, msg_cnt, _me)
            self.mem.write(head_buff, offset=0)
        self.lock.release()
        return ret

if __name__ == '__main__':
    import time
    mq = IPC_MsgQ(0x20170306, 0x20170307, 10, 4)
    print mq.get()
    print mq.put('aaaaaaaaaa')
    print mq.put('bbbbbbbbbb')
    print mq.get()
    print mq.put('cccccccccc')
    print mq.put('dddddddddd')
    print mq.put('eeeeeeeeee')
    print mq.put('ffffffffff')
    print mq.get()
    print mq.get()
    print mq.get()
    time.sleep(3)
    print 'acquire ...'
    mq.lock.acquire()
    print 'acquire .'
    time.sleep(10)
    mq.lock.release()
    print 'release .'
