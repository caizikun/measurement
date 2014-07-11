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
    m.params['pts'] = 21
    m.params['C_init_method'] = 'MBI'

    m.params['Addressed_Carbon'] = 1
    m.params['C13_init_state'] = 'up' 
    m.params['C_RO_Z'] = False 
    
    m.params['sweep_name']       = 'RO_phase_(degree)' 
    # m.params['sweep_name'] = 'wait_times'
    # m.params['sweep_name'] = 'C1_init_phase_offset' 

    if m.params['sweep_name'] == 'RO_phase_(degree)':
        m.params['C_RO_phase'] =  np.linspace(-65,90,m.params['pts']) 
        m.params['C1_init_phase_offset'] =  (np.ones(m.params['pts'])*0)
        m.params['wait_times'] = (np.ones(m.params['pts'])*100e-6+30e-6) #Note: wait time must be atleast carbon init time +5us 
        m.params['sweep_pts']        = m.params['C_RO_phase']

        print     'C_RO_phase %s'%m.params['C_RO_phase']

    elif m.params['sweep_name']  == 'wait_times':
        m.params['C_RO_phase'] =np.ones(m.params['pts'] )*0 # [None]*m.params['pts'] #
        m.params['wait_times'] = np.linspace(130e-6, 5e-3,m.params['pts'])#Note: wait time must be atleast carbon init time +5us 
        m.params['sweep_pts'] = m.params['wait_times']

    elif m.params['sweep_name'] == 'C1_init_phase_offset': 
        m.params['C1_init_phase_offset'] =  np.linspace(-105,75,m.params['pts']) 
        m.params['C_RO_phase'] = np.ones(m.params['pts'] )*0 
        m.params['wait_times'] = (np.ones(m.params['pts'])*100e-6+30e-6) #Note: wait time must be atleast carbon init time +5us 
        m.params['sweep_pts']        = m.params['C1_init_phase_offset']

        print 'C1_init_phase_offset %s'%    m.params['C1_init_phase_offset']




    #############################
    #!NB: These should go into msmt params
    #############################


    ##########
    # Overwrite certain params to test
    m.params['C13_MBI_threshold']       = 1
    m.params['MBI_threshold']           = 1
    
    m.params['C13_MBI_RO_duration']     = 31 
    m.params['E_C13_MBI_amplitude']     = 1e-9

    # m.params['C1_init_phase_offset'] = 0


    m.params['SP_duration_after_C13']   = 50
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    
    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    NuclearRamseyWithInitialization(SAMPLE)

