# -*- coding: utf-8 -*-
"""
Created on Thu May 05 21:59:18 2016
test.py
仅仅用作开发测试使用，每次开发一个模块完毕必须清空。
@author: WangTao
"""
import pandas as pd
import numpy as np


#查找大行情的函数
def find_big(code='', check=pd.DataFrame()):
    ''
    result = {}
    start = 1
    #开始进行数据处理  
    if len(check) > 0:
        for i in xrange(len(check)): #出发点，遍历全部节点
            p = check.iloc[i] #当前节点P
            if np.isnan(p.values[0]):
                continue
            else:
                if start == 1: #带start的P节点
                    m1 = m2 = m3 = p
                    start = 0
                    continue
                else: #P节点
                    m1 = p
                
                if m1[0] >= m2[0]: #爬坡
                    m2[0] = m1[0]
                    continue
                else:
                    if m1[0] <= m3[0]: #返回起始节点
                        start = 1
                        continue 
                    else:
                        if m2[0] != 0: 
                            back = m1[0]/m2[0]
                        else:
                            back = 0.91
                        if back >= 0.9:
                            continue
                        else:
                            rate = m2[0]/m3[0]
                            if rate < 1.7: #非大行情
                                start = 1
                                continue
                            else: #大行情
                                
                            
                
            



if __name__ == '__main__':
    
    #获得基础数据
    filesave = 'c:\\tmp\\save.h5'
    fileinfo = 'c:\\tmp\\info.h5'
    calender = pd.read_hdf(fileinfo, 'calender')
    qfq000155 = pd.read_hdf(filesave, 'qfq/000155')
    
    cal = pd.DataFrame(calender)
    close = pd.DataFrame(qfq000155.close)
    check = pd.merge(close, cal, left_index=1, right_index=1)
    