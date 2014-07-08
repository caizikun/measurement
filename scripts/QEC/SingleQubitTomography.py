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

def NuclearRamseyWithInitialization(name,tau = None, RO_phase=0, RO_Z=False):

    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 21 


    #Carbon to be addressed
    m.params['Addressed_Carbon'] = 1
    # State to be initialized into 
    m.params['C13_init_state'] = 'up' 
    m.params['C_init_method'] = 'swap'#'MBI'

    m.params['sweep_name'] = 'C_RO_phase' 

    m.params['C_RO_phase'] =  np.linspace(0,360*3,m.params['pts'])+ RO_phase 
    m.params['C_RO_Z'] = RO_Z 

    m.params['wait_times'] = (np.ones(m.params['pts'])*100e-6+30e-6) #Note: wait time must be atleast carbon init time +5us 
    m.params['sweep_pts']  = m.params['C_RO_phase'] - RO_phase # This needs to substracted for the data analysis. 

    # m.params['wait_times'] = np.linspace(130e-6, 150e-6,m.params['pts'])#Note: wait time must be atleast carbon init time +5us 
    # m.params['sweep_pts'] = m.params['wait_times']



    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to test
    
    m.params['C13_MBI_RO_duration']     = 30 
    m.params['E_C13_MBI_amplitude']     = 1e-9

    m.params['SP_duration_after_C13']   = 50
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    
    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    # Tomography 
    NuclearRamseyWithInitialization(SAMPLE,RO_phase = 0, RO_Z = False)
    NuclearRamseyWithInitialization(SAMPLE,RO_phase = 90, RO_Z = False)
    NuclearRamseyWithInitialization(SAMPLE,RO_phase = 0, RO_Z = True)


