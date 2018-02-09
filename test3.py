# -*- coding: utf8 -*-
u'''
Created on 2017年8月29日 上午11:45:59

@author: shaofeng.yang
'''

import multiprocessing

def test(id=2, msg=None, sex=None):
    print('{0} {1} {2}'.format(id,msg, sex))

def multi(fun):
    pool = multiprocessing.Pool(2)
    p1 = [1, None,'aaa']
    p2 = (2, 'bbb')

    pool.apply_async(fun,p1)
    pool.apply_async(fun,p2)

    pool.close()
    pool.join()

if __name__ == '__main__':
    multi(test)