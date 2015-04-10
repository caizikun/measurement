"""
This script performs a gate that relies on the geometric phase acquired by a carbon spin.

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

def GeometricGate(name, C13_init_method='swap',carbon_nr = 5,C13_init_state='up',N_uncond=[28],N_cond=[36]):

    m = DD.GeometricGate(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_nr'] = carbon_nr    
    
    m.params['reps_per_ROsequence'] = 200
    m.params['C13_init_state']      = C13_init_state
    m.params['sweep_name']          = 'waiting time (us)'
    m.params['e_ro_orientation']    = 'positive'
    m.params['C13_init_method']     = C13_init_method
    m.params['calibrate_pulses']= False
    m.params['no_unconditional_rotation'] = False

    f0=m.params['C'+str(carbon_nr)+'_freq_0']
    f1=m.params['C'+str(carbon_nr)+'_freq_1']
    HalfWaittime=(1/np.abs(f1-f0))/4.


    m.params['C5_geo_cond_N'] = N_cond
    m.params['C5_geo_uncond_N']= N_uncond

#     ### Sweep parameters
    m.params['waiting_times']=np.linspace(HalfWaittime-7e-6,HalfWaittime+30e-6,11)
    m.params['pts'] = len(m.params['waiting_times']) 

    m.params['sweep_pts'] =[x*2*10**6 for x in m.params['waiting_times']] ## rescale to microseconds and total waiting time!

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0
    
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    GeometricGate(SAMPLE + '_C5_pZ_Ncond_46_Nuncond_34',carbon_nr = 5,C13_init_state='up',N_uncond=[34],N_cond=[46])

    GeometricGate(SAMPLE + '_C5_pZ_Ncond_36_Nuncond_28',carbon_nr = 5,C13_init_state='up')
    
    GeometricGate(SAMPLE + '_C5_pZ_Ncond_26_Nuncond_20',carbon_nr = 5,C13_init_state='up',N_uncond=[20],N_cond=[26])
    GeometricGate(SAMPLE + '_C5_pZ_Ncond_18_Nuncond_14',carbon_nr = 5,C13_init_state='up',N_uncond=[14],N_cond=[18])
       






