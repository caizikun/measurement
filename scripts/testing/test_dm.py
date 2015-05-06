import comtypes
import comtypes.client as cc
import ctypes
import numpy as np
import test_01

dev= cc.CreateObject('{615FAAA3-B515-4d4c-9F04-013D13FEB154}', interface=test_01.IHostDrv)
#dev= cc.CreateObject('CIUsbLib2.HostDrv')
#dev = cc.GetActiveObject('{615FAAA3-B515-4d4c-9F04-013D13FEB154}')

#ll = ctypes.c_long(32)
#ret= np.ones(32, dtype=np.long)
#stat=ctypes.c_long(1)
res = dev.CIUsb_GetStatus(0,1)
print res
#c_array = ctypes.c_long*32
#point_c_array = ctypes.POINTER(c_array)

#dev.CIUsb_GetAvailableDevices.restype = [point_c_array,ctypes.POINTER(ctypes.c_long)] 
res = dev.CIUsb_GetAvailableDevices(32)
#res = dev.CIUsb_GetAvailableDevices(ret.ctypes.data)

a= res[0]
print [a[i] for i in range(31)]
res = dev.CIUsb_SetControl(0,3)

res = dev.CIUsb_SetControl(0,2)


res = dev.CIUsb_SetControl(0,4) #turn on the the HV

ushort_array = ctypes.c_ushort*160
ushort_data = ushort_array(0)

for i in np.arange(160):
	ushort_data[i]=0xffff

res = dev.CIUsb_StepFrameData(0,ushort_data,320)
print res 


