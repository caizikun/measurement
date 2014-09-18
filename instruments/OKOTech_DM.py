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
        self._V_min=-6
        self._V_max=6

        # TO DO: for now this driver only uses DAC value. should implement gain, global offset and offset per pin as well.
        dac.set_all(0,0)
        dac.set_all(1,32768)
        dac.set_all(2,65545)
        dac.set_all(3,8191)

        # To add functions that are externally available
        self.add_function('get_current_voltage')
        self.add_function('value_from_voltage')
        self.add_function('set_voltage_single_pin')

    def get_current_voltage(self,pin_nr):
        return self.dac_values[pin_nr-1]

    def voltage_from_dac_value(self,dac_value):
        voltage=4*self.voltage_ref*(dac_value-32767/(2**16-1)
        return voltage

    def value_from_voltage(self,voltage):
        dac_value =np.uint16((2**16-1)*0.5+(2**16-1)*voltage/float(4*self.voltage_ref))
        return dac_value
    '''
    #TO DO: make this function work with offset and gain as well
    def value_from_voltage(self,pin_nr,voltage):
        dac_value =(4*self.global_offset+(2**16-1)*voltage/float(4*self.voltage_ref))
        dac_value=np.uint16((DAC_CODE+(2**15-1)-self.offset[pin_nr-1])/float(self.gain[pin_nr-1]+1))
        return dac_value
    '''

    def set_voltage_single_pin(self,pin_nr,voltage):
        if (voltage > self._V_max) or (voltage < self._V_min):
            print 'Error, %d Volt is out of range (V max %d , V min %d)' %(voltage,self._V_max,self._V_min)
        else:
            dac_value=self.value_from_voltage(pin_nr,voltage)
            self._dac.set_single_pin(0,pin_nr-1,dac_value)
            self.dac_values[pin_nr-1] = dac_value



