import numpy as np
import qt 
import msvcrt

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

    
    ### tomoraphy bases for determining the fidelity of the logical states.
    Tomo_bases_Z = ([['I','I','X'],['I','X','I'],['X','I','I'], ['I','X','X'], ['X','I','X'], ['X','X','I'], ['X','X','X']])
    Tomo_bases_X = ([['I','X','X'],['X','I','X'],['X','X','I'], ['Y','Y','Z'], ['Y','Z','Y'], ['Z','Y','Y'], ['Z','Z','Z']])
    Tomo_bases_Y = ([['I','X','X'],['X','I','X'],['X','X','I'], ['Y','Y','Y'], ['Y','Z','Z'], ['Z','Y','Z'], ['Z','Z','Y']])
    



    Tomo_bases = [['Y','Y','Y'],['Z','Z','Z']]
    # Tomo_bases = [['X','X'],['Y','Y'],['Z','Z']]
    #[1,2,3], is missing
    carbon_combinations = [[1,2,5],[1,2,6],[1,3,5],[1,3,6],[1,5,6],[2,3,5],[2,3,6],[2,5,6],[3,5,6]]
    carbon_combinations = [[1,2,3]]
    for kk in carbon_combinations:
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

            #str(kk[2])+
        MBE(SAMPLE +'_positive_'+str(kk[0])+str(kk[1])+str(kk[2])+'_init', el_RO= 'positive',Tomo_bases = Tomo_bases,carbon_list=kk,carbon_init_list=kk,logic_state='Y')
        MBE(SAMPLE +'_negative_'+str(kk[0])+str(kk[1])+str(kk[2])+'_init', el_RO= 'negative',Tomo_bases = Tomo_bases,carbon_list=kk,carbon_init_list=kk,logic_state='Y')

        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(3)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
        
        # stools.turn_off_all_lt2_lasers()
        # GreenAOM.set_power(7e-6)
        # optimiz0r.optimize(dims=['x','y','z'])

