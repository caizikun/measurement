
import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class CavityExpManager (Instrument):

    def __init__ (self, name, adwin, wm_adwin, laser, moc, counter):
        Instrument.__init__(self,name)

        self._adwin = adwin
        self._wm_adwin = wm_adwin
        self._laser = laser
        self._moc = moc
        self._ctr = counter
        self._wm_port = 45

        #trigger signals to update Control Panel, for changes induced by other panels
        self._laser_updated = False
        self._moc_updated = False
        self._piezo_updated = False

        self._laser_wavelength = None
        self._laser_power = None
        self._laser_fine_tuning = None
        self._coarse_piezos = None
        self._fine_piezos = None
        self.room_T = None
        self.low_T = None
        self.wait_cycles = 1

        # I do not understand why we need the get and set for this separately here.
        # We have them in the NewFocusVelocity instruemt.
        # It seems like things might be working against eachother if I do it like this.
        # maybe I can do this better, by refering to the laser function in GUI?? 
        self.add_parameter('laser_wavelength',
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET,
                units = 'nm'
                minval = 636, maxval = 640)

        self.add_parameter('laser_power',
                type = types.TupleType,
                flags = Instrument.FLAG_GET,
                units = 'mW'
                minval = 0, maxval = 20)
        self.set_laser_wavelength(637)#this was for some reason in the UI_control_panel init. 
        # It seems very silly there. but also silly here. do we need it at all????
        #Rather initialize to latest setting upon startup


    def do_set_laser_wavelength (self, wavelength):
        self._laser.set_wavelength (wavelength=wavelength)
        self.update_coarse_wavelength (wavelength)
        #return 0 #I think the failure/success of this function is nowhere processed
   
    def do_get_laser_wavelength (self):
        l = self._laser.get_wavelength()
        self.update_coarse_wavelength (l)
        return l

    def do_get_laser_power (self):
        l = self._laser.get_power_level()
        self.update_laser_power (l)
        return l

    def do_set_laser_power(self, value):
        self._laser.set_power_level (power=value)


    def set_piezo_voltage (self, V, wait_time = 0.01):
        self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_1'], dac_voltage=V)
        self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_2'], dac_voltage=V)
        self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_3'], dac_voltage=V)
        self.update_fine_piezos (V)
        qt.msleep(wait_time)

    def update_coarse_wavelength (self, value):
        self._laser_wavelength = value
        self._system_updated = True

    def update_laser_power (self, value):
        self._laser_power = value
        self._system_updated = True

    def update_coarse_piezos (self, x, y, z):
        self._coarse_piezos = np.array([x, y, z])
        self._system_updated = True

    def update_fine_piezos (self, value):
        self._fine_piezos = value
        self._system_updated = True
