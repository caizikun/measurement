import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)


def run(name):
    m = pulsar_mbi_espin.ElectronRabi(name)
    funcs.prepare(m)
    print 'MBI threshold =' + str(m.params['MBI_threshold'])
    print 'Ex_MBI_amplitude =' + str(m.params['Ex_MBI_amplitude'])
    print 'SSRO_duration =' + str(m.params['SSRO_duration'])

    pts = 61
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 300

    if 1:
        m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
        m.params['MW_pulse_delays'] = np.ones(pts) * 2000e-9
    # MW pulses
        m.params['MW_pulse_durations']  = np.linspace(0,2100e-9,pts) + 10e-9 #why this +10 here?
        m.params['sweep_name'] = 'MW pulse duration (ns)'
        m.params['sweep_pts']  = m.params['MW_pulse_durations'] * 1e9


    if 0:
        m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)*4
        tau_larmor = 2.999e-6
        m.params['MW_pulse_delays'] = 2 * np.linspace(tau_larmor,pts*tau_larmor,pts)
        m.params['MW_pulse_durations']  = np.ones(pts)* m.params['fast_pi_duration']#why this +10 here?
        m.params['sweep_name'] = 'MW_pulse_delays'
        m.params['sweep_pts']  = m.params['MW_pulse_delays'] * 1e9


    m.params['MW_pulse_amps']       = np.ones(pts) * m.params['fast_pi_amp']
    m.params['MW_pulse_mod_frqs']   = np.ones(pts) * m.params['AWG_MBI_MW_pulse_mod_frq']

    print m.params['MW_pulse_mod_frqs']

    # for the autoanalysis

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run('hans1_finding_fast_rabi_frequency')

