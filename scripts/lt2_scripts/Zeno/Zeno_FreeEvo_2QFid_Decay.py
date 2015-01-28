import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

import msvcrt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Zeno(name, carbon_list   = [1,5],               
        
        carbon_init_list        = [5,1],
        carbon_init_states      = 2*['up'], 
        carbon_init_methods     = 2*['swap'], 
        carbon_init_thresholds  = 2*[0],  

        number_of_MBE_steps = 1,
        logic_state         ='X',
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,

        number_of_zeno_msmnts = 0,
        parity_msmnts_threshold = 1, 

        free_evolution_time = 0e-6,

        el_RO               = 'positive',
        debug               = False,
        Tomo_bases          = []):

    m = DD.Zeno_TwoQB(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 300

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['Tomography Bases'] = Tomo_bases 
    
    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = number_of_MBE_steps 
    m.params['MBE_bases']           = mbe_bases
    m.params['MBE_threshold']       = MBE_threshold
    m.params['2qb_logical_state']   = logic_state
    m.params['2C_RO_trigger_duration'] = 150e-6
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = parity_msmnts_threshold
    m.params['Nr_Zeno_parity_msmts']     = number_of_zeno_msmnts
    m.params['Zeno_SP_A_power'] = 18e-9
    m.params['Repump_duration']= 300e-6 #how long the 'Zeno' beam is shined in.

    ### Derive other parameters
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        if len(carbon_list) == 2:
            m.params['sweep_pts'].append(BP[0]+BP[1])
        elif len(carbon_list) == 3:
            m.params['sweep_pts'].append(BP[0]+BP[1]+BP[2])
    print m.params['sweep_pts']

    ####################################
    ### waiting time and measurement ###
    ####################################
       
    m.params['free_evolution_time']=free_evolution_time


    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':

    Tomo2=[]
    RO_bases=['X','Y','Z']
    for i,bas1 in enumerate(RO_bases):
        for j, bas2 in enumerate(RO_bases):
                Tomo2.append([bas1]+[bas2])

    logic_state_list=['X','mX','Y','mY','Z','mZ']

    #gives the necessary RO basis for detemrining the 2Qubit fidelity.

    RO_bases_dict={'X':[['Y','Y'],['Z','Z']],
    'mX':[['Y','Y'],['Z','Z']],
    'Y':[['Y','Z'],['Z','Y']],
    'mY':[['Y','Z'],['Z','Y']],
    'Z':[['I','X'],['X','I']],
    'mZ':[['I','X'],['X','I']]}

    eRO_list = ['positive','negative']

    #
    #Measure a single point for a single state.
    
    # Zeno(SAMPLE +'positive'+'_debug', 
    #                 el_RO= 'positive',
    #                 logic_state='X',
    #                 Tomo_bases = RO_bases_dict['X'],
    #                 free_evolution_time=20e-3,
    #                 number_of_zeno_msmnts = 1,
    #                 debug=True)


    # #########################
    # # 1 measurement         #
    # #########################
    # breakstatement=False

    # EvoTime_arr=np.r_[0,np.linspace(3.5e-3,50e-3,14)]

    # for EvoTime in EvoTime_arr:

    #     if breakstatement:
    #         break

    #     for logic_state in logic_state_list:

    #         print '-----------------------------------'            
    #         print 'press q to stop measurement cleanly'
    #         print '-----------------------------------'
    #         qt.msleep(2)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             breakstatement=True
    #             break

    #         for eRO in eRO_list:
    #             Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_1msmt_'+'_EvoTime_'+str(EvoTime), 
    #                 el_RO= eRO,
    #                 logic_state=logic_state,
    #                 Tomo_bases = RO_bases_dict[logic_state],
    #                 free_evolution_time=EvoTime,
    #                 number_of_zeno_msmnts = 1,
    #                 debug=False)

    #     GreenAOM.set_power(7e-6)
    #     counters.set_is_running(1)  
    #     optimiz0r.optimize(dims = ['x','y','z'])
    #     stools.turn_off_all_lt2_lasers()

    #     ssrocalibration(SAMPLE_CFG)

    # # #########################
    # # # 2 measurements        #
    # # ######################### estimated duration parity duration: 6.3 ms 2015-01-27
    EvoTime_arr=np.r_[0,np.linspace(7.5e-3,50e-3,14)]

    breakstatement=False

    for EvoTime in EvoTime_arr:

        if breakstatement:
            break

        for logic_state in logic_state_list:

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                breakstatement=True
                break

            for eRO in eRO_list:
                Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_2msmt_'+'_EvoTime_'+str(EvoTime), 
                    el_RO= eRO,
                    logic_state=logic_state,
                    Tomo_bases = RO_bases_dict[logic_state],
                    free_evolution_time=EvoTime,
                    number_of_zeno_msmnts = 2,
                    debug=False)

        GreenAOM.set_power(7e-6)
        counters.set_is_running(1)  
        optimiz0r.optimize(dims = ['x','y','z'])
        stools.turn_off_all_lt2_lasers()

        ssrocalibration(SAMPLE_CFG)


    # # #########################
    # # # 3 measurements        #
    # # ######################### estimated duration parity duration: 9.4 ms 2015-01-27
    EvoTime_arr=np.r_[0,np.linspace(10.5e-3,60e-3,14)]

    breakstatement=False

    for EvoTime in EvoTime_arr:

        if breakstatement:
            break

        for logic_state in logic_state_list:

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                breakstatement=True
                break

            for eRO in eRO_list:
                Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_3msmt_'+'_EvoTime_'+str(EvoTime), 
                    el_RO= eRO,
                    logic_state=logic_state,
                    Tomo_bases = RO_bases_dict[logic_state],
                    free_evolution_time=EvoTime,
                    number_of_zeno_msmnts = 3,
                    debug=False)

        GreenAOM.set_power(7e-6)
        counters.set_is_running(1)  
        optimiz0r.optimize(dims = ['x','y','z'])
        stools.turn_off_all_lt2_lasers()

        ssrocalibration(SAMPLE_CFG)

    # # #########################
    # # # 4 measurements        #
    # # ######################### estimated duration parity duration: 12.6 ms 2015-01-27
    EvoTime_arr=np.r_[0,np.linspace(14e-3,60e-3,14)]

    breakstatement=False

    for EvoTime in EvoTime_arr:

        if breakstatement:
            break

        for logic_state in logic_state_list:

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                breakstatement=True
                break

            for eRO in eRO_list:
                Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_4msmt_'+'_EvoTime_'+str(EvoTime), 
                    el_RO= eRO,
                    logic_state=logic_state,
                    Tomo_bases = RO_bases_dict[logic_state],
                    free_evolution_time=EvoTime,
                    number_of_zeno_msmnts = 4,
                    debug=False)

        GreenAOM.set_power(7e-6)
        counters.set_is_running(1)  
        optimiz0r.optimize(dims = ['x','y','z'])
        stools.turn_off_all_lt2_lasers()

        ssrocalibration(SAMPLE_CFG)