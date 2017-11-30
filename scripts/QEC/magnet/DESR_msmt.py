# import the msmt class
import numpy as np
import qt
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

temperature_sensor = qt.instruments['kei2000']
magnet_Z_scanner = qt.instruments['conex_scanner_Z']

def darkesr(name, ms = 'msp', range_MHz = 6, pts = 81, reps = 1000, freq=0, 
        pulse_length = 2e-6, ssbmod_amplitude = None, mw_power = 20, mw_switch=False):
    if mw_switch:
        m = pulsar_msmt.DarkESR_Switch(name)
    else:
        m = pulsar_msmt.DarkESR(name)


    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['111_1_sil18']['pulses']) #Added to include the MW switch MA

    m.params['mw_power'] = mw_power
    m.params['temp'] = temperature_sensor.get_readlastval()
    m.params['magnet_position'] = magnet_Z_scanner.GetPosition()

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

    m.params['sweep_pts'] = (np.linspace(m.params['ssbmod_frq_start'],
                    m.params['ssbmod_frq_stop'], m.params['pts']) 
                    + m.params['mw_frq'])*1e-9

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    darkesr()

