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
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    #m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    
    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 1500
    m.params['Ex_SP_amplitude']=0

    sweep_param = 'amplitude'


    #m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_modulation_frequency']  
    #print m.params['ms+1_cntr_frq']    #for ms=-1   'ms-1_cntr_frq'
    #m.params['mw_frq'] = 3.45e9      #for ms=+1

    if sweep_param == 'length':
        m.params['MW_pulse_durations'] =  np.linspace(0, 600, pts) * 1e-9
        m.params['MW_pulse_amplitudes'] = np.ones(pts)*0.8
        m.params['sweep_name'] = 'Pulse durations (ns)'
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
        

    elif sweep_param == 'amplitude':    
        m.params['MW_pulse_durations'] =  np.ones(pts)*3e-6 
        m.params['MW_pulse_amplitudes'] = np.linspace(0,0.03,pts) #0.02
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
    erabi(SAMPLE+'_'+'msm1')
