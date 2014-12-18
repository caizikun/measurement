"""
Script for a carbon Rabi sequence
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

def Crosstalk(name, RO_phase=0, RO_Z=False, C13_init_method = 'swap', carbon_A = 1, carbon_B = 5,  
    N = np.arange(4,100,8), tau_list= None):

    m = DD.Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_A'] = carbon_A    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B'] = carbon_B    ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = 3000 
    m.params['C13_init_state']      = 'up' 
    m.params['C13_init_method']     = C13_init_method
    m.params['sweep_name']          = 'Number of pulses'
    m.params['C_RO_phase']          = RO_phase 
    m.params['C_RO_Z']              = RO_Z 

#     ### Sweep parameters
    m.params['Rabi_N_Sweep']= [0] + N
    
    if tau_list == None:
        tau_list = m.params['C'+str(carbon_B)+'_Ren_tau']*len(N)
    
    m.params['Rabi_tau_Sweep']= m.params['C'+str(carbon_B)+'_Ren_tau'] +  tau_list

    m.params['pts'] = len(m.params['Rabi_N_Sweep']) 

    x_tick_labels = []
    for i in range(len(tau_list)):
        x_tick_labels = x_tick_labels + [str(tau_list[i]*1e6) + ', ' + str(N_list[i])]

    m.params['sweep_pts'] = x_tick_labels

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0 
    
    funcs.finish(m, upload =True, debug=False)

def Optimizor():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(4)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        n=0
    else:
        n=1
    GreenAOM.set_power(5e-6)
    ins_counters.set_is_running(0)  
    optimiz0r.optimize(dims=['x','y','z'])

    # ssrocalibration(SAMPLE_CFG)

    return n

if __name__ == '__main__':

    n = 1
    n = Optimizor()
  

    ### 5 to 2
    if n==1:

        tau_list = [qt.exp_params['samples']['111_1_sil18']['C5_gate_optimize_tau_list'][i] for i in [4,6,7]]
        N_list   = [qt.exp_params['samples']['111_1_sil18']['C5_gate_optimize_N_list'][i] for i in [4,6,7]]


        tau_list = 
        N_list   = 

        Crosstalk(SAMPLE + '_5to2_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 2, carbon_B = 5, tau_list=tau_list, N = N_list)
        Crosstalk(SAMPLE + '_5to2_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 2, carbon_B = 5, tau_list=tau_list, N = N_list)
        # Crosstalk(SAMPLE + '_5to2_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 2, carbon_B = 5, tau_list=tau_list, N = N_list)
      
        n = Optimizor()

    ### 5 to 1
    if n==1:

        Crosstalk(SAMPLE + '_5to1_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 1, carbon_B = 5, tau_list=tau_list, N = N_list)
        Crosstalk(SAMPLE + '_5to1_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 1, carbon_B = 5, tau_list=tau_list, N = N_list)
        # Crosstalk(SAMPLE + '_5to1_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 1, carbon_B = 5, tau_list=tau_list, N = N_list)
      
        n = Optimizor()

    
    # ### 2 to 5
    # if n==1:

    #     tau_list = [qt.exp_params['samples']['111_1_sil18']['C2_gate_optimize_tau_list'][i] for i in [1,3,4]]
    #     N_list   = [qt.exp_params['samples']['111_1_sil18']['C2_gate_optimize_N_list'][i] for i in [1,3,4]]


    #     Crosstalk(SAMPLE + '_2to5_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 5, carbon_B = 2, tau_list = tau_list, N = N_list)
    #     Crosstalk(SAMPLE + '_2to5_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 5, carbon_B = 2, tau_list = tau_list, N = N_list)
    #     # Crosstalk(SAMPLE + '_2to5_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 5, carbon_B = 2, tau_list = tau_list, N = N_list)

    #     # n = Optimizor()

        ### 2 to 1
    # if n==1:

    #     Crosstalk(SAMPLE + '_2to1_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 1, carbon_B = 2, tau_list = tau_list, N = N_list)
    #     Crosstalk(SAMPLE + '_2to1_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 1, carbon_B = 2, tau_list = tau_list, N = N_list)
    #     # Crosstalk(SAMPLE + '_2to1_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 1, carbon_B = 2, tau_list = tau_list, N = N_list)

    #     n = Optimizor()



    # ### 1 to 2
    # if n==1:

    #     tau_list = [qt.exp_params['samples']['111_1_sil18']['C1_gate_optimize_tau_list'][i] for i in [1,5,7]]
    #     N_list   = [qt.exp_params['samples']['111_1_sil18']['C1_gate_optimize_N_list'][i] for i in [1,5,7]]

    #     Crosstalk(SAMPLE + '_1to2_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 2, carbon_B = 1, tau_list=tau_list, N = N_list)
    #     Crosstalk(SAMPLE + '_1to2_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 2, carbon_B = 1, tau_list=tau_list, N = N_list)
    #     # Crosstalk(SAMPLE + '_1to2_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 2, carbon_B = 1, tau_list=tau_list, N = N_list)
        
    #     n = Optimizor()

    # ### 1 to 5
    # if n==1:

    #     Crosstalk(SAMPLE + '_1to5_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 5, carbon_B = 1, tau_list=tau_list, N = N_list)
    #     Crosstalk(SAMPLE + '_1to5_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 5, carbon_B = 1, tau_list=tau_list, N = N_list)
    #     # Crosstalk(SAMPLE + '_1to5_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 5, carbon_B = 1, tau_list=tau_list, N = N_list)

    ''' Full set'''
    '''
    ### 2 to 5
    if n==1:
        Crosstalk(SAMPLE + '_2to5_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 5, carbon_B = 2, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_2to5_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 5, carbon_B = 2, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_2to5_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 5, carbon_B = 2, N = np.arange(4,130,8))

        # n = Optimizor()

    ### 2 to 1
    if n==1:
        Crosstalk(SAMPLE + '_2to1_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 1, carbon_B = 2, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_2to1_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 1, carbon_B = 2, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_2to1_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 1, carbon_B = 2, N = np.arange(4,130,8))

        n = Optimizor()

    ### 5 to 2
    if n==1:
        Crosstalk(SAMPLE + '_5to2_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 2, carbon_B = 5, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_5to2_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 2, carbon_B = 5, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_5to2_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 2, carbon_B = 5, N = np.arange(4,130,8))
      
        n = Optimizor()

    ### 5 to 1
    if n==1:
        Crosstalk(SAMPLE + '_5to1_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 1, carbon_B = 5, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_5to1_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 1, carbon_B = 5, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_5to1_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 1, carbon_B = 5, N = np.arange(4,130,8))
      
        n = Optimizor()

    ### 1 to 2
    if n==1:
        Crosstalk(SAMPLE + '_1to2_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 2, carbon_B = 1, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_1to2_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 2, carbon_B = 1, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_1to2_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 2, carbon_B = 1, N = np.arange(4,130,8))
        
        n = Optimizor()

    ### 1 to 5
    if n==1:
        Crosstalk(SAMPLE + '_1to5_RO_X',RO_phase = 0, RO_Z = False, carbon_A = 5, carbon_B = 1, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_1to5_RO_Y',RO_phase = 90, RO_Z = False, carbon_A = 5, carbon_B = 1, N = np.arange(4,160,8))
        Crosstalk(SAMPLE + '_1to5_RO_Z',RO_phase = 90, RO_Z = True, carbon_A = 5, carbon_B = 1, N = np.arange(4,130,8))
    '''


    







