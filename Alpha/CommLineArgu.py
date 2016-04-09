#C:\Users\WangTao\Documents\Python
# FileName: test04.py
# -*- coding:utf-8 -*-

import sys
def test01():
	print 'test01'

#测试
print 'The command line arguments are:'

for i in sys.argv:
	print i

print '\nThe PYTHONPATH is'
for j in sys.path:
	print j



if __name__ == "__main__":
	test01()

