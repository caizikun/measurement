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

        number_of_MBE_steps        = 1,
        logic_state                = 'X',
        mbe_bases                  = ['Y','Y','Y'],
        MBE_threshold               = 1,
        RO_C                        = 1,

        number_of_parity_msmnts = 2,

        el_RO_0               = 'positive',
        el_RO_1               = 'negative',
        debug                 = False):

    m = DD.Three_QB_det_QEC(name)
    funcs.prepare(m)

    error_probability_list        = np.linspace(0,1,3)
    phase_error                   = 2*np.arcsin(np.sqrt(error_probability_list))*180./np.pi
    Qe                            = [1,0,0]
    m.params['phase_error_array'] = np.transpose([phase_error*Qe[0],phase_error*Qe[1],phase_error*Qe[2]])

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

    # # if logic_state == 'X' or logic_state == 'mX':
    # m.params['Tomo_Bases_00'] = ['Z','Z','Z']
    # m.params['Tomo_Bases_01'] = ['Z','-Z','Z']
    # m.params['Tomo_Bases_10'] = ['Z','Z','-Z']
    # m.params['Tomo_Bases_11'] = ['Z','Z','Z']

    # elif logic_state == 'Y' or logic_state == 'mY':
    if RO_C == 1:
        m.params['Tomo_Bases_00'] = ['Y','Z','Z']
        m.params['Tomo_Bases_01'] = ['Y','-Z','Z']
        m.params['Tomo_Bases_10'] = ['Y','Z','-Z']
        m.params['Tomo_Bases_11'] = ['-Y','Z','Z']
    if RO_C == 2:
        m.params['Tomo_Bases_00'] = ['Z','Y','Z']
        m.params['Tomo_Bases_01'] = ['Z','-Y','Z']
        m.params['Tomo_Bases_10'] = ['Z','Y','-Z']
        m.params['Tomo_Bases_11'] = ['Z','Y','Z']
    if RO_C == 3:
        m.params['Tomo_Bases_00'] = ['Z','Z','Y']
        m.params['Tomo_Bases_01'] = ['Z','-Z','Y']
        m.params['Tomo_Bases_10'] = ['Z','Z','-Y']
        m.params['Tomo_Bases_11'] = ['Z','Z','Y']

    # elif logic_state == 'Z' or logic_state == 'mZ':
    #     m.params['Tomo_Bases_00'] = ['X','I','I']
    #     m.params['Tomo_Bases_01'] = ['X','I','I']
    #     m.params['Tomo_Bases_10'] = ['-X','I','I']
    #     m.params['Tomo_Bases_11'] = ['X','I','I']
   
    # if RO_C == 1:
    #     m.params['Tomo_Bases_00'] = ['X','I','I']
    #     m.params['Tomo_Bases_01'] = ['X','I','I']
    #     m.params['Tomo_Bases_10'] = ['X','I','I']
    #     m.params['Tomo_Bases_11'] = ['-X','I','I']

    # elif RO_C == 2:
    #     m.params['Tomo_Bases_00'] = ['I','X','I']
    #     m.params['Tomo_Bases_01'] = ['I','-X','I']
    #     m.params['Tomo_Bases_10'] = ['I','X','I']
    #     m.params['Tomo_Bases_11'] = ['I','X','I']
    # elif RO_C == 3:
    #     m.params['Tomo_Bases_00'] = ['I','I','X']
    #     m.params['Tomo_Bases_01'] = ['I','I','X']
    #     m.params['Tomo_Bases_10'] = ['I','I','-X']
    #     m.params['Tomo_Bases_11'] = ['I','I','X']
    
    # if RO_C == 1:
    #     m.params['Tomo_Bases_00'] = ['X','X','I']
    #     m.params['Tomo_Bases_01'] = ['X','X','I']
    #     m.params['Tomo_Bases_10'] = ['X','X','I']
    #     m.params['Tomo_Bases_11'] = ['X','X','I']
    # elif RO_C == 2:
    #     m.params['Tomo_Bases_00'] = ['X','I','X']
    #     m.params['Tomo_Bases_01'] = ['X','I','X']
    #     m.params['Tomo_Bases_10'] = ['X','I','X']
    #     m.params['Tomo_Bases_11'] = ['X','I','X']
    # elif RO_C == 3:
    #     m.params['Tomo_Bases_00'] = ['I','X','X']
    #     m.params['Tomo_Bases_01'] = ['I','X','X']
    #     m.params['Tomo_Bases_10'] = ['I','X','X']
    #     m.params['Tomo_Bases_11'] = ['I','X','X']


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
    m.params['Parity_threshold']    = 1

    m.params['Parity_a_carbon_list'] = [2,1]
    m.params['Parity_b_carbon_list'] = [5,1]   

    m.params['Parity_a_RO_list'] = ['X','X']
    m.params['Parity_b_RO_list'] = ['X','X']




    ### Derive other parameters
    m.params['pts']                 = len(error_probability_list)
    m.params['sweep_name']          = 'Error Probability' 
    m.params['sweep_pts']           = error_probability_list

    ### RO params
    m.params['electron_readout_orientation_00'] = el_RO_0
    m.params['electron_readout_orientation_10'] = el_RO_0
    m.params['electron_readout_orientation_01'] = el_RO_1
    m.params['electron_readout_orientation_11'] = el_RO_1  
    
    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':

    MBE(SAMPLE + 'positive_1',RO_C = 1, el_RO_0 = 'positive',el_RO_1 = 'negative')
    MBE(SAMPLE + 'negative_1',RO_C = 1, el_RO_0 = 'negative',el_RO_1 = 'positive')
