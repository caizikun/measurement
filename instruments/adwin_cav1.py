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
                default_processes=['counter', 'set_dac', 'set_dio', 'read_adc', 'voltage_scan_sync'], 
                dacs=adwinscfg.config['adwin_cav1_dacs'], 
                adcs=adwinscfg.config['adwin_cav1_adcs'],            
                tags=['virtual'],
                use_cfg  = True,
                process_subfolder = qt.config['adwin_pro_subfolder'], **kw)
                
        self.add_function('measure_counts')
        self.add_function('scan_photodiode')


    def scan_photodiode(self, scan_type, nr_steps = 100, nr_scans = 5, wait_cycles = 50, 
            start_voltage = -3, end_voltage = 3, use_sync = 0, delay_ms = 0):

        voltage_step = (end_voltage - start_voltage)/float(nr_steps)
        montana_sync_ch = adwinscfg.config['adwin_cav1_dios']['montana_sync_ch']
        ADC_ch = self.adcs['photodiode']
        delay_cycles = int(delay_ms/3.3e-6)

        do_scan = True

        if (scan_type == 'fine_piezos'):
            DAC_ch_1 = self.dacs['jpe_fine_tuning_1']
            DAC_ch_2 = self.dacs['jpe_fine_tuning_2']
            DAC_ch_3 = self.dacs['jpe_fine_tuning_3']
            if ((start_voltage <-2) or (end_voltage >10)):
                do_scan = False
                print 'Piezo voltage exceeds specifications! Scan aborted.'
        elif (scan_type == 'laser'):
            DAC_ch_1 = self.dacs['newfocus_freqmod']
            DAC_ch_2 = 0
            DAC_ch_3 = 0
            if ((start_voltage < -4) or (end_voltage > 4)):
                do_scan = False
                print 'Voltage exceeds specifications! Scan aborted.'
        else: 
            print "Scan type unknown! Scan aborted."
            do_scan = False

        if do_scan:
            print 'Running scan... Params:'
            scan_params = {}
            scan_params['DAC_ch_1'] = DAC_ch_1
            scan_params['DAC_ch_2'] = DAC_ch_2
            scan_params['DAC_ch_3'] = DAC_ch_3            
            scan_params['ADC channels'] = ADC_ch
            scan_params['use_montana_sync'] = use_sync
            scan_params['sync_ch'] = montana_sync_ch
            scan_params['sync_delay_ms'] = delay_ms            
            scan_params['start_voltage'] = start_voltage
            scan_params['end_voltage'] = end_voltage
            scan_params['step_voltage'] = voltage_step
            scan_params['nr_scans'] = nr_scans
            scan_params['nr_steps'] = nr_steps

            self.start_voltage_scan_sync (DAC_ch_1=DAC_ch_1, DAC_ch_2=DAC_ch_2, DAC_ch_3=DAC_ch_3, ADC_channel=ADC_ch, 
                    nr_steps=nr_steps, nr_scans=nr_scans, wait_cycles=wait_cycles, voltage_step=voltage_step,
                    start_voltage_1 = start_voltage, start_voltage_2 = start_voltage, start_voltage_3 = start_voltage,
                    use_sync=use_sync, sync_ch=montana_sync_ch, delay_us=delay_cycles)

            data_idx = self.processes['voltage_scan_sync']['data_float']['photodiode_voltage']
            timestamps_idx = self.processes['voltage_scan_sync']['data_long']['timestamps']
            
            while (self.is_voltage_scan_sync_running()):
                qt.msleep (0.1)

            tstamps = self.physical_adwin.Get_Data_Long(timestamps_idx, 1, nr_scans)
            tstamps_ms = tstamps [1:]*3.3*1e-6
            success = tstamps[0]
            raw_data = self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps*nr_scans)

            data = np.reshape (raw_data, (nr_scans, nr_steps))
            if success:
                scan_params['scan_successfull'] = True
            else:
                scan_params['scan_successfull'] = False

            print scan_params
            return success, data, tstamps_ms, scan_params


    def set_laser_coarse (self, voltage):
        DAC_ch = self.dacs['laser_scan']
        self.start_set_dac (dac_no=DAC_ch, dac_voltage=voltage)

    def measure_counts(self, int_time):
        self.start_counter(set_integration_time=int_time, set_avg_periods=1, set_single_run= 1)
        while self.is_counter_running():
            time.sleep(0.01)
        return self.get_last_counts()

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

    def read_photodiode (self, adc_no = 16):
        self.start_read_adc (adc_no = adc_no)
        a = self.physical_adwin.Get_FPar (21)
        return a 



        
