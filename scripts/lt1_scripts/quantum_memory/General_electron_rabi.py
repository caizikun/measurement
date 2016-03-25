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
    m = pulsar_msmt.GeneralElectronRabi(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    #m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    
    m.params['pts'] = 16
    pts = m.params['pts']
    m.params['repetitions'] = 1000
    m.params['Ex_SP_amplitude']=0

    sweep_param = 'length'

    m.params['mw_power']=5
    #m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_modulation_frequency']  
    #print m.params['ms+1_cntr_frq']    #for ms=-1   'ms-1_cntr_frq'
    #m.params['mw_frq'] = 3.45e9      #for ms=+1

    if sweep_param == 'length':
        m.params['pulse_sweep_durations'] =  np.linspace(0, 4000, pts) * 1e-9
        pulse_amp=3*0.016
        m.params['pulse_sweep_amps'] = np.ones(pts) * pulse_amp # * 0.05 #*0.49
        m.params['fast_pi_amp'] = pulse_amp
        m.params['sweep_name'] = 'Pulse durations (ns)'
        m.params['sweep_pts'] = m.params['pulse_sweep_durations']*1e9
        

    elif sweep_param == 'amplitude':    
        pulse_duration=44e-9
        m.params['pulse_sweep_durations'] =  np.ones(pts)*pulse_duration 
        m.params['fast_pi_duration'] = pulse_duration
        m.params['pulse_sweep_amps'] = np.linspace(0.3,0.6,pts) #0.02
        m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
        m.params['sweep_pts'] = m.params['pulse_sweep_amps']

    m.params['MW_modulation_frequency'] = 40e6
    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-m.params['MW_modulation_frequency']   # for ms+1
    m.params['pulse_shape']='Square'
    m.params['pulse_type'] = m.params['pulse_shape'] 
    X_pi = ps.X_pulse(m)
    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    print m.params['sweep_pts']

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True,pulse_pi=X_pi)
    m.run()
    qt.msleep(2)
    m.save()
    qt.msleep(2)
    m.finish()

if __name__ == '__main__':
    erabi(SAMPLE+'_'+'msm1')
