"""
Script for a carbon Rabi sequence
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

def NuclearRabiWithInitialization(name,tau = None):

    m = DD.NuclearRabiWithInitialization(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 31 

    m.params['Addressed_Carbon'] = 1



    m.params['sweep_name'] = 'Number of pulses'

    m.params['Rabi_N_Sweep']= np.arange(4,10000,4)[0: m.params['pts']]
    print m.params['Rabi_N_Sweep']
    m.params['sweep_pts']        = m.params['Rabi_N_Sweep']



    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to make the script always work 
    m.params['C13_MBI_threshold']       = 1
    m.params['MBI_threshold'] = 1

    m.params['C13_MBI_RO_duration']     = 30 
    m.params['SP_duration_after_C13']   = 10

    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 
    m.params['E_C13_MBI_amplitude']           = 1e-9

    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    NuclearRabiWithInitialization(SAMPLE)

