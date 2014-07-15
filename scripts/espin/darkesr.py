"""
Script for e-spin manipulations using the pulsar sequencer
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

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def darkesr(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    #m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])

    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 500
    m.params['range']        = 4e6
    m.params['pts'] = 56
    m.params['pulse_length'] = .5e-6
    m.params['ssbmod_amplitude'] = 0.06
    
    m.params['Ex_SP_amplitude']=0



    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def darkesrp1(name):
    '''dark ESR on the 0 <-> +1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

    m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['mw_frq']         = m.params['ms+1_cntr_frq'] - m.params['ssmod_detuning'] # MW source frequency, detuned from the target
    m.params['mw_power'] = 20
    m.params['repetitions'] = 500
    m.params['range']        = 20e6
    m.params['pts'] = 151
    m.params['pulse_length'] = 2.5e-6
    m.params['ssbmod_amplitude'] = 0.025

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] #- m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + 2*m.params['range']

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()



if __name__ == '__main__':
    darkesr(SAMPLE_CFG)
    #raw_input ('Do the fitting...')
    #darkesrp1(SAMPLE_CFG)
