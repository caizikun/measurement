"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
#import measurement.lib.pulsar.DynamicalDecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling(name):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 1000
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'


    Number_of_pulses = np.append(-1,np.linspace(2,32,16).astype(int))
    #Number_of_pulses = np.linspace(8,32,4).astype(int)

    pts = len(Number_of_pulses)
    tau_list = np.ones(pts)*qt.exp_params['samples'][SAMPLE]['C1_Ren_tau']
    print 'tau_list =' + str(tau_list)



    m.params['pts'] = pts
    m.params['tau_list'] = tau_list
    m.params['Number_of_pulses'] = Number_of_pulses
    m.params['sweep_pts'] = Number_of_pulses
    print m.params['sweep_pts']
    m.params['sweep_name'] = 'Number of pulses'

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_C3_sweep_N')


