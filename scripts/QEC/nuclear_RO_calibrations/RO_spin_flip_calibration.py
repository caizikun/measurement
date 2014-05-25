'''script to use the MBI class to calibrate the spin flip probability in the RO
(or alternatively how projective the electron spin RO is) 
prepares ms=0, then performs readout twice (dynamical stop).
'''
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)


def run(name):
    m = pulsar_mbi_espin.ElectronRabi(name)
    funcs.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 4000
    
    #Switch spin pumping towards ms=0
    m.params['Ex_SP_amplitude'] = 0e-9 
    m.params['A_SP_amplitude']  = 10e-9   
    m.params['SP_E_duration']   = 50

    #No repump in between
    m.params['repump_after_MBI_A_amplitude'] = [0e-9]
    
    #First RO (dynamical stop)
    m.params['Ex_MBI_amplitude'] = 0.1e-9
    m.params['MBI_duration']     = 32
    m.params['AWG_wait_for_adwin_MBI_duration'] = 32e-6+15e-6#1.2*m.params['MBI_duration']*1e-6# Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us


    #Do you want to condition on getting a click?
    m.params['MBI_threshold'] = 1

    # NO MW pulses
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays']     = np.ones(pts) * 2000e-9
    m.params['MW_pulse_durations']  = np.ones(pts) * 0
    m.params['MW_pulse_amps']       = np.ones(pts) * 0
    m.params['MW_pulse_mod_frqs']   = np.linspace(m.params['MW_modulation_frequency']-1.5e6, m.params['MW_modulation_frequency']+5.5e6, pts)

    
    # for the autoanalysis
    m.params['sweep_name'] = 'repetitions'
    m.params['sweep_pts']  = range(pts)
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run('RO_spin_flip_calibration')
