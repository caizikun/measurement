"""
Script for a carbon parity measurement with following Tomography
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

def Two_QB_MBE(name,tau = None):

    m = DD.Two_QB_MBE(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 15 
    # Carbon Initialization 
    m.params['C_init_method'] = 'MBI'
    m.params['C13_init_state'] = 'up' 
    m.params['Carbon A'] = 1
    m.params['Carbon B'] = 4  


    # Initial state for Carbon Parity measurement 
    m.params['Phases_C_A'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_A']= [False]*m.params['pts'] 
    m.params['Phases_C_B'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_B']= [False]*m.params['pts'] 


    # Tomography Readout stuff 
    m.params['Tomography Bases'] = ([
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],['X','I'],
            ['Y','X'],['Y','Y'],['Y','Z'],['Y','I'],
            ['Z','X'],['Z','Y'],['Z','Z'],['Z','I']])





    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to test
    m.params['C13_MBI_threshold']       = 1
    m.params['MBI_threshold']           = 1
    
    m.params['C13_MBI_RO_duration']     = 30 
    m.params['E_C13_MBI_amplitude']     = 1e-9

    m.params['SP_duration_after_C13']   = 50
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    
    # Specific for Parity
    m.params['N_init_C']= 2
    m.params['N_MBE'] =1
    m.params['N_parity_msmts']=0


    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=True)

if __name__ == '__main__':
    Two_QB_MBE(SAMPLE)

