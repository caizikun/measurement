from time import sleep, time
import numpy as np
from instrument import Instrument
import logging
import qt
import ctypes

class Multi_DM(Instrument): 
    '''
    This is the driver for the Multi Driver box: the DAC module that is used
    to drive the Boston micromachines/thorlabs Deformable mirror. 
    (Dec 2014 - Machiel Blok)

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'MultiDM')
    
    
    status:
     1) create this driver!=> is never finished
    TODO:
    '''

    def __init__(self, name): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument MultiDM')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        #sleep(0.01)


        #Get ip address

        
        #Open device connection

        # To add functions that are externally available
        #self.add_function('close')
        #self.add_function('set_single_pin')


    def _load_dll(self): 
        print __name__ +' : Loading CIUsbLib.dll'
        self.multidm = ctypes.cdll.LoadLibrary('D:\measuring\measurement\hardware\MultiDM\CIUsbLib\CIUsbLib.dll')
        sleep(0.02)
    def return_dll(self):
        return self.multidm
    def find_device(self,MAC_address):
        c_MAC=ctypes.create_string_buffer(MAC_address)
        self._edac40.edac40_find_device.restype=ctypes.c_char_p

        ip = self._edac40.edac40_find_device(c_MAC)
        return ip
