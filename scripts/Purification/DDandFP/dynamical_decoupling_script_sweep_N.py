"""
Script for a simple Decoupling sequence
Based on Electron T1 script
"""
import numpy as np
import qt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling_swp_N(name,tau=None, NoP=np.arange(4,254,4),reps_per_ROsequence=1000, mbi = True):

    m = DD.SimpleDecoupling(name+'_tau_'+str(tau*1e9))


    funcs.prepare(m)
    #input parameters
    m.params['reps_per_ROsequence'] = reps_per_ROsequence
    Number_of_pulses =NoP

    pts = len(Number_of_pulses)

    if tau == None: 
        tau = m.params['C3_Ren_tau'][0] 
    tau_list = tau*np.ones(pts)
    print 'tau_list =' + str(tau_list)

    #inital and final pulse
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x' 
    #Method to construct the sequence
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    m.params['pts'] = pts
    m.params['tau_list'] = tau_list
    m.params['Number_of_pulses'] = Number_of_pulses
    m.params['sweep_pts'] = Number_of_pulses
    print m.params['sweep_pts']
    m.params['sweep_name'] = 'Number of pulses'

    m.autoconfig()


    funcs.finish(m, upload =True, debug=False)

def interrupt_script(wait = 5):
    print 'press q now to exit measurement script'
    qt.msleep(wait)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
        sys.exit()

if __name__ == '__main__':

    tau = 4.818e-6 
    NoP1=np.arange(10,40,2)

    SimpleDecoupling_swp_N(SAMPLE+'_sweep_N',
        NoP=NoP1,
        tau =tau, 
        reps_per_ROsequence = 500)
