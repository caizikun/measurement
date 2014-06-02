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

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 750


    m.params['MW_pulse_amps']       = np.ones(pts) * 0.09#m.params['fast_pi_amp']
    m.params['MW_pulse_mod_frqs']   = np.ones(pts) * m.params['MW_modulation_frequency'] -m.params['N_HF_frq']#m.params['AWG_MBI_MW_pulse_mod_frq']


    if 1:
        m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
        m.params['MW_pulse_delays'] = np.ones(pts) * 2000e-9
    # MW pulses
        m.params['MW_pulse_durations']  = np.linspace(0,7500e-9,pts) # 05-30-'14 Took away the +10 ns -Machiel
        m.params['sweep_name'] = 'MW pulse duration (ns)'
        m.params['sweep_pts']  = m.params['MW_pulse_durations'] * 1e9

        #m.params['sweep_name'] = 'MW amp (V)'
        #m.params['sweep_pts']  = m.params['MW_pulse_amps'] 


    if 0:
        m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)*4
        tau_larmor = 2.999e-6
        m.params['MW_pulse_delays'] = 2 * np.linspace(tau_larmor,pts*tau_larmor,pts)
        m.params['MW_pulse_durations']  = np.ones(pts)* m.params['fast_pi_duration']#why this +10 here?
        m.params['sweep_name'] = 'MW_pulse_delays'
        m.params['sweep_pts']  = m.params['MW_pulse_delays'] * 1e9


    # for the autoanalysis

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run('hans1_finding_slow_pi')

