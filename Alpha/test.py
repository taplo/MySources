# -*- coding: utf-8 -*-
"""
Created on Thu May 05 21:59:18 2016
test.py
仅仅用作开发测试使用，每次开发一个模块完毕必须清空。
@author: WangTao
"""
import pandas as pd
import numpy as np

global totalStatus
totalStatus = {}
#加载本地数据路径
def load_local_path():
    """
    判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
    """
    import os
    hostname=os.popen('hostname').read()

    if 'PrivateBook' in hostname:#家庭笔记本
        filepath = 'c:\\tmp\\'
        #filename = 'c:\\tmp\\save.h5'
    elif 'USER-20160422LP' in hostname:#办公室台式机
        filepath = u'D:\\用户目录\\My Documents\\Python\\'
        #filename = u'D:\\用户目录\\My Documents\\Python\\save.h5'
    else:
        filepath = 'd:\\'
        #filename = 'd:\\save.h5'

    totalStatus['filepath'] = filepath
    return filepath

#检查是否有停盘
def check_suspend(check=pd.DataFrame(), limit=3):
    if len(check) > 0:
        count = 0
        for i in xrange(len(check)):
            c = check.iloc[i]
            if np.isnan(c.values[0]):
                if c.values[1] == 1:
                    count +=1
        if count > limit:
            return True
        else:
            return False

#查找大行情的函数
def find_big(code='', check=pd.DataFrame(), drawback=0.1, bigrate=1.7):
    ''
    result = []
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
                
                if m1.values[0] >= m2.values[0]: #爬坡
                    m2 = m1
                    continue
                else:
                    if m1.values[0] <= m3.values[0]: #返回起始节点
                        start = 1
                        continue 
                    else:
                        if m2.values[0] != 0: 
                            back = m1.values[0]/m2.values[0]
                        else:
                            back = 0.91
                        if back >= (1-drawback):
                            continue
                        else:
                            rate = m2.values[0]/m3.values[0]
                            if rate < bigrate: #非大行情
                                start = 1
                                continue
                            else: #大行情
                                pos = check.index.get_loc(m3.name)
                                if pos > 30:
                                    startpos = pos - 30
                                else:
                                    startpos = 0
                                if check_suspend(check.iloc[startpos:pos]): #停盘行情
                                    start = 1
                                    continue
                                else: #添加到行情列表
                                    mark = {}
                                    mark['code'] = code
                                    mark['start'] = m3
                                    mark['end'] = m2
                                    result.append(mark)
                                    start = 1
    return result

if __name__ == '__main__':
    code = '002713'
    #获得基础数据
    filesave = load_local_path() + 'save.h5'
    fileinfo = load_local_path() + 'info.h5'
    calender = pd.read_hdf(fileinfo, 'calender')
    qfq = pd.read_hdf(filesave, 'qfq/' + code)
    
    cal = pd.DataFrame(calender)
    close = pd.DataFrame(qfq.close)
    
    close = close.resample('d')
    check = pd.merge(close, cal, left_index=1, right_index=1)
    result = find_big(code, check, drawback=0.1)
    df = pd.Series(result)
    print code
    print result
    