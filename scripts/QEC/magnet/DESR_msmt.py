# import the msmt class
import qt
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


def darkesr(name, ms = 'msp', range_MHz = 6, pts = 81, reps = 1000, freq=0, 
        pulse_length = 2e-6, ssbmod_amplitude = None, mw_switch=False):
    if mw_switch:
        m = pulsar_msmt.DarkESR_Switch(name)
    else:
        m = pulsar_msmt.DarkESR(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    if ms == 'msp':
        m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
        m.params['pulse_length'] = pulse_length
        
        if ssbmod_amplitude == None:
            m.params['ssbmod_amplitude'] = 0.025
        else:
            m.params['ssbmod_amplitude'] = ssbmod_amplitude

    elif ms == 'msm':
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] - 43e6
        m.params['pulse_length'] = pulse_length
        
        if ssbmod_amplitude == None:
            m.params['ssbmod_amplitude'] = 0.010
        else:
            m.params['ssbmod_amplitude'] = ssbmod_amplitude
        
    if freq != 0:
        m.params['mw_frq'] = freq - 43e6
            
    m.params['repetitions'] = reps

    m.params['ssbmod_frq_start'] = 43e6 - range_MHz*1e6 
    m.params['ssbmod_frq_stop'] = 43e6 + range_MHz*1e6
    m.params['pts'] = pts

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()