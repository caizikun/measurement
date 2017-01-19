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
    def __init__(self, name, physical_adwin ='physical_adwin', **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments[physical_adwin], 
                processes = adwinscfg.config['adwin_cav1_processes'],
                default_processes=['counter', 'set_dac', 'set_dio', 'linescan','read_adc', 'voltage_scan_sync'], 
                dacs=adwinscfg.config['adwin_cav1_dacs'], 
                adcs=adwinscfg.config['adwin_cav1_adcs'],            
                tags=['virtual'],
                use_cfg  = kw.pop('use_cfg',True),
                process_subfolder = qt.config['adwin_pro_subfolder'], **kw)
                

   
    def get_xyz_U(self):
        return self.get_dac_voltages(['scan_mirror_x','scan_mirror_y'])

    def move_to_xyz_U(self, target_voltages, speed=5000, blocking=False):
        current_voltages = self.get_xyz_U()
        dac_names = ['scan_mirror_x','scan_mirror_y']
        steps, pxtime = self.speed2px(dac_names, target_voltages, speed)
        self.linescan(dac_names, current_voltages, target_voltages,
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)
        
        return

    # def photodiodeRO_voltagescan(self,dac_names,DAC_channels,ADC_ch,sync_ch,
    #         nr_steps,nr_scans,voltage_step,
    #         start_voltages,stop_voltages,final_voltages, 
    #         wait_cycles = 1, ADC_averaging_cycles = 5,
    #         use_sync = False, delay_us = 1,
    #         scan_to_start = True, scan_auto_reverse = False):
    #     """
    #     TODO: turn this into a measurement class, based on m2 measurement. 
    #     linescan where the photodiode is readout very step. 
    #     There is the option to sync with the Montana pulse tube
    #     arguments:
    #     dac_names - names of the dacs incolved
    #     DAC_channels  - [DAC_ch_1,DAC_ch_2,DAC_ch_3]. If 0 , no channel is used 
    #             # TODO : could make this more like in the linescan, looping over dacs in adwin.
    #     ADC_ch    -  the ADC channel to use 
    #     sync_ch    - the channel the Montana sync is connected to
    #     nr_steps   - number of voltage steps
    #     nr_scans  - number of consecutive linescans in a single adwin cycle. 
    #         Be careful using this: there is no scan_to_start in between these scans; consider useing scan_auto_reverse
    #     voltage_step  - the size of the step
    #     start_voltages - the start voltages per channel ; same start_voltage for each channel is required
    #     stop_voltages   - the stop voltages per channel used
    #     final_voltages  - the voltage to be set after the voltagescan is finished 
    #     kw arguments:
    #     wait_cycles  - the number of cycles (in us) without action after each step (default:1)
    #     ADC_averaging_cycles - the number of cycles (in us) that are averaged over (default:5)
    #     use_sync   - whether to use the Montana sync (default:False)
    #     delay_us   - the number of delay cycles after the Montana sync signal, before starting a scan (in us) (default: 1)
    #     scan_to_start - if True, scans to start (default: True)
    #     scan_auto_reverse - whether to scan in a 'zig-zag' for consecutive scans (if True), or in a sawtooth (if False) (default:False)
    #     """
    #     DAC_ch_1=DAC_channels[0]
    #     DAC_ch_2=DAC_channels[1]        
    #     DAC_ch_3=DAC_channels[2]
    #     start_voltage=start_voltages[0]

    #     print wait_cycles

    #     if scan_to_start:
    #         _steps,_pxtime = self.speed2px(dac_names, start_voltages)
    #         self.linescan(dac_names, self.get_dac_voltages(dac_names),
    #                 start_voltages, _steps, _pxtime, value='none', 
    #                 scan_to_start=False, blocking = True)
    #         print 'started scan to start'
    #     qt.msleep(0.4)

    #     self.start_voltage_scan_sync(DAC_ch_1=DAC_ch_1, DAC_ch_2=DAC_ch_2, DAC_ch_3=DAC_ch_3, ADC_channel=ADC_ch, 
    #             nr_steps=nr_steps, nr_scans=nr_scans, wait_cycles=wait_cycles, voltage_step=voltage_step,
    #             start_voltage_1 = start_voltage, start_voltage_2 = start_voltage, start_voltage_3 = start_voltage,
    #             use_sync=use_sync, sync_ch=sync_ch, delay_us=delay_us, ADC_averaging_cycles = ADC_averaging_cycles,
    #             scan_auto_reverse=scan_auto_reverse)

    #     while (self.is_voltage_scan_sync_running()):
    #         qt.msleep (0.1)
        
    #     for i,n in enumerate(dac_names):
    #         self._dac_voltages[n] = stop_voltages[i]


    #     tstamps = self.get_voltage_scan_sync_var('timestamps',length=nr_scans) #self.physical_adwin.Get_Data_Long(timestamps_idx, 1, nr_scans) 
    #     raw_data = self.get_voltage_scan_sync_var('photodiode_voltage',length=nr_steps*nr_scans)# self.physical_adwin.Get_Data_Float(data_idx, 1, nr_steps*nr_scans)
    #     freq_data = self.get_voltage_scan_sync_var('laser_frequency',length=nr_steps*nr_scans)# self.physical_adwin.Get_Data_Float(freqs_idx, 1, nr_steps*nr_scans)


    #     # after a piezo scan return the piezo voltage to the initial voltage.\
    #     _steps,_pxtime = self.speed2px(dac_names, final_voltages)
    #     self.linescan(dac_names, self.get_dac_voltages(dac_names),
    #             final_voltages, _steps, _pxtime, value='none', 
    #             scan_to_start=False, blocking = True)
        
    #     return tstamps,raw_data,freq_data