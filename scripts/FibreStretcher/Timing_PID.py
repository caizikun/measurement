import numpy as np
import logging

import qt

import measurement.lib.measurement2.measurement as m2
reload(m2)

class PIDtiming(m2.AdwinControlledMeasurement):

    mprefix = 'PIDtiming'
    max_repetitions = 20000
    adwin_process = 'singleshot'

        
    def autoconfig(self):


    def setup(self):
    
    
    def set_adwin_process_variable_from_params(self,key):


    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()         
        if setup:
            self.setup()
        print 'PIDtiming'
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
            
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_adwin_process()


    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   (])

    def finish(self, **kw):

