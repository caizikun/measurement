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

    m = DD.SimpleDecoupling(name)
    """
    ##### MODIFICATION FOR LT1 ######
    """
    # m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    # m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    # # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO+MBI'])
    # m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    # m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    # m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    # Default values when no MBI
    if mbi == False:
        m.params['MBI_threshold'] = 0
        m.params['Ex_SP_amplitude'] = 0
        m.params['Ex_MBI_amplitude'] = 0
        m.params['SP_E_duration'] = 20 #2000
        
        m.params['repump_after_MBI_A_amplitude'] = [15e-9]
        m.params['repump_after_MBI_duration'] = [300] # 50  
    """
    END MODIFICATIONS FOR LT1
    """

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
    m.params['Final_Pulse'] ='x'
    #Method to construct the sequence
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'
    #m.params['Decoupling_sequence_scheme'] = 'single_block'

    m.params['pts'] = pts
    m.params['tau_list'] = tau_list
    m.params['Number_of_pulses'] = Number_of_pulses
    m.params['sweep_pts'] = Number_of_pulses
    print m.params['sweep_pts']
    m.params['sweep_name'] = 'Number of pulses'

    m.autoconfig()
    ### MODIFICATION FOR LT1 ###
    m.params['E_RO_durations'] = [m.params['SSRO_duration']]
    m.params['E_RO_amplitudes'] = [m.params['Ex_RO_amplitude']]
    ### END MODIFICATION FOR LT1 ###

    funcs.finish(m, upload =True, debug=False)

def interrupt_script(wait = 5):
    print 'press q now to exit measurement script'
    qt.msleep(wait)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
        sys.exit()

if __name__ == '__main__':
    tau_ctr = 39.472e-6
    #tau_ctr = 65.836e-6
    #tau_ctr=26.75e-6
    #tau_ctr=53.154
    NoP1=np.arange(100,160,20)
    idx=0
    t=tau_ctr
    SimpleDecoupling_swp_N(SAMPLE+'sweep_N_larm_tauidx_'+str(idx)+'_',NoP=NoP1,tau =t, reps_per_ROsequence = 750)
    '''
    tau_array = tau_ctr+np.linspace(-.048e-6,.048e-6,9)
    for idx,t in enumerate(tau_array):
        #2.370304e-3/(16*2) # tau_L nr 32 dip in N=16
        
        SimpleDecoupling_swp_N(SAMPLE+'sweep_N_tauidx_'+str(idx),NoP=NoP1,tau =t, reps_per_ROsequence = 750)
        interrupt_script()
        #print 'start counters in script'
        #qt.instruments[counters].set_is_running(True)
    '''
    
    '''
    NoP1=np.arange(4,124,4)
    NoP2=np.arange(124,194,4)
    NoP3=np.arange(194,254,4)
    SimpleDecoupling_swp_N(SAMPLE+'sweep_N'+'_part1',NoP=NoP1,tau =tau, reps_per_ROsequence = 500)
    SimpleDecoupling_swp_N(SAMPLE+'sweep_N'+'_part2',NoP=NoP2,tau =tau, reps_per_ROsequence = 500)
    SimpleDecoupling_swp_N(SAMPLE+'sweep_N'+'_part3',NoP=NoP3,tau =tau, reps_per_ROsequence = 500)
    '''