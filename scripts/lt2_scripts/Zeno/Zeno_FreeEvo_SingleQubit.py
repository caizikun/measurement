### This script measures the bloch vector length of a single qubit.
### takes the measurement with the regular bases first and runs then a measurement for the orthogonal ones.
### NK 2015


import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.lt2_scripts.Zeno.Zeno as Zen; reload(Zen)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import time
import msvcrt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Zeno(name, carbon_list   = [1,2],               
        
        carbon_init_list        = [2,1],
        carbon_init_states      = 2*['up'], 
        carbon_init_methods     = 2*['swap'], 
        carbon_init_thresholds  = 2*[0],  

        number_of_MBE_steps = 1,
        logic_state         ='X',
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,

        number_of_zeno_msmnts = 0,
        parity_msmnts_threshold = 1, 

        free_evolution_time = [0e-6],

        el_RO               = 'positive',
        debug               = False,
        Tomo_bases          = [],
        Repetitions=500):

    m = Zen.Zeno_TwoQB(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds



    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = Repetitions

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ###         RO bases           ###
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
    m.params['Zeno_SP_A_power'] = 108e-9
    m.params['Repump_duration']= 30e-6 #how long the 'Zeno' beam is shined in.

    m.params['echo_like']=False # this is a bool to set the delay inbetween measurements.

    ### Derive other parameters
    m.params['free_evolution_time'] = free_evolution_time
    m.params['pts']                 = len(m.params['free_evolution_time'])
    m.params['sweep_name']          = 'free_evolution_time' 
    m.params['sweep_pts']           = m.params['free_evolution_time']
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO



    ####################################
    ### waiting time and measurement ###
    ####################################
       
    m.params['free_evolution_time']=free_evolution_time


    funcs.finish(m, upload =True, debug=debug)

def array_slicer(Evotime_slicer,evotime_arr):
    """
    this function is used to slice up the free evolution times into a list of lists
    such that the sequence can be loaded into the AWG 
    """

    no_of_cycles=int(np.floor(len(evotime_arr)/Evotime_slicer))
    returnEvos = []
    for i in range(no_of_cycles):
        returnEvos.append(evotime_arr[i*Evotime_slicer:(i+1)*Evotime_slicer])

    if len(evotime_arr)%Evotime_slicer !=0 : #only add the remaining array if there are some elements left to add.
        (returnEvos.append(evotime_arr[no_of_cycles*Evotime_slicer:]))

    return returnEvos


if __name__ == '__main__':

    logic_state_list=['X','mX','Y','mY','Z','mZ']

    #gives the necessary RO basis when decoding to carbon 5

    RO_bases_dict={'X':['I','Z'],
    'mX':['I','Z'],
    'Y':['I','Y'],
    'mY':['I','Y'],
    'Z':['I','X'],
    'mZ':['I','X']}


    breakstatement=False
    last_check=time.time()

    # logic_state = 'Z'
    # evotime = [40e-3,43e-3,45e-3]
    # for eRO in ['positive','negative']:
    #     Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_'+str(0)+'msmt_'+'singleQubit'+'_ROBasis_'+RO_bases_dict[logic_state][0]+RO_bases_dict[logic_state][1],
    #                             carbon_list   = [1,2],               
                                
    #                             carbon_init_list        = [2,1],
    #                             carbon_init_states      = 2*['up'], 
    #                             carbon_init_methods     = 2*['swap'], 
    #                             carbon_init_thresholds  = 2*[0],  

    #                             number_of_MBE_steps = 1,
    #                             logic_state         =logic_state,
    #                             mbe_bases           = ['I','Y'],
    #                             MBE_threshold       = 1,

    #                             number_of_zeno_msmnts = 0,
    #                             parity_msmnts_threshold = 1, 

    #                             free_evolution_time = evotime,

    #                             el_RO               = eRO,
    #                             debug               = False,
    #                             Tomo_bases          = RO_bases_dict[logic_state],
    #                             Repetitions         = 300)


    # RO_bases_dict={'X':['I','Z'],
    # 'mX':['I','Z'],
    # 'Y':['I','Y'],
    # 'mY':['I','Y'],
    # 'Z':['I','Y'],
    # 'mZ':['I','Y']}
    # for eRO in ['positive','negative']:
    #     Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_'+str(0)+'msmt_'+'singleQubit'+'_ROBasis_'+RO_bases_dict[logic_state][0]+RO_bases_dict[logic_state][1],
    #                             carbon_list   = [1,5],               
                                
    #                             carbon_init_list        = [5,1],
    #                             carbon_init_states      = 2*['up'], 
    #                             carbon_init_methods     = 2*['swap'], 
    #                             carbon_init_thresholds  = 2*[0],  

    #                             number_of_MBE_steps = 1,
    #                             logic_state         =logic_state,
    #                             mbe_bases           = ['I','Y'],
    #                             MBE_threshold       = 1,

    #                             number_of_zeno_msmnts = 0,
    #                             parity_msmnts_threshold = 1, 

    #                             free_evolution_time = evotime,

    #                             el_RO               = eRO,
    #                             debug               = False,
    #                             Tomo_bases          = RO_bases_dict[logic_state],
    #                             Repetitions         = 500)

    # #0 measurements --> 9 data points per run


    # ############################ 9 data points per run
    # #                         ## 
    # # obtain single qubit proc #
    # #                         ##
    # ############################ estimated duration parity duration: 12.6 ms 2015-01-27

    EvoTime_arr=np.r_[np.linspace(0e-3,50e-3,14),60e-3,70e-3,80e-3,100e-3]
    EvoTime_arr=array_slicer(9,EvoTime_arr)
    for logic_state in logic_state_list:
        if not breakstatement:
            for evotime in EvoTime_arr:
                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    breakstatement=True
                    break
                if not breakstatement:
                    for eRO in ['positive','negative']:
                        Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_'+str(0)+'msmt_'+'singleQubit'+'_ROBasis_'+RO_bases_dict[logic_state][0]+RO_bases_dict[logic_state][1],
                                carbon_list   = [1,2],               
                                
                                carbon_init_list        = [2,1],
                                carbon_init_states      = 2*['up'], 
                                carbon_init_methods     = 2*['swap'], 
                                carbon_init_thresholds  = 2*[0],  

                                number_of_MBE_steps = 1,
                                logic_state         =logic_state,
                                mbe_bases           = ['I','Y'],
                                MBE_threshold       = 1,

                                number_of_zeno_msmnts = 0,
                                parity_msmnts_threshold = 1, 

                                free_evolution_time = evotime,

                                el_RO               = eRO,
                                debug               = False,
                                Tomo_bases          = RO_bases_dict[logic_state],
                                Repetitions         = 300)

                if time.time()-last_check>2*60*60: #perform a consistency check every two hours
                    if not breakstatement:

                        print '-----------------------------------'            
                        print 'press q to stop measurement cleanly'
                        print '-----------------------------------'
                        qt.msleep(2)
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            breakstatement=True
                            break

                        ssrocalibration(SAMPLE_CFG)
                        GreenAOM.set_power(15e-6)
                        counters.set_is_running(1)
                        optimiz0r.optimize(dims = ['x','y','z'])
                        stools.turn_off_all_lt2_lasers()
                        ssrocalibration(SAMPLE_CFG)                 
                        last_check=time.time()


    
    logic_state_list=['Y','mY','Z','mZ']
    RO_bases_dict={'X':['I','Z'],
    'mX':['I','Z'],
    'Y':['I','X'],
    'mY':['I','X'],
    'Z':['I','Y'],
    'mZ':['I','Y']}

    for logic_state in logic_state_list:
        if not breakstatement:
            for evotime in EvoTime_arr:
                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    breakstatement=True
                    break
                if not breakstatement:
                    for eRO in ['positive','negative']:
                        Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_'+str(0)+'msmt_'+'singleQubit'+'_ROBasis_'+RO_bases_dict[logic_state][0]+RO_bases_dict[logic_state][1],
                                carbon_list   = [1,2],               
                                
                                carbon_init_list        = [2,1],
                                carbon_init_states      = 2*['up'], 
                                carbon_init_methods     = 2*['swap'], 
                                carbon_init_thresholds  = 2*[0],  

                                number_of_MBE_steps = 1,
                                logic_state         =logic_state,
                                mbe_bases           = ['I','Y'],
                                MBE_threshold       = 1,

                                number_of_zeno_msmnts = 0,
                                parity_msmnts_threshold = 1, 

                                free_evolution_time = evotime,

                                el_RO               = eRO,
                                debug               = False,
                                Tomo_bases          = RO_bases_dict[logic_state],
                                Repetitions         = 300)

                if time.time()-last_check>2*60*60: #perform a consistency check every two hours
                    if not breakstatement:

                        print '-----------------------------------'            
                        print 'press q to stop measurement cleanly'
                        print '-----------------------------------'
                        qt.msleep(2)
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            breakstatement=True
                            break

                        ssrocalibration(SAMPLE_CFG)
                        GreenAOM.set_power(15e-6)
                        counters.set_is_running(1)
                        optimiz0r.optimize(dims = ['x','y','z'])
                        stools.turn_off_all_lt2_lasers()
                        ssrocalibration(SAMPLE_CFG)

                        last_check=time.time()

