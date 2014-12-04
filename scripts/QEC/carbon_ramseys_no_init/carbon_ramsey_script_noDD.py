"""
Script for a carbon ramsey sequence, without electron DD during the waiting time.
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

def Carbon_Ramsey(name, tau = None, N=None):

    m = DD.NuclearRamsey_no_elDD(name)

    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse']       = 'x'
    m.params['Final_Pulse']         = '-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['addressed_carbon'] = 6

    ### Sweep parameter ###
    m.params['free_evolution_times'] = np.linspace(3.2e3,16e3,20).astype(int)*1e-9
    

    print 'free evolution times: %s' %m.params['free_evolution_times']
    m.params['pts']              = len(m.params['free_evolution_times'])
    m.params['sweep_pts']        = m.params['free_evolution_times']
    m.params['sweep_name']       = 'Free evolution time'


    # if N ==None: 
    #     m.params['C_Ren_N'] = m.params['C5_Ren_N'][0]  
    # else:
    #     m.params['C_Ren_N'] = N
    # if tau ==None: 
    #     m.params['C_Ren_tau'] = m.params['C5_Ren_tau'][0]
    # else: 
    #     m.params['C_Ren_tau'] = tau 

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)
    print m.params['sweep_pts'] 

if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE)

# if __name__ == '__main__':
#     tau_list = np.linspace(6.522e-6-20e-9,6.522e-6+20e-9,21)
#     for tau in tau_list:
#         print tau 
#         Carbon_Ramsey(SAMPLE+str(tau),tau, N=16)

#         print 'press q now to cleanly exit this measurement loop'
#         qt.msleep(5)
#         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
#             break

