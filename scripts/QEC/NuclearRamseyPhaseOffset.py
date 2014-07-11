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
    m.params['pts'] = 2
    m.params['C_init_method'] = 'MBI'

    m.params['Addressed_Carbon'] = 1
    m.params['C13_init_state'] = 'up' 
    m.params['C_RO_Z'] = False 
    
    # m.params['sweep_name']       = 'RO_phase_(degree)' 
    m.params['sweep_name'] = 'Phase_offset'
    m.params['C'+str(m.params['Addressed_Carbon'])+'_init_phase_offset'] = np.linspace(0,180,m.params['pts']) 


    m.params['C_RO_phase'] =np.ones(m.params['pts'] )*0 
    m.params['wait_times'] = (np.ones(m.params['pts'])*130e-6) #Note: wait time must be atleast carbon init time +5us 
    m.params['sweep_pts']        = m.params['C'+str(m.params['Addressed_Carbon'])+'_init_phase_offset']

    #############################
    #!NB: These should go into msmt params
    #############################


    ##########
    # Overwrite certain params to test
    m.params['C13_MBI_threshold']       = 1
    m.params['MBI_threshold']           = 1
    
    m.params['C13_MBI_RO_duration']     = 31 
    m.params['E_C13_MBI_amplitude']     = 1e-9

    m.params['SP_duration_after_C13']   = 50
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    
    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=True)

if __name__ == '__main__':
    NuclearRamseyWithInitialization(SAMPLE)
