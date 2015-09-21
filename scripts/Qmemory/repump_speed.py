"""
Measures how fast we repump by elongating the repumping time for a given power.

NK 2015
"""
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import mbi.mbi_funcs as funcs
reload(funcs)


SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']



def run(name):
    m = pulsar_mbi_espin.ElectronRamsey_Dephasing(name)
    funcs.prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500
    m.params['detuning'] = 0e6 #artificial detuning

    # MW pulses
        ## First pulse
    #print 'PULSE AMP'
    #print m.params['fast_pi_amp']
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi_duration']
    m.params['MW_pulse_amps'] = np.ones(pts) * m.params['fast_pi_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * m.params['AWG_MBI_MW_pulse_mod_frq']
    m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    
        ## Second pulse
    m.params['MW_pulse_2_durations'] = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_amps']      = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_phases']    = np.linspace(0,0,pts) 


    # laser beam
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    m.params['laser_dephasing_amplitude']= 900e-9 #in Watts
    m.params['repumping_time'] = np.linspace(0.0e-6,2e-6,pts) 
    m.params['MW_repump_delay1'] =  np.ones(pts) * 500e-9
    #sweep param
    m.params['MW_repump_delay2'] = np.ones(pts) * 2500e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'Repump duration (us)'
    m.params['sweep_pts'] = m.params['repumping_time']/(1e-6)

    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run(SAMPLE_CFG+'ElectronRepump')



