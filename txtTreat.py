#c:\python
#FileName:txtTreat.py
# -*- coding: utf-8 -*-
"""Text file treated.

This program only tread simple text file in these ways:
1)Sort lines;
2)Delete longer than 64 chars or shorter than 8 chars;
3)Delete the duplicated lines;
4)Delete the lines have Non-ASCII chars.
***Caution: This program only can tread the file's size smaller than 1/5 of avilibe memory!"""
import win32ui

#选择源文件
dlg=win32ui.CreateFileDialog(1) # 1表示打开文件对话框
dlg.SetOFNInitialDir('e:\\allpass') # 设置打开文件对话框中的初始显示目录
dlg.DoModal()
inFile=dlg.GetPathName() # 获取选择的文件名称

#选择目标文件
dlg=win32ui.CreateFileDialog(0,'txt') # 1表示打开文件对话框
dlg.SetOFNInitialDir('e:\\allpass') # 设置打开文件对话框中的初始显示目录
dlg.DoModal()
outFile=dlg.GetPathName() # 获取选择的文件名称

del dlg


#inFile="e:\\allpass\\12.txt"
#outFile="e:\\allpass\\l.txt"
isEnd=False
i=0
j=0
s=[]
t=[]
done=0

f=open(inFile)
#    t=f.readlines()
tmp=f.read()
t=tmp.split('\n')

f.close()
print "File loaded!"
print "Total ",len(t),"Lines"
o=len(t)
#sort
t.sort()
print "List sorted!"
#Delete too long or too short line.
while isEnd==False:
	if len(t[i])>=8 or len(t[i])<64:
		s.append(t[i])
		i+=1
	else:
		j+=1
	if i+1==len(t):
		isEnd=True
	if i%1000000==0:
		print "treated:",i/1000000,'Mil lines...,\tdeleted',j,"lines..."
t=s
s=[]
p=len(t)
print "No use string deleted ",o-p-1," lines!"
#Delete Duplications.
isEnd=False
i=0
j=0
while isEnd==False:
	if t[i]!=t[i+1]:
		s.append(t[i])
		i+=1
	else:
		i+=1
		j+=1
		
	if i+1==len(t):
		isEnd=True
	if i%1000000==0:
		print "treated:",i/1000000,'Mil lines...,\tdeleted',j,"lines..."
t=s
s=[]
q=len(t)
print "Duplications deleted ",p-q," lines!"
#Delete Non-ASCII lines.
isEnd=False
i=0
j=0
s1=t[i]
while isEnd==False:
	try:
		s2=s1.decode('utf-8','replace')
	except UnicodeError:
		i+=1
		if i+1==len(t):isEnd=True
		else:s1=t[i]
		continue
	if len(s1)==len(s2):
		s.append(t[i])
		i+=1
	else:
		i+=1
		j+=1
	if i+1==len(t):
		isEnd=True
	else:
		s1=t[i]
	if i%1000000==0:
		print "treated:",i/1000000,'Mil lines...,\tdeleted',j,"lines..."
t=s
s=[]		
f=open(outFile,"w")
f.writelines(t)
f.close()
r=len(t)
print "Deleted ",q-r-1," none ASCII lines!"

print "Done! Deleted ",o-r," lines!"
print "New file has ",r,"lines!"
