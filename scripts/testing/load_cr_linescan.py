"""
LT1/2 script for adwin ssro.
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']

class CR_linescan(ssro.AdwinSSRO):

    adwin_process = 'cr_linescan'

    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()
        self.adwin.set_cr_linescan_var(set_steps=0)
        self.start_adwin_process(stop_processes=['counter'])

def load_cr_linsescan(name):
    m = CR_linescan(name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.run()

def unload_cr_linescan():
    qt.instruments['adwin'].load_linescan()


if __name__ == '__main__':
    stools.turn_off_all_lasers()
    load_cr_linsescan(SAMPLE_CFG)
    #unload_cr_linescan()