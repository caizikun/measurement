"""
Performs a ramsey measurement where a laser beam is shined in during the wait time. 
"""
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import mbi.mbi_funcs as funcs
reload(funcs)

###################################################################
#TODO: check the implementation of a general AOM channel!!!!!!!!!##
###################################################################

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']
Name='111_No1_Sil18_'


def run(name):
    m = pulsar_mbi_espin.ElectronRamsey_Dephasing(name)
    funcs.prepare(m)

    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    m.params['evolution_time']=400e-9
    m.params['MW_pulse_delays'] = np.ones(pts)*m.params['evolution_time'] #during this time we shine in a laser
    m.params['detuning'] = 0e6 #artificial detuning

    # MW pulses
        ## First pulse
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi2_duration']
    m.params['MW_pulse_amps'] = np.ones(pts) * m.params['fast_pi2_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
    m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    
        ## Second pulse
    m.params['MW_pulse_2_durations'] = m.params['MW_pulse_durations'] 
    m.params['MW_pulse_2_amps']      = m.params['MW_pulse_amps']
    m.params['MW_pulse_2_phases']    = np.linspace(0,360,pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['MW_pulse_2_phases'] /1e-9

    # laser beam
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    m.params['laser_dephasing_amplitude']= 0e-9 #in Watts
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run(Name+'mbi_eramsey_dephasing')


