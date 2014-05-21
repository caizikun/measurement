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

def NuclearRamsey_no_elDD(name,tau = None):

    m = DD.NuclearRamsey_no_elDD(name)
    funcs.prepare(m)

    '''set experimental parameters'''


    ### Sweep parameters
    m.params['wait_times'] = np.arange(3e-6,10e-3,.4e-3)

    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Ren_Decoupling_scheme'] = 'repeating_T_elt'
    m.params['Phases_of_Ren_B'] =np.ones(len(m.params['wait_times']))*0  #np.linspace(0,4*np.pi,41) #
    m.params['C1_freq'] =m.params['C1_freq']+.2e3 # Overwrites the msmst params. Usefull to calibrate and find the correct freq 
    
    tau_larmor = m.get_tau_larmor()
    m.params['Addressed_Carbon'] = 1 
 
    m.params['pts']              = len(m.params['Phases_of_Ren_B'])
    # m.params['sweep_pts']        =m.params['Phases_of_Ren_B']
    # m.params['sweep_name']       = 'Phase'
    m.params['sweep_pts']        = np.ones(len(m.params['wait_times'])) #NB! This value is overwritten in the measurement class when the sweep name is 'Free Evolution Time (s)' 
    m.params['sweep_name']       = 'Free Evolution time (s)' 


    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['min_dec_tau']         = 20e-9 + m.params['fast_pi_duration']/2.0
    m.params['max_dec_tau']         = 0.35e-6 #Based on simulation for fingerprint at low tau
    m.params['dec_pulse_multiple']  = 4 #lowest multiple of 4 pulses

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    NuclearRamsey_no_elDD(SAMPLE)

