"""
Made by Adriaan Rol
fingerprint measurement script based on the SimpleDecoupling measurement class
"""
import numpy as np
import qt
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def fingerprint(name):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)
    #############
    # Parameters for Fingerprint
    #############
    pts = 201
    tau_start = 2e-6  #!!! Measurement class has minimal tau of 4us
    tau_final = 4e-6
    m.params['reps_per_ROsequence'] = 200 #Repetitions of each data point


    ########
    # parameters specific for fingerprint
    ###########
    Number_of_pulses = 32
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    #####
    #Calculate/set remaining paramters
    tau_list = np.linspace(tau_start,tau_final,pts)
    m.params['pts'] = pts
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(pts).astype(int)
    m.params['tau_list'] = tau_list
    m.params['sweep_pts'] =  2*tau_list*1e6
    m.params['sweep_name'] = '2*tau (us)'
    m.autoconfig()

    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    fingerprint(SAMPLE+'_fingerprint_'+'N32')


