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

        parity_msmnts_threshold = 1, 

        free_evolution_time = 0e-6,

        el_RO               = 'positive',
        debug               = False,
        Tomo_bases          = []):

    m = DD.DFS_check(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 500

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
    m.params['Zeno_SP_A_power'] = 18e-9
    m.params['Repump_duration']= np.linspace(0e-6,0.7e-6,7) #how long the repumper beam is shined in.

    m.params['echo_like']=False # this is a bool to set the delay inbetween measurements.

    ### Derive other parameters
    m.params['free_evolution_time'] = free_evolution_time
    m.params['pts']                 = len(m.params['Repump_duration'])
    m.params['sweep_name']          = 'Repump_duration'
    m.params['sweep_pts']           = m.params['Repump_duration']
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO



    ####################################
    ### waiting time and measurement ###
    ####################################
       
    m.params['free_evolution_time']=free_evolution_time


    funcs.finish(m, upload =True, debug=debug)



if __name__ == '__main__':

    logic_state_list=['X','mX','Y','mY','Z','mZ']

    #gives the necessary RO basis when decoding to carbon 5

    RO_bases_dict={'X':['Y','Y'],
    'mX':['Y','Y'],
    'Y':['Z','Y'],
    'mY':['Z','Y'],
    'Z':['I','X'],
    'mZ':['I','X']}
   

    #0 measurements --> 9 data points per run
    #Measure a single point for a single state.
    # EvoTime_arr=1e-3
    # teststate='X'
    # Zeno(SAMPLE +'positive'+'_0msmts_debug_'+RO_bases_dict[teststate][0]+RO_bases_dict[teststate][1], 
    #                 el_RO= 'positive',
    #                 logic_state=teststate,
    #                 Tomo_bases = RO_bases_dict[teststate],
    #                 free_evolution_time=EvoTime_arr,
    #                 debug=False)

    # teststate='X'
    # for RO in ['positive','negative']:
    #     EvoTime=1e-3
    #     Zeno(SAMPLE +RO+'_'+'state_'+teststate+RO_bases_dict[teststate][0]+RO_bases_dict[teststate][1], 
    #                     el_RO= RO,
    #                     logic_state=teststate,
    #                     Tomo_bases = RO_bases_dict[teststate],
    #                     free_evolution_time=EvoTime,
    #                     debug=False)
    EvoTime=1e-3
    teststate='mX'
    for RO in ['positive','negative']:
        Zeno(SAMPLE +RO+'state_'+teststate+RO_bases_dict[teststate][0]+RO_bases_dict[teststate][1], 
                        el_RO= RO,
                        logic_state=teststate,
                        Tomo_bases = RO_bases_dict[teststate],
                        free_evolution_time=EvoTime,
                        debug=False)
