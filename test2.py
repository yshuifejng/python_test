# -*- coding: utf8 -*-
u'''
Created on 2017年8月29日 上午11:45:59

@author: shaofeng.yang
'''

import socket
from utils import *
import time
from device import *
import binascii


def send_pack(host='192.168.88.241', port=8000, device_id='test001'):
    # 调试使用,用于直接发送原始16进制报文

    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect((host, port))
    ss.send(login_pack)
    print '------ 开始注册 ------- '
    print '设备登陆注册 : ', repr(login_pack), ' ===> len : ', len(login_pack)
    buf = ss.recv(1024)
    unpack_data = LoginPack().unpack(buf)
    print '解析注册响应 : ', LoginPack().unpack(buf)


    data = '75:72:d3:20:20:68:dc:11:00:00'
    # str_data = ''.join(data.split())  # 去除空格
    str_data = ''.join(data.split(':'))  # 去除冒号
    hex_data = binascii.a2b_hex(str_data)
    if unpack_data[6] == 1:
        print '------ 登陆注册成功 ------- '
        # ss.setblocking(0)
        ss.settimeout(5)
        for i in range(1):
            ss.send(hex_data)
            print '发送数据：', str_to_hexstring(hex_data), ' ===> len : ', len(data)
            try:
            	buf = ss.recv(1024)
            except socket.timeout:
            	print '接收数据: 5秒超时,无返回数据'
            	continue

            print '接收数据: ', str_to_hexstring(buf), ' ===> len : ', len(buf)
            time.sleep(10)
            print '等待5s 开始发送数据.....'

    time.sleep(5)
    print '------断开连接---------- '
    ss.close()



if __name__ == '__main__':
    # send_pack(host='58.251.157.184', port=8000, device_id='yiwu001')
    send_pack(host='192.168.80.220', port=8000, device_id='xizhantest006')
