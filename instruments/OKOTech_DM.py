from time import sleep, time
import numpy as np
from instrument import Instrument
import logging
import qt

class OKOTech_DM(Instrument): 
    '''
    This is the driver for the OKOTech Deformable mirror, controlled by the EDAC40  
    (Aug 2014 - Machiel Blok)

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'OKOTech_DM',dac=qt.instruments[<dac_instrument_name>])
    
    status:
     1) create this driver!=> is never finished
    TODO:
    - make better system for updating current dac values (see master of space)
    '''

    def __init__(self, name,dac): 
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument OKOTech DM')
        Instrument.__init__(self, name, tags=['virtual'])
        self._dac=dac

        #Variables, keeping track of voltage properties per pin
        self.dac_values = [0]*40
        self.offset = [32768]*40
        self.gain = [65535]*40
        self.global_offset = 8191
        self.voltage_ref=3


        # To add functions that are externally available
        self.add_function('get_current_voltage')
        self.add_function('value_from_voltage')
        self.add_function('set_voltage_single_pin')

    def get_current_voltage(self,pin_nr):
        VOUT=4*self.voltage_ref*((self.dac_values[pin_nr-1]/np.uint16(2**16))-(self.global_offset/float(2**14-1)))
        return VOUT

    def value_from_voltage(self,pin_nr,voltage):
        print 'global part', self.global_offset/float(2**14-1)
        print 'total part',self.global_offset/float(2**14-1)+voltage/float(4*self.voltage_ref)
        DAC_CODE =(4*self.global_offset+(2**16-1)*voltage/float(4*self.voltage_ref))
        print DAC_CODE
        dac_value=np.uint16((DAC_CODE+(2**15-1)-self.offset[pin_nr-1])/float(self.gain[pin_nr-1]+1))
        print 'set %d Volt to pin nr %d ' %(voltage,pin_nr)
        print 'value from voltage: ', dac_value
        return dac_value

    def set_voltage_single_pin(self,pin_nr,voltage):
        dac_value=self.value_from_voltage(pin_nr,voltage)
        #self._dac.set_single_pin(1,pin_nr-1,dac_value)
        self.dac_values[pin_nr-1] = dac_value