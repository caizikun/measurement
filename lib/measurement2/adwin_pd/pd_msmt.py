"""
Photodiode based measurement class 
SvD 12-2016
"""
import numpy as np
import logging

import qt

import measurement.lib.measurement2.measurement as m2

class AdwinPhotodiode(m2.AdwinControlledMeasurement):

    mprefix = 'AdwinPhotodiode'
    adwin_process = 'voltage_scan_sync'
    adwin=None

    def set_adwin_process_variable_from_params(self,key):
        try:
            # Here we can do some checks on the settings in the adwin
            if np.isnan(self.params[key]):
                raise Exception('Adwin process variable {} contains NAN'.format(key))
            self.adwin_process_params[key] = self.params[key]
        except:
            logging.error("Cannot set adwin process variable '%s'" \
                    % key)
            raise Exception('Adwin process variable {} has not been set in the measurement params dictionary!'.format(key))

    def setup(self):
        pass

    def run(self, autoconfig=True, setup=True):
        
        if autoconfig:
            self.autoconfig()         
        if setup:
            self.setup()

        ###scan to start###########
        if self.params['scan_to_start']:
            print 'scan to start'
            speed = self.params['scan_to_start_speed']#mV/s; scan slowly
            _steps,_pxtime = self.adwin.speed2px(self.params['dac_names'], self.params['start_voltages'], speed=speed)
            self.adwin.linescan(self.params['dac_names'], self.adwin.get_dac_voltages(self.params['dac_names']),
                    self.params['start_voltages'], _steps, _pxtime, value='none', 
                    scan_to_start=False, blocking = True)

        ###actual scanning process###########
        self.start_adwin_process()
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        aborted=False
        CR_counts = 0
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                aborted = True
                self.stop_keystroke_monitor('abort')
                break
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_adwin_process()

        ###make adwin instrument aware of changed voltage###########
        curr_voltage = self.adwin_var('curr_voltage')
        self.params['curr_voltage'] = curr_voltage
        for i,n in enumerate(self.params['dac_names']):#should think of a way to fix it if stopped halfway through process
            self.adwin.set_dac_voltage((n,curr_voltage))

        # qt.msleep(1)
        return not(aborted)

    def save(self, name = 'pd'):
        self.save_adwin_data(name,
            [   ('timestamps', self.params['nr_scans']+1),
                ('photodiode_voltage', self.params['nr_steps']*self.params['nr_scans']),
                ('laser_frequency', self.params['nr_steps']*self.params['nr_scans']),
                ('photodiode_voltage_ms', self.params['nr_steps']*self.params['nr_scans']*self.params['nr_ms_per_point'])
            ])

