"""
Script for e-spin T1 using the pulsar sequencer.
"""
import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from analysis.lib.m2.ssro import ssro as ssroanal

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

class ElectronT1_without_AWG(ssro.IntegratedSSRO):

    mprefix = 'ElectronT1'
    adwin_process = 'T1_without_AWG_SHUTTER'

def T1(name, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', 
        pump_to_1 = False, wait_times = np.linspace(1e3,200e3,15),
        debug = False):

    m = pulsar_msmt.ElectronT1(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    '''set experimental paramqeters'''
        #T1 experiment

    # Measurement settings
    m.params['pts'] = len(wait_times)

    m.params['T1_initial_state'] = T1_initial_state #currently 'ms=0' or 'ms=-1'
    m.params['T1_readout_state'] = T1_readout_state #currently 'ms=0' or 'ms=-1'
    m.params['wait_times'] =  wait_times
    m.params['wait_time_repeat_element'] = 10 #in us, this element is repeated to create the wait times max of 6 seconds
    m.params['repetitions'] = 150
    m.params['use_shutter'] = 0

        #Plot parameters
    m.params['sweep_name'] = 'Times (us)'
    m.params['sweep_pts'] = m.params['wait_times']

        #Set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0

        #Optional: To prepare in ms=-1/+1 by laser pumping
    if pump_to_1:
        m.params['A_SP_amplitude']  = 0
        m.params['Ex_SP_amplitude'] = 15e-9

    m.autoconfig()

    print 'initial_state: ' + m.params['T1_initial_state']
    print 'readout_state: ' + m.params['T1_readout_state']
    print m.params['sweep_pts']
    '''generate sequence'''
    m.generate_sequence(upload=True, debug=debug)
    m.run()
    m.save()
    m.finish()


if __name__ == '__main__':

    times = np.linspace(1e2,50e3,7)

    
    T1(SAMPLE+'_'+'init_0_RO_0', T1_initial_state = 'ms=0',wait_times = times, 
                    T1_readout_state = 'ms=0', debug=False)
    T1(SAMPLE+'_'+'init_1_RO_1', T1_initial_state = 'ms=-1',wait_times = times, 
                    T1_readout_state = 'ms=-1', debug=False)
    
