"""
Photodiode based measurement class 
SvD 12-2016
"""

import numpy as np
import logging

import qt

import measurement.lib.measurement2.measurement as m2
reload(m2)

class AdwinPhotodiode(m2.AdwinControlledMeasurement):
    mprefix = 'AdwinPhotodiode'
    adwin_process = 'voltage_scan_sync'

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




            
        print self.adwin_process
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
        # qt.msleep(1)
        return not(aborted)

    def save(self, name = 'pd'):
        self.save_adwin_data(name,
            [('timestamps', self.params['nr_scans']+1)
            ('photodiode_voltage', self.params['nr_steps']*self.params['nr_scans']),
            ('laser_frequency', self.params['nr_steps']*self.params['nr_scans']),
            ('photodiode_voltage_ms', self.params['nr_steps']*self.params['nr_scans']*self.params['nr_ms_per_point'])
            ])

