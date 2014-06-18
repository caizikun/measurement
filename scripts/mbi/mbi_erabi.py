import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
print SAMPLE_CFG
print SAMPLE

def run(name):
    m = pulsar_mbi_espin.ElectronRabi(name)
    funcs.prepare(m)
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    print 'TIM/Julia/Adriaan, not sure if you use this script, but I changed a few things - 14-05-30 -Machiel'
    print 'MBI threshold =' + str(m.params['MBI_threshold'])
    print 'Ex_MBI_amplitude =' + str(m.params['Ex_MBI_amplitude'])
    print 'SSRO_duration =' + str(m.params['SSRO_duration'])

    pts = 15
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 750

    sweep_duration=True
    sweep_detuning=False

    m.params['MW_pulse_mod_frqs']   = np.ones(pts) * m.params['MW_modulation_frequency'] #+m.params['N_HF_frq']
    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-m.params['MW_modulation_frequency']
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)#*5
    m.params['MW_pulse_delays'] = np.ones(pts) * 200e-9
    
    if sweep_duration:        
    # MW pulses
        m.params['MW_pulse_amps']       = np.ones(pts) * m.params['pi2pi_mIm1_amp']
        m.params['MW_pulse_durations']  = np.linspace(0,600e-9,pts) # 05-30-'14 Took away the +10 ns -Machiel
        m.params['sweep_name'] = 'MW pulse duration (ns)'
        m.params['sweep_pts']  = m.params['MW_pulse_durations'] * 1e9
    else:
        tau_larmor = 2.999e-6
        m.params['MW_pulse_amps']       = np.linspace(0.0,0.31,pts)
        m.params['MW_pulse_durations']  = np.ones(pts)* 394e-9
        m.params['sweep_name'] = 'MW pulse amp'
        m.params['sweep_pts']  = m.params['MW_pulse_amps']
    if sweep_detuning:    
        m.params['MW_pulse_amps']       = np.ones(pts) * 0.108#m.params['fast_pi_amp']
        m.params['MW_pulse_durations']  = np.ones(pts)* 394e-9 # 05-30-'14 Took away the +10 ns -Machiel
        fctr=m.params['MW_modulation_frequency']
        m.params['MW_pulse_mod_frqs']   = np.linspace(fctr-500e3,fctr+500e3,pts) 
        m.params['sweep_name'] = 'MW added detuning (KHz)'
        m.params['sweep_pts']  = m.params['MW_pulse_mod_frqs'] * 1e-3


    # for the autoanalysis

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run('hans1_pi2pi_calibr_init-m1_RO-0')

