"""
Script for basic carbon ramsey sequence
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Carbon_Ramsey(name,tau = None,N=None):

    # m = DD.NuclearRamsey(name)
    # m = DD.NuclearRamsey_v2(name)
    m = DD.NuclearRamsey_no_elDD(name)

    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] =   200 #Repetitions of each data point
    m.params['Initial_Pulse']       =   'x'
    m.params['Final_Pulse']         =   '-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['addressed_carbon'] = 3
    carbon_str = str(m.params['addressed_carbon'])
    ### Sweep paramater
    # m.params['free_evolution_times']    = (np.concatenate([np.linspace(1e3,7.5e3,25).astype(int)*1e-9, 
    #                                                        np.linspace(15e3,22e3,25).astype(int)*1e-9]))

    m.params['free_evolution_times']    = np.linspace(10e3,20e3,22).astype(int)*1e-9

    m.params['pts']                     = len(m.params['free_evolution_times'])
    m.params['sweep_pts']               = m.params['free_evolution_times']
    m.params['sweep_name']              = 'Free evolution time (us)'

    print 'free evolution times: %s' %m.params['free_evolution_times']
    
    if N ==None: 
        m.params['C'+carbon_str+'_Ren_N'+m.params['electron_transition']] = m.params['C'+carbon_str+'_Ren_N'+m.params['electron_transition']] 
    else:
        m.params['C'+carbon_str+'_Ren_N'+m.params['electron_transition']] = N
    if tau ==None: 
        m.params['C'+carbon_str+'_Ren_tau'+m.params['electron_transition']] = m.params['C'+carbon_str+'_Ren_tau'+m.params['electron_transition']]
    else: 
        print tau
        m.params['C'+carbon_str+'_Ren_tau'+m.params['electron_transition']] = tau 


    funcs.finish(m, upload =True, debug=False)


if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE_CFG)#,tau=6.35e-6,N=26)
