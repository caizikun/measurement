"""
Script for e-spin T1 using the pulsar sequencer.
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def T1(name, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0'):

    m = pulsar_msmt.ElectronT1(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    '''set experimental parameters'''
        #T1 experiment
    m.params['T1_initial_state'] = T1_initial_state #currently 'ms=0' or 'ms=-1'
    m.params['T1_readout_state'] = T1_readout_state #currently 'ms=0' or 'ms=-1'
    m.params['wait_times'] =  np.linspace(100,1.5e3,16) #in us, values must be divisible by the repeat element
    m.params['wait_time_repeat_element'] = 100      #in us, this element is repeated to create the wait times
    m.params['repetitions'] = 500

        #Plot parameters
    m.params['sweep_name'] = 'Times (Us)'
    m.params['sweep_pts'] = m.params['wait_times']
    m.params['pts'] = len(m.params['sweep_pts']) #Check if we need this line, Tim

        #Set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0

    m.autoconfig()

    print 'initial_state: ' + m.params['T1_initial_state']
    print 'readout_state: ' + m.params['T1_readout_state']
    print m.params['sweep_pts']
    '''generate sequence'''
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    

    T1(SAMPLE+'_'+'init_0_RO_0', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0')
    # T1(SAMPLE+'_'+'init_0_RO_-1', T1_initial_state = 'ms=0', T1_readout_state = 'ms=-1')
    # T1(SAMPLE+'_'+'init_-1_RO_0', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=0')
    # T1(SAMPLE+'_'+'init_-1_RO_-1', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1')
