# -*- coding: utf8 -*-
u'''
Created on 2017年8月22日 上午11:45:59

@author: shaofeng.yang
'''

from binascii import b2a_hex
from urllib import parse
import time
import struct


def bytes_to_hexlist(bytes_buf):
    '''
    处理recv到的字节数据，转换为16进制数据
    :param strbuf: bytes
    :return: 16进制表示的列表
    '''
    if isinstance(bytes_buf, bytes):
        return [str(hex(x))[2:] for x in bytes_buf]
    else:
        raise Exception('bytes_buf type is error!')

def bytes_to_hexstr(bytes_buf):
    '''
    处理recv到的字节数据，转换为16进制数据
    :param strbuf: bytes
    :return: 16进制表示的
    '''
    if isinstance(bytes_buf, bytes):
        return ' '.join([str(hex(x))[2:] for x in bytes_buf])
    else:
        raise Exception('bytes_buf type is error!')


def str_escape(data):
    '''
    字符串转义,此种转义规则与URLEncoder等效(注：目前实际实现的转意是，每个字节都转)
    :param str:  待转义的字符 (英文字母（a-zA-Z）、数字（0-9）、“-_.~”4个字符 为普通字符，不需要转义)
    :return: 转义结果
    '''
    if isinstance(data, str):
        escape = parse.quote(data, safe='~')
    elif isinstance(data, int):
        escape = data
    else:
        raise Exception('data is not str or int object!')
    return escape

def escape_bytes(data):
    '''
    数字转义,注：目前实际实现的转意是，每个字节都转)
    :param str:  转义的方法就是按“%XX”的格式，以2个十六进制数字字符代表该字节，若包含字母，则统一为大写字母A-F
    :return: 字节
    '''
    if isinstance(data, int):
        b = str(data).encode('utf-8')
        if len(b) < 2:
            value = b'%' + b'0' + b
        else:
            value = b'%' + b
    else:
        value = to_bytes(data)

    return value

def escape_recovery(data):
    '''
    对应str_escape，把转义的数据还原
    :param data: 被转义的数据
    :return: 还原后的数据
    '''

    return parse.unquote(data)

def to_str(bytes_or_str):
    '''
    不管传入的是字节还是字符，都返回字符对象
    :param bytes_or_str:
    :return: 字符对象
    '''
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str

    return value

def to_bytes(data):
    '''
    不管传入的是字节还是字符，都返回字节对象
    :param data: 字符串、整数、字节
    :return: 字节对象
    '''
    if isinstance(data, str):
        # value = data.encode('utf-8')
        value = data.encode()
    elif isinstance(data, int):
        if 0 <= data <= 255:
            value = struct.pack('B', data)
        else:
            value = struct.pack('H', data)
    else:
        value = data

    return value

def standard_time(sep=0, ttime=None, ftag=None):
    '''
    格式化时间
    :param sep: 时间间隔，单位为分钟；默认为当前时间 +时间间隔
    :param ttime: 时间锉
    :return:  格式 20170613_142350
    '''
    if ttime is None:
        ttime = time.localtime()
    if sep == 0:
        f_time = time.strftime("%Y%m%d%H%M%S", ttime)

    else:
        f_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time() - sep))

    if ftag is None:
        return f_time[:8] + f_time[8:]
    else:
        return f_time[:8] + ftag + f_time[8:]

def checksum(bytes_data):
    '''
    计算校验码,指从消息头开始，同后一字节异或，直到校验码前一个字节。包含了消息头、消息体（解密前）及之前的分隔符，
    结果用十六进制表示的一个字节
    :param str_data: 字节串，消息头+消息体+,
    :return: 返回str or int
    '''
    if isinstance(bytes_data, bytes):
        tmp = 0
        for i in [b for b in bytes_data]:
            tmp = tmp ^ i
    else:
        raise Exception('bytes_data is not bytes')
    if tmp == 91:
        checksum = '%5B'
    elif tmp == 93:
        checksum = '%5D'
    elif tmp == 44:
        checksum = '%2C'
    else:
        checksum = tmp


    return checksum

def hextoint(hexdata):
    '''16进制数转换为10进制，注意hexdata应该为列表'''
    if hexdata is None or hexdata == []:
        raise Exception('hextoint: hexdata is None or []')
    if len(hexdata) > 1:
        return int(''.join(hexdata[::-1]), 16)
    else:
        return int(hexdata, 16)



def hexstrip(data):
    '''\x00的移除'''
    if isinstance(data, str):
        return data.translate(None, '\x00').strip()
    else:
        return data


def inttobin(intdata):
    '''10进制数转换为2进制,不足8位,则高位补足0'''
    bindata = bin(intdata)[2:]
    bin_len = len(bindata)
    bin_mod = bin_len % 8
    if bin_mod != 0:
        bindata = ('0' * (8 - bin_mod)) + bindata
    else:
        pass
    return bindata


def str_join(hexstr):
    '''
    hexstr 是报文文字符串
    返回一个带：分隔的字符串,比如：'75:72:2a:00:02:00:00'
    '''

    hex_list = [hexstr[i:i + 2] for i in range(0, len(hexstr), 2)]

    return ':'.join(hex_list)


if __name__ == '__main__':
    # b = b'[test7777777,A3,20170913_220042,11,%2F%2F%2F%2F,evc=e/val=\x01/evt=/now=20170913220042/sw=\x01/fpA=E/fpB=0/fpC=(/td2=\xa1/td1=\xdf/wsr=\x1e/ect=\x05/flg=\x02/dnt=\xd1/int=\x05/tnt=\x05/sgt=\x15,'
    # check = checksum(b)
    # print(isinstance(check, str))
    # print(len(check))
    # print(check)
    # print(str_escape(check))
    # print(to_bytes('%2c'))
    print(to_bytes(21))
