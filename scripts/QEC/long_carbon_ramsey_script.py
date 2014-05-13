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

def Carbon_Ramsey(name,tau = None):

    m = DD.LongNuclearRamsey(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    ### Sweep parmater

    m.params['N_list'] = range(0,36,4)
    m.params['pts']              = len(m.params['N_list'])
    m.params['sweep_pts']        =m.params['N_list']
    m.params['sweep_name']       = 'Number of pulses'

    m.params['Addressed_Carbon'] = 1 


    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['min_dec_tau'] = 20e-9 + m.params['fast_pi_duration']/2.0
    m.params['max_dec_tau'] = 0.35e-6 #Based on simulation for fingerprint at low tau
    m.params['dec_pulse_multiple'] = 4#lowest multiple of 4 pulses



    m.autoconfig()
    funcs.finish(m, upload =True, debug=True)

if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE)

