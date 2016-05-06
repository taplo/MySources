# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 21:14:56 2016
test13:only test the progressbar
@author: WangTao
"""
import time
from progressbar import ProgressBar,Percentage,SimpleProgress,Bar


lines=[235,120,345,600]


for line in lines:
    pbar = ProgressBar(widgets=[Percentage(), Bar(), SimpleProgress()], maxval=line).start()
    for i in range(line):
        time.sleep(0.01)
        pbar.update(i+1)
    pbar.finish()
    print "this part is over!"

for line in lines:
    pbar = ProgressBar(widgets=[Percentage()], maxval=line).start()
    for i in range(line):
        time.sleep(0.01)
        pbar.update(i+1)
    pbar.finish()
    print "this part is over!"


for line in lines:
    pbar = ProgressBar(widgets=[SimpleProgress()], maxval=line).start()
    for i in range(line):
        time.sleep(0.01)
        pbar.update(i + 1)
    pbar.finish()
    print "this part is over!"

'''

for i in range(5):
    sys.stdout.write(' '*10+'\r')
    sys.stdout.flush()
    sys.stdout.write(str(i)*(5-i)+'\r')
    sys.stdout.flush()
    time.sleep(1)

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