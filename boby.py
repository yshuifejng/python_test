# -*- coding: utf8 -*-
u'''
Created on 2017年8月22日 上午11:45:59

@author: shaofeng.yang
'''

import collections


class Boby(object):
    def __init__(self, msg_id=None, boby=None):
        '''
        消息体
        :param msg_id: 消息ID， 字符串
        :param boby: 消息体, 字典
        '''


        self.msg_id = msg_id
        self.boby = boby
        self.init_check()


    def init_check(self):

        if self.msg_id:
            if isinstance(self.msg_id, str):
                pass
            else:
                raise Exception('msg_id is not string!')
        else:
            raise Exception('msg_id is None!')

    def universal_response(self, response_boby):
        '''
        通用响应
        :param response_boby:
        :return:
           （终端通用应答）                                （平台通用应答）
          错误号	含义                                    错误号	   含义
            0	正常/成功/确认                             0	    正常/成功/确认
            1	失败                                      1	    失败
            2	意外错误                                   2	    意外错误
            3	数据格式/内容错误                           3	    数据格式/内容错误
            4	不支持                                     4	    不支持
                                                          101	未鉴权
                                                          102	终端已注销

        '''
        self.response_boby = collections.OrderedDict()
        self.response_boby['OriMsgNO'] = response_boby['OriMsgNO']  # 原消息流水号, int32
        self.response_boby['OriMsgID'] = response_boby['OriMsgID']  # 原消息类型, String
        self.response_boby['Error'] = response_boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多

        return self.response_boby

    def get_boby(self):

        if self.msg_id.upper() == 'A101':
            # GSM向平台注册
            self.boby_A101 = collections.OrderedDict()
            self.boby_A101['phone'] = self.boby['phone']  # 电话号码, String
            self.boby_A101['password'] = self.boby['password']  # 密钥, String
            self.boby_A101['model'] = self.boby['model']  # 机器型号, String
            self.boby_A101['mainFirm'] = self.boby['mainFirm']  # 主机ble板固件版本, String
            self.boby_A101['ctrlFirm'] = self.boby['ctrlFirm']  # 控制板固件版本, String
            self.boby_A101['gsmFirm'] = self.boby['gsmFirm']  # GSM模块板固件版本, String
            self.boby_A101['proVer'] = self.boby['proVer']  # GSM模块TCP通信协议版本, String
            return self.boby_A101
        elif self.msg_id.upper() == 'B101':
            # 平台响应注册
            self.boby_B101 = collections.OrderedDict()
            self.boby_B101['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_B101['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_B101['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：等待后台人工审核
            self.boby_B101['authCode'] = self.boby['authCode']  # 鉴权码, String
            return self.boby_B101
        elif self.msg_id.upper() == 'A2':
            # GSM发送签权
            self.boby_A2 = collections.OrderedDict()
            self.boby_A2['authCode'] = self.boby['authCode']  # 鉴权码, String
            return self.boby_A2
        elif self.msg_id.upper() == 'B2':
            # 平台响应签权
            self.boby_B2 = collections.OrderedDict()
            self.boby_B2['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_B2['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_B2['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_B2
        elif self.msg_id.upper() == 'C11':
            # 平台设置GSM参数，终端参数表
            self.boby_C11 = collections.OrderedDict()
            self.boby_C11['ParamrNum'] = self.boby['ParamrNum']  # 参数个数, int
            self.boby_C11['heartbeat'] = self.boby['heartbeat']  # 心跳间隔, int
            return self.boby_C11
        elif self.msg_id.upper() == 'D11':
            # 平台响应GSM参数设置
            self.boby_D11 = collections.OrderedDict()
            self.boby_D11['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_D11['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_D11['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_D11
        elif self.msg_id.upper() == 'A7':
            # GSM发送心跳
            self.boby_A7 = collections.OrderedDict()
            self.boby_A7['hatMsg'] = self.boby['hatMsg']  # 字符串, 协议上没用key/value模式
            return self.boby_A7
        elif self.msg_id.upper() == 'B7':
            # 平台响应心跳
            self.boby_B7 = collections.OrderedDict()
            self.boby_B7['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_B7['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_B7['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_B7
        elif self.msg_id.upper() == 'C17':
            # 平台下发套餐
            self.boby_C17 = collections.OrderedDict()
            self.boby_C17['stTime'] = self.boby['stTime']  # 开始时间
            self.boby_C17['edTime'] = self.boby['edTime']  # 结束时间
            return self.boby_C17
        elif self.msg_id.upper() == 'D17':
            # GSM响应套餐
            self.boby_D17 = collections.OrderedDict()
            self.boby_D17['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_D17['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_D17['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            self.boby_D17['stTime'] = self.boby['stTime']  # 开始时间
            self.boby_D17['edTime'] = self.boby['edTime']  # 结束时间
            return self.boby_D17
        elif self.msg_id.upper() == 'A5':
            # GSM汇报机器动态
            self.boby_A5 = collections.OrderedDict()
            self.boby_A5['now'] = self.boby['now']  # 当前时间
            self.boby_A5['sw'] = self.boby['sw']  # 开关位，int
            self.boby_A5['fpA'] = self.boby['fpA']  # 滤芯A状态（滤芯百分比）
            self.boby_A5['fpB'] = self.boby['fpB']  # 滤芯B状态（滤芯百分比）
            self.boby_A5['fpC'] = self.boby['fpC']  # 滤芯C状态（滤芯百分比）
            self.boby_A5['td2'] = self.boby['td2']  # TDS2
            self.boby_A5['td1'] = self.boby['td1']  # TDS1
            self.boby_A5['wsr'] = self.boby['wsr']  # 节水比率
            self.boby_A5['ect'] = self.boby['ect']  # 错误数量
            self.boby_A5['flg'] = self.boby['flg']  # 错误旗标
            self.boby_A5['dnt'] = self.boby['dnt']  # 断网时长（秒
            self.boby_A5['int'] = self.boby['int']  # 进水次数（Inlet Counter）
            self.boby_A5['tnt'] = self.boby['tnt']  # 累计用水量（##单位：公升）
            self.boby_A5['sgt'] = self.boby['sgt']  # 基站信号数量，信号强度

            return self.boby_A5
        elif self.msg_id.upper() == 'B5':
            # 平台响应GSM动态
            self.boby_B5 = collections.OrderedDict()
            self.boby_B5['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_B5['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_B5['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_B5
        elif self.msg_id.upper() == 'A3':
            # GSM汇报机器动态事件
            self.boby_A3 = collections.OrderedDict()
            self.boby_A3['evc'] = self.boby['evc']  # 事件类型编码
            self.boby_A3['val'] = self.boby['val']  # 事件参数
            self.boby_A3['evt'] = self.boby['evt']  # 事件详情
            self.boby_A3['now'] = self.boby['now']  # 当前时间
            self.boby_A3['sw'] = self.boby['sw']  # 开关位，int
            self.boby_A3['fpA'] = self.boby['fpA']  # 滤芯A状态（滤芯百分比）
            self.boby_A3['fpB'] = self.boby['fpB']  # 滤芯B状态（滤芯百分比）
            self.boby_A3['fpC'] = self.boby['fpC']  # 滤芯C状态（滤芯百分比）
            self.boby_A3['td2'] = self.boby['td2']  # TDS2
            self.boby_A3['td1'] = self.boby['td1']  # TDS1
            self.boby_A3['wsr'] = self.boby['wsr']  # 节水比率
            self.boby_A3['ect'] = self.boby['ect']  # 错误数量
            self.boby_A3['flg'] = self.boby['flg']  # 错误旗标
            self.boby_A3['dnt'] = self.boby['dnt']  # 断网时长（秒
            self.boby_A3['int'] = self.boby['int']  # 进水次数（Inlet Counter）
            self.boby_A3['tnt'] = self.boby['tnt']  # 累计用水量（##单位：公升）
            self.boby_A3['sgt'] = self.boby['sgt']  # 基站信号数量，信号强度

            return self.boby_A3
        elif self.msg_id.upper() == 'B3':
            # 平台响应GSM动态事件
            self.boby_B3 = collections.OrderedDict()
            self.boby_B3['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_B3['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_B3['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_B3
        elif self.msg_id.upper() == 'C21':
            # 平台发送GSM固件更新
            self.boby_C21 = collections.OrderedDict()
            self.boby_C21['fwsize'] = self.boby['fwsize']  # 固件大小, String
            return self.boby_C21
        elif self.msg_id.upper() == 'D21':
            # GSM响应平台固件更新指令
            self.boby_D21 = collections.OrderedDict()
            self.boby_D21['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_D21['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_D21['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_D21
        elif self.msg_id.upper() == 'C22':
            # 平台发送水机固件更新
            self.boby_C22 = collections.OrderedDict()
            self.boby_C22['fwsize'] = self.boby['fwsize']  # 固件大小, String
            return self.boby_C22
        elif self.msg_id.upper() == 'D22':
            # 水机响应平台固件更新指令
            self.boby_D22 = collections.OrderedDict()
            self.boby_D22['OriMsgNO'] = self.boby['OriMsgNO']  # 原消息流水号, int32
            self.boby_D22['OriMsgID'] = self.boby['OriMsgID']  # 原消息类型, String
            self.boby_D22['Error'] = self.boby['Error']  # 应答结果, int, 0：成功；1：失败；2：失败次数过多
            return self.boby_D22
        else:
            raise Exception('msg_id is Not found')


