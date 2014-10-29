"""
Script for a carbon ramsey sequence
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

def Long_Carbon_Ramsey(name,tau = None,Addressed_Carbon = 1):

    m = DD.LongNuclearRamsey(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Ren_Decoupling_scheme'] = 'repeating_T_elt'
    m.params['DD_wait_scheme'] = 'auto'#XY8'

    ### Sweep parameters

    m.params['N_list'] = range(4,320,20)# np.ones(len(m.params['Phases_of_Ren_B']))*4 #
    m.params['Phases_of_Ren_B'] = np.ones(len(m.params['N_list']))*0 

    # m.params['N_list'] = np.ones(21)*4#
    # m.params['Phases_of_Ren_B'] = np.linspace(0,360*2,21)  
 
    m.params['C'+str(Addressed_Carbon)+'_freq'] = ( 
        m.params['C'+str(Addressed_Carbon)+'_freq']+0.25e3) # Overwrites the msmst params. Usefull to calibrate and find the correct freq 
    
    tau_larmor = m.get_tau_larmor()
    m.params['tau_list']           = np.ones(len(m.params['N_list']) )*tau_larmor*8
    m.params['Addressed_Carbon']   = Addressed_Carbon 
 

    m.params['pts']              = len(m.params['Phases_of_Ren_B'])
    m.params['sweep_pts']        = np.ones(len(m.params['N_list'])) #NB! This value is overwritten in the measurement class 
                                                   # when the sweep name is 'Free Evolution Time (s)' 
    m.params['sweep_name'] = 'Free Evolution time (s)' 



    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    Long_Carbon_Ramsey(SAMPLE)

