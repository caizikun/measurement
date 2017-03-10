#####################################################################################################
# CONTROLLER for fine voltage controller PI for cav characterization set-up    --- Lisanne Coenen, 2016  --- coenen.lisanne@gmail.com
# 
# 'master_of_char_cavity' (MOC) controls the fine voltage PI controller for cavity length control of the cavity characterization set up.
#
#  Please run MOC.close() before quitting, to close the tracker file
#####################################################################################################

import os
from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
import time
import types
import gobject
import numpy as np
from lib import config
from measurement.lib.config import moc_cfg

                    
class master_of_char_cavity(CyclopeanInstrument):
    def __init__(self, name, adwin, **kw):
        print 'init cyclopean_instrument'
        CyclopeanInstrument.__init__(self, name, tags =[])
        print 'initialising masterofchar'
        self._adwin = qt.instruments[adwin]
        self._fine_piezos = 'PI_fine_tuning'
        #self.set_fine_piezo_voltages(0,0,0)

        # #design properties in mm (see JPE datasheet).
        # self.cfg_pars = moc_cfg.config['moc_cav1']
        # self.fiber_z_offset = self.cfg_pars['fiber_z_offset'] #fiber offset with respect to fiber interface
        # self.h = self.cfg_pars['h_mm']+self.fiber_z_offset#33.85+self.fiber_z_offset
        # self.R = self.cfg_pars['R_mm']#14.5
        # self.max_spindle_steps = self.cfg_pars['max_spindle_steps']

        # #Cartesian coordinates in the lab-frame (mm)
        self.track_v_piezo_1 = None


# Do I need this? 
        # reinit_spindles = kw.pop('reinit_spindles', False)
        # if reinit_spindles:         
        #     self.reset_spindle_tracker()
        # else:
        #     print 'Tracker initialized from file...'
        #     self.tracker_file_readout()

        self.add_function('set_fine_piezo_voltages')

    # def ramp_fine_piezo_voltages(self,v1,v2,v3,voltage_steps=0.0001):
    #     target_voltages = np.array([v1,v2,v3])
    #     if not(self._adwin.is_linescan_running()) and self.check_fine_piezo_voltage_limits(target_voltages):
    #         curr_voltages = self.get_fine_piezo_voltages()
    #         voltage_difference = np.max(np.abs(target_voltages-curr_voltages))
    #         number_of_steps = min([500,max([10,int(voltage_difference/voltage_steps)])]) #minumum 10 steps, max 500
    #         self._adwin.linescan(self._fine_piezos,curr_voltages, target_voltages, number_of_steps, 5, value='none',blocking=False)
    #         return True
    #     return False

    def check_fine_piezo_voltage_limits(self,voltage):
        if ((voltage<0) or (voltage>10)):
            print 'Voltage out of range  - v1'
            return False
        else:
            return True

    def set_fine_piezo_voltages(self,v1):
        target_voltages = v1
        print 'voltage  = ',target_voltages
        if self.check_fine_piezo_voltage_limits(target_voltages):
            print 'checking fine piezo limit'
            self._adwin.set_dac_voltage((self._fine_piezos,target_voltages))
            
            return True
        return False

    def get_fine_piezo_voltages(self):
        return self._adwin.get_dac_voltage(self._fine_piezos)



