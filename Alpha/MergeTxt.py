#c:\python
#FileName:MergeTxt.py
# -*- coding:utf-8 -*-

"""Merge two text files.

This program only merge two text files into one file.
These two files must be sorted and non-duplication."""

inF1="e:\\allpass\\3.txt"
inF2="e:\\allpass\\a.txt"
L1=0
L2=0
LO=0

outFile="e:\\allpass\\NetUP.txt"

f1=open(inF1)
f2=open(inF2)

outf=open(outFile,"w")

isEnd=False
End1=False
End2=False
s1=f1.readline()
L1+=1
s2=f2.readline()
L2+=1

while isEnd==False:
	
	#print L1,'\t',L2,'\t',LO,'\t',End1,'\t',End2,'\t',len(s1),'\t',len(s2)
	#print End1,'\t',End2
	if LO%1000000==0 and LO>0:print "Finished ",LO/1000000,"Mil lines..."
	
	if End1==True and End2==False:
		while End2==False:
			s2=f2.readline()
			L2+=1
			if len(s2)>0:
				outf.write(s2)
				LO+=1
			else:
				End2=True
	elif End2==True and End1==False:
		while End1==False:
			s1=f1.readline()
			L1+=1
			if len(s1)>0:
				outf.write(s1)
				LO+=1
			else:
				End1=True
	elif End1==True and End2==True:
		isEnd=True
	else:
		if s1<s2:
			outf.write(s1)
			LO+=1
			s1=f1.readline()
			L1+=1
			if len(s1)==0:End1=True	
		elif s1>s2:
			outf.write(s2)
			LO+=1
			s2=f2.readline()
			L2+=1
			if len(s2)==0:End2=True
		else:
			outf.write(s1)
			LO+=1
			s1=f1.readline()
			L1+=1
			s2=f2.readline()
			L2+=1
			if len(s1)==0:End1=True
			if len(s2)==0:End2=True

f1.close()
f2.close()
outf.close()

print "File 1 has ",L1," lines."
print "File 2 has ",L2," lines."
print "Output ",LO," lines."
print "Delete duplicat ",(L1+L2)-LO," lines."
