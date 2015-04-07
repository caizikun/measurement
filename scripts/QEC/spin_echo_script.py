"""
Made by Adriaan Rol
spin echo measurement script based on the SimpleDecoupling measurement class
"""
import numpy as np
import qt
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def spin_echo(name):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)
    #############
    # Parameters for spin-echo
    #############
    pts = 21
    tau_start = 8e-6  #!!! Measurement class has minimal tau of 4us
    tau_final = 2.5e-3
    m.params['reps_per_ROsequence'] = 400 #Repetitions of each data point


    ########
    # parameters specific for spin -echo
    ###########
    Number_of_pulses = 1
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='x'
    m.params['Decoupling_sequence_scheme']='repeating_T_elt'
    #####
    #Calculate/set remaining paramters
    tau_list = np.linspace(tau_start/2.0,tau_final/2.0 ,pts) #The way tau is defined is different in hahn spin-echo and decoupling experiments
    m.params['pts'] = pts
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(pts).astype(int)
    m.params['tau_list'] = tau_list
    m.params['sweep_pts'] =  2*Number_of_pulses*tau_list*1e6
    m.params['sweep_name'] = '2*N*tau (us)'
    m.autoconfig()

    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    spin_echo(SAMPLE+'_spin_echo_'+'N=1')


