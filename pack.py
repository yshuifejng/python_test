# -*- coding: utf8 -*-
u'''
Created on 2017年8月22日 上午11:45:59

@author: shaofeng.yang
'''

import struct
import random
from utils import *
from boby import *
import collections
import logging

u'''
注意：数据单元中如果没有强制说明低字节在前高字节在后，即网络字节序 big-endian
'''


class Pack(object):
    def __init__(self, header=None, boby=None):
        u'''
        ==============  帧结构 ===========================
        起始位	起始符（startFlag）	    固定为字符“[”（0x5B）
        消息头	设备唯一编号(deviceId)	设备的唯一标识，实际可能是产品编号、MAC地址或其它
                消息编码（msgId）	        消息类型编码
                日期时间(msgTime)	    yyyyMMdd_HHmmss，如：20170610_224530
                消息流水号(msgNo)	        以终端上行消息为例，每次递增
                消息包属性 ( msgAttr)	    提供加密分包属性。格式：encType/encSeed/pkgNo/pkgNum
                                        加密分包属性的格式分为4段：加密算法（encType）/加密种子（encSeed）/分包序号（pkgNo）/总分包数（pkgNum）
                                        其中，分包序号从1开始。每一部分都可以为空，本字段全空相当于：0/0/1/1，
                                        即：不加密、加密种子无意义、只有一个分包、当前包是第1个分包
        消息体	消息体内容(msgBody)	    根据业务类型，若是应答类消息，开头有3段：
                                        原消息类型、原消息流水号、错误号（Error）（详见“全局通用错误号”）
        校验码	校验码（checksum）	    指从消息头开始，同后一字节异或，直到校验码前一个字节。
                                        包含了消息头、消息体（解密前）及之前的分隔符，结果用十六进制表示的一个字节
        结束位	结束符（endFlag）        	固定为字符“]”（0x5D）
        ==============  帧结构 ===========================
        '''

        if header:
            head = {'msg_time': None}
            head.update(header)
        else:
            head = {'dev_id': 'test007', 'msg_id': 'A101', 'msg_time': None, 'msg_no': 16, 'msg_attr': ''}

        self.frame_head = '['  # 帧头，1字节,char
        self.msg_head = collections.OrderedDict()
        self.msg_head['dev_id'] = head['dev_id']  # 设备编号,string
        self.msg_head['msg_id'] = head['msg_id'].upper()  # 消息编号,相当于命令字,string
        if head['msg_time'] is None:
            self.msg_head['msg_time'] = standard_time(ftag='_')  # 消息时间
        else:
            self.msg_head['msg_time'] = head['msg_time']  # 消息时间
        self.msg_head['msg_no'] = str(head['msg_no'])  # 消息流水号,int32
        self.msg_head['msg_attr'] = head['msg_attr']  # 消息包属性,char
        self.msg_boby = Boby(self.msg_head['msg_id'], boby).get_boby()  # 消息体,key=value格式,逗号,进行分隔
        self.checksum = None  # 校验码，1字节，int
        self.frame_end = ']'  # 帧尾，1字节,char

    def byte_conversion(self, data):
        '''
        先转码，然后转换为字节
        :param data: 数据，可以是str or int
        :return: bytes
        '''
        return to_bytes(str_escape(data))

    def byte_conversion2(self, data):
        '''
        先转码，然后转换为字节
        :param data: 数据，可以是str or int
        :return: bytes
        '''
        return to_bytes(data)


    def head(self):
        '''
        构造消息头
        :return: 字节
        '''
        _head = []
        _head.append(self.byte_conversion(self.msg_head['dev_id']))
        _head.append(self.byte_conversion(self.msg_head['msg_id']))
        _head.append(self.byte_conversion(self.msg_head['msg_time']))
        _head.append(self.byte_conversion(self.msg_head['msg_no']))
        _head.append(self.byte_conversion(self.msg_head['msg_attr']))

        return b','.join(_head)

    def boby(self):
        '''
        构造消息体
        :return: 字节
        '''
        _boby = []
        if self.msg_boby and isinstance(self.msg_boby, dict):
            for k, v in self.msg_boby.items():
                if k in ('hatMsg', 'authCode', 'OriMsgNO', 'OriMsgID', 'Error', 'stTime', 'edTime'):
                    _tmp = self.byte_conversion(v)
                elif self.msg_head['msg_id'] in ['A3', 'A5']:
                    _tmp = self.byte_conversion(k) + b'=' + escape_bytes(v)
                else:
                    _tmp = self.byte_conversion(k) + b'=' + self.byte_conversion(v)
                _boby.append(_tmp)
        if self.msg_head['msg_id'] in ['A5', 'A3']:
            _msg_boby = b'/'.join(_boby)
        else:
            _msg_boby = b','.join(_boby)

        return _msg_boby

    def get_msg(self):
        '''
        构造消息帧，msg = 开始标记 + 消息头 + 消息体 + 检验码 + 结束标记
        :return: 字节
        '''
        _msg = []
        self.checksum = checksum(self.head() + self.boby())
        # _head = _msg.append(self.byte_conversion(self.frame_head))
        # _end = _msg.append(self.byte_conversion(self.frame_end))
        _msg.append(self.head())
        _msg.append(self.boby())
        _msg.append(to_bytes(self.checksum))

        return b'[' + b','.join(_msg) + b']'

    @staticmethod
    def byte_decode(bytes_data):
        '''
        先转字符，然后在转码
        :param data: bytes
        :return: str
        '''
        return escape_recovery(to_str(bytes_data))

    @staticmethod
    def unpack(bytes_pack):
        '''

        :param bytes_pack:  必须是完整的帧，即包含[ ]
        :return:
        '''
        if isinstance(bytes_pack, bytes):
            msg_list = bytes_pack.strip(b'[]').split(b',')
            head_list = msg_list[:5]
            boby_list = msg_list[5:-1]
            checksum_list = msg_list[-1:]

        return head_list, boby_list, checksum_list

    @staticmethod
    def unpack_head(bytes_pack):
        msg_head = Pack.unpack(bytes_pack)[0]
        head = {}
        head['dev_id'] = Pack.byte_decode(msg_head[0])
        head['msg_id'] = Pack.byte_decode(msg_head[1])
        head['msg_time'] = Pack.byte_decode(msg_head[2])
        head['msg_no'] = Pack.byte_decode(msg_head[3])
        head['msg_attr'] = Pack.byte_decode(msg_head[4])

        return head

    def unpack_boby(bytes_pack):
        msg_id = Pack.unpack_head(bytes_pack)['msg_id']
        msg_boby = Pack.unpack(bytes_pack)[1]
        boby = {}
        key_b101 = ['OriMsgNO', 'OriMsgID', 'Error', 'authCode']
        key_comm = ['OriMsgNO', 'OriMsgID', 'Error']
        key_c17 = ['stTime', 'edTime']
        if msg_id == 'B101':
            for i, b in enumerate(msg_boby):
                boby[key_b101[i]] = Pack.byte_decode(b)
            return boby
        elif msg_id == 'B2':
            for i, b in enumerate(msg_boby):
                boby[key_comm[i]] = Pack.byte_decode(b)
            return boby
        elif msg_id == 'C17':
            for i, b in enumerate(msg_boby):
                boby[key_c17[i]] = Pack.byte_decode(b)
            return boby
        elif msg_id == 'B5':
            for i, b in enumerate(msg_boby):
                boby[key_comm[i]] = Pack.byte_decode(b)
            return boby
        elif msg_id == 'B3':
            for i, b in enumerate(msg_boby):
                boby[key_comm[i]] = Pack.byte_decode(b)
            return boby
        elif msg_id == 'C11':
            for i, b in enumerate(msg_boby):
                boby[key_comm[i]] = Pack.byte_decode(b)
            return boby



if __name__ == '__main__':
    # d_boby = {'phone':'15989453055', 'password':'123456', 'model':'N2000', 'mainFirm':'1.1', 'ctrlFirm':'1.1',
    #           'gsmFirm':'1.2.1', 'proVer':'1.0.0'}
    # d_boby2 = {}
    # head101 = head = {'dev_id': 'test007', 'msg_id': 'A101', 'msg_no': 16, 'msg_attr': 'aa'}

    hat_boby = {'hatMsg': 'hello'}
    headA7 = head = {'dev_id': '865933030028621', 'msg_id': 'A7', 'msg_no': '3', 'msg_time': '20170830_164801',
                     'msg_attr': '////'}

