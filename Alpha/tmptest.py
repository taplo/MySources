# -*- coding: utf-8 -*-
"""
Created on Fri Apr 01 07:57:11 2016
tmptest.py 仅供测试
@author: Administrator
"""

'''进度条测试
import time 
from progressbar import ProgressBar,Percentage

lines=[3000,]


for line in lines: 
    pbar = ProgressBar(widgets=[Percentage()], maxval=line).start() 
    for i in range(line): 
        time.sleep(0.01) 
        pbar.update(i+1) 
    pbar.finish() 
    print u"此部分已经完成！"
    print i
    print line
'''

'''重复打印到屏幕测试
import sys
from time import sleep

output = sys.stdout
for count in range(0,100):
    second=0.3
    sleep(second)
    output.write('\r%d\r'%(count+1))
    output.flush()
'''
#获得当日大单数据测试

def GetDayData(code):
    import tushare as ts
    import datetime as dt

    if code=='':
        code='600030'
    df=ts.get_sina_dd(code, date=str(dt.date.today()))
    s=df.describe()
    print code
    print s
    #return s

#获得高转送测试
def GetHighBack(t):
    import tushare as ts

    if t==0:
        t=50
    df = ts.profit_data()
    print t
    if len(df)<2:
        print '无！'        
        #return '无！'
    else:
        df=df.sort_values('shares',ascending=False)
        print df[:t]        
        #return df[:t]


#多线程测试
import multiprocessing

if __name__ == '__main__':
    '''
    res=[]
    pool=multiprocessing.Pool(processes=2)
    res.append(pool.apply_async(GetDayData,('600999',)))
    res.append(pool.apply_async(GetHighBack,(10,)))
    pool.close()
    pool.join()
    for i in res:
        print i.get()
    ''' 
    
    
    p1=multiprocessing.Process(target=GetDayData,args=('600999',))
    p2=multiprocessing.Process(target=GetHighBack,args=(10,))
    p1.start()
    p2.start()
    p1.run()
    p2.run()
    p1.join()
    p2.join()
   
'''    
    df1=GetDayData('600999')
    print df1
    
    df2=GetHighBack(10)
    print df2
'''    
    #pass