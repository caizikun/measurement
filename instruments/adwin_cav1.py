# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config

from measurement.instruments.adwin import adwin
from measurement.lib.config import adwins as adwinscfg


class adwin_cav1(adwin):
    def __init__(self, name, **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments['physical_adwin_cav1'], 
                processes = adwinscfg.config['adwin_cav1_processes'],
                default_processes=['counter', 'set_dac', 'set_dio', 'laserscan_photodiode'], 
                dacs=adwinscfg.config['adwin_cav1_dacs'], 
                adcs=adwinscfg.config['adwin_cav1_adcs'],                 
                tags=['virtual'],
                use_cfg  = True,
                process_subfolder = qt.config['adwin_pro_subfolder'], **kw)
                
        self.add_function('measure_counts')
        self.add_function('laserscan_photodiode')


    def laserscan_photodiode(self, ADC_channel=1, nr_steps = 100, wait_cycles = 50, 
            start_voltage = 0, voltage_step=0.01):

        DAC_ch = self.dacs['laser_scan']
        ADC_ch = self.adcs['photodiode']

        self.start_laserscan_photodiode (DAC_channel=DAC_ch, ADC_channel=ADC_ch, nr_steps=nr_steps,
                wait_cycles=wait_cycles, start_voltage=start_voltage, voltage_step=voltage_step)

        data_idx = self.processes['laserscan_photodiode']['data_long']['photodiode_voltage']
        return self.physical_adwin.Get_Data_Long(data_idx, 1, nr_steps)


    def measure_counts(self, int_time):
        self.start_counter(set_integration_time=int_time, set_avg_periods=1, set_single_run= 1)
        while self.is_counter_running():
            time.sleep(0.01)
        return self.get_last_counts()
