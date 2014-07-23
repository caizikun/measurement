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

def NuclearRamseyWithInitialization(name, state = 'up', 
            tau = None, RO_phase=0, RO_Z=False, N = None, method = 'swap' ):

    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)

    '''set experimental parameters'''
   

    ### Initialize:
    m.params['Addressed_Carbon']    = 1
    m.params['C_init_method']       = 'MBI'         #'MBI'->X, 'swap'-> 0 
    m.params['C13_MBI_threshold']   = 1 
    m.params['C13_init_state']      = state         # 'up' or 'down'
    m.params['electron_init_state'] = '0'           # '0' or '1'

    ### Sweep parameters
    detuning_ms0                    = None
    detuning_ms1                    = None
    m.params['reps_per_ROsequence'] = 500 
    m.params['pts']                 = 25 
    
    ### sweeping the readout phase
    # m.params['C_RO_phase']  = RO_phase + np.linspace(0,420,m.params['pts'])  
    # m.params['C_RO_Z']      = RO_Z 
    # m.params['wait_times']  = (np.ones(m.params['pts'])*100e-6+30e-6) #Note: wait time must be atleast carbon init time +5us 
    # m.params['sweep_pts']   = m.params['C_RO_phase'] - RO_phase       #This needs to substracted for the data analysis. 
    # m.params['sweep_name']  = 'C_RO_phase' 

    ### sweeping the waittime
    m.params['wait_times']  = np.linspace(130e-6, 130e-6 + 1e-3,m.params['pts']) #Note: wait time must be atleast carbon init time +5us 
    m.params['C_RO_phase']  = np.ones(m.params['pts'])*RO_phase 
    m.params['C_RO_Z']      = RO_Z 
    m.params['sweep_pts']   = m.params['wait_times']
    m.params['sweep_name']  = 'evolution time' 

    ##
    if detuning_ms0 != None:
        m.params['C1_freq_0']   = m.params['C1_freq_0'] - detuning_ms0   
    if detuning_ms1 != None:
        m.params['C1_freq_1']   = m.params['C1_freq_1'] - detuning_ms1
    
    #### Overwrite certain params for quick tests ###
    m.params['C13_MBI_RO_duration']     = 20 
    m.params['E_C13_MBI_amplitude']     = 3e-9
    if N !=None:
        m.params['C1_Ren_N']=    [N      , 10]

    m.params['SP_duration_after_C13']           = 50
    m.params['A_SP_amplitude_after_C13_MBI']    = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']    = 0e-9 
    
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    
    # Tomography 
    NuclearRamseyWithInitialization(SAMPLE, state = 'up', RO_phase = 0, RO_Z = False)
    NuclearRamseyWithInitialization(SAMPLE, state = 'up', RO_phase = 90, RO_Z = False)
    NuclearRamseyWithInitialization(SAMPLE, state = 'up', RO_phase = 0, RO_Z = True)

