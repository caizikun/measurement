from ctypes import *
import os
from instrument import Instrument
import pickle
from time import sleep, time
import types
import logging
import numpy
import qt
import ctypes
from qt import *
import numpy as np
from data import Data

class edac40_list_node(ctypes.Structure):
    _fields_ = [
        ('ip_address', ctypes.c_char_p),
        ('MAC_address', ctypes.c_char_p),
    ]

class EDAC40(Instrument): #1
    '''
    This is the driver for the EDAC40 ethernet connected 40-channel DAC module. 
    Initially used to drive an OKOtech Deformable mirror (Aug 2014 - Machiel Blok)

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'EDAC40')
    
    status:
     1) create this driver!=> is never finished
    TODO:
    '''

    def __init__(self, name): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument EDAC40')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)
        device_num=self.list_devices(2,500,1)
        #print device_num
        # add parameters to instrument
        #self.add_parameter('wavelength', flags = Instrument.FLAG_GET, type=types.FloatType,units='nm',format = '%.6f')
        #self.add_parameter('integration_time', flags = Instrument.FLAG_GETSET, type=types.IntType, minval = 0, maxval = 9999, units = 'ms')
                
        
        # To add functions that are externally available??
        #self.add_function('')
        #self.add_function('')        
        
        #Initialize some values
        #self._ref_freq = 470.400
        #self._last_valid = [self._ref_freq, self._ref_freq, self._ref_freq, self._ref_freq]
        
    def _load_dll(self): #3
        print __name__ +' : Loading edac40.dll'
        self._edac40 = windll.LoadLibrary('D:\measuring\measurement\hardware\EDAC40\edac40.dll')
        sleep(0.02)


    def list_devices(self,max_device_num,discover_timeout,discover_attempts):
        list_node=np.zeros(max_device_num,dtype=edac40_list_node)  
        arr_tmp=(('0'*16,'0'*18))     
        arr=(('0'*16,'0'*18),('0'*16,'0'*18))       
        for i in arange(max_device_num-2):
            arr=arr+arr_tmp
        print arr    
        list_node=(edac40_list_node*max_device_num)(*arr)    
        try:
            self._edac40.edac40_list_devices(ctypes.byref(list_node),ctypes.c_int(max_device_num),ctypes.c_int(discover_timeout),ctypes.c_int(discover_attempts))
        except:
            print 'Timeout error'   
        #return list_node

    #def Get_Wavelength(self,channel):
    #    Wavelength = self._wlmData.GetWavelengthNum(channel, c_double(0))
    #    return Wavelength
