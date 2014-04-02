"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)
AWG.delete_all_waveforms_from_list()
import measurement.lib.pulsar.DynamicalDecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling(name, sweep = 'N'):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    pts = 6
    m.params['reps_per_ROsequence'] = 300 #Repetitions of each data point

    m.params['Initial_Pulse'] ='pi/2'
    m.params['Final_Pulse'] ='pi/2'
    m.params['pts'] = pts

    ##### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])/m.params['g_factor']*1.07e3
    tau_larmor = round(1/f_larmor,9) #rounds to ns
    print 'tau_larmor = %s' %tau_larmor

    if sweep == 'N':
        tau_list = np.ones(pts)*tau_larmor# np.linspace(tau_larmor,pts*tau_larmor,pts)
        Number_of_pulses = [4,8,16,32,64,128]

        m.params['tau_list'] = tau_list
        m.params['Number_of_pulses'] = Number_of_pulses
        m.params['sweep_pts'] = [str(n) for n in Number_of_pulses]
        m.params['sweep_name'] = 'Numberof pulses'

    if sweep == 'tau':
        tau_list = np.linspace(tau_larmor,pts*tau_larmor,pts)
        Number_of_pulses = 32
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(pts).astype(int)
        m.params['tau_list'] = tau_list
        m.params['sweep_pts'] = [str(tau) for tau in tau_list]
        m.params['sweep_name'] = 'tau (us)'

    m.autoconfig()

    m.params['sequence_wait_time'] =  (tau_larmor*4*pts)*1e6+20
    m.params['tau_list'] = tau_list

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_'+'')


