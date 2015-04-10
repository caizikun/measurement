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
                default_processes=['counter', 'set_dac', 'set_dio', 'laserscan_photodiode', 'fine_piezo_jpe_scan', 'read_adc'], 
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

    def fine_piezo_jpe_scan(self, nr_steps = 100, wait_cycles = 50, 
            start_voltages = [0,0,0], voltage_step=0.01):

        DAC_ch_1 = self.dacs['jpe_fine_tuning_1']
        DAC_ch_2 = self.dacs['jpe_fine_tuning_2']
        DAC_ch_3 = self.dacs['jpe_fine_tuning_3']
        ADC_ch = self.adcs['photodiode']
        ADC_ref_ch = self.adcs['photodiode_ref']

        if ((start_voltages[0]>-2) and (start_voltages[0]>-2) and (start_voltages[0]>-2)):
            end1 = start_voltages[0]+nr_steps*voltage_step
            end2 = start_voltages[1]+nr_steps*voltage_step
            end3 = start_voltages[2]+nr_steps*voltage_step

            if ((end1<10) and (end2<10) and (end3<10)):
                self.start_fine_piezo_jpe_scan (DAC_ch_fpz1=DAC_ch_1, DAC_ch_fpz2=DAC_ch_2, DAC_ch_fpz3=DAC_ch_3, ADC_channel=ADC_ch, 
                        ADC_ref_channel = ADC_ref_ch, nr_steps=nr_steps, wait_cycles=wait_cycles, voltage_step=voltage_step,
                        start_voltage_1 = start_voltages[0], start_voltage_2 = start_voltages[1], start_voltage_3 = start_voltages[2])

                data_idx = self.processes['fine_piezo_jpe_scan']['data_float']['photodiode_voltage']
                
                while (self.is_fine_piezo_jpe_scan_running()):
                    qt.msleep (0.1)
                #qt.msleep (nr_steps*wait_cycles*1e-5) #TO BE IMPROVED!!!!!
                #print 'Data is stored in array: ', data_idx
                #print self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps)
                return self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps)
            else:
                print 'Voltage > 10V!!'
                print 'V = ', end1, end2, end3
                print 'values:', start_voltages, voltage_step, nr_steps
        else:
            print 'Voltage <-2!!'

    def measure_counts(self, int_time):
        self.start_counter(set_integration_time=int_time, set_avg_periods=1, set_single_run= 1)
        while self.is_counter_running():
            time.sleep(0.01)
        return self.get_last_counts()

    #def set_dac(self, ch, v):
    #    pass

    def set_fine_piezos (self, voltage):
        DAC_ch_1 = self.dacs['jpe_fine_tuning_1']
        DAC_ch_2 = self.dacs['jpe_fine_tuning_2']
        DAC_ch_3 = self.dacs['jpe_fine_tuning_3']

        if ((type(voltage)==np.ndarray) and (len(voltage)>2)):
            type_v = 'array'
        elif (type(voltage)==int):
            type_v = 'int'
        else:
            type_v = 'none'

        if type_v == 'array':            
            
            if ((voltage[0]<-2) or (voltage[0]>10)):
                print 'Voltage out of range  - v1'
            elif ((voltage[1]<-2) or (voltage[1]>10)):
                print 'Voltage out of range  - v2'
            elif ((voltage[2]<-2) or (voltage[2]>10)):
                print 'Voltage out of range  - v3'
            else:
                print 'Setting values one by one'
                self.start_set_dac(dac_no=DAC_ch_1, dac_voltage=voltage[0])
                self.start_set_dac(dac_no=DAC_ch_2, dac_voltage=voltage[1])
                self.start_set_dac(dac_no=DAC_ch_3, dac_voltage=voltage[2])

        elif type_v == 'int':            
            if ((voltage<-2) or (voltage>10)):
                print 'Voltage out of range'
            else:
                print 'Setting all identical values'
                self.start_set_dac(dac_no=DAC_ch_1, dac_voltage=voltage)
                self.start_set_dac(dac_no=DAC_ch_2, dac_voltage=voltage)
                self.start_set_dac(dac_no=DAC_ch_3, dac_voltage=voltage)
        else:
            print 'Voltage type incorrect!'

    def set_dacs_to_zero(self):
        for i in  np.arange (20):
            self.start_set_dac(dac_no=i, dac_voltage=0)



