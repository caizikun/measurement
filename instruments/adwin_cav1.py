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


    def set_laser_coarse (self, voltage):
        DAC_ch = self.dacs['laser_scan']
        self.start_set_dac (dac_no=DAC_ch, dac_voltage=voltage)

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

    def fine_piezo_jpe_scan_sync (self, nr_steps = 100, nr_scans=100, wait_cycles = 1, 
            start_voltages = [0,0,0], voltage_step=0.01, delay_ms = 0):

        DAC_ch_1 = self.dacs['jpe_fine_tuning_1']
        DAC_ch_2 = self.dacs['jpe_fine_tuning_2']
        DAC_ch_3 = self.dacs['jpe_fine_tuning_3']
        ADC_ch = self.adcs['photodiode']
        ADC_ref_ch = self.adcs['photodiode_ref']
        montana_sync_ch = adwinscfg.config['adwin_cav1_dios']['montana_sync_ch']
        print "Montana sync channel: ", montana_sync_ch

        if ((start_voltages[0]>-2) and (start_voltages[0]>-2) and (start_voltages[0]>-2)):
            end1 = start_voltages[0]+nr_steps*voltage_step
            end2 = start_voltages[1]+nr_steps*voltage_step
            end3 = start_voltages[2]+nr_steps*voltage_step

            delay_cycles = int(delay_ms/3.3e-6)
            print "delay cycles = ", delay_cycles
            if ((end1<10) and (end2<10) and (end3<10)):
                self.start_fine_piezo_jpe_scan_sync (DAC_ch_fpz1=DAC_ch_1, DAC_ch_fpz2=DAC_ch_2, DAC_ch_fpz3=DAC_ch_3, ADC_channel=ADC_ch, 
                        nr_steps=nr_steps, nr_scans=nr_scans, wait_cycles=wait_cycles, voltage_step=voltage_step,
                        start_voltage_1 = start_voltages[0], start_voltage_2 = start_voltages[1], start_voltage_3 = start_voltages[2],
                        montana_sync_channel=montana_sync_ch, delay_us=delay_cycles)

                data_idx = self.processes['fine_piezo_jpe_scan_sync']['data_float']['photodiode_voltage']
                timestamps_idx = self.processes['fine_piezo_jpe_scan_sync']['data_long']['timestamps']
                
                while (self.is_fine_piezo_jpe_scan_running()):
                    qt.msleep (0.1)
                #qt.msleep (nr_steps*wait_cycles*1e-5) #TO BE IMPROVED!!!!!
                #print 'Data is stored in array: ', data_idx
                #print self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps)
                tstamps = self.physical_adwin.Get_Data_Long(timestamps_idx, 1, nr_scans)
                tstamps_ms = tstamps [1:]*3.3*1e-6
                success = tstamps[0]
                raw_data = self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps*nr_scans)

                data = np.reshape (raw_data, (nr_scans, nr_steps))
                return success, data, tstamps_ms
            else:
                print 'Voltage > 10V!!'
                print 'V = ', end1, end2, end3
                print 'values:', start_voltages, voltage_step, nr_steps
        else:
            print 'Voltage <-2!!'



    def fine_piezo_jpe_scan_CCD (self, nr_steps = 100, wait_cycles = 50, 
            start_voltages = [0,0,0], voltage_step=0.01):

        DAC_ch_1 = self.dacs['jpe_fine_tuning_1']
        DAC_ch_2 = self.dacs['jpe_fine_tuning_2']
        DAC_ch_3 = self.dacs['jpe_fine_tuning_3']

        if ((start_voltages[0]>-2) and (start_voltages[0]>-2) and (start_voltages[0]>-2)):
            end1 = start_voltages[0]+nr_steps*voltage_step
            end2 = start_voltages[1]+nr_steps*voltage_step
            end3 = start_voltages[2]+nr_steps*voltage_step

            if ((end1<10) and (end2<10) and (end3<10)):
                self.start_fine_piezo_jpe_scan_CCD (DAC_ch_fpz1=DAC_ch_1, DAC_ch_fpz2=DAC_ch_2, DAC_ch_fpz3=DAC_ch_3, 
                        nr_steps=nr_steps, wait_cycles=wait_cycles, voltage_step=voltage_step,
                        start_voltage_1 = start_voltages[0], start_voltage_2 = start_voltages[1], start_voltage_3 = start_voltages[2])

                data_idx = self.processes['fine_piezo_jpe_scan_CCD']['data_float']['integrated_CCD_signal']
                
                while (self.is_fine_piezo_jpe_scan_running()):
                    qt.msleep (0.1)
                #qt.msleep (nr_steps*wait_cycles*1e-5) #TO BE IMPROVED!!!!!
                print 'Data is stored in array: ', data_idx
                print self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps)
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
        elif (type(voltage)==float):
            type_v = 'float'
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
                #print 'Setting values one by one'
                self.start_set_dac(dac_no=DAC_ch_1, dac_voltage=voltage[0])
                self.start_set_dac(dac_no=DAC_ch_2, dac_voltage=voltage[1])
                self.start_set_dac(dac_no=DAC_ch_3, dac_voltage=voltage[2])

        elif type_v == 'float':            
            if ((voltage<-2) or (voltage>10)):
                print 'Voltage out of range'
            else:
                #print 'Setting all identical values'
                self.start_set_dac(dac_no=DAC_ch_1, dac_voltage=voltage)
                self.start_set_dac(dac_no=DAC_ch_2, dac_voltage=voltage)
                self.start_set_dac(dac_no=DAC_ch_3, dac_voltage=voltage)
        else:
            print 'Voltage type incorrect!'

    def set_dacs_to_zero(self):
        for i in  np.arange (20):
            self.start_set_dac(dac_no=i, dac_voltage=0)

    def timeseries_photodiode (self, nr_steps, wait_cycles=1):
        self.start_timeseries_photodiode (nr_steps = nr_steps, wait_cycles = wait_cycles)

        pd_volt_idx = self.processes['timeseries_photodiode']['data_float']['photodiode_voltage']
        timer_idx = self.processes['timeseries_photodiode']['data_long']['timer']
        return self.physical_adwin.Get_Data_Float(pd_volt_idx, 1, nr_steps), 3.3333333e-9*self.physical_adwin.Get_Data_Long(timer_idx, 1, nr_steps)

    def widerange_laserscan (self, start_coarse_volt, step_size_coarse, nr_coarse_steps, nr_fine_steps = 100, wait_cycles = 1):

        DAC_coarse_ch = self.dacs['laser_coarse_wav_imput']
        DAC_fine_ch = self.dacs['newfocus_freqmod']
        ADC_ch = self.adcs['photodiode']

        self.start_widerange_laserscan (DAC_coarse_ch=DAC_coarse_ch, DAC_fine_ch=DAC_fine_ch, ADC_ch=ADC_ch, 
                        nr_fine_steps=nr_fine_steps, nr_coarse_steps = nr_coarse_steps, wait_cycles=wait_cycles, 
                        start_coarse_volt = start_coarse_volt, step_size_coarse = step_size_coarse, start_fine_volt = -3, stop_fine_volt = 3)

        while (self.is_widerange_laserscan_running()):
                    qt.msleep (3)

        data_idx = self.processes['widerange_laserscan']['data_float']['photodiode_voltage']
        wm_idx = self.processes['widerange_laserscan']['data_float']['wavemeter']

        data = self.physical_adwin.Get_Data_Float(data_idx, 1, nr_fine_steps*nr_coarse_steps)
        wavemeter_readout = self.physical_adwin.Get_Data_Float(wm_idx, 1, nr_fine_steps*nr_coarse_steps)

        return data, wavemeter_readout



        
