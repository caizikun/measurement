"""
Script for basic carbon ramsey sequence
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

def Carbon_Ramsey(name,tau = None,N=None):

    #m = DD.NuclearRamsey(name)
    m = DD.NuclearRamsey_v2(name)
    #m = DD.NuclearRamsey_no_elDD(name)

    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] =   2500 #Repetitions of each data point
    m.params['Initial_Pulse']       =   'x'
    m.params['Final_Pulse']         =   '-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['addressed_carbon'] = 1 

    ### Sweep parmater
    m.params['free_evolution_times']    = (np.concatenate([np.linspace(1e3,7.5e3,25).astype(int)*1e-9, 
                                                           np.linspace(15e3,22e3,25).astype(int)*1e-9]))

    m.params['free_evolution_times']    = np.linspace(10e3,1000e3,30).astype(int)*1e-9

    m.params['pts']                     = len(m.params['free_evolution_times'])
    m.params['sweep_pts']               = m.params['free_evolution_times']
    m.params['sweep_name']              = 'Free evolution time'

    print 'free evolution times: %s' %m.params['free_evolution_times']
    
    if N ==None: 
        m.params['C_Ren_N'] = m.params['C'+str(m.params['addressed_carbon'])+'_Ren_N'][0]  
    else:
        m.params['C_Ren_N'] = N
    if tau ==None: 
        m.params['C_Ren_tau'] = m.params['C'+str(m.params['addressed_carbon'])+'_Ren_tau'][0]
    else: 
        m.params['C_Ren_tau'] = tau 

    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['min_dec_tau'] = 20e-9 + m.params['fast_pi_duration']/2.0
    m.params['max_dec_tau'] = 0.35e-6 #0.35e-6 #Based on measurement for fingerprint at low tau
    m.params['dec_pulse_multiple'] = 4#lowest multiple of 4 pulses

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)
    print m.params['sweep_pts'] 

if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE,N=16,tau=6.6625e-6)
