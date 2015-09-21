"""
Script for a simple Decoupling sequence
Based on Electron T1 script
"""
import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

reload(DD)

ins_counters = qt.instruments['counters']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

carbons = [2,5]

def SimpleDecoupling_swp_N(name,tau=None, Number_of_pulses=np.arange(80,100,2), 
            Final_Pulse='x', Initial_Pulse ='x', reps_per_ROsequence=1000):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    #input parameters
    m.params['reps_per_ROsequence'] = reps_per_ROsequence
    pts = len(Number_of_pulses)

    if tau == None: 
        tau = m.params['C3_Ren_tau'+m.params['electron_transition']][0] 
    tau_list = tau*np.ones(pts)
    print 'tau_list =' + str(tau_list)

    #inital and final pulse
    m.params['Initial_Pulse'] =Initial_Pulse
    m.params['Final_Pulse'] = Final_Pulse
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

def XY_initialization(name, carbon_list = [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['MBI'], 
        carbon_init_thresholds  =   [1],  

        tau = 1e-6,
        N  = 32,

        el_RO               = 'positive',
        debug               = False):

    m = DD.Two_QB_Probabilistic_MBE_v3(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds
    m.params['el_after_init'] = '0'

    if len(carbon_list) > 1:
        raise Exception('More than one carbon used, see syntax')
    else:
        m.params['C'+str(carbon_list[0])+'_Ren_tau'+m.params['electron_transition']]  = [tau]
        m.params['C'+str(carbon_list[0])+'_Ren_N'+m.params['electron_transition']]    = [N]

    # m.params['C1_Ren_tau']  = [tau]
    # m.params['C1_Ren_N']    = [N]

    # m.params['C2_Ren_tau']  = [tau]
    # m.params['C2_Ren_N']    = [N]

    # m.params['C3_Ren_tau']  = [tau]
    # m.params['C3_Ren_N']    = [N]

    # m.params['C5_Ren_tau']  = [tau]
    # m.params['C5_Ren_N']    = [N]

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 1000

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings
    m.params['carbon_init_list']    = carbon_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = 1

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['Tomography Bases'] = [['X'],['Y']]
        
    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = 0 
    m.params['MBE_bases']           = []
    m.params['MBE_threshold']       = 1
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = 1
    
    ### Derive other parameters
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0])
    
    funcs.finish(m, upload =True, debug=debug)
    
    
if __name__ == '__main__':

    
    ''' for sweeping specific sets of params for each carbon'''

    # ########## CARBON 1 ###############
    electron_transition = qt.exp_params['samples']['111_1_sil18']['electron_transition']
    if 1 in carbons:
        tau_list = qt.exp_params['samples']['111_1_sil18']['C1_gate_optimize_tau_list'+electron_transition]
        N_list   = qt.exp_params['samples']['111_1_sil18']['C1_gate_optimize_N_list'+electron_transition]
        for ii in range(len(tau_list)):

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(4)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break
            GreenAOM.set_power(20e-6)
            ins_counters.set_is_running(0)  
            optimiz0r.optimize(dims=['x','y','z'])

            XY_initialization('Gate_calibration_Sil18_C1'+ '_ii_'+ str(ii) +'_positive'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'positive', tau = tau_list[ii], N = N_list[ii],  carbon_list = [1])
            XY_initialization('Gate_calibration_Sil18_C1'+ '_ii_'+ str(ii) +'_negative'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'negative', tau = tau_list[ii], N = N_list[ii],  carbon_list = [1])

        # tau0 = 9.436e-6
        # tau_range = 8e-9
        # tau_list = np.arange(tau0 - tau_range,tau0 + tau_range,2e-9)
        # N_list   = np.arange(34,60,2)
        # for ii in range(len(tau_list)):
        #     for count in range(len(N_list)):
        #         print '-----------------------------------'            
        #         print 'press q to stop measurement cleanly'
        #         print '-----------------------------------'
        #         qt.msleep(4)
        #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        #             break
        #         GreenAOM.set_power(20e-6)
        #         ins_counters.set_is_running(0)  
        #         optimiz0r.optimize(dims=['x','y','z'])

        #         XY_initialization('Gate_calibration_Sil18_C1'+ '_ii_'+ str(ii) +'_positive'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[count]), 
        #                 el_RO= 'positive', tau = tau_list[ii], N = N_list[count],  carbon_list = [1])
        #         XY_initialization('Gate_calibration_Sil18_C1'+ '_ii_'+ str(ii) +'_negative'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[count]), 
        #                 el_RO= 'negative', tau = tau_list[ii], N = N_list[count],  carbon_list = [1])
       

        # ######## CARBON 2 ###############

    if 2 in carbons:
        tau_list = qt.exp_params['samples']['111_1_sil18']['C2_gate_optimize_tau_list'+electron_transition]
        N_list   = qt.exp_params['samples']['111_1_sil18']['C2_gate_optimize_N_list'+electron_transition]

        for ii in range(len(tau_list)):

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(4)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break
            GreenAOM.set_power(20e-6)
            ins_counters.set_is_running(0)  
            optimiz0r.optimize(dims=['x','y','z'])

            XY_initialization('Gate_calibration_Sil18_C2'+ '_ii_'+ str(ii) +'_positive'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'positive', tau = tau_list[ii], N = N_list[ii],  carbon_list = [2])
            XY_initialization('Gate_calibration_Sil18_C2'+ '_ii_'+ str(ii) +'_negative'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'negative', tau = tau_list[ii], N = N_list[ii],  carbon_list = [2])


    # ######## CARBON 3 ###############
    if 3 in carbons:

        tau_list = qt.exp_params['samples']['111_1_sil18']['C3_gate_optimize_tau_list'+electron_transition]
        N_list   = qt.exp_params['samples']['111_1_sil18']['C3_gate_optimize_N_list'+electron_transition]

        for ii in range(len(tau_list)):
            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(4)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break
            GreenAOM.set_power(20e-6)
            ins_counters.set_is_running(0)  
            optimiz0r.optimize(dims=['x','y','z'])

            XY_initialization('Gate_calibration_Sil18_C3'+ '_ii_'+ str(ii) +'_positive'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'positive', tau = tau_list[ii], N = N_list[ii],  carbon_list = [3])
            XY_initialization('Gate_calibration_Sil18_C3'+ '_ii_'+ str(ii) +'_negative'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'negative', tau = tau_list[ii], N = N_list[ii],  carbon_list = [3])
            
            

        # ssrocalibration(SAMPLE_CFG)

        # tau0=10.806
        # tau_list = np.arange(tau0*1e-6-14e-9, tau0*1e-6+14e-9, 2e-9)
        # N_list   = np.arange(6, 22, 2)

        # print len(N_list)*len(tau_list)    

        # for ii in range(len(tau_list)):
        #     for count in range(len(N_list)):
        #         print '-----------------------------------'            
        #         print 'press q to stop measurement cleanly'
        #         print '-----------------------------------'
        #         qt.msleep(4)
        #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        #             break
        #         GreenAOM.set_power(20e-6)
        #         ins_counters.set_is_running(0)  
        #         optimiz0r.optimize(dims=['x','y','z'])
        #         print 'N=', N_list[count], ' tau=', tau_list[ii]
        #         XY_initialization('Gate_calibration_Sil18_C3'+ '_ii_'+ str(ii) +'_positive'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[count]), 
        #                 el_RO= 'positive', tau = tau_list[ii], N = N_list[count],  carbon_list = [3])
        #         XY_initialization('Gate_calibration_Sil18_C3'+ '_ii_'+ str(ii) +'_negative'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[count]), 
        #                 el_RO= 'negative', tau = tau_list[ii], N = N_list[count],  carbon_list = [3])
        
        # ssrocalibration(SAMPLE_CFG)

        # ######## CARBON 5 ###############

    if 5 in carbons:
        tau_list = qt.exp_params['samples']['111_1_sil18']['C5_gate_optimize_tau_list'+electron_transition]
        N_list   = qt.exp_params['samples']['111_1_sil18']['C5_gate_optimize_N_list'+electron_transition]

        for ii in range(len(tau_list)):

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(4)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break
            GreenAOM.set_power(20e-6)
            ins_counters.set_is_running(0)
            optimiz0r.optimize(dims=['x','y','z'])

            XY_initialization('Gate_calibration_Sil18_C5'+ '_ii_'+ str(ii) +'_positive'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'positive', tau = tau_list[ii], N = N_list[ii],  carbon_list = [5],debug=False)
            XY_initialization('Gate_calibration_Sil18_C5'+ '_ii_'+ str(ii) +'_negative'+'_tau' + str(tau_list[ii]) + '_N' + str(N_list[ii]), 
                    el_RO= 'negative', tau = tau_list[ii], N = N_list[ii],  carbon_list = [5],debug=False)

   

    '''
    ### Carbon1 ##
    Number_of_pulses_list = np.concatenate([np.arange(1),np.arange(32,52,2)])
    tau_list         = np.linspace(4.988e-6,5.004e-6,9)

    for tau in tau_list:

        GreenAOM.set_power(5e-6)
        ins_counters.set_is_running(0)  
        optimiz0r.optimize(dims=['x','y','z'])

        ssrocalibration(SAMPLE_CFG)

        for N in Number_of_pulses_list:
            
            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(4)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            XY_initialization('Gate_calibration_Sil18_C1_tau' + str(tau) + '_N' + str(N) + 'positive', 
                    el_RO= 'positive', tau = tau, N = N)
            XY_initialization('Gate_calibration_Sil18_C1_tau' + str(tau) + '_N' + str(N) + 'negative', 
                    el_RO= 'negative', tau = tau, N = N)

    '''
    ### Carbon2 ##
    # Number_of_pulses_list   = np.arange(16,25,2)
    # tau_list           = np.linspace(10.058e-6-14e-9,10.058e-6+14e-9,15)
    # tau_list           =   [1.0056e-5, 1.0058e-5,1.006e-5, 1.0066e-5]
  

    # tau_list                = [1.1228e-5, 1.123e-5,1.1232e-5,1.1234e-5,1.1236e-5]
    # Number_of_pulses_list   = np.arange(10,17,2)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break
    #     GreenAOM.set_power(5e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z'])

    #     ssrocalibration(SAMPLE_CFG)

    #     for N in Number_of_pulses_list:
            
    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(4)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break

    #         XY_initialization('Gate_calibration_Sil18_C2_tau' + str(tau) + '_N' + str(N) + 'positive', 
    #                 el_RO= 'positive', tau = tau, N = N,  carbon_list = [2])
    #         XY_initialization('Gate_calibration_Sil18_C2_tau' + str(tau) + '_N' + str(N) + 'negative', 
    #                 el_RO= 'negative', tau = tau, N = N,  carbon_list = [2])

    # tau_list           = np.linspace(13.61e-6,13.618e-6,5)
    # Number_of_pulses_list   = np.arange(30,40,2)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     GreenAOM.set_power(5e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z'])

    #     ssrocalibration(SAMPLE_CFG)


    #     for N in Number_of_pulses_list:
            
    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(4)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break

    #         XY_initialization('Gate_calibration_Sil18_C2_tau' + str(tau) + '_N' + str(N) + 'positive', 
    #                 el_RO= 'positive', tau = tau, N = N,  carbon_list = [2])
    #         XY_initialization('Gate_calibration_Sil18_C2_tau' + str(tau) + '_N' + str(N) + 'negative', 
    #                 el_RO= 'negative', tau = tau, N = N,  carbon_list = [2])

    
    ################
    ### Carbon 3 ###
    ################

    # breakStatement = False
    # tau_list = np.arange(9.668e-6, 9.668e-6+16e-9, 2e-9)
    # N_list   = np.arange(6, 16, 2)

    # for tau in tau_list:

    #     if breakStatement:
    #         break

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         breakStatement = True
    #         break

    #     GreenAOM.set_power(20e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z','x','y'])

    #     ssrocalibration(SAMPLE_CFG)


    #     for N in N_list:
            
    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(4)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break
    #             breakStatement=True

    #         XY_initialization('Gate_calibration_Sil18_C3_tau' + str(tau) + '_N' + str(N) + 'positive', 
    #                 el_RO= 'positive', tau = tau, N = N,  carbon_list = [3])
    #         XY_initialization('Gate_calibration_Sil18_C3_tau' + str(tau) + '_N' + str(N) + 'negative', 
    #                 el_RO= 'negative', tau = tau, N = N,  carbon_list = [3])


    # tau_list = np.arange(11.944e-6-10e-9, 11.944e-6+10e-9, 2e-9)
    # N_list   = np.arange(10,24, 2)

    # for tau in tau_list:

    #     if breakStatement:
    #         break

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break
    #         breakStatement=True

    #     for N in N_list:
            
    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(4)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break
    #             breakStatement=True

    #         XY_initialization('Gate_calibration_Sil18_C3_tau' + str(tau) + '_N' + str(N) + 'positive', 
    #                 el_RO= 'positive', tau = tau, N = N,  carbon_list = [3])
    #         XY_initialization('Gate_calibration_Sil18_C3_tau' + str(tau) + '_N' + str(N) + 'negative', 
    #                 el_RO= 'negative', tau = tau, N = N,  carbon_list = [3])

    #     GreenAOM.set_power(20e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z','x','y'])

    #     ssrocalibration(SAMPLE_CFG)


    # tau_list = np.arange(13.082e-6-10e-9, 13.082e-6+10e-9, 2e-9)
    # N_list   = np.arange(10, 24, 2)

    # for tau in tau_list:

    #     if breakStatement:
    #         break

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break
    #         breakStatement=True

    #     GreenAOM.set_power(20e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z','x','y'])

    #     ssrocalibration(SAMPLE_CFG)


    #     for N in N_list:
            
    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(4)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break
    #             breakStatement=True

    #         XY_initialization('Gate_calibration_Sil18_C3_tau' + str(tau) + '_N' + str(N) + 'positive', 
    #                 el_RO= 'positive', tau = tau, N = N,  carbon_list = [3])
    #         XY_initialization('Gate_calibration_Sil18_C3_tau' + str(tau) + '_N' + str(N) + 'negative', 
    #                 el_RO= 'negative', tau = tau, N = N,  carbon_list = [3])


    # ### Carbon5 ##
    # Number_of_pulses_list = np.arange(32,53,2)
    # tau_list              = np.linspace(11.302e-6-14e-9, 11.302e-6+14e-9,15)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break
    #     GreenAOM.set_power(5e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z'])

    #     ssrocalibration(SAMPLE_CFG)

    #     for N in Number_of_pulses_list:
            
    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(4)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break

    #         XY_initialization('Gate_calibration_Sil18_C5_tau' + str(tau) + '_N' + str(N) + 'positive', 
    #                 el_RO= 'positive', tau = tau, N = N, carbon_list = [5])
    #         XY_initialization('Gate_calibration_Sil18_C5_tau' + str(tau) + '_N' + str(N) + 'negative', 
    #                 el_RO= 'negative', tau = tau, N = N,  carbon_list = [5])
    


    
    ''' Measurements of the length of the electron Bloch vector ''' 

    # ### Measurement set for Carbon 5 gate ###
        
    # Number_of_pulses = np.concatenate([np.arange(1), np.arange(32,61,2)])
    # Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    # tau_list         = np.linspace(8.916e-6,8.936e-6,11)

    # GreenAOM.set_power(5e-6)
    # ins_counters.set_is_running(0)  
    # optimiz0r.optimize(dims=['x','y','z'])

    # ssrocalibration(SAMPLE_CFG)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     for Final_Pulse in Final_Pulse_list:
    #         SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
    #                 reps_per_ROsequence = 2000)


    # ### Measurement set for Carbon 1 gate ###
    # Number_of_pulses = np.concatenate([np.arange(1),np.arange(28,57,2)])
    # Final_Pulse_list = ['x','-x','y','-y','no_pulse']
    # tau_list         = np.linspace(4.984e-6,5.004e-6,11)

    # GreenAOM.set_power(5e-6)
    # ins_counters.set_is_running(0)  
    # optimiz0r.optimize(dims=['x','y','z'])

    # ssrocalibration(SAMPLE_CFG)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     for Final_Pulse in Final_Pulse_list:
    #         SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, Final_Pulse= Final_Pulse, Number_of_pulses =Number_of_pulses,  
    #                 reps_per_ROsequence = 2000)


    ### Measurement set for Carbon 2 gate ###        

    # Number_of_pulses   = np.concatenate([np.arange(1),np.arange(16,26,2)])
    # Initial_Pulse_list = ['x', 'x', 'x', 'x', 'x', '-x']
    # Final_Pulse_list   = ['x','-x','y','-y','no_pulse', 'no_pulse']
    # tau_list           = np.linspace(10.058e-6-10e-9,10.058e-6+10e-9,11)

    # GreenAOM.set_power(5e-6)
    # ins_counters.set_is_running(0)  
    # optimiz0r.optimize(dims=['x','y','z'])

    # ssrocalibration(SAMPLE_CFG)

    # for tau in tau_list:
    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     for ii, Final_Pulse in enumerate(Final_Pulse_list):
    #         Initial_Pulse = Initial_Pulse_list[ii]
    #         SimpleDecoupling_swp_N(SAMPLE+'sweep_N_' + Final_Pulse +'_tau' +str(tau) , tau =tau, 
    #                 Final_Pulse= Final_Pulse, Initial_Pulse =Initial_Pulse, Number_of_pulses =Number_of_pulses,  
    #                 reps_per_ROsequence = 2000)
    
