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

def NuclearRamseyWithInitialization(name,tau = None):

    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)

    '''set experimental parameters'''


    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 10 

    m.params['Addressed_Carbon'] = 1
    m.params['Carbon_init_RO_wait']   = 15e-6

    m.params['C_RO_phase'] =  np.linspace(0,360,m.params['pts'])
    
    m.params['wait_times'] = np.ones( m.params['pts'] )* m.params['Carbon_init_RO_wait'] +5e-6 #Note: wait time must be atleast carbon init time +5us 
    
    print     m.params['C_RO_phase']

    m.params['sweep_pts']        = m.params['C_RO_phase']#NB! This value is overwritten in the measurement class when the sweep name is 'Free Evolution Time (s)' 
    m.params['sweep_name']       = 'Free Evolution time (s)' 


    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to make the script always work 
    # m.params['MBI_threshold']           = 0
    m.params['C13_MBI_threshold']       = 1
    m.params['SP_duration_after_C13']   = 10

    # We don't want to specify voltages but powers ... Let's see how this works for the other powers.. Not trivial 
    m.params['A_SP_amplitude_after_C13_MBI']  = 5e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    m.params['E_C13_MBI_amplitude']       = 5e-9

    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    NuclearRamseyWithInitialization(SAMPLE)

