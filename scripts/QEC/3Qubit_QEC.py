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
        logic_state         = 'Y',
        mbe_bases           = ['Y','Y','Y'],
        MBE_threshold       = 1,

        number_of_parity_msmnts = 0,
        parity_msmnts_threshold = 1, 
        RO_C                    = 1,
        el_RO               = 'positive',
        debug               = False,
        error_sign          = 1,
        Tomo_bases          = ['Z','-Y','Z']):

    m = DD.Three_QB_QEC(name)
    funcs.prepare(m)

    error_probability_list        = np.linspace(0,1,6)
    phase_error                   = error_sign * 2*np.arcsin(np.sqrt(error_probability_list))*180./np.pi
    Qe                            = [1,1,1]

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


    '''Select right tomography basis '''

    m.params['Tomography Bases'] = TD.get_tomo_bases(Flip_qubit = '',  Flip_axis = '', RO_list = logic_state+'_list')[RO_C-1]



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
    m.params['pts']                 = len(error_probability_list)
    m.params['sweep_name']          = 'Error Probability' 
    m.params['sweep_pts']           = error_probability_list

    ### RO params
    m.params['electron_readout_orientation'] = el_RO
      
    
    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':

    for state in ['Z','mZ','X','mX','Y','mY']:
        logic_state = state
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
        for error_sign in [1,-1]:
            logic_state = state
            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break
            GreenAOM.set_power(10e-6)
            ins_counters.set_is_running(0)  
            optimiz0r.optimize(dims=['x','y','z'])

            for RO in range(7):
                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break
            MBE(SAMPLE + 'positive_RO'+str(RO)+'_sign'+ str(error_sign)+'_'+logic_state,RO_C = RO, 
                logic_state = logic_state,el_RO = 'positive', 
                error_sign= error_sign)
            
            MBE(SAMPLE + 'negative_RO'+str(RO)+'_'+logic_state,RO_C = RO,
                logic_state = logic_state,el_RO = 'negative', 
                    error_sign= e_sign,)


