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
    def __init__(self, name, physical_adwin ='physical_adwin_cav1', **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments[physical_adwin], 
                processes = adwinscfg.config['adwin_cav1_processes'],
                default_processes=['counter', 'set_dac', 'set_dio', 'linescan','read_adc', 'voltage_scan_sync'], 
                dacs=adwinscfg.config['adwin_cav1_dacs'], 
                adcs=adwinscfg.config['adwin_cav1_adcs'],            
                tags=['virtual'],
                use_cfg  = True,
                process_subfolder = qt.config['adwin_pro_subfolder'], **kw)
                
        self.add_function('measure_counts')
        self.add_function('scan_photodiode')

        # linescanning
        self.add_function('linescan')
        self.add_function('get_linescan_counts')
        self.add_function('get_linescan_px_clock')
        self.add_function('get_linescan_supplemental_data')

         # advanced dac functions
        self.add_function('move_to_xyz_U')
        self.add_function('get_xyz_U')
        self.add_function('move_to_dac_voltage')

    # linescan
    def linescan(self, dac_names, start_voltages, stop_voltages, steps, 
            px_time, value='counts', scan_to_start=False, blocking=False, 
            abort_if_running=True):
        """
        Starts the multidimensional linescan on the adwin. 
        
        Arguments:
                
        dac_names : [ string ]
            array of the dac names
        start_voltages, stop_voltages: [ float ]
            arrays for the corresponding start/stop voltages
        steps : int
            no of steps between these two points, incl start and stop
        px_time : int
            time in ms how long to measure per step
        value = 'counts' : string id
            one of the following, to indicate what to measure:
            'counts' : let the adwin measure the counts per pixel
            'none' : adwin only steps
            'counts+suppl' : counts per pixel, plus adwin will record
                the value of FPar #2 as supplemental data
            'counter_process' : counts from the running counter process
            in any case, the pixel clock will be incremented for each step.
        scan_to_start = False : bool
            if True, scan involved dacs to start first 
            right now, with default settings of speed2px()

        blocking = False : bool
            if True, do not return until finished

        abort_if_running = True : bool
            if True, check if linescan is running, and if so, quit right away
        
        """
        if abort_if_running and self.is_linescan_running():
            return

        if scan_to_start:
            _steps,_pxtime = self.speed2px(dac_names, start_voltages)
            self.linescan(dac_names, self.get_dac_voltages(dac_names),
                    start_voltages, _steps, _pxtime, value='none', 
                    scan_to_start=False)
            while self.is_linescan_running():
                time.sleep(0.005)
            for i,n in enumerate(dac_names):
                self._dac_voltages[n] = start_voltages[i]
                self.save_cfg()
            
            # stabilize a bit, better for attocubes
            time.sleep(0.05)

        p = self.processes['linescan']
        dacs = [ self.dacs[n] for n in dac_names ]

        # set all the required input params for the adwin process
        # see the adwin process for details
        self.physical_adwin.Set_Par(p['par']['set_cnt_dacs'], len(dac_names))
        self.physical_adwin.Set_Par(p['par']['set_steps'], steps)
        self.physical_adwin.Set_FPar(p['fpar']['set_px_time'], px_time)
        
        self.physical_adwin.Set_Data_Long(np.array(dacs), p['data_long']\
                ['set_dac_numbers'],1,len(dac_names))
        self.physical_adwin.Set_Data_Float(start_voltages, 
                p['data_float']['set_start_voltages'], 1, len(dac_names))
        self.physical_adwin.Set_Data_Float(stop_voltages, 
                p['data_float']['set_stop_voltages'], 1, len(dac_names))
        
        # what the adwin does on each px is int-encoded
        px_actions = {
                'none' : 0,
                'counts' : 1,
                'counts+suppl' : 2,
                'counter_process' : 3,
                }
        self.physical_adwin.Set_Par(p['par']['set_px_action'],px_actions[value])
        self.physical_adwin.Start_Process(p['index'])
        
        if blocking:
            while self.is_linescan_running():
                time.sleep(0.005)
        
        # FIXME here we might lose the information about the current voltage,
        # if the scan is not finished properly
        for i,n in enumerate(dac_names):
            self._dac_voltages[n] = stop_voltages[i]
        self.save_cfg()

    def speed2px(self, dac_names, target_voltages, speed=5000, pxtime=5,
            minsteps=10):
        """
        Parameters:
        - dac_names : [ string ]
        - end_voltages : [ float ], one voltage per dac
        - speed : float, (mV/s)
        - pxtime : int, (ms)
        - minsteps : int, never return less than this number for steps
        """
        current_voltages = self.get_dac_voltages(dac_names)
        maxdiff = max([ abs(t-current_voltages[i]) for i,t in \
                enumerate(target_voltages) ])
        steps = int(1e6*maxdiff/(pxtime*speed)) # includes all unit conversions

        return max(steps, minsteps), pxtime

    def stop_linescan(self):
        p = self.processes['linescan']
        self.physical_adwin.Stop_Process(p['index'])

    def is_linescan_running(self):
        return bool(self.get_process_status('linescan'))

    def get_linescan_counts(self, steps):
        p = self.processes['linescan']
        c = []
        
        for i in p['data_long']['get_counts']:

            #disregard the first value (see adwin program)
            c.append(self.physical_adwin.Get_Data_Long(i, 1, steps+1)[1:])
        return c

    def get_linescan_supplemental_data(self, steps):
        p = self.processes['linescan']
        return self.physical_adwin.Get_Data_Float(
                p['data_float']['get_supplemental_data'], 1, steps+1)[1:]
        
    def get_linescan_px_clock(self):
        p = self.processes['linescan']
        return self.physical_adwin.Get_Par(p['par']['get_px_clock'])

    # end linescan            
   
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

    def move_to_dac_voltage(self, dac_name, target_voltage, speed=5000, 
            blocking=False):

        current_voltage = self.get_dac_voltage(dac_name)
        steps, pxtime = self.speed2px([dac_name], [target_voltage], speed)
        self.linescan([dac_name], [current_voltage], [target_voltage],
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)



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
            dac_names = np.array(['jpe_fine_tuning_1', 'jpe_fine_tuning_2', 'jpe_fine_tuning_3'])
            start_voltages = np.array([start_voltage,start_voltage,start_voltage])
            if ((start_voltage <-2) or (end_voltage >10)):
                do_scan = False
                print 'Piezo voltage exceeds specifications! Scan aborted.'
        elif (scan_type == 'laser'):
            DAC_ch_1 = self.dacs['newfocus_freqmod']
            DAC_ch_2 = 0
            DAC_ch_3 = 0
            dac_names=np.array(['newfocus_freqmod'])
            start_voltages=np.array([start_voltage])
            if ((start_voltage < -4) or (end_voltage > 4)):
                do_scan = False
                print 'Voltage exceeds specifications! Scan aborted.'
        else: 
            print "Scan type unknown! Scan aborted."
            do_scan = False

        if do_scan:
            print 'Running scan... '
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

            _steps,_pxtime = self.speed2px(dac_names, start_voltages)
            self.linescan(dac_names, self.get_dac_voltages(dac_names),
                    start_voltages, _steps, _pxtime, value='none', 
                    scan_to_start=False)

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

