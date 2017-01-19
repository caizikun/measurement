"""
Script for a simple Decoupling sequence
Based on Electron T1 script
"""
import numpy as np
import qt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD
import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)
reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def SimpleDecoupling_swp_mw_amp(name,tau=None,N=None, mw_amps=np.arange(0.6,0.8,0.01),reps_per_ROsequence=1000, mbi = True):

    m = DD.SimpleDecoupling(name+'_tau_'+str(tau*1e9))


    funcs.prepare(m)
    #input parameters
    m.params['reps_per_ROsequence'] = reps_per_ROsequence

    pts = len(mw_amps)

    tau_list = tau*np.ones(pts)
    N_list = N*np.ones(pts)
        
    #inital and final pulse
    m.params['Initial_Pulse'] ='y'
    m.params['Final_Pulse'] ='-y' 
    #Method to construct the sequence
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt' # repeating_T_elt
    
    m.params['pts'] = pts
    m.params['tau_list'] = tau_list
    m.params['Number_of_pulses'] = N_list
    m.params['sweep_pts'] = mw_amps
    m.params['do_general_sweep'] = 1
    m.params['general_sweep_name'] = 'Hermite_pi_length'
    m.params['general_sweep_pts'] = mw_amps
    m.params['sweep_name'] = 'Hermite_pi_length'
    m.autoconfig()


    m.params['DD_in_eigenstate'] = False

    funcs.finish(m, upload =True, debug=False)

def interrupt_script(wait = 5):
    print 'press q now to exit measurement script'
    qt.msleep(wait)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
        sys.exit()

if __name__ == '__main__':

    tau = 3.17e-6 #6.406e-6 
    N = 100
    mw_amps=np.arange(70e-9,110e-9,5e-9)
    SimpleDecoupling_swp_mw_amp(SAMPLE+'_sweep_N',
        mw_amps=mw_amps,
        tau =tau, 
        N = N,
        reps_per_ROsequence = 500)
