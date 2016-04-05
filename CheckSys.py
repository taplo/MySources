#c:\python
#FileName:CheckSys.py
# -*- coding:utf-8 -*-

"""The status of system check program

This program will check the status of system to decide the params of program.
This program will check such information:
1)The memory size and the available memory size;
2)The threads of the CPU;
3)The available space of each disk;
"""
import sys
import wmi
reload(sys)
print sys.getdefaultencoding()
sys.setdefaultencoding("utf-8")

'''
#get the disk list
disks=wmi.WMI().Win32_LogicalDisk()

for d in disks:
	print d
'''
#Show each disk available percent
d=wmi.WMI()
for disk in d.Win32_LogicalDisk(DriveType=3):
  print disk.Caption, "%0.2f%% free" %(100.0 * long(disk.FreeSpace) / long(disk.Size)),"It's ",(long(disk.FreeSpace)/1024),"K"

'''
#show all processor in running
c=wmi.WMI ()
for process in c.Win32_Process ():
	print process.ProcessId, process.Name
'''
#shwo phyisical memory	
for Memory in c.Win32_PhysicalMemory(): 
	print "Memory Capacity: %.fMB" %(int(Memory.Capacity)/1048576)


"""
import time
c = wmi.WMI()
while True:
    for cpu in c.Win32_Processor():
        timestamp = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        print '%s | Utilization: %s: %d %%' % (timestamp, cpu.DeviceID, cpu.LoadPercentage)
    #end for
    time.sleep(5)
#end while
"""

from ctypes import *
class MEMORYSTATUS(Structure):
    _fields_ = [('dwLength', c_int), ('dwMemoryLoad', c_int), ('dwTotalPhys', c_int), ('dwAvailPhys', c_int), ('dwTotalPageFile', c_int),
            ('dwAvailPageFile', c_int), ('dwTotalVirtual', c_int), ('dwAvailVirtual', c_int)]
MEMORYSTATUS = MEMORYSTATUS()
windll.kernel32.GlobalMemoryStatus(byref(MEMORYSTATUS))
print 'To use memory percentage:', MEMORYSTATUS.dwMemoryLoad#使用物理内存的百分比
print 'Physical memory total:', MEMORYSTATUS.dwTotalPhys / (1024 * 1024)#物理内存总数
print 'Physical memory available:', MEMORYSTATUS.dwAvailPhys / (1024 * 1024) #可用内存总数