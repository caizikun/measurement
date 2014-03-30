"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.pulsar.DynamicalDecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling(name):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
        #Repetitions of each data
    m.params['reps_per_ROsequence'] = 300
        #Set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0

    #######
    pts = 11
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])/m.params['g_factor']*1.07e3
    tau_larmor = 1/f_larmor
    print 'tau_larmor = %s' %tau_larmor
    tau_larmor = 2.999e-6  #Dirty fix for length of string being to long in AWG
    tau_list = np.linspace(tau_larmor,pts*tau_larmor,pts)
    # tau_list =np.linspace(5e-7,50e-7,pts)

    #######

    m.params['pts'] = pts#len(m.params['sweep_pts'])
    m.params['sweep_name'] = 'tau (us)'
    m.params['sweep_pts'] =tau_list*1e6 # m.params['tau_list']*1e6  #np.linspace(1,10,10)#

    m.autoconfig()

    m.params['sequence_wait_time'] =  (tau_larmor*4*pts)*1e6+20
    #Decoupling specific parameters
    m.params['Number_of_pulses'] = 4
    m.params['tau_list'] = tau_list #Larmor period for B =314G
    m.params['Initial_Pulse'] ='pi/2'
    m.params['Final_Pulse'] ='pi/2'

    funcs.finish(m, debug=True)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_'+'')


