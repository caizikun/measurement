# -*- coding: mbcs -*-
typelib_path = u'C:\\Windows\\SysWOW64\\CIUsbLib.dll'
_lcid = 0 # change this if required
from ctypes import *
from comtypes import GUID
from ctypes import HRESULT
from comtypes.typeinfo import ULONG_PTR
from comtypes.automation import VARIANT
from comtypes import helpstring
from comtypes import COMMETHOD
from comtypes import dispid
from comtypes import CoClass
from comtypes.automation import VARIANT
#from comtypes import IUnknown
from comtypes.automation import IDispatch


class IHostDrv(IDispatch):
    _case_insensitive_ = True
    u'IHostDrv Interface'
    _iid_ = GUID('{41487896-06E3-42ED-AA6A-25FC6E99C4FB}')
    _idlflags_ = ['dual', 'oleautomation']
IHostDrv._methods_ = [
    COMMETHOD([dispid(1), helpstring(u'method CIUsb_GetStatus')], HRESULT, 'CIUsb_GetStatus',
              ( ['in'], c_int, 'nDevId' ),
              ( ['in'], c_int, 'nStatId' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
    COMMETHOD([dispid(2), helpstring(u'method CIUsb_SetControl')], HRESULT, 'CIUsb_SetControl',
              ( ['in'], c_int, 'nDevId' ),
              ( ['in'], c_int, 'nCntlId' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
    COMMETHOD([dispid(3), helpstring(u'method CIUsb_SendFrameData')], HRESULT, 'CIUsb_SendFrameData',
              ( ['in'], c_int, 'nDevId' ),
              ( ['in'], POINTER(c_ubyte), 'pFrameData' ),
              ( ['in'], c_int, 'nBuffSize' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
    COMMETHOD([dispid(4), helpstring(u'method CIUsb_SetNotify')], HRESULT, 'CIUsb_SetNotify',
              ( ['in'], ULONG_PTR, 'uWindow' ),
              ( ['in'], c_uint, 'uMessageId' )),
    COMMETHOD([dispid(5), helpstring(u'method CIUsb_GetAvailableDevices')], HRESULT, 'CIUsb_GetAvailableDevices',
              ( ['out'], POINTER(c_long*32), 'pDeviceIds' ),
              ( ['in'], c_int, 'nSizeBuff' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
    COMMETHOD([dispid(6), helpstring(u'method CIUsb_StreamFrameData')], HRESULT, 'CIUsb_StreamFrameData',
              ( ['in'], c_int, 'nDevId' ),
              ( ['in'], POINTER(c_ubyte), 'pFrameData' ),
              ( ['in'], c_int, 'nBuffSize' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
    COMMETHOD([dispid(7), helpstring(u'method CIUsb_StepFrameData')], HRESULT, 'CIUsb_StepFrameData',
              ( ['in'], c_int, 'nDevId' ),
              ( ['in'], POINTER(c_ushort*160), 'pFrameData' ),
              ( ['in'], c_int, 'nBuffSize' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
    COMMETHOD([dispid(8), helpstring(u'method CIUsb_FlushStream')], HRESULT, 'CIUsb_FlushStream',
              ( ['in'], c_int, 'nDevId' ),
              ( ['out'], POINTER(c_int), 'p_nStatus' )),
]
################################################################
## code template for IHostDrv implementation
##class IHostDrv_Impl(object):
##    def CIUsb_SetNotify(self, uWindow, uMessageId):
##        u'method CIUsb_SetNotify'
##        #return 
##
##    def CIUsb_StreamFrameData(self, nDevId, pFrameData, nBuffSize):
##        u'method CIUsb_StreamFrameData'
##        #return p_nStatus
##
##    def CIUsb_GetAvailableDevices(self, nSizeBuff, p_nStatus):
##        u'method CIUsb_GetAvailableDevices'
##        #return pDeviceIds
##
##    def CIUsb_GetStatus(self, nDevId, nStatId):
##        u'method CIUsb_GetStatus'
##        #return p_nStatus
##
##    def CIUsb_FlushStream(self, nDevId):
##        u'method CIUsb_FlushStream'
##        #return p_nStatus
##
##    def CIUsb_StepFrameData(self, nDevId, pFrameData, nBuffSize):
##        u'method CIUsb_StepFrameData'
##        #return p_nStatus
##
##    def CIUsb_SetControl(self, nDevId, nCntlId):
##        u'method CIUsb_SetControl'
##        #return p_nStatus
##
##    def CIUsb_SendFrameData(self, nDevId, pFrameData, nBuffSize):
##        u'method CIUsb_SendFrameData'
##        #return p_nStatus
##
##    def CIUsb_StepFrameDataVar(self, nDevId, pFrameDataVar, nBuffSize):
##        u'method CIUsb_StepFrameDataVar'
##        #return p_nStatus
##
##    def CIUsb_StreamFrameDataVar(self, nDevId, pFrameDataVar, nBuffSize):
##        u'method CIUsb_StreamFrameDataVar'
##        #return p_nStatus
##

class CHostDrv(CoClass):
    u'HostDrv Class'
    _reg_clsid_ = GUID('{615FAAA3-B515-4D4C-9F04-013D13FEB154}')
    _idlflags_ = []
    _typelib_path_ = typelib_path
    _reg_typelib_ = ('{0B17F235-D808-4A8B-82FB-F892607C1D55}', 1, 0)
CHostDrv._com_interfaces_ = [IHostDrv]

class Library(object):
    u'CIUsbLib 1.0 Type Library'
    name = u'CIUsbLib'
    _reg_typelib_ = ('{0B17F235-D808-4A8B-82FB-F892607C1D55}', 1, 0)

__all__ = [ 'CHostDrv', 'IHostDrv']
from comtypes import _check_version; _check_version('')
