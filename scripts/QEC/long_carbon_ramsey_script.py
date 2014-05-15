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

def Long_Carbon_Ramsey(name,tau = None):

    m = DD.LongNuclearRamsey(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Ren_Decoupling_scheme'] = 'repeating_T_elt'

    ### Sweep parmater

    m.params['N_list'] = range(0,129,4)# np.ones(len(m.params['Phases_of_Ren_B']))*4 #
    m.params['Phases_of_Ren_B'] =np.ones(len(m.params['N_list']))*0  #np.linspace(0,4*np.pi,41) #


    m.params['C1_freq'] =345.2e3-2e3 # Overwrites the msmst params. Usefull to calibrate and find the correct freq

    tau_larmor = m.get_tau_larmor()
    m.params['tau_list']           = np.ones(len(m.params['N_list']) )*tau_larmor
    m.params['Addressed_Carbon'] = 1


    m.params['pts']              = len(m.params['Phases_of_Ren_B'])
    # m.params['sweep_pts']        =m.params['Phases_of_Ren_B']
    # m.params['sweep_name']       = 'Phase'
    m.params['sweep_pts']      = np.ones(len(m.params['N_list'])) #NB! This value is overwritten in the measurement class when the sweep name is 'Free Evolution Time (s)'
    m.params['sweep_name'] = 'Free Evolution time (s)'


    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['min_dec_tau'] = 20e-9 + m.params['fast_pi_duration']/2.0
    m.params['max_dec_tau'] = 0.35e-6 #Based on simulation for fingerprint at low tau
    m.params['dec_pulse_multiple'] = 4#lowest multiple of 4 pulses



    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    Long_Carbon_Ramsey(SAMPLE)

