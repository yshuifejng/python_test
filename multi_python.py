# -*- coding: utf8 -*-
u'''
Created on 2017年9月1日 下午6:43:59

@author: shaofeng.yang
'''

from utils import *
import asynagent3
from agent import agent
import time
from device import Device
import multiprocessing
import logging
import socket


def generator(server=('127.0.0.1', 8000), client_bind=None, device_count=1, prefix='test',start_index=1, rate=None, duration=None):
    '''

    :param server: 待连接的服务端，格式元组（服务端ip,服务的port）
    :param client_bind: 客户端绑定信息（客户端IP，开始端口，结束端口）
    :param device_count: 需要模拟的设备总数
    :param prefix:  模拟的设备ID前缀
    :param start_index: 模拟的设备ID的自增后缀的开始数字,默认为1
    :param rate: 设备建立连接的速度
    :param duration: 多长时间完成设备的连接建立
    :return:
    '''
    device_list = []
    start_index = start_index
    str_prefix = prefix + '00'
    current_time = time.time()
    for i in range(start_index, device_count + start_index):
        _id = str_prefix + str(i)
        device_list.append(Device(dev_id=_id))

    if rate and duration is None:
        current_time = time.time()
        for i, dev in enumerate(device_list):
            tt = current_time + ((1/rate) * i)
            agent(server, dev, conn_time=tt)
    elif rate is None and duration:
        current_time = time.time()
        for i, dev in enumerate(device_list):
            tt = current_time + ((duration/device_count) * i)
            agent(server, dev, conn_time=tt)
    else:
        logging.error('rate and duration cannot be true at the same time!')

    asynagent3.loop(use_poll=True, timeout=3)


def generator2(server=('127.0.0.1', 8000), client_soket=None, device_count=1, prefix='test', start_index=1, start_time=None, rate=None, duration=None):
    device_list = []
    start_index = start_index
    tmp_perfix = '00000000000'
    tmp_len = len(tmp_perfix)
    if start_time is None:
        current_time = time.time()
    else:
        current_time = start_time
    for i in range(start_index, device_count + start_index):
        _id = prefix + (tmp_perfix + str(i))[-tmp_len:]
        device_list.append(Device(dev_id=_id))

    if rate and duration is None:
        for i, dev in enumerate(device_list):
            tt = current_time + ((1/rate) * i)
            if client_soket is None:
                agent(server, dev, conn_time=tt)
            else:
                agent(server, dev, conn_time=tt, sock=client_soket[i])
    elif rate is None and duration:
        for i, dev in enumerate(device_list):
            tt = current_time + ((duration/device_count) * i)
            if client_soket is None:
                agent(server, dev, conn_time=tt)
            else:
                agent(server, dev, conn_time=tt, sock=client_soket[i])
    else:
        logging.error('rate and duration cannot be true at the same time!')

    asynagent3.loop(use_poll=True, timeout=3)

def batch_socket(client_ip='127.0.0.1', number=10):
    '''
    批量生产socket，并绑定端口
    :param client_ip: 需要绑定的地址
    :param number: 需要的socket数目
    :return: 绑定端口成功的socket list
    '''
    sock_list = []
    start_port = 1024
    end_port = 65000
    count = 0
    if number > (end_port - start_port):
        raise Exception('deivce number is too many!')
    else:
        for port in (p for p in range(start_port, end_port)):
            try:
                if count < number:
                    ss = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
                    ss.bind((client_ip, port))
                    sock_list.append(ss)
                    count = count + 1
                else:
                    break
            except Exception as ex:
                print(ex)
                ss.close()

    return sock_list


def multiprocess(func, server=('127.0.0.1', 8000), client_ip=None, proc_nmber=4, device_count=4, prefix='test',rate=None, duration=None):
    if client_ip is not None:
        client_soket = batch_socket(client_ip, device_count)
        if len(client_soket) != device_count:
            raise Exception('The number of client_sock does not match device_count!')

    PROCESS_COUNT = proc_nmber
    if PROCESS_COUNT > multiprocessing.cpu_count():
        raise Exception('CPU core number={0} , PROCESS_COUNT={1},Exceeded the actual number of CPU coress'.format(multiprocessing.cpu_count(),PROCESS_COUNT))

    pool = multiprocessing.Pool(processes=PROCESS_COUNT)
    args_list = []
    dev_rem = device_count % PROCESS_COUNT   # 余数
    dev_int = device_count // PROCESS_COUNT  # 整数
    duration_split = duration/PROCESS_COUNT  # 平分时间
    index = 1
    if dev_int == 0:
        # 不够核心数，启动一个进程
        args_list.append((server, client_soket, device_count, prefix, 1, None, None, duration))
    elif dev_rem == 0:
        # 超过核心数，并且设备数目可平分，则启动没个核心进程，启动平均设备数目
        start_time = time.time()
        for i in range(PROCESS_COUNT):
            if client_ip is not None:
                args_list.append((server, client_soket[i*dev_int:(i+1)*dev_int], dev_int, prefix, index, start_time, None, duration_split))
            else:
                args_list.append((server, None, dev_int, prefix, index,start_time, None, duration_split))
            index = index + dev_int
            start_time = start_time + duration_split
    else:
        # 超过核心数，设备不可平分，则其中一个进程多分一些设备
        start_time = time.time()
        for i in range(PROCESS_COUNT):
            if i < 3:
                if client_ip is not None:
                    args_list.append((server, client_soket[i*dev_int:(i+1)*dev_int], dev_int, prefix, index, start_time, None, duration_split))
                else:
                    args_list.append((server, None, dev_int, prefix, index, start_time, None, duration_split))
            else:
                if client_ip is not None:
                    args_list.append((server, client_soket[i*dev_int:], (dev_int + dev_rem), prefix, index, start_time, None, duration_split))
                else:
                    args_list.append((server, None, (dev_int + dev_rem), prefix, index, start_time,None, duration_split))
            index = index + dev_int
            start_time = start_time + duration_split

    for arg in args_list:
        pool.apply_async(func, args=arg)

    pool.close()
    pool.join()


if __name__ == '__main__':
    server1 = ('58.250.17.19', 18327)
    # server2 = ('192.168.1.22', 18327)
    # server3 = ('111.230.218.154', 18327)
    multiprocess(func=generator2, server=server1, device_count=30, prefix='test', duration=1 * 60)
    # multiprocess(func=generator2, server=server1, client_ip='192.168.1.149', proc_nmber=4, device_count=5, prefix='test', duration=1*60)
    # multiprocess(func=generator2, server=server2, client_ip='192.168.1.149', proc_nmber=4, device_count=10000, prefix='feng', duration=5 * 60)
