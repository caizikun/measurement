import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

        
def MBE(name, carbon_list   = [1,2],      

        carbon_init_list        = [2,1],
        carbon_init_states      = 2*['up'], 
        carbon_init_methods     = 2*['swap'], 
        carbon_init_thresholds  = 2*[0],  

        number_of_MBE_steps = 1,
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,
        number_of_parity_msmnts = 0,
        parity_msmnts_threshold = 1, 

        el_RO               = 'positive',
        debug               = False):

    m = DD.Two_QB_Probabilistic_MBE_v3(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 1000 

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)
    m.params['el_after_init']                = '0'
    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    # # m.params['Tomography Bases'] = 'full'
    # m.params['Tomography Bases'] = ([
    #         ['X','I'],['Y','I'],['Z','I'],
    #         ['I','X'],['I','Y'],['I','Z'],
    #         ['X','X'],['X','Y'],['X','Z'],
    #         ['Y','X'],['Y','Y'],['Y','Z'],
    #         ['Z','X'],['Z','Y'],['Z','Z']])

    # m.params['Tomography Bases'] = ([
    #         ['X','I'],['Y','I'],['Z','I'],
    #         ['I','X'],['I','Y'],['I','Z']])

    # m.params['Tomography Bases'] = ([
    #         ['X','X'],['X','Y'],['X','Z'],
    #         ['Y','X'],['Y','Y'],['Y','Z'],
    #         ['Z','X'],['Z','Y'],['Z','Z']])
    
    m.params['Tomography Bases'] = ([
            ['X','X'],['Y','Y'],['Z','Z']])


    # m.params['Tomography Bases'] = ([
    #         ['X','I'],['Y','I'],['Z','I']])

    # m.params['Tomography Bases'] = ([
    #         ['X','I','I'],['Y','I','I'],['Z','I','I'],
    #         ['I','X','I'],['I','Y','I'],['I','Z','I'],
    #         ['I','I','X'],['I','I','Y'],['I','I','Z']])


    # m.params['Tomography Bases'] = TD.get_tomo_bases(nr_of_qubits = 1)
        
    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = number_of_MBE_steps 
    m.params['MBE_bases']           = mbe_bases
    m.params['MBE_threshold']       = MBE_threshold
    
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
  
    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':

    MBE(SAMPLE + 'positive', el_RO= 'positive',carbon_list = [1,2],carbon_init_list = [1,2])
    # MBE(SAMPLE + 'negative', el_RO= 'negative')



