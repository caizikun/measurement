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
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
print SAMPLE_CFG
print SAMPLE

def darkesr(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])

    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 1000
    m.params['range']        = 4.0e6
    m.params['pts'] = 101
    m.params['pulse_length'] = 2.5e-6
    m.params['ssbmod_amplitude'] = 0.01
    
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

    print ' darkESR on +1...' 
    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    
    
    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']         = m.params['ms+1_cntr_frq'] - m.params['ssmod_detuning'] # MW source frequency, detuned from the target
    #print m.params['ms+1_cntr_frq']
    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000
    m.params['range'] = 20e6
    m.params['pts'] = 201
    m.params['pulse_length'] = 2.5e-6
    m.params['ssbmod_amplitude'] = 0.027
    m.params['Ex_SP_amplitude'] = 0

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def init_N_darkesr(name, init_reps):
    '''
    Initialize the Nitrogen with conditional pulses and Ex_SP_amplitude
    then
    dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.initNitrogen_DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])

    #m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['wait_after_RO_pulse_duration']=1#10000
    m.params['mw_frq']       = m.params['ms+1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 3000
    m.params['range']        = 1.5*m.params['N_HF_frq']
    m.params['pts'] = 51
    m.params['pulse_length'] = m.params['AWG_MBI_MW_pulse_duration']
    m.params['ssbmod_amplitude'] = m.params['AWG_MBI_MW_pulse_amp']
    m.params['init_repetitions']=init_reps
    m.params['RF_amp']=1*0
    #m.params['pi2pi_mI0_amp']=0
    m.params['RF1_duration']=0*53.6e-6
    m.params['RF2_duration']=0*30.4e-6

    B=(m.params['zero_field_splitting']-m.params['ms-1_cntr_frq'])/m.params['g_factor']
    m.params['RF1_frq'] = m.params['Q_splitting'] - m.params['N_HF_frq'] + m.params['g_factor_N14']*B
    m.params['RF2_frq'] = m.params['Q_splitting'] + m.params['N_HF_frq'] - m.params['g_factor_N14']*B
    m.params['RF1_frq'] = 2.667e6
    m.params['RF2_frq'] = 7.234e6

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()
if __name__ == '__main__':
    #darkesr(SAMPLE_CFG)
    #raw_input ('Do the fitting...')
    darkesrp1(SAMPLE_CFG)
    #reps = 100
    #for reps in [1,2,3,5,10]:
    #init_N_darkesr('test_init_pi2pi_mI0_and_mIm1_noRF_' +str(reps), init_reps=reps)
    #    raw_input('analysze...')
    #darkesr(SAMPLE_CFG)
