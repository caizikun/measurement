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

def Carbon_Ramsey(name,tau = None,N=None, carbon = 1, evolution_times = [],debug = False):

    m = DD.NuclearRamsey_v2(name)

    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] =   500 #Repetitions of each data point
    m.params['Initial_Pulse']       =   'x'
    m.params['Final_Pulse']         =   '-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['addressed_carbon'] = carbon 

    ### Sweep parmater
    m.params['free_evolution_times']    = evolution_times

    m.params['pts']                     = len(m.params['free_evolution_times'])
    m.params['sweep_pts']               = m.params['free_evolution_times']
    m.params['sweep_name']              = 'Free evolution time'

    print 'free evolution times: %s' %m.params['free_evolution_times']
    
    if N ==None: 
        m.params['C_Ren_N'+m.params['electron_transition']] = m.params['C'+str(m.params['addressed_carbon'])+'_Ren_N'+m.params['electron_transition']][0]  
    else:
        m.params['C_Ren_N'+m.params['electron_transition']] = N
    if tau ==None: 
        m.params['C_Ren_tau'+m.params['electron_transition']] = m.params['C'+str(m.params['addressed_carbon'])+'_Ren_tau'+m.params['electron_transition']][0]
    else: 
        m.params['C_Ren_tau'+m.params['electron_transition']] = tau 

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)
    print m.params['sweep_pts'] 

if __name__ == '__main__':

    evolution_times1 = np.linspace(2e3,5e3,20).astype(int)*1e-9
    evolution_times2 = np.linspace(10e3,13e3,20).astype(int)*1e-9
    evolution_times3 = np.linspace(18e3,21e3,20).astype(int)*1e-9

    # for decoupling on the larmor revival
    # evolution_times1 = np.linspace(15e3,20e3,20).astype(int)*1e-9
    # evolution_times2 = np.linspace(30e3,33e3,20).astype(int)*1e-9
    # evolution_times3 = np.linspace(38e3,41e3,20).astype(int)*1e-9

    for carbon in [1]:
        Carbon_Ramsey(SAMPLE + '_evo_times_1' + '_C' +str(carbon),tau = None, N=None, carbon = carbon, evolution_times = evolution_times1,debug = False)
        Carbon_Ramsey(SAMPLE + '_evo_times_2' + '_C' +str(carbon),tau = None, N=None, carbon = carbon, evolution_times = evolution_times2)
        Carbon_Ramsey(SAMPLE + '_evo_times_3' + '_C' +str(carbon),tau = None, N=None, carbon = carbon, evolution_times = evolution_times3)
