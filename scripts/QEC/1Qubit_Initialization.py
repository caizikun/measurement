import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, carbon            =   1,               
        
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],  

        el_RO               = 'positive',
        debug               = False):

    m = DD.Two_QB_Probabilistic_MBE_v3(name)
    funcs.prepare(m)


    m.params['el_after_init']                = '0'


    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 400

    ### Carbons to be used
    m.params['carbon_list']         = [carbon]

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['Tomography Bases'] = TD.get_tomo_bases(nr_of_qubits = 1)
    # m.params['Tomography Bases'] = [['X'],['Y'],['Z']]
    # m.params['Tomography Bases'] = [['X'],['Y']]
    # m.params['Tomography Bases'] = [['X']]
        
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
    carbons = [1,2,5]
    debug = False
    init_method = 'MBI'

    if init_method == 'swap':
        for c in carbons:

            MBE(SAMPLE + 'positive_'+str(c)+'_swap', el_RO= 'positive', carbon = c, carbon_init_list = [c]
                                                ,debug = debug,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])


            MBE(SAMPLE + 'negative_'+str(c)+'_swap', el_RO= 'negative', carbon = c, carbon_init_list = [c]
                                                ,debug = debug,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])

    elif init_method == 'MBI':
        for c in carbons:

            MBE(SAMPLE + 'positive_'+str(c)+'_MBI', el_RO= 'positive', carbon = c, carbon_init_list = [c]
                                                ,carbon_init_methods     =   ['MBI'], carbon_init_thresholds  =   [1])

            MBE(SAMPLE + 'negative_'+str(c)+'_MBI', el_RO= 'negative', carbon = c, carbon_init_list = [c]
                                                ,carbon_init_methods     =   ['MBI'], carbon_init_thresholds  =   [1])

