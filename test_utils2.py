#!/usr/bin/env python
# encoding: utf-8
u"""
@version: ??
@author: shaofeng.yang
@contact: marvin_yang@novowater.com.cn
@software: PyCharm Community Edition
@file: test_utils.py
@time: 2017/9/12 18:18
"""

from utils import *

def test_to_bytes():
    s = b'c'
    t = to_bytes('c')
    assert t == s

def test_to_bytes4():
    s = b'c'
    t = to_bytes('c')
    assert t == 'g'