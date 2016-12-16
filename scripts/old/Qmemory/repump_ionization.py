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



def run(name, **kw):
    m = pulsar_mbi_espin.ElectronRamsey_Dephasing(name)
    funcs.prepare(m)
    pts = 30# even number
    m.params['pts'] = pts
    max_reps = kw.get('Element_reps',3000)
    m.params['Repump_multiplicity'] = np.round(np.arange(1,max_reps,(max_reps-1)/float(pts)))
    pts = len(m.params['Repump_multiplicity'])


    m.params['reps_per_ROsequence'] = 500
    m.params['detuning'] = 0e6 #artificial detuning (MW)

    # MW pulses
        ## First pulse
    #print 'PULSE AMP'
    #print m.params['fast_pi_amp']
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['fast_pi_duration']
    m.params['MW_pulse_amps'] = np.ones(pts) * m.params['fast_pi_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) *  m.params['AWG_MBI_MW_pulse_mod_frq']
    m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    
        ## Second pulse
    m.params['MW_pulse_2_durations'] = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_amps']      = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_phases']    = np.linspace(0,0,pts) 


    # laser beam
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    #m.params['laser_dephasing_amplitude']= 2400e-9 #in Watts
    m.params['repumping_time'] = np.ones(pts)*1.5e-6 
    #m.params['repumping_time'] = np.r_[np.linspace(0.03e-6,0.5e-6,pts/4.), np.linspace(0.2e-6,5e-6,3.*pts/4.)]
    m.params['MW_repump_delay1'] =  np.ones(pts) * 500e-9
    #sweep param
    m.params['MW_repump_delay2'] = np.ones(pts) * 2500e-9
    
    # for the autoanalysis
    m.params['sweep_name'] = 'Number of repetitions'
    m.params['sweep_pts'] = m.params['Repump_multiplicity']

    m.params['laser_dephasing_amplitude'] = kw.get('repump_power',2400e-9)
    funcs.finish(m, debug = kw.get('debug',False))

if __name__ == '__main__':
    #repump_power_list = [3500e-9, 2700e-9, 2000e-9, 1500e-9, 1000e-9, 500e-9, 200e-9, 100e-9, 60e-9, 40e-9, 30e-9]
    repump_power_list = [2000e-9]#, 350e-9, 200e-9, 100e-9, 50e-9, 20e-9]
    for sweep_element in repump_power_list:
        print 'current repump power ', str(sweep_element)
        run('ElectronRepumpIonization_'+str(sweep_element)+'nW_A1A2', repump_power=sweep_element,debug=False,max_reps=50)