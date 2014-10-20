import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)


def run(name):
    m = pulsar_mbi_espin.ElectronRabi(name)
    funcs.prepare(m)

    print 'threshold =' + str(m.params['MBI_threshold'])

    # m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    pts = 61
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.ones(pts).astype(int)
    m.params['MW_pulse_delays'] = np.ones(pts) * 2500e-9

    # MW pulses
    m.params['MW_pulse_durations']  = np.ones(pts) * 2e-6 #3000e-9
    m.params['MW_pulse_amps']       = np.ones(pts) * 0.02 #for msp1,  0.022 for msm1, 

    m.params['MW_pulse_mod_frqs']   = np.linspace(m.params['MW_modulation_frequency']
            -1.5e6, m.params['MW_modulation_frequency']+5.5e6, pts)

    print m.params['MW_pulse_mod_frqs']

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pulse frequency (MHz)'
    m.params['sweep_pts']  = (m.params['MW_pulse_mod_frqs'] + m.params['mw_frq'])/1.e6
    

    print m.params['MBI_threshold']
    funcs.finish(m, debug=False)

    print m.params['AWG_MBI_MW_pulse_mod_frq']



if __name__ == '__main__':
    run('MBI_DESR_Hans_sil1_msm1')

