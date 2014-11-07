from time import sleep, time
import numpy as np
from instrument import Instrument
import logging
import qt
import types
from lib.misc import dict_to_ordered_tuples
import hdf5_data as h5

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
        self._name=name

        self.add_parameter('dac_values',
                type=types.ListType,
                flags=Instrument.FLAG_GET)
        self.add_parameter('voltages',
                type=types.ListType,
                flags=Instrument.FLAG_GET)
        
        #Variables, keeping track of voltage properties per pin
        self.voltage_ref=3
        dv_init=self.dac_value_from_voltage(1)
        self._dac_values = [dv_init]*40
        self._voltages   = [1]*40
        self.offset = [32768]*40
        self.gain = [65535]*40
        self.global_offset = 8191
        
        self._V_min=-6
        self._V_max=6
        self.V_hardcode_max=2.5
        self.V_hardcode_min=0


        # TO DO: for now this driver only uses DAC value. should implement gain, global offset and offset per pin as well.
        dac.set_all_to_constant(0,32768)
        dac.set_all_to_constant(1,32768)
        dac.set_all_to_constant(2,65535)
        dac.set_all_to_constant(3,8191)

        # To add functions that are externally available
        self.add_function('get_voltage')
        self.add_function('get_voltages')
        self.add_function('get_dac_values')
        self.add_function('dac_value_from_voltage')
        self.add_function('set_voltage_single_pin')
        self.add_function('set_voltage_all_pins')


    #Automatically created??
    def get_voltage(self,pin_nr):
        return self._voltages[pin_nr-1]

    def do_get_voltages(self):
        return self._voltages

    def do_get_dac_values(self):
        return self._dac_values

    def voltage_from_dac_value(self,dac_value):
        voltage=4*self.voltage_ref*(dac_value-32767/(2**16-1))
        return voltage

    def dac_value_from_voltage(self,voltage):
        dac_value =np.uint16((2**16-1)*0.5+(2**16-1)*voltage/float(4*self.voltage_ref))
        return dac_value
    '''
    #TO DO: make all functions work with offset and gain as well
    #Example:
    def value_from_voltage(self,pin_nr,voltage):
        dac_value =(4*self.global_offset+(2**16-1)*voltage/float(4*self.voltage_ref))
        dac_value=np.uint16((DAC_CODE+(2**15-1)-self.offset[pin_nr-1])/float(self.gain[pin_nr-1]+1))
        return dac_value
    '''

    def set_voltage_single_pin(self,pin_nr,voltage):
        """
        Set voltage between -6 and 6 V to a single pin.
        
        pin_nr:        Integer, 1-40
        Pin nr 

        voltage:          Integer, in Volt between -6 and 6
        sets Voltage to Pin_nr
        """
        if (voltage > self.V_hardcode_max) or (voltage < self.V_hardcode_min):
            print 'Error, %d Volt is out of range (V max %d , V min %d)' %(voltage,self.V_hardcode_max,self.V_hardcode_min)
        else:
            dac_value=self.dac_value_from_voltage(voltage)
            self._dac.set_single_pin(0,pin_nr,dac_value)
            self._dac_values[pin_nr-1] = dac_value
            self._voltages[pin_nr-1]=voltage

    def set_voltage_all_pins(self,voltages):
        """
        Set each pin to a unique voltage in one command.

        voltages:          [Integer]*40 , in Volt between -6 and 6
        sets voltages[i] to physical pin nr i+1 
        """
        set_voltages=True
        dac_values=[0]*40
        if len(voltages)!=40:
            print 'Input should be a list of len 40, with the desired voltages (len(%d) given)'%len(voltages)
        else:
            for i in np.arange(len(voltages)):
                if (voltages[i] > self.V_hardcode_max) or (voltages[i] < self.V_hardcode_min):
                    print 'Error, %d Volt is out of range (V max %d , V min %d)' %(voltages[i],self.V_hardcode_max,self.V_hardcode_min)
                    set_voltages=False
                else:
                    dac_values[i]=self.dac_value_from_voltage(voltages[i])
        if set_voltages:
            self._dac.set_all_pins(0,dac_values)
            self._dac_values = dac_values
            self._voltages = voltages

    def save_current_settings(self,parent=None,name=''):
        if parent == None:    
            parent = h5.HDF5Data(name='OKOTech_DM'+'_'+name)
            flush=True
        instrument_grp = parent.create_group('instrument_settings')
        #inslist = dict_to_ordered_tuples(qt.instruments.get_instruments())
    
    #for (iname, ins) in inslist:
        insgroup = instrument_grp.create_group(self._name)
        parlist = dict_to_ordered_tuples(self.get_parameters())
        
        for (param, popts) in parlist:
            try:
                insgroup.attrs[param] = self.get(param, query=True) \
                        if 'remote' in self.get_options()['tags'] \
                        else self.get(param, query=False)
            except (ValueError, TypeError):
                    insgroup.attrs[param] = str(self.get(param, query=False))
        if flush: parent.flush()            
  

        