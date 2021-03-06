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

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def erabi(name):
    m = pulsar_msmt.ElectronRabi(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin']) #
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    
    m.params['pts']             = 21
    pts                         = m.params['pts']
    m.params['repetitions']     = 5000
    m.params['Ex_SP_amplitude'] = 0

    # m.params['pulse_shape'] = 'Hermite'
    # print m.params['pulse_shape']

    sweep_param = 'length'

    m.params['mw_power']=-1
    m.params['MW_modulation_frequency'] = 43e6
    m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_modulation_frequency']
  
    if sweep_param == 'length':
        if m. params['electron_transition'] == '_m1':
            print 'minus 1 transition'
            m.params['MW_pulse_durations'] =  np.linspace(0, 8000, pts) * 1e-9
        elif m. params['electron_transition'] == '_p1':
            print 'plus 1 transition'
            m.params['MW_pulse_durations'] =  np.linspace(0, 8000, pts) * 1e-9            
        m.params['MW_pulse_amplitudes'] = np.ones(pts) * 0.08 
        # m.params['MW_pulse_amplitudes'] = np.ones(pts) * m.params['fast_pi_amp'] 
        # m.params['MW_pulse_amplitudes'] = np.ones(pts) * m.params['Square_pi_amp']
        m.params['sweep_name'] = 'Pulse durations (ns)'
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
        

    elif sweep_param == 'amplitude':    
        m.params['MW_pulse_durations'] =  np.ones(pts)*4000e-9 
        m.params['MW_pulse_amplitudes'] = np.linspace(0.0,0.08,pts) #0.02
        m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
        m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    m.params['MW_pulse_frequency'] = m.params['MW_modulation_frequency']

    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    print m.params['sweep_pts']

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    m.run()
    qt.msleep(2)
    m.save()
    qt.msleep(2)
    m.finish()

if __name__ == '__main__':
    erabi(SAMPLE)
