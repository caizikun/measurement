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

def SimpleDecoupling(name, sweep = 'tau'):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 200 #Repetitions of each data point

    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    ##### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    print tau_larmor
    #tau_larmor = 2.981e-6
    tau_larmor =2.982e-6
    print 'tau_larmor = %s' %tau_larmor

    if sweep == 'N':
        Number_of_pulses = [4,8,16,32,64,128,256,512]#,1024,2048]
        pts = len(Number_of_pulses)
        m.params['pts'] = pts
        tau_list = np.ones(pts)*tau_larmor# np.linspace(tau_larmor,pts*tau_larmor,pts)
        m.params['tau_list'] = tau_list
        m.params['Number_of_pulses'] = Number_of_pulses
        m.params['sweep_pts'] = Number_of_pulses
        m.params['sweep_name'] = 'Number of pulses'

    if sweep == 'tau':
        pts = 201
        Number_of_pulses = 16
        # tau_list = np.linspace(tau_larmor,10000/50/Number_of_pulses*pts*tau_larmor,pts)
        tau_list = np.linspace(2e-6, 4e-6,pts)
        m.params['pts'] = pts

        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(pts).astype(int)
        m.params['tau_list'] = tau_list
        m.params['sweep_pts'] =  2*Number_of_pulses*tau_list*1e6
        m.params['sweep_name'] = '2*N*tau (us)'

    m.autoconfig()


    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_N32'+'')


