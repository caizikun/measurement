"""
This script calibrates the rotations for the unconditional gate. 
Goal find a unconditional rotation which undoes one of the two conditional ones.
AR & NK 2015
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def GeometricGate(name, C13_init_method='swap',carbon_nr = 5,C13_init_state='up'):

    m = DD.GeometricGate(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_nr'] = carbon_nr    
    
    m.params['reps_per_ROsequence'] = 200
    m.params['C13_init_state']      = C13_init_state
    m.params['sweep_name']          = 'Number of pulses'
    m.params['e_ro_orientation']    = 'positive'
    m.params['C13_init_method']     = C13_init_method
    m.params['calibrate_pulses']= False
    m.params['no_unconditional_rotation'] = True

    f0=m.params['C'+str(carbon_nr)+'_freq_0']
    f1=m.params['C'+str(carbon_nr)+'_freq_1']
    HalfWaittime=(1/np.abs(f1-f0))/4.

#     ### Sweep parameters
    # m.params['waiting_times']=np.linspace(HalfWaittime-10e-6,HalfWaittime+10e-6,11)
    m.params['Number_of_pulses_cond'] = np.arange(4,54,4)
    m.params['waiting_times'] = len(m.params['Number_of_pulses_cond'])*[4*HalfWaittime]  ###Do a full rotation.
    m.params['pts'] = len(m.params['Number_of_pulses_cond']) 

    m.params['sweep_pts'] =m.params['Number_of_pulses_cond'] 

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    GeometricGate(SAMPLE + '_C5_pZ_noUnconditional',carbon_nr = 5,C13_init_state='up')
    #Echo_gate(SAMPLE + '_C5_mZ_eROX',carbon_nr = 5,C13_init_state='down')
       






