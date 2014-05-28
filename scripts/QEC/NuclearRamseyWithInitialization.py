"""
Script for a carbon ramsey sequence
"""
import numpy as np
import qt
import msvcrt

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
    m.params['wait_times'] = np.arange(15e-6, 26e-6 ,5e-6)

    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Ren_Decoupling_scheme'] = 'auto' 
    m.params['Phases_of_Ren_B'] =np.ones(len(m.params['wait_times']))*0  #np.linspace(0,4*np.pi,41) #
    # m.params['C1_freq'] = m.params['C1_freq'] # +100e3 # Overwrites the msmst params. Usefull to calibrate and find the correct freq 
    
    m.params['Addressed_Carbon'] = 1
 
    m.params['pts']              = len(m.params['wait_times'])
    m.params['sweep_pts']        = np.ones(len(m.params['wait_times'])) #NB! This value is overwritten in the measurement class when the sweep name is 'Free Evolution Time (s)' 
    m.params['sweep_name']       = 'Free Evolution time (s)' 


    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['Carbon_init_RO_wait']   = 10e-6 # Should be sweeped for optimal in adwin 
    m.params['min_dec_tau']         = 20e-9 + m.params['fast_pi_duration']/2.0
    m.params['max_dec_tau']         = 0.35e-6 #Based on simulation for fingerprint at low tau

    m.params['dec_pulse_multiple']  = 4 #lowest multiple of 4 pulses



    ##########
    # Overwrite certain params to make the script always work 
    m.params['MBI_threshold']=0

    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    NuclearRamseyWithInitialization(SAMPLE)

