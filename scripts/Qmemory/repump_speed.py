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



def run(name,rp_power=500):
    m = pulsar_mbi_espin.ElectronRamsey_Dephasing(name)
    funcs.prepare(m)

    pts = 36
    m.params['pts'] = pts
    min_repumptime = 0.07e-6 # minimum number of LDE reps
    max_repumptime = 50e-6 # max number of LDe reps. this number is going to be rounded
    times_linear_incr=np.linspace(min_repumptime**(1/3.),max_repumptime**(1/3.),pts)
    m.params['reps_per_ROsequence'] = 1500
    m.params['detuning'] = 0e6 #artificial detuning

    # MW pulses
        ## First pulse
    #print 'PULSE AMP'
    #print m.params['fast_pi_amp']
    m.params['MW_pulse_durations'] = np.ones(pts) * m.params['Hermite_fast_pi_duration']
    m.params['MW_pulse_amps'] = np.ones(pts) * m.params['Hermite_fast_pi_amp']
    m.params['MW_pulse_mod_frqs'] = np.ones(pts) * m.params['Hermite_fast_pi_mod_frq']
    m.params['MW_pulse_1_phases'] = np.ones(pts) * 0
    
        ## Second pulse
    m.params['MW_pulse_2_durations'] = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_amps']      = np.linspace(0,0,pts) 
    m.params['MW_pulse_2_phases']    = np.linspace(0,0,pts) 


    # laser beam
    m.params['dephasing_AOM'] = 'NewfocusAOM' 
    m.params['laser_dephasing_amplitude']= rp_power*1e-9 #in Watts
    m.params['repumping_time'] = times_linear_incr**3#np.linspace(min_repumptime,max_repumptime,pts) #times_linear_incr**3
    m.params['MW_repump_delay1'] =  np.ones(pts) * 2500e-9
    #sweep param
    m.params['MW_repump_delay2'] = np.ones(pts) * 2500e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'Repump duration (us)'
    m.params['sweep_pts'] = m.params['repumping_time']/(1e-6)

    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    powers=[5]
    #powers=[1500]
    for rp_power in powers:
        if rp_power == powers[len(powers)/2]:
            GreenAOM.set_power(7e-6)
            qt.msleep(2)
            optimiz0r.optimize(dims=['x','y','z','x','y'])
        run(SAMPLE_CFG+'ElectronRepump_'+str(rp_power)+'nW',rp_power=rp_power)



