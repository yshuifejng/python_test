# -*- coding: utf8 -*-
u'''
Created on 2017年8月22日 上午11:45:59

@author: shaofeng.yang
'''


class test(object):
    def __init__(self, name, sex):
        self._name = name
        self._sex = sex

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, dict):
            raise Exception('name is dict')
        else:
            self._name = name

    def get_msg(self):
        return self._name

if __name__ == '__main__':
    t = test('hello', 'famax')
    t.name = 'abc'
    print(t.name)
    print(t.get_msg())