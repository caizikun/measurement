import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import mbi.mbi_funcs as funcs
reload(funcs)


SIL_NAME = 'nr1_sil18'

def run(name, phase = 0, ):
    m = pulsar_mbi_espin.ElectronRamsey(name)
    funcs.prepare(m, SIL_NAME)

    ### sweep the length of the second pulse
    MW_pulse_2_durations = np.arange(0, m.params['fast_pi_duration']+10e-9, 8e-9) 

    pts = len(MW_pulse_2_durations)
    m.params['pts']                 = pts
    m.params['reps_per_ROsequence'] = 2000       
    m.params['MW_pulse_delays']     = np.ones(pts) * 20e-6     # Time between the first and second pulse
 
    ## MW pulses
    m.params['MW_pulse_mod_frqs']   = np.ones(pts) * m.params['AWG_MBI_MW_pulse_mod_frq']

        ## First pulse
    m.params['MW_pulse_durations']  = np.ones(pts) * m.params['fast_pi2_duration']
    m.params['MW_pulse_amps']       = np.ones(pts) * m.params['fast_pi2_amp']
    m.params['MW_pulse_1_phases']   = np.ones(pts) * 90
    
        ## Second pulse
    m.params['MW_pulse_2_durations'] = MW_pulse_2_durations
    m.params['MW_pulse_2_amps']      = np.ones(pts) * m.params['fast_pi_amp']
    m.params['MW_pulse_2_phases']    = np.ones(pts) * phase
    # for the autoanalysis
    m.params['sweep_name'] = 'MW_pulse_2_duration (ns)'
    m.params['sweep_pts'] = MW_pulse_2_durations/1e-9
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run(SIL_NAME+'pi2_calibration', phase = 0)

