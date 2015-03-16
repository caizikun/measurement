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
                default_processes=['counter', 'set_dac', 'set_dio', 'laserscan_photodiode', 'fine_piezo_jpe_scan'], 
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

        data_idx = self.processes['laserscan_photodiode']['data_float']['photodiode_voltage']
        return self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps)

    def fine_piezo_jpe_scan(self, ADC_channel=1, nr_steps = 100, wait_cycles = 50, 
            start_voltages = [0,0,0], voltage_step=0.01):

        DAC_ch_1 = self.dacs['jpe_fine_tuning_1']
        DAC_ch_2 = self.dacs['jpe_fine_tuning_2']
        DAC_ch_3 = self.dacs['jpe_fine_tuning_3']
        ADC_ch = self.adcs['photodiode']

        self.start_fine_piezo_jpe_scan (DAC_ch_fpz1=DAC_ch_1, DAC_ch_fpz2=DAC_ch_2, DAC_ch_fpz3=DAC_ch_3, ADC_channel=ADC_ch, 
                nr_steps=nr_steps, wait_cycles=wait_cycles, voltage_step=voltage_step,
                start_voltage_1 = start_voltages[0], start_voltage_2 = start_voltages[1], start_voltage_3 = start_voltages[2])

        data_idx = self.processes['fine_piezo_jpe_scan']['data_float']['photodiode_voltage']
        return self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps)

    def measure_counts(self, int_time):
        self.start_counter(set_integration_time=int_time, set_avg_periods=1, set_single_run= 1)
        while self.is_counter_running():
            time.sleep(0.01)
        return self.get_last_counts()
