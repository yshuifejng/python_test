# -*- coding: utf8 -*-
u'''
Created on 2016年9月12日 下午6:43:59

@author: shaofeng.yang
'''
from pack import *
from utils import *
from pack import Pack


class Device(object):
    msg_no = 0  # 消息流水号

    def __init__(self, dev_id='KHSZ001'):
        self.dev_id = dev_id
        self.msg_attr = '////'
        self.model = 'T1'
        self.mainFirm = '1.0'
        self.ctrlFirm = '1.1'
        self.gsmFirm = '1.2.1'
        self.proVer = '1.0.0'
        self.authCode = ''

    def get_head(self, msg_attr='////', msg_id=''):
        Device.msg_no = Device.msg_no + 1
        self.msg_no = Device.msg_no
        head = {'dev_id': self.dev_id, 'msg_id': msg_id, 'msg_no': self.msg_no, 'msg_attr': msg_attr}

        return head

    def get_register(self):
        boby = {'phone': '15989453055', 'password': '123456', 'model': self.model, 'mainFirm': self.mainFirm,
                'ctrlFirm': self.ctrlFirm, 'gsmFirm': self.gsmFirm, 'proVer': self.proVer}
        head_A101 = self.get_head(msg_id='A101')

        return Pack(head_A101, boby).get_msg()

    def get_hat(self):
        boby = {'hatMsg': 'hello'}
        head_A7 = self.get_head(msg_id='A7')

        return Pack(head_A7, boby).get_msg()

    def get_sign(self):
        boby = {'authCode': self.authCode}
        head_A2 = self.get_head(msg_id='A2')

        return Pack(head_A2, boby).get_msg()

    def get_setmeal_reponse(self, res_boby):
        # 获取套餐响应 C17-D17
        boby = res_boby
        head_D17 = self.get_head(msg_id='D17')

        return Pack(head_D17, boby).get_msg()

    def get_gsmpara_reponse(self, res_boby):
        # 获取gsm参数设置响应 C11-D11
        boby = res_boby
        head_D11 = self.get_head(msg_id='D11')

        return Pack(head_D11, boby).get_msg()

    def get_gsm_update_reponse(self, res_boby):
        # 获取gsm响应平台固件更新 C21-D21
        boby = res_boby
        head_D21 = self.get_head(msg_id='D21')

        return Pack(head_D21, boby).get_msg()

    def get_WaterMachine_update_reponse(self, res_boby):
        # 获取水机响应平台固件更新 C22-D22
        boby = res_boby
        head_D22 = self.get_head(msg_id='D22')

        return Pack(head_D22, boby).get_msg()

    def get_devdynamic(self):
        # 汇报设备动态 A5-B5
        self.boby_A5 = collections.OrderedDict()
        self.boby_A5['now'] = standard_time()  # 当前时间
        self.boby_A5['sw'] = 1 << 0  # 开关位，int
        self.boby_A5['fpA'] = random.randrange(30, 50)  # 滤芯A状态（滤芯百分比）
        self.boby_A5['fpB'] = random.randrange(30, 50)  # 滤芯B状态（滤芯百分比）
        self.boby_A5['fpC'] = random.randrange(30, 50)  # 滤芯C状态（滤芯百分比）
        self.boby_A5['td2'] = random.randrange(10, 20)  # TDS2
        self.boby_A5['td1'] = random.randrange(80, 100)  # TDS1
        self.boby_A5['wsr'] = random.randrange(30, 40)  # 节水比率
        self.boby_A5['ect'] = random.randrange(5, 15)  # 错误数量
        self.boby_A5['flg'] = 1 << 1  #  错误旗标
        self.boby_A5['dnt'] = random.randrange(60, 254)   # 断网时长（秒)
        self.boby_A5['int'] = random.randrange(5, 15)   # 进水次数（Inlet Counter）
        self.boby_A5['tnt'] = random.randrange(5, 15)   # 累计用水量（##单位：公升）
        self.boby_A5['sgt'] = random.randrange(1, 31)  # 基站信号数量，信号强度

        head_A5 = self.get_head(msg_id='A5')

        print('boby_A5 = {0}'.format(self.boby_A5))
        return Pack(head_A5, self.boby_A5 ).get_msg()

    def get_event(self):
        '''
        bit位        开关名称
         0            出水开关
         1            电源开关
         2            加热开关
         3            制冷开关
         4            臭氧开关
        # 汇报设备动态 A3-B3
        :return:
        '''
        self.boby_A3 = collections.OrderedDict()
        self.boby_A3['evc'] = 101  # 事件类型编码
        self.boby_A3['val'] = 1  # 事件参数
        self.boby_A3['evt'] = ''  # 事件详情

        self.boby_A3['now'] = standard_time()  # 当前时间
        self.boby_A3['sw'] = 1 << 0  # 开关位，int
        self.boby_A3['fpA'] = random.randrange(30, 90)  # 滤芯A状态（滤芯百分比）
        self.boby_A3['fpB'] = random.randrange(30, 90)  # 滤芯B状态（滤芯百分比）
        self.boby_A3['fpC'] = random.randrange(30, 90)  # 滤芯C状态（滤芯百分比）
        self.boby_A3['td2'] = random.randrange(50, 254)  # TDS2
        self.boby_A3['td1'] = random.randrange(50, 254)  # TDS1
        self.boby_A3['wsr'] = random.randrange(30, 40)  # 节水比率
        self.boby_A3['ect'] = random.randrange(5, 15)  # 错误数量
        self.boby_A3['flg'] = 1 << 1  # 错误旗标
        self.boby_A3['dnt'] = random.randrange(60, 254)  # 断网时长（秒)
        self.boby_A3['int'] = random.randrange(5, 15)  # 进水次数（Inlet Counter）
        self.boby_A3['tnt'] = random.randrange(5, 15)  # 累计用水量（##单位：公升）
        self.boby_A3['sgt'] = random.randrange(20, 60)  # 基站信号数量，信号强度

        head_A3 = self.get_head(msg_id='A3')

        return Pack(head_A3, self.boby_A3).get_msg()

    # def randrom_alarm(self):
    #     #  随机错误

if __name__ == '__main__':
    d1 = Device(dev_id='test001')
    d2 = Device(dev_id='test002')

    print(d1.get_register())
    print(d2.get_register())
    print(d1.get_hat())

    hexstr = bytes_to_hexstr(d1.get_register())
    print(hexstr)
