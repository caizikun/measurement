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

def SimpleDecoupling(name, sweep = 'N',N=4):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] =500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    ### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor


    if sweep == 'N':
        Number_of_pulses=[50,500,3400]
        #Number_of_pulses = linspace(2,3003,500).astype(int)

        pts = len(Number_of_pulses)
        m.params['pts'] = pts
        tau_list = np.ones(pts)*tau_larmor
        m.params['tau_list'] = tau_list
        m.params['Number_of_pulses'] = Number_of_pulses
        m.params['sweep_pts'] = [x*tau_larmor*2e3 for x in Number_of_pulses]
        m.params['sweep_name'] = 'decoupling time (ms)'
        m.params['Decoupling_sequence_scheme']='repeating_T_elt'

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
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astydpe(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e6
        print m.params['sweep_pts']
        m.params['sweep_name']       = 'total evolution time (us)'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

    if sweep == 'short_times':

        pts = 50
        Number_of_pulses = N #256
        # nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        tau_list = np.arange(3.8e-6,4.e-6,10e-9)

        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  [x*1e6 for x in tau_list]
        m.params['sweep_name']       = 'tau (us)'
        m.params['Decoupling_sequence_scheme']='single_block'


        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

    if sweep == 'N_in_eigenstate':
        #Made by MAB to measure decay due pulse errors for large N
        
        tau = 2e-6
        print m.params['fast_pi_duration']
        print m.params['fast_pi_duration']*10 

        Number_of_pulses = np.arange(25)*160

        # Number_of_pulses = np.arange(3)*8

        # Number_of_pulses = np.arange(20)*3*32e1
        
        m.params['pts']              = len(Number_of_pulses)
        m.params['fast_pi2_amp'] = 0.
        m.params['DD_in_eigenstate'] = True
        m.params['tau_list']         = tau*np.ones(m.params['pts'])
        m.params['Number_of_pulses'] = Number_of_pulses.astype(int)
        m.params['sweep_pts']        = Number_of_pulses.astype(int)
        m.params['sweep_name']       = 'Number of Pulses'
        m.params['Decoupling_sequence_scheme']='single_block'
        # m.params['fast_pi2_duration'] = 0.

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

def SimpleDecoupling2(name, sweep = 'N',N=4):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] =200 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    ### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor


    if sweep == 'N':
        Number_of_pulses=[50,500,3400]
        #Number_of_pulses = linspace(2,3003,500).astype(int)

        pts = len(Number_of_pulses)
        m.params['pts'] = pts
        tau_list = np.ones(pts)*tau_larmor
        m.params['tau_list'] = tau_list
        m.params['Number_of_pulses'] = Number_of_pulses
        m.params['sweep_pts'] = [x*tau_larmor*2e3 for x in Number_of_pulses]
        m.params['sweep_name'] = 'decoupling time (ms)'
        m.params['Decoupling_sequence_scheme']='repeating_T_elt'

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
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astydpe(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e6
        print m.params['sweep_pts']
        m.params['sweep_name']       = 'total evolution time (us)'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

    if sweep == 'short_times':

        pts = 50
        Number_of_pulses = N #256
        # nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        tau_list = np.arange(3.8e-6,4.e-6,10e-9)

        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  [x*1e6 for x in tau_list]
        m.params['sweep_name']       = 'tau (us)'
        m.params['Decoupling_sequence_scheme']='single_block'


        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

    if sweep == 'N_in_eigenstate':
        #Made by MAB to measure decay due pulse errors for large N
        
        tau = 2e-6
        print m.params['fast_pi_duration']
        print m.params['fast_pi_duration']*10 

        Number_of_pulses = np.arange(25)*160

        # Number_of_pulses = np.arange(3)*8

        # Number_of_pulses = np.arange(20)*3*32e1
        
        m.params['pts']              = len(Number_of_pulses)
        m.params['fast_pi2_amp'] = 0.
        m.params['fast_pi_amp'] = 0.
        m.params['DD_in_eigenstate'] = True
        m.params['tau_list']         = tau*np.ones(m.params['pts'])
        m.params['Number_of_pulses'] = Number_of_pulses.astype(int)
        m.params['sweep_pts']        = Number_of_pulses.astype(int)
        m.params['sweep_name']       = 'Number of Pulses'
        m.params['Decoupling_sequence_scheme']='single_block'
        # m.params['fast_pi2_duration'] = 0.

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    # N=2
    # SimpleDecoupling(SAMPLE+'sweep_short_tau_N_'+str(N),sweep='short_times',N=N)
    
    # N=32
    # SimpleDecoupling(SAMPLE+'sweep_short_tau_N_'+str(N),sweep='short_times',N=N)
    # N=16
    # SimpleDecoupling(SAMPLE+'sweep_short_tau_N_'+str(N),sweep='short_times',N=N)

    # N=8
    # SimpleDecoupling(SAMPLE+'sweep_short_tau_N_'+str(N),sweep='short_times',N=N)

    # N=4
    # SimpleDecoupling(SAMPLE+'sweep_short_tau_N_'+str(N),sweep='short_times',N=N)

    SimpleDecoupling(SAMPLE+'DD_in_eigenstate_W',sweep='N_in_eigenstate')
    SimpleDecoupling2(SAMPLE+'DD_in_eigenstate_T1_',sweep='N_in_eigenstate')
