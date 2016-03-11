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
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
#reload(funcs)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def darkesr(name):
    '''dark ESR on the 0 <-> -1 transition
    '''
    m = pulsar_msmt.DarkESR(name)
    print 'adwin3 ' + str(m.adwin)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    # m.params['ssmod_detuning'] = 250e6#m.params['MW_modulation_frequency']
    m.params['mw_frq'] = m.params['ms-1_cntr_frq']-43e6 #MW source frequency
    m.params['repetitions']  = 1000
    m.params['range']        = 5e6 #5e6
    m.params['pts'] = 151
    m.params['pulse_length'] = m.params['DESR_pulse_duration'] # was 2.e-6 changed to msmt params # NK 2015-05 27
    m.params['ssbmod_amplitude'] = m.params['DESR_pulse_amplitude'] #0.03 changed to msmt params # NK 2015-05-27
    m.params['mw_power'] = 20
    m.params['Ex_SP_amplitude']=0

    m.params['ssbmod_frq_start'] = 43e6 - m.params['range']  
    m.params['ssbmod_frq_stop'] = 43e6 + m.params['range'] 
    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    
    m.autoconfig()
    #m.params['sweep_pts']=m.params['pts']
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
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

    # m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['mw_frq']         = m.params['ms+1_cntr_frq']-43e6# - m.params['ssmod_detuning'] # MW source frequency, detuned from the target
    m.params['mw_power'] = 20
    m.params['Ex_SP_amplitude']=0
    m.params['range']        = 5e6
    m.params['pts'] = 151
    m.params['repetitions'] = 1000
    m.params['pulse_length'] = m.params['DESR_pulse_duration'] # was 2.e-6 changed to msmt params # NK 2015-05 27
    m.params['ssbmod_amplitude'] = m.params['DESR_pulse_amplitude'] #0.03 changed to msmt params # NK 2015-05-27

    m.params['ssbmod_frq_start'] = 43e6 - m.params['range']  
    m.params['ssbmod_frq_stop'] = 43e6 + m.params['range'] 
    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] =(np.array(list_swp_pts) + m.params['mw_frq'])*1e-9
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def Generaldarkesr(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.GeneralDarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['ssmod_detuning'] = m.params['desr_modulation_frequency']
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 750
    m.params['range']        = 2.35e6
    m.params['pts'] = 61
    m.params['mw_power']=m.params['desr_MW_power']
    m.params['Ex_SP_amplitude']=0

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']
    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    
    m.params['pulse_shape']='Square'
    m.params['pulse_type'] = m.params['pulse_shape'] 
    desr_pi = ps.desr_pulse(m)
    print desr_pi
    m.params['MW_pi_duration'] = m.params['desr_pulse_duration']
    m.autoconfig()
    #m.params['sweep_pts']=m.params['pts']
    #print m.params['MW_pi_duration']
    m.generate_sequence(upload=True,pulse_pi = desr_pi)
    m.run()
    m.save()
    m.finish()
    

if __name__ == '__main__':
    # darkesr(SAMPLE_CFG)
    darkesrp1(SAMPLE_CFG)
    