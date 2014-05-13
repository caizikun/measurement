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

def CarbonGateSequence(name):

    m = DD.CarbonGateSequence(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    ### Sweep parmater
    m.params['free_evolution_times'] = np.concatenate([np.array([0]),np.linspace(1e3,20e3,40).astype(int)*1e-9])
    print m.params['free_evolution_times']
    m.params['pts']              = len(m.params['free_evolution_times'])
    m.params['sweep_pts']        =m.params['free_evolution_times']*1e6
    m.params['sweep_name']       = 'Free evolution time (us)'


    m.autoconfig()
    funcs.finish(m, upload =True, debug=True)



# if __name__ == '__main__':
#     Carbon_Ramsey(SAMPLE)

if __name__ == '__main__':
    CarbonGateSequence(SAMPLE)
    # print 'press q now to cleanly exit this measurement loop'
    # qt.msleep(5)
    # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #     break

