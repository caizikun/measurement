
import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class CavityScan ():

    def __init__ (self, exp_mngr):

        self._exp_mngr = exp_mngr

        self._scan_initialized = False
        self.V_min = None
        self.V_max = None
        self.nr_V_points = None
        self.nr_avg_scans = 1
        self.nr_repetitions = 1

        self.use_sync = False
        self.sync_delay_ms = None

        self.autostop = None
        self.autosave = None
        self.file_Tag = None

        self.data = None
        self.PD_signal = None
        self.tstamps_ms = None
        self.scan_params = None

    def set_scan_params (self, v_min, v_max, nr_points):
        self.V_min = v_min
        self.V_max = v_max
        self.nr_V_steps = nr_points
        self._scan_initialized = True

    def laser_scan (self, use_wavemeter = False, force_single_scan = True):

        v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
        self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
        
        self.frequencies = np.zeros (self.nr_V_steps)
        self.PD_signal = np.zeros (self.nr_V_steps)

        if use_wavemeter:
            avg_nr_samples = self.nr_avg_scans
            if force_single_scan:
                avg_nr_samples = 1
            dac_no = self._exp_mngr._adwin.dacs['newfocus_freqmod']
            self._exp_mngr._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.V_min)
            qt.msleep (0.1)
            for n in np.arange (self.nr_V_steps):
                self._exp_mngr._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.v_vals[n])
                value = 0
                for j in np.arange (avg_nr_samples):
                    self._exp_mngr._adwin.start_read_adc (adc_no = self._adwin.adcs['photodiode'])
                    value = value + self._exp_mngr._adwin.get_read_adc_var ('fpar')[0][1]
                value = value/avg_nr_samples
                self.PD_signal[n] = value
                qt.msleep (0.01)
                self.frequencies[n] = self._exp_mngr._wm_adwin.Get_FPar (self._wm_port)
                qt.msleep (0.05)
        else:
            self.success, self.data, self.tstamps_ms, self.scan_params = self._exp_mngr._adwin.scan_photodiode (scan_type = 'laser',
                     nr_steps = self.nr_V_steps, nr_scans = self.nr_avg_scans, wait_cycles = self._exp_mngr.wait_cycles, 
                    start_voltage = self.V_min, end_voltage = self.V_max, 
                    use_sync = self.use_sync, delay_ms = self.sync_delay_ms)

            for j in np.arange (self.nr_avg_scans):
                if (j==0):
                    values = self.data[0]
                else:
                    values = values + self.data[j]
            self.PD_signal = values/float(self.nr_avg_scans)


    def initialize_piezos (self, wait_time=0.2):
        self._exp_mngr._adwin.start_set_dac(dac_no=self._exp_mngr._adwin.dacs['jpe_fine_tuning_1'], dac_voltage=self.V_min)
        self._exp_mngr._adwin.start_set_dac(dac_no=self._exp_mngr._adwin.dacs['jpe_fine_tuning_2'], dac_voltage=self.V_min)
        self._exp_mngr._adwin.start_set_dac(dac_no=self._exp_mngr._adwin.dacs['jpe_fine_tuning_3'], dac_voltage=self.V_min)
        qt.msleep(wait_time)

    def piezo_scan (self):

        v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
        self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)  
        self.PD_signal = np.zeros (self.nr_V_steps)

        self.success, self.data, self.tstamps_ms, self.scan_params = self._exp_mngr._adwin.scan_photodiode (scan_type = 'fine_piezos',
                nr_steps = self.nr_V_steps, nr_scans = self.nr_avg_scans, wait_cycles = self.wait_cycles, 
                start_voltage = self.V_min, end_voltage = self.V_max, 
                use_sync = self.use_sync, delay_ms = self.sync_delay_ms)

        #output PD_signal as the average over nr_avg_scans
        for j in np.arange (self.nr_avg_scans):
            if (j==0):
                values = self.data[0]
            else:
                values = values + self.data[j]
        self.PD_signal = values/float(self.nr_avg_scans)
