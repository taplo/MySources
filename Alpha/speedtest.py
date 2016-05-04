# -*- coding: utf-8 -*-
"""
Created on %(date)s
测速程序
@author: %Taplo
"""
import datetime as dt
import decimal
import math

'''
def piprod(n):
    start=2**0.5
    pi=1
    for i in range(0,n+1):
        for j in range(0,i):
            start=(start+2)**0.5    
        pi*=start
    pi=2**(n+2)/pi
    return pi
				
def pisum(n):
    pi=3
    sign=1
    for i in range(1,n+1):
        pi+=sign*4.0/((i+1)*(i+2)*(i+3))
        sign=-sign
    return pi				
				
def chudnovsky(n):
	pi=decimal.Decimal(0)
	k=0
	while k < n:
		pi+=(decimal.Decimal(-1)**k)*(decimal.Decimal(math.factorial(6*k))/((math.factorial(k)**3)*(math.factorial(3*k)))*(13591409+545140134*k)/(640320**(3*k)))
		k+=1
	pi=pi*decimal.Decimal(10005).sqrt()/4270934400
	pi=pi**(-1)
	return pi
'''
if __name__ == '__main__':
	start_time = dt.datetime.now()
	#n = int(raw_input('请键入想要计算到小数点后的位数n:'))    #先键入字符串,再转化为整数
	n = 50000
	w = n+10                    #多计算10位，防止尾数取舍的影响
	b = 10**w                   #算到小数点后w位
	x1 = b*4//5                 #求含4/5的首项
	x2 = b// -239               #求含1/239的首项
	he = x1+x2                  #求第一大项
	n *= 2 			    #设置下面循环的终点，即共计算n项
	for i in xrange(3,n,2):     #循环初值=3，末值2n,步长=2
		x1 //= -25              #求每个含1/5的项及符号
		x2 //= -57121           #求每个含1/239的项及符号
		x = (x1+x2) // i        #求两项之和
		he += x                 #求总和
	pai = he*4             	    #求出π
	pai //= 10**10              #舍掉后十位
	
	end_time = dt.datetime.now()
	
	print end_time - start_time
	#print pai