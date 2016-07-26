#!/usr/bin/env python
# -*- coding: utf8 -*-

from ctypes import *

def encipher(v, k):
    y=c_uint32(v[0]);
    z=c_uint32(v[1]);
    sum=c_uint32(0);
    delta=0x9E3779B9;
    n=32
    w=[0,0]

    while(n>0):
        sum.value += delta
        y.value += ( z.value << 4 ) + k[0] ^ z.value + sum.value ^ ( z.value >> 5 ) + k[1]
        z.value += ( y.value << 4 ) + k[2] ^ y.value + sum.value ^ ( y.value >> 5 ) + k[3]
        n -= 1

    w[0]=y.value
    w[1]=z.value
    return w

def decipher(v, k):
    y=c_uint32(v[0])
    z=c_uint32(v[1])
    sum=c_uint32(0xC6EF3720)
    delta=0x9E3779B9
    n=32
    w=[0,0]

    while(n>0):
        z.value -= ( y.value << 4 ) + k[2] ^ y.value + sum.value ^ ( y.value >> 5 ) + k[3]
        y.value -= ( z.value << 4 ) + k[0] ^ z.value + sum.value ^ ( z.value >> 5 ) + k[1]
        sum.value -= delta
        n -= 1

    w[0]=y.value
    w[1]=z.value
    return w

if __name__ == '__main__':
    key = [0xbe168aa1, 0x16c498a3, 0x5e87b018, 0x56de7805]
    v = [0, 123456]
    x = encipher(v, key)
    print x
    assert v == decipher(x, key)
