import numpy as np
import qt 
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro


def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    
    if RO_power != None: 
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None: 
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')
    
    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 15e-9#20e-9
    m.run()
    m.save('ms1')

    m.finish()
def MBE(name, carbon_list   = [1,5,2],               
        
        carbon_init_list              = [2,5,1],
        carbon_init_states            = 3*['up'], 
        carbon_init_methods           = 3*['swap'], 
        carbon_init_thresholds        = 3*[0],  

        number_of_MBE_steps           = 1,
        logic_state                   = 'X',
        mbe_bases                     = ['Y','Y','Y'],
        MBE_threshold                 = 1,
        RO_C                          = 1,  

        number_of_parity_msmnts       = 2,
        error_on_qubit                = 'all',
        el_RO                         = 'positive',
        debug                         = False,
        error_sign                    = 1,
        error_probability_list        = np.linspace(0,1,3),
        parity_orientations           = ['positive','negative']):

    m = DD.Three_QB_det_QEC(name)
    funcs.prepare(m)

    phase_error                   = error_sign * 2*np.arcsin(np.sqrt(error_probability_list))*180./np.pi
    if error_on_qubit ==1:
        Qe                            = [1,0,0]
    elif error_on_qubit ==2:
        Qe                            = [0,1,0]
    elif error_on_qubit ==3:
        Qe                            = [0,0,1]
    elif error_on_qubit =='all':
        Qe                            = [1,1,1]

    m.params['phase_error_array_1'] = np.transpose([phase_error*Qe[0],phase_error*Qe[1],phase_error*Qe[2]])
    m.params['phase_error_array_2'] = np.transpose([phase_error*0,phase_error*0,phase_error*0])

    m.params['free_evolution_time_1'] = np.array([0])/2.
    m.params['free_evolution_time_2'] = np.array([0])/2.

    m.params['add_wait_gate']  = True
    m.params['wait_in_msm1']  = False

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    m.params['Parity_a_RO_orientation'] = parity_orientations[0]
    m.params['Parity_b_RO_orientation'] = parity_orientations[1]

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 500 

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list
    m.params['MBE_list']            = carbon_list
    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    '''Select right tomography basis '''

    if parity_orientations == ['positive','positive']:
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '',  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]
    
    elif parity_orientations == ['negative','negative']:
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '',  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]
    
    elif parity_orientations == ['positive','negative']:
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '',  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]

    elif parity_orientations == ['negative','positive']:
        m.params['Tomo_Bases_10'] = TD.get_tomo_bases(Flip_qubit = '',  Flip_axis = '', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_11'] = TD.get_tomo_bases(Flip_qubit = '2',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_00'] = TD.get_tomo_bases(Flip_qubit = '3',  Flip_axis = 'Y', RO_list = logic_state+'_list')[RO_C]
        m.params['Tomo_Bases_01'] = TD.get_tomo_bases(Flip_qubit = '1',  Flip_axis = 'Z', RO_list = logic_state+'_list')[RO_C]

    ###################
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
    m.params['electron_readout_orientation'] = el_RO
    
    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':
    
    error_list = {}
    error_list['0'] = [0]#[0,0.5]

    for state in ['X','Y','Z']:
        if state == 'X':
            RO_list = [6]
        elif state == 'Y':
            RO_list = [4,5] 
        elif state == 'Z': 
            RO_list = [0]

        logic_state = state
        # print '-----------------------------------'            
        # print 'press q to stop measurement cleanly'
        # print '-----------------------------------'
        # qt.msleep(2)
        # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            # break
        for error_sign in [1]:
            # print '-----------------------------------'            
            # print 'press q to stop measurement cleanly'
            # print '-----------------------------------'
            # qt.msleep(2)
            # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            #     break
            # GreenAOM.set_power(7e-6)
            # ins_counters.set_is_running(0)  
            # optimiz0r.optimize(dims=['x','y','z'])

            for RO in RO_list:#range(7):
                
                # print '-----------------------------------'            
                # print 'press q to stop measurement cleanly'
                # print '-----------------------------------'
                # qt.msleep(2)
                # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                #     break
                # ssrocalibration(SAMPLE_CFG)
                for k in range(1):
                    e_list = error_list[str(k)]
                    # print '-----------------------------------'            
                    # print 'press q to stop measurement cleanly'
                    # print '-----------------------------------'
                    # qt.msleep(2)
                    # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    #     break
                    MBE(SAMPLE + '00_positive_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO, 
                        logic_state = logic_state,el_RO = 'positive', 
                        error_sign= error_sign, 
                        error_on_qubit = 'all',
                        error_probability_list= e_list,
                        parity_orientations           = ['positive','positive'])

                    MBE(SAMPLE + '00_negative_RO'+str(RO)+'_k'+str(k)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO, 
                        logic_state = logic_state,el_RO = 'negative', 
                        error_sign= error_sign, 
                        error_on_qubit = 'all',
                        error_probability_list= e_list,
                        parity_orientations           = ['positive','positive'])



