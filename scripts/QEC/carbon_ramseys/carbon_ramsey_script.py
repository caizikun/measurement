"""
Script for basic carbon ramsey sequence
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

def Carbon_Ramsey(name,tau = None,N=None):

    m = DD.NuclearRamsey(name)
    #m = DD.NuclearRamsey_v2(name)
    # m = DD.NuclearRamsey_no_elDD(name)

    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] =   500 #Repetitions of each data point
    m.params['Initial_Pulse']       =   'x'
    m.params['Final_Pulse']         =   '-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['addressed_carbon'] = 4 

    ### Sweep parmater
    m.params['free_evolution_times']    = np.concatenate([np.array([0]),np.linspace(1e3,20e3,41).astype(int)*1e-9])
    m.params['pts']                     = len(m.params['free_evolution_times'])
    m.params['sweep_pts']               = m.params['free_evolution_times']
    m.params['sweep_name']              = 'Free evolution time'

    print 'free evolution times: %s' %m.params['free_evolution_times']
    
    if N ==None: 
        m.params['C_Ren_N'] = m.params['C4_Ren_N'][0]  
    else:
        m.params['C_Ren_N'] = N
    if tau ==None: 
        m.params['C_Ren_tau'] = m.params['C4_Ren_tau'][0]
    else: 
        m.params['C_Ren_tau'] = tau 

    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['min_dec_tau'] = 20e-9 + m.params['fast_pi_duration']/2.0
    m.params['max_dec_tau'] = 0.35e-6 #Based on measurement for fingerprint at low tau
    m.params['dec_pulse_multiple'] = 4#lowest multiple of 4 pulses

    m.autoconfig()
    funcs.finish(m, upload =True, debug=True)
    print m.params['sweep_pts'] 

if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE)
