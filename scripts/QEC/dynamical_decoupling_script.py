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

def SimpleDecoupling(name):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 300 #Repetitions of each data point
    #m.params['sequence_wait_time'] = 0    #Set sequence wait time for AWG triggering

    pts = 8
    m.params['pts'] = pts#len(m.params['sweep_pts'])

    m.params['Initial_Pulse'] ='pi/2'
    m.params['Final_Pulse'] ='pi/2'

    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])/m.params['g_factor']*1.07e3
    tau_larmor = 1/f_larmor
    print 'tau_larmor = %s' %tau_larmor
    tau_larmor = 2.964e-6  #Dirty fix for length of string being to long in AWG

    tau_list = np.linspace(tau_larmor,pts*tau_larmor,pts)
    m.params['Number_of_pulses'] = 32*np.ones(pts).astype(int)

    tau_list = np.ones(pts)*tau_larmor# np.linspace(tau_larmor,pts*tau_larmor,pts)
    m.params['Number_of_pulses'] =  [4,8,16,32,64,128,256,512] #32*np.ones(pts).astype(int)
    #######

    m.params['sweep_name'] = 'Numberof pulses'#total evolution time (us)'
    m.params['sweep_pts']  = ['4','8','16','32','64','128','256','512'] #2*m.params['Number_of_pulses'][0]*tau_list*1e6 # m.params['tau_list']*1e6

    m.autoconfig()

    m.params['sequence_wait_time'] =  (tau_larmor*4*pts)*1e6+20
    m.params['tau_list'] = tau_list

    funcs.finish(m, debug=False)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_'+'')


