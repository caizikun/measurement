import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, carbon_list   = [1,5,2],               
        
        carbon_init_list        = [2,5,1],
        carbon_init_states      = 3*['up'], 
        carbon_init_methods     = 3*['swap'], 
        carbon_init_thresholds  = 3*[0],  

        number_of_MBE_steps = 1,
        logic_state         = 'X',
        mbe_bases           = ['Y','Y','Y'],
        MBE_threshold       = 1,

        number_of_parity_msmnts = 0,
        parity_msmnts_threshold = 1, 

        el_RO               = 'positive',
        debug               = False,
        Tomo_bases          = []):

    m = DD.Three_QB_Probabilistic_MBE(name)
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
    m.params['3qb_logical_state']   = logic_state
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

    # m.params['C13_MBI_threshold']       = carbon_init_thresholds
       
    
    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':

    
    Tomo_bases_single = ([
            ['X','I','I'],['Y','I','I'],['Z','I','I'],
            ['I','X','I'],['I','Y','I'],['I','Z','I'],
            ['I','I','X'],['I','I','Y'],['I','I','Z']])

    Tomo_bases_2 = ([['Z','I','I'], ['I','Z','I'], ['I','I','Z'], ['Z','Z','I'], ['Z','I','Z'], ['I','Z','Z'], ['Z','Z','Z']])

    Tomo_bases2 = ([['I','I','X'],['X','X','I'],['I','X','X'],['X','I','X']])


    Tomo_bases = ([
            ['X','I','I'],['Y','I','I'],['Z','I','I'],
            ['I','X','I'],['I','Y','I'],['I','Z','I'],
            ['I','I','X'],['I','I','Y'],['I','I','Z'],

            ['X','X','I'],['X','Y','I'],['X','Z','I'],
            ['Y','X','I'],['Y','Y','I'],['Y','Z','I'],
            ['Z','X','I'],['Z','Y','I'],['Z','Z','I'],

            ['X','I','X'],['Y','I','X'],['Z','I','X'],
            ['X','I','Y'],['Y','I','Y'],['Z','I','Y'],
            ['X','I','Z'],['Y','I','Z'],['Z','I','Z'],

            ['I','X','X'],['I','Y','X'],['I','Z','X'],
            ['I','X','Y'],['I','Y','Y'],['I','Z','Y'],
            ['I','X','Z'],['I','Y','Z'],['I','Z','Z'],

            ['X','X','X'],['X','Y','X'],['X','Z','X'],
            ['Y','X','X'],['Y','Y','X'],['Y','Z','X'],
            ['Z','X','X'],['Z','Y','X'],['Z','Z','X'],

            ['X','X','Y'],['X','Y','Y'],['X','Z','Y'],
            ['Y','X','Y'],['Y','Y','Y'],['Y','Z','Y'],
            ['Z','X','Y'],['Z','Y','Y'],['Z','Z','Y'],

            ['X','X','Z'],['X','Y','Z'],['X','Z','Z'],
            ['Y','X','Z'],['Y','Y','Z'],['Y','Z','Z'],
            ['Z','X','Z'],['Z','Y','Z'],['Z','Z','Z']])

    Tomo_bases_Z = ([['I','I','X'],['I','X','I'],['X','I','I'], ['I','X','X'], ['X','I','X'], ['X','X','I'], ['X','X','X']])
    Tomo_bases_X = ([['I','X','X'],['X','I','X'],['X','X','I'], ['Y','Y','Z'], ['Y','Z','Y'], ['Z','Y','Y'], ['Z','Z','Z']])
    Tomo_bases_Y = ([['I','X','X'],['X','I','X'],['X','X','I'], ['Y','Y','Y'], ['Y','Z','Z'], ['Z','Y','Z'], ['Z','Z','Y']])

    # MBE(SAMPLE + 'positive', el_RO= 'positive', Tomo_bases = Tomo_bases_X)
    # MBE(SAMPLE + 'negative', el_RO= 'negative', Tomo_bases = Tomo_bases_X)


    for state in ['Z','mZ','X','mX','Y','mY']:
        logic_state = state

        for k in range(len(Tomo_bases)/7):
            tomo = Tomo_bases[0+k*7:7+k*7]

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(10)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            MBE(SAMPLE +'_state_'+logic_state+'positive_'+str(k), el_RO= 'positive',Tomo_bases = tomo, logic_state = logic_state)
            MBE(SAMPLE +'_state_'+logic_state+'negative_'+str(k), el_RO= 'negative',Tomo_bases = tomo, logic_state = logic_state)

