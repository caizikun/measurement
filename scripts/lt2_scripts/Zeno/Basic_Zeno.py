import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.lt2_scripts.Zeno.Zeno as Zen; reload(Zen)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

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

        number_of_parity_msmnts = 0,
        parity_msmnts_threshold = 1, 

        free_evolution_time = 0e-6,

        el_RO               = 'positive',
        debug               = False,
        Tomo_bases          = []):

    m = Zen.Zeno_TwoQB(name)
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

    m.params['Nr_parity_msmts']     = number_of_parity_msmnts
    m.params['Parity_threshold']    = parity_msmnts_threshold
    

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

    Tomo1 = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z']])


    Zeno(SAMPLE + 'positive'+'_logicState_'+'wait_Gate'+'_singleQ', 
            el_RO= 'positive',
            logic_state='X',
            Tomo_bases = Tomo1,
            debug=False)
    Zeno(SAMPLE + 'positive'+'_logicState_'+'wait_Gate'+'_twoQ', 
            el_RO= 'positive',
            logic_state='X',
            Tomo_bases = Tomo2,
            debug=False)


    # logic_state_list=['mX','Y','mY','Z','mZ']

    # # MBE(SAMPLE + 'positive', el_RO= 'positive', Tomo_bases = Tomo_bases1)
    # # MBE(SAMPLE + 'negative', el_RO= 'negative', Tomo_bases = Tomo_bases1)

    # for logic_state in logic_state_list:
    #     Zeno(SAMPLE + 'positive'+'_logicState_'+logic_state+'_singleQ', el_RO= 'positive',logic_state=logic_state,Tomo_bases = Tomo1,debug=False)
    #     Zeno(SAMPLE + 'positive'+'_logicState_'+logic_state+'_2QValues', el_RO= 'positive',logic_state=logic_state,Tomo_bases = Tomo2,debug=False)
    # Zeno(SAMPLE + 'negative', el_RO= 'negative',Tomo_bases = Tomo_bases2)


