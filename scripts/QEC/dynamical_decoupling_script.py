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

def SimpleDecoupling(name, sweep = 'N'):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 1000 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    ### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    tau_larmor =3.071e-6
    print tau_larmor
    print 'tau_larmor = %s' %tau_larmor


    if sweep == 'N':
        Number_of_pulses = linspace(2,100,50).astype(int)

        pts = len(Number_of_pulses)
        m.params['pts'] = pts
        tau_list = np.ones(pts)*tau_larmor
        m.params['tau_list'] = tau_list
        m.params['Number_of_pulses'] = Number_of_pulses
        m.params['sweep_pts'] = Number_of_pulses
        m.params['sweep_name'] = 'Number of pulses'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

    if sweep == 'tau':

        pts = 4
        Number_of_pulses = 1024 #256
        start   = 75e-3 + tau_larmor*(2*Number_of_pulses)
        end     = 100e-3
        nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        tau_list = nr_list*tau_larmor

        print nr_list
        print tau_list

        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e6
        print m.params['sweep_pts']
        m.params['sweep_name']       = 'total evolution time (us)'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_N16_zoom')


