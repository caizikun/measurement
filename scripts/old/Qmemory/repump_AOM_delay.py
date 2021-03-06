"""
Measures the relative delay between repumper and microwaves at the NV.
Applies a repumping beam and then a MW pi pulse.
time between the two pulses is varied.
"""
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin

execfile(qt.reload_current_setup)
import mbi.mbi_funcs as funcs
reload(funcs)


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
Name=SAMPLE_CFG

def run(name):
    m = pulsar_mbi_espin.ElectronRamsey_Dephasing(name)
    funcs.prepare(m)

    pts = 51
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 200
    m.params['detuning'] = 0e6 #artificial detuning

    # sequence parameters
    m.params['readout_with_second_source'] = False
    m.params['pump_using_MW2'] = False
    m.params['init_with_second_source'] = False
    m.params['init_in_zero'] = True

    # MW pulses
    ps.X_pulse(m) #this updated fast_pi_amp
        ## First pulse
    m.params['MW_pulse_2_durations'] = np.ones(pts) * m.params['fast_pi_duration']
    m.params['MW_pulse_2_amps'] = np.ones(pts) * m.params['fast_pi_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * \
        m.params['AWG_MBI_MW_pulse_mod_frq']
    m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    
        ## Second pulse
    m.params['MW_pulse_durations'] = np.linspace(0,0,pts) 
    m.params['MW_pulse_amps']      = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_phases']    = np.linspace(0,0,pts) 

    m.params['Repump_multiplicity'] = np.ones(pts)*1 ### this parameter is used for ionization studies.
    # laser beam
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    m.params['laser_dephasing_amplitude']= 1000e-9 #in Watts
    m.params['repumping_time'] = np.ones(pts)*0.7e-6 
    m.params['MW_repump_delay1'] =  np.ones(pts) * 500e-9
    #sweep param
    m.params['MW_repump_delay2'] = np.linspace(-0.5e-6, 0.5e-6,pts)


    # for the autoanalysis
    m.params['sweep_name'] = 'MW vs. repump delay'
    m.params['sweep_pts'] = m.params['MW_repump_delay2']/(1e-6)

    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    run(Name+'AOM_delay')



