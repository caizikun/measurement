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
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling(name):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    Number_of_pulses = 32 #256
    pts = 26 # 51
    #start   = 12.45e-6
    #end     = 12.55e-6
    #tau_list = np.linspace(start, end, pts)
    tau_list = np.array(range(15000,15500,10))*1e-9

    print tau_list

    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        = tau_list*1e6
    m.params['sweep_name']       = 'tau (us)'

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE)


