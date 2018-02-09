#!/usr/bin/env python
# encoding: utf-8
u"""
@version: ??
@author: shaofeng.yang
@contact: marvin_yang@novowater.com.cn
@software: PyCharm Community Edition
@file: test4.py
@time: 2017/9/21 9:58
"""

import pymysql
import traceback

# 打开数据库连接
db = pymysql.connect("58.250.17.19", "root", "yqjp123456", "yqjp_db", 13306, use_unicode=True, charset="utf8")
# db = pymysql.connect("58.250.17.19", "root", "yqjp123456", "yqjp_db", 13306, use_unicode=True)

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# SQL 插入语句
sql = """UPDATE `t_customer` SET nickname= '<<<EOT"  \ud83d\udca5  "EOT' WHERE customer_no = '15989453055''"""
cursor.execute('SET NAMES utf8mb4;')
# cursor.execute('SET CHARACTER SET utf8mb4;')
# cursor.execute('SET character_set_connection=utf8mb4;')
try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
except Exception as ex:
    # 如果发生错误则回滚
    # print(ex)
    print(traceback.print_exc())
    db.rollback()

# 关闭数据库连接
db.close()