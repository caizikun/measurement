"""
Made by Adriaan Rol
decoupling sweep N measurement script based on the SimpleDecoupling measurement class
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
    # Parameters for dd sweep N
    #############
    Number_of_pulses = [4,8,16,32,64,128,256,512,1024,2048]
    m.params['reps_per_ROsequence'] = 200 #Repetitions of each data point

    ########
    # parameters specific for dyn dec sweep N
    ###########
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    ##### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    print tau_larmor
    #tau_larmor = 2.981e-6
    tau_larmor =2.982e-6
    print 'tau_larmor = %s' %tau_larmor

    #####
    #Calculate/set remaining paramters
    pts = len(Number_of_pulses)
    m.params['pts'] = pts
    tau_list = np.ones(pts)*tau_larmor# np.linspace(tau_larmor,pts*tau_larmor,pts)
    m.params['tau_list'] = tau_list
    m.params['Number_of_pulses'] = Number_of_pulses
    m.params['sweep_pts'] = Number_of_pulses
    m.params['sweep_name'] = 'Number of pulses'

    m.autoconfig()

    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    spin_echo(SAMPLE+'_sweepN_'+'')


