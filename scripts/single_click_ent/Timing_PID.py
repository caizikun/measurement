import numpy as np
import logging
from instrument import Instrument
import qt

import measurement.lib.measurement2.measurement as m2



class PIDtiming(m2.AdwinControlledMeasurement):

    mprefix = 'PIDtiming'
    adwin_process = 'Phase_stable_pid'



    def __init__(self, name):
        m2.AdwinControlledMeasurement.__init__(self, name)
        self.params = m2.MeasurementParameters('LocalParameters')
        self.PhaseAOM = qt.get_instruments()['PhaseAOM']
        self.adwin = qt.get_instruments()['adwin']

    def setup(self):
        self.PhaseAOM.apply_voltage(self.params['PhaseAOMvoltage'])

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

    def run(self, autoconfig=True, setup=True):   
        if autoconfig:
            self.autoconfig() 

        if setup:
            self.setup()
        print 'Phase_stable_pid'
        print self.adwin_process
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        aborted=False
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                aborted = True
                self.stop_keystroke_monitor('abort')
                break
            
             
            reps_completed = self.adwin_var('completed_reps')

            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['max_repetitions']))
            # print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_adwin_process()

    def save(self, name='pidfs'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('PID_counts', reps * self.params['PID_cycles']),
                    ('sample_counts', reps * self.params['sample_cycles']),
                    'completed_reps',
                    'setpoint'])

    def finish(self, **kw):
        self.PhaseAOM.apply_voltage(0.0)
