# -*- coding: utf8 -*-
u'''
Created on 2016年9月12日 下午6:43:59

@author: shaofeng.yang
'''
import socket
# from pack import *
import logging
import logging.config
# from functools import wraps
from utils import *
import asynagent3
import asynagentchat3
import time
from device import *
from pack import Pack
from loghandler import SafeFileHandler


logging.config.fileConfig('logger.conf')
log = logging.getLogger('root')


# def valid_execpetion(fun):
#     def wrap(*args, **kwargs):
#         try:
#             is_valid = fun(*args, **kwargs)
#         except Exception as ex:
#             # log.error('报文丢弃,函数{1} 抛出异常,{2}'.format(fun.__name__, ex))
#             msg = traceback.format_exc()
#             print '报文丢弃,函数 抛出异常', msg
#             is_valid = false
#         return is_valid
#     return wrap

MSG_TYPE = {'A101': 'GSM注册', 'B101': '平台响应GSM注册', 'A3': 'GSM动态事件', 'B3': ' 平台响应动态事件',
            'A5': 'GSM汇报设备状态', 'B5': ' 平台响应汇报设备状态', 'A7': 'GSM发送心跳', 'B7': '平台响应心跳',
            'A2': 'GSM签权', 'B2': '平台响应签权', 'C17': '平台下发套餐', 'D17': 'GSM响应套餐',  'C11': '设置GSM参数',
            'D11': '响应GSM参数', 'C21': '平台通知GSM更新固件', 'D21': 'GSM响应平台固件更新', 'C22': '平台通知水机更新固件', 'D22': '水机响应平台固件更新'}

# 设备通用应答码
DEV_ERROR = ['正常/成功/确认', '失败', '意外错误', '数据格式/内容错误', '不支持']

# 通用平台应答码
PLATFORM_ERROR = ['正常/成功/确认', '失败', '意外错误', '数据格式/内容错误', '不支持', '未签权', '终端已注销']

class agent(asynagentchat3.async_chat):
    def __init__(self, server=('127.0.0.1', 8000), device=None, conn_time=None, sock=None):
        asynagentchat3.async_chat.__init__(self, sock)
        self.g_host = server[0]
        self.g_port = server[1]
        self.device = device
        self.received_data = []  # 缓存接收到的帧数据
        self.process_reponse = self._process_reponse
        self.process_request = self._process_request
        self.is_invalid_pack = self._is_invalid_pack
        self.handle_pack = self._handle_pack
        self.init_sock(sock)
        self.timing_conn_time = conn_time  # 链接定时时间
        self.is_conn = False  # 是否已经完成连接
        self.set_terminator(b']')  # 设置帧尾为终止条件
        self.is_reconn_flag = False  # 默认启用重连机制

        self.init_state()

    def init_sock(self, sock):
        if sock is None:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

    def client_bind(self, client_ip=None, client_port=1024):
        try:
            self.bind(client_ip, client_port)
        except Exception as ex:
            return False
        return True

    def timing_conn(self):
        if not self.is_conn:
            # 如果还未链接，则判断定时时间是否到了在链接
            if self.timing_conn_time is None:
                self.connect((self.g_host, self.g_port))
                self.is_conn = True
            elif time.time() >= self.timing_conn_time:
                self.connect((self.g_host, self.g_port))
                self.is_conn = True
        else:
            # 如果已经链接，则不处理
            pass

    def init_state(self):

        self.received_data = []  # 缓存接收到的帧数据

        # 重新建立socket连接
        self.reconn_status = False  # 是否重新连接状态
        self.reconn_start_time = None  # 重连时间
        self.reconnection_interval = 30  # 重新连接服务器的时间间隔(s)
        self.reconn_count = 0  # 重新连接次数

        # 注册登陆
        self.is_logined = False  # 登陆完成
        self.is_register = False # 签权码，存在则使用

        # self.is_register = True  # 签权码，存在则使用

        self.register_delay_time = 15  # 登陆报文的超时时间(s)
        self.register_cumulative_time = None  # 登陆累加时间,超过超时时间或登陆失败则重新发送

        # 签权登陆
        # self.is_sign = True #
        self.sign_delay_time = 15  # 签权报文的超时时间(s)
        self.sign_cumulative_time = None  # 登陆累加时间,超过超时时间或签权失败则重新发送

        # 心跳
        # self.is_hating = True  # 是否心跳
        self.hat_start_time = None  # 心跳开始时间
        self.hat_timeout = 1 * 30  # 心跳超时时间(s),默认30s
        self.hat_interval = 10 * 30  # 心跳发送间隔（s）,默认5分钟
        self.hat_cumulative_time = None  # 心跳累加时间,超过超时时间则断开连接

        #  定时汇报设备状态
        self.state_start_time = None  # 汇报设备状态开始时间
        self.state_interval = 10 * 30  # 设备状态发送间隔（s）

        #  随机产生设备动态事件
        self.is_event = False    #  是否发送动态事件
        self.event_start_time = None  # 事件开始时间
        self.event_interval = 10 * 30  # 事件发送间隔（s）



    def init_reconnect(self):
        self.received_data = []  # 缓存接收到的帧数据

        # 重新建立socket连接
        self.reconn_status = False  # 是否重新连接状态
        self.reconn_start_time = None  # 重连时间
        self.reconnection_interval = 30  # 重新连接服务器的时间间隔(s)
        self.reconn_count = 0  # 重新连接次数

        # 注册登陆
        self.is_logined = False  # 登陆完成
        self.register_delay_time = 15  # 登陆报文的超时时间(s)
        self.register_cumulative_time = None  # 登陆累加时间,超过超时时间或登陆失败则重新发送

        # 签权登陆
        self.sign_delay_time = 15  # 签权报文的超时时间(s)
        self.sign_cumulative_time = None  # 登陆累加时间,超过超时时间或签权失败则重新发送

        # 心跳
        self.hat_start_time = None  # 心跳开始时间
        self.hat_timeout = 3 * 30  # 心跳超时时间(s)
        self.hat_interval = 2 * 30  # 心跳发送间隔（s）
        self.hat_cumulative_time = None  # 心跳累加时间,超过超时时间则断开连接

    def handle_connect(self):
        '''连接成功处理,初始化'''
        log.info('[{0}] 与服务器[{1}, {2}]连接==成功'.format(self.device.dev_id, self.g_host, self.g_port))
        self.init_reconnect()


    def handle_close(self):
        # 与服务器断开后，关闭socket
        log.error('[{0}] 与服务器[{1}, {2}]连接==断开'.format(self.device.dev_id, self.g_host, self.g_port))
        self.close()
        # 清空缓冲区
        self.discard_buffers()
        # 重连开关
        if self.is_reconn_flag == True:
            # 重连次数递增
            self.reconn_count = self.reconn_count + 1
            log.info('[{0}] 等待{1}秒,第{2}次重新连接'.format(self.device.dev_id, self.reconnection_interval, self.reconn_count))
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.reconn_status = True
            self.reconn_start_time = self.reconnection_interval + time.time()

    def writable(self):
        # 定时链接判断
        self.timing_conn()
        if self.reconn_status and self.reconn_start_time < time.time():
            self.connect((self.g_host, self.g_port))
        elif self.connected:
            #  如果不需要重连，则已经连接中，则处理请求
            self.process_request()
        else:
            pass

        return self.producer_fifo or (not self.connected)

    def collect_incoming_data(self, data):
        '''缓存收集按terminator分割的数据,这里相当于协议里定义的帧，当然去掉了帧头ur'''

        self.received_data.append(data)

    def found_terminator(self):
        '''接收数据,处理collect_incoming_data收集的数据,解析每一帧'''
        self.process_reponse()

    def _process_reponse(self):
        '''实际的接收数据处理方法'''
        # 接收缓冲列表不为空则处理
        if self.received_data:
            # 添加过滤掉的帧头
            new_received_data = [x + b']' for x in self.received_data]
            log.info('[{0}] 接收==个数={1} 报文内容={2}'.format(self.device.dev_id, len(new_received_data), new_received_data))
            hex_pack_data = bytes_to_hexstr(b''.join(new_received_data))
            log.debug('[{0}] 接收==个数={1} 原始报文={2}'.format(self.device.dev_id, len(new_received_data), hex_pack_data))
            # 批量处理缓冲区中报文
            for _data in new_received_data:
                # 对报文进行合法性校验
                if self.is_invalid_pack(_data):
                    # 如果报文通过校验,则对报文进行业务处理
                    self.handle_pack(_data)
            # 处理完缓冲区报文则清空缓冲区
            self.received_data = []

    def _process_request(self):
        '''实际的发送数据处理'''
        if not self.is_logined:
            # 未登陆成功
            if not self.is_register:
                # 未注册,则发生注册
                if self.register_cumulative_time is None:
                    register_msg = self.device.get_register()
                    self.push(register_msg)
                    log.info('[{0}] 设备开始注册'.format(self.device.dev_id))
                    log.debug('[{0}] 生成注册报文A101：{1}'.format(self.device.dev_id, register_msg))
                    log.debug('[{0}] 发送==注册A101：{1}'.format(self.device.dev_id, bytes_to_hexstr(register_msg)))
                    self.register_cumulative_time = time.time()
                elif time.time() - self.register_cumulative_time > self.register_delay_time:
                    # 超时重发注册
                    register_msg = self.device.get_register()
                    self.push(register_msg)
                    log.debug('[{0}] 超时重发==注册A101：{1}'.format(self.device.dev_id, bytes_to_hexstr(register_msg)))
                    self.register_cumulative_time = time.time()
            elif self.device.authCode:
                # 已经注册，开始签权
                if self.sign_cumulative_time is None:
                    log.info('[{0}] 已经注册过,使用签权码={1} 进行签权登录'.format(self.device.dev_id, self.device.authCode))
                    sign_msg = self.device.get_sign()
                    self.push(sign_msg)
                    log.debug('[{0}] 生成签权报文A2：{1}'.format(self.device.dev_id, sign_msg))
                    log.debug('[{0}] 发送==签权A2：{1}'.format(self.device.dev_id, bytes_to_hexstr(sign_msg)))
                    self.sign_cumulative_time = time.time()
                elif time.time() - self.sign_cumulative_time > self.sign_delay_time:
                    sign_msg = self.device.get_sign()
                    self.push(sign_msg)
                    log.info('[{0}]  重发签权'.format(self.device.dev_id))
                    log.debug('[{0}] 重发签权A2：{1}'.format(self.device.dev_id, bytes_to_hexstr(sign_msg)))
                    self.sign_cumulative_time = time.time()

        if self.is_logined:
            # 登录成功，开正常通讯
            # 心跳
            if self.hat_start_time is None:
                hat_msg = self.device.get_hat()
                self.push(hat_msg)
                log.info('[{0}] 发送心跳A7'.format(self.device.dev_id))
                # log.debug('[{0}] 生成心跳报文A7：{1}'.format(self.device.dev_id, hat_msg))
                log.debug('[{0}] 发送==心跳A7：{1}'.format(self.device.dev_id, bytes_to_hexstr(hat_msg)))
                self.hat_start_time = time.time() + self.hat_interval
            elif self.hat_start_time < time.time():
                hat_msg = self.device.get_hat()
                self.push(hat_msg)
                log.info('[{0}] 发送心跳A7'.format(self.device.dev_id))
                # log.debug('[{0}] 生成心跳报文A7：{1}'.format(self.device.dev_id, hat_msg))
                log.debug('[{0}] 发送==心跳A7：{1}'.format(self.device.dev_id, bytes_to_hexstr(hat_msg)))
                self.hat_start_time = time.time() + self.hat_interval
            else:
                pass

            # 随机产生设备动态事件
            if not self.is_event:
                pass
            elif self.event_start_time is None:
                event_msg = self.device.get_event()
                self.push(event_msg)
                log.info('[{0}] 发送设备动态事件A3'.format(self.device.dev_id))
                log.debug('[{0}] 生成设备动态事件报文A3：{1}'.format(self.device.dev_id, event_msg))
                log.debug('[{0}] 发送==设备动态事件A3：{1}'.format(self.device.dev_id, bytes_to_hexstr(event_msg)))
                self.event_start_time = time.time() + self.event_interval
            elif self.event_start_time < time.time():
                event_msg = self.device.get_event()
                self.push(event_msg)
                log.info('[{0}] 发送设备动态事件A3'.format(self.device.dev_id))
                log.debug('[{0}] 生成设备动态事件报文A3：{1}'.format(self.device.dev_id, event_msg))
                log.debug('[{0}] 发送==设备动态事件A3：{1}'.format(self.device.dev_id, bytes_to_hexstr(event_msg)))
                self.event_start_time = time.time() + self.event_interval
            else:
                pass

            # 定时汇报设备状态
            if self.state_start_time is None:
                state_msg = self.device.get_devdynamic()
                self.push(state_msg)
                log.info('[{0}] 发送设备状态A5'.format(self.device.dev_id))
                log.debug('[{0}] 生成设备状态报文A5：{1}'.format(self.device.dev_id, state_msg))
                log.debug('[{0}] 发送==设备状态A5：{1}'.format(self.device.dev_id, bytes_to_hexstr(state_msg)))
                self.state_start_time = time.time() + self.state_interval
            elif self.state_start_time < time.time():
                state_msg = self.device.get_devdynamic()
                self.push(state_msg)
                log.info('[{0}] 发送设备状态A5'.format(self.device.dev_id))
                log.debug('[{0}] 生成设备状态报文A5：{1}'.format(self.device.dev_id, state_msg))
                log.debug('[{0}] 发送==设备状态A5：{1}'.format(self.device.dev_id, bytes_to_hexstr(state_msg)))
                self.state_start_time = time.time() + self.state_interval
            else:
                pass


    # @valid_execpetion
    def _is_invalid_pack(self, recv_bytes):

        _checksum = b''.join(Pack.unpack(recv_bytes)[2])
        _check_info = recv_bytes.strip(b'[]')[:-1]
        _checksum_calc = to_bytes(checksum(_check_info))
        _msg_id = Pack.unpack_head(recv_bytes)['msg_id']

        log.debug('[{0}] 接收==验证报文==消息类型={1}({2}) 待校验信息=({3})'.format(self.device.dev_id, _msg_id, MSG_TYPE[_msg_id], _check_info))

        if _checksum == _checksum_calc:
            log.debug('[{0}] 接收==验证报文==消息类型={1}({2}) 报文校验码正确(checksum={3} checksum_calc={4})'.format(
            self.device.dev_id, _msg_id, MSG_TYPE[_msg_id], _checksum, _checksum_calc))
            return True
        else:
            log.error('[{0}] 接收==验证报文==消息类型={1}({2}) 报文长度验证失败(checksum={3} checksum_calc={4})'.format(
                self.device.dev_id, _msg_id, MSG_TYPE[_msg_id], _checksum, _checksum_calc))
            return True



    def _handle_pack(self, recv_bytes):
        _msg_id = Pack.unpack_head(recv_bytes)['msg_id']
        if _msg_id == 'B7':
            # 响应心跳指令
            self.hat_cumulative_time = time.time()  # 收到心跳响应的时间
        elif _msg_id == 'B101':
            # 处理收到的注册响应
            if not self.is_register:
                self.register_cumulative_time = time.time()  # 收到登陆响应的时间
                error = Pack.unpack_boby(recv_bytes)['Error']
                if error == '0':
                    self.device.authCode = Pack.unpack_boby(recv_bytes)['authCode']
                    self.is_register = True
                    log.info('[{0}] 注册成功'.format(self.device.dev_id))
                else:
                    self.is_register = False
                    log.info('[{0}] 注册失败,原因={1}'.format(self.device.dev_id, error))
            else:
                log.info('[{0}] 已经注册,收到无效的注册响应'.format(self.device.dev_id))
        elif _msg_id == 'B2':
            # 响应签权
            if self.is_register:
                self.sign_cumulative_time = time.time()  # 收到签权响应的时间
                error = Pack.unpack_boby(recv_bytes)['Error']
                if error == '0':
                    self.is_logined = True
                    log.info('[{0}] 签权登录成功'.format(self.device.dev_id))
                else:
                    self.is_logined = False
                    log.info('[{0}] 签权登录失败,原因={1}'.format(self.device.dev_id, error))
        elif _msg_id == 'C17':
            # 响应套餐指令
            log.info('[{0}] 接受套餐信息成功'.format(self.device.dev_id))
            # 构造响应信息，发送
            res_boby = {}
            res_boby['OriMsgNO'] = Pack.unpack_head(recv_bytes)['msg_no']
            res_boby['OriMsgID'] = Pack.unpack_head(recv_bytes)['msg_id']
            res_boby['Error'] = '0'
            res_boby['stTime'] = Pack.unpack_boby(recv_bytes)['stTime']
            res_boby['edTime'] = Pack.unpack_boby(recv_bytes)['edTime']
            res_setmeal_msg = self.device.get_setmeal_reponse(res_boby)
            self.push(res_setmeal_msg)
            log.info('[{0}] 响应套餐 ( {1} )'.format(self.device.dev_id, DEV_ERROR[int(res_boby['Error'])]))
            log.debug('[{0}] 生成套餐响应报文D17：{1}'.format(self.device.dev_id, res_setmeal_msg))
            log.debug('[{0}] 响应==套餐D17：{1}'.format(self.device.dev_id, bytes_to_hexstr(res_setmeal_msg)))
        elif _msg_id == 'B5':
            # 处理收到的动态汇报响应
            error = Pack.unpack_boby(recv_bytes)['Error']
            log.info('[{0}] 接收平台响应设备状态,应答码= ( {1}, {2} )'.format(self.device.dev_id, error, PLATFORM_ERROR[int(error)]))
        elif _msg_id == 'B3':
            # 处理收到的事件响应
            error = Pack.unpack_boby(recv_bytes)['Error']
            log.info('[{0}] 接收平台事件响应,应答码= ( {1}, {2} )'.format(self.device.dev_id, error, PLATFORM_ERROR[int(error)]))

        elif _msg_id == 'C11':
            # 收到的终端参数设置指令,返回相应
            # 构造响应信息，发送
            res_boby = {}
            res_boby['OriMsgNO'] = Pack.unpack_head(recv_bytes)['msg_no']
            res_boby['OriMsgID'] = Pack.unpack_head(recv_bytes)['msg_id']
            res_boby['Error'] = '0'
            res_gsmpara_msg = self.device.get_gsmpara_reponse(res_boby)
            self.push(res_gsmpara_msg)
            log.info('[{0}] 响应GSM参数设置 ( {1} )'.format(self.device.dev_id, DEV_ERROR[int(res_boby['Error'])]))
            # log.debug('[{0}] 生成GSM参数响应报文D17：{1}'.format(self.device.dev_id, res_gsmpara_msg))
            log.debug('[{0}] 响应==套餐D11：{1}'.format(self.device.dev_id, bytes_to_hexstr(res_gsmpara_msg)))
        elif _msg_id == 'C21':
            # 收到平台下发的GSM固件更新通知,返回D21响应
            # 构造响应信息，发送
            res_boby = {}
            res_boby['OriMsgNO'] = Pack.unpack_head(recv_bytes)['msg_no']
            res_boby['OriMsgID'] = Pack.unpack_head(recv_bytes)['msg_id']
            res_boby['Error'] = '0'
            res_gsm_update_msg = self.device.get_gsm_update_reponse(res_boby)
            self.push(res_gsm_update_msg)
            log.info('[{0}] 响应平台GSM固件更新 ( {1} )'.format(self.device.dev_id, DEV_ERROR[int(res_boby['Error'])]))
            # log.debug('[{0}] 生成响应平台GSM固件更新报文D21：{1}'.format(self.device.dev_id, res_gsm_update_msg))
            log.debug('[{0}] 响应==套餐D21：{1}'.format(self.device.dev_id, bytes_to_hexstr(res_gsm_update_msg)))
        elif _msg_id == 'C22':
            #  收到水机升级指令，放D22响应
            #  构造响应信息，发送
            res_boby = {}
            res_boby['OriMsgNO'] = Pack.unpack_head(recv_bytes)['msg_no']
            res_boby['OriMsgID'] = Pack.unpack_head(recv_bytes)['msg_id']
            res_boby['Error'] = '0'
            res_WaterMachine_update_msg = self.device.get_WaterMachine_update_reponse(res_boby)
            self.push(res_WaterMachine_update_msg)
            log.info('[{0}] 响应平台水机固件更新 ( {1} )'.format(self.device.dev_id, DEV_ERROR[int(res_boby['Error'])]))
            # log.debug('[{0}] 生成响应平台GSM固件更新报文D21：{1}'.format(self.device.dev_id, res_WaterMachine_update_msg))
            log.debug('[{0}] 响应==套餐D22：{1}'.format(self.device.dev_id, bytes_to_hexstr(res_WaterMachine_update_msg)))
        else:
            log.info('[{0}] 未知报文，不处理丢弃'.format(self.device.dev_id))


    def start(self):
        asynagent3.loop(timeout=5)



if __name__ == '__main__':
    #  生产环境  '111.230.218.154', 18327
    device1 = Device('test00000000001')

    # ss = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    # ss.bind(('192.168.1.149', 1025))
    # agent(('192.168.1.31', 18327), device1, sock=ss).client_bind(('192.168.1.149', 1025))
    # 测试环境
    agent(('58.250.17.19', 18327), device1)
    # 开发环境
    # agent(('192.168.2.12', 18327), device1)
    # 工厂测试环境
    # agent(('192.168.2.11', 18326), device1)
    # 生产环境
    # agent(('111.230.218.154', 18327), device1)


    asynagent3.loop(timeout=5)

