#!/usr/bin/env python
# -*- coding: utf8 -*-

import random
import time

_r = random.Random()

def jump_basic(key, num_buckets):
    _r.seed(key)
    b = 0
    for j in xrange(1, num_buckets):
        if _r.random() < 1.0 / (j+1):
            b = j
    return b

def jump(key, num_buckets):
    # http://arxiv.org/ftp/arxiv/papers/1406/1406.2294.pdf
    _r.seed(key)
    b = -1
    j = 0
    while j < num_buckets:
        b = j
        # 主要是这里加速循环(一次性跳过多个)
        # P(j ≥ i) = P( ch(k, i) = ch(k, b+1) )
        #   P( ch(k, 10) = ch(k, 11) ) is 10/11,
        #     and P( ch(k, 11) = ch(k, 12) ) is 11/12,
        #     then P( ch(k, 10) = ch(k, 12) ) is 10/11 * 11/12 = 10/12
        #   P( ch(k, n) = ch(k, m) ) = m / n
        # P(j ≥ i) = P( ch(k, i) = ch(k, b+1) ) = (b+1) / i
        r = _r.random()
        j = int((b+1) / r)
    return b

if __name__ == '__main__':
    print jump_basic(222, 4), jump_basic(222, 4)
    print jump_basic(111, 4), jump_basic(222, 4), jump_basic(333, 4), \
        jump_basic(444, 4), jump_basic(555, 4), jump_basic(666, 4), \
        jump_basic(777, 4), jump_basic(888, 4), jump_basic(999, 4)
    print jump_basic(1111, 4), jump_basic(2222, 4), jump_basic(3333, 4), \
        jump_basic(4444, 4), jump_basic(5555, 4), jump_basic(6666, 4), \
        jump_basic(7777, 4), jump_basic(8888, 4), jump_basic(9999, 4)
    print jump_basic(11111, 4), jump_basic(22222, 4), jump_basic(33333, 4), \
        jump_basic(44444, 4), jump_basic(55555, 4), jump_basic(66666, 4), \
        jump_basic(77777, 4), jump_basic(88888, 4), jump_basic(99999, 4)

    print jump(222, 4), jump(222, 4)
    print jump(111, 4), jump(222, 4), jump(333, 4), \
        jump(444, 4), jump(555, 4), jump(666, 4), \
        jump(777, 4), jump(888, 4), jump(999, 4)
    print jump(1111, 4), jump(2222, 4), jump(3333, 4), \
        jump(4444, 4), jump(5555, 4), jump(6666, 4), \
        jump(7777, 4), jump(8888, 4), jump(9999, 4)
    print jump(11111, 4), jump(22222, 4), jump(33333, 4), \
        jump(44444, 4), jump(55555, 4), jump(66666, 4), \
        jump(77777, 4), jump(88888, 4), jump(99999, 4)

    n = 10
    bs = [0 for i in xrange(n)]
    for i in xrange(10000):
        k = random.randint(0, 100000)
        b = jump_basic(k, n)
        assert 0 <= b < n
        bs[b] += 1
    print bs

    n = 10
    bs = [0 for i in xrange(n)]
    for i in xrange(10000):
        k = random.randint(0, 100000)
        b = jump(k, n)
        assert 0 <= b < n
        bs[b] += 1
    print bs

    bgn = time.time()
    for i in xrange(1000000):
        k = random.randint(0, 10000)
        n = random.randint(3, 500)
        assert 0 <= jump_basic(k, n) < n
    end = time.time()
    print 'jump_basic:\n  %sms' % ((end - bgn) * 1000)

    bgn = time.time()
    for i in xrange(1000000):
        k = random.randint(0, 10000)
        n = random.randint(3, 500)
        assert 0 <= jump(k, n) < n
    end = time.time()
    print 'jump:\n  %sms' % ((end - bgn) * 1000)
