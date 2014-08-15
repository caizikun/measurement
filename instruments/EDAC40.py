from ctypes import *
import os
from instrument import Instrument
import pickle
from time import sleep, time
import types
import logging
import numpy
import qt
from qt import *
from numpy import *
from data import Data



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
        WINDIR=os.environ['WINDIR']
        self._edac40 = windll.LoadLibrary(WINDIR+'\\System32\\wlmData')
        self._edac40.GetFrequencyNum.restype = c_double
        sleep(0.02)




    def Get_Wavelength(self,channel):
        Wavelength = self._wlmData.GetWavelengthNum(channel, c_double(0))
        return Wavelength
