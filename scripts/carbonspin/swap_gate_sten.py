

## SCRIPT SWAP GATE

import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

##################################################
## FIRST PREPARE CARBONS IN STATE 0 USING SWAP ###
##################################################
####################################################################################################
### APPLY SWAP GATE TO CARBONS. DO THIS MULTIPLE TIMES AND MEASURE FOR THE 6 DIFFERENT BASES ###
####################################################################################################

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

print '@ done SAMPLE and SAMPLE_CFG'

def SWAP(name, 
        carbon                  =   1,               
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0,1],  

        elec_init_state         =   ['Z'],
        RO_after_swap           =   True,
   
        el_RO                   = 'positive',
        debug                   =  False):

    m = DD.Two_QB_Swap_Sten(name)
    
    #RO_basis_list           =   ['Z'], removed

    # Adwin parameters

    print '@ funcs.prepare(m)'
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds
    
    ## Maybe? NEED TO VERIFY. DOES SOLVE PROBLEM OF THIS PARAMETER NOT BEING DEFINED
    'My doubts'
    # m.params['C13_MBI_threshold'] = 0

    #Electron state after carbon initialisation
    m.params['el_after_init']               = '0'

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 300


    ######################################
    ### Carbon Initialization settings ###
    ######################################
    m.params['carbon_init_list']    = [carbon]
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_thresholds)

    ### Carbons to be used
    m.params['carbon_list']         = [carbon]
 

    ##############################
    ### Electron intialisation ###
    ##############################
    m.params['elec_init_state']     = elec_init_state


    ##########################
    ### ELECTRON repumping ###
    ##########################
    m.params['Repump_duration']             = 10e-6
    m.params['after_swap_repump_power']     = 100e-9
    m.params['RO_after_swap']               = RO_after_swap


    ##################################
    ### RO bases (sweep parameter) ###
    ##################################
    # m.params['Tomography Bases'] = TD.get_tomo_bases(nr_of_qubits = 1)
    m.params['Tomography Bases'] = [['X'],['Y'],['Z']]
    # m.params['Tomography Bases'] = [['X'],['Z']]
    # m.params['Tomography Bases'] = [['X']]
    # m.params['Tomography Bases'] = [['Z'],['I']]
    

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
    
    
    ### ###############
    ### Tomo params ###
    ###################
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0])
    
    print '@ funcs.finish'

    ## Change
    funcs.finish(m, upload =True, debug=debug)

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False


if __name__ == '__main__':
    print 'Starting Loop, engage!'

    breakst     = False
    debug       = True

    ''' Non Loop'''
    e = 'Y'
    c = 5
    c_i_t = [0,1]
    RO_after_swap = True
    RO_orientation = 'positive'


    print 'RO_after_swap = ' + str(RO_after_swap)
    print 'carbon initialisation RO threshold = '+ str(c_i_t)

    print 'el_state = ' + str(e)

    SWAP(SAMPLE + '_carbon' + str(c) +'_'+RO_orientation+ '_elState'+str(e)+'_swapRO_'+str(RO_after_swap), 
                    el_RO= RO_orientation, carbon = c
                    ,debug = debug, elec_init_state = e,
                    carbon_init_thresholds = c_i_t)

    print 'Done with non-loop part'

    # RO_orientation = 'negative'

    # SWAP(SAMPLE + '_carbon' + str(c) +'_'+RO_orientation+ '_elState'+str(e)+'_swapRO_'+str(RO_after_swap), 
    #                 el_RO= RO_orientation, carbon = c
    #                 ,debug = debug, elec_init_state = e,
    #                 carbon_init_thresholds = c_i_t)
    

    # '''' NOTE REMOVE RO_after_swap from SWAP params '''
    # breakst     = False
    # debug       = True

    # carbons     = [5]
    # init_method = 'swap'
    # el_state    = ['Y','mZ','Z']
    # RO_after_swap = [True]

    # for r in RO_after_swap:

    #     if r == True:
    #         c_i_t = [0, 1]
    #     else:
    #         c_i_t = [0]    

    #     print 'RO_after_swap = ' + str(RO_after_swap)
    #     print 'carbon initialisation RO threshold = '+ str(c_i_t)


    #     for e in el_state:
    #         print 'Loop over electron state!'
    #         print 'el_state = ' + str(e)

    #         breakst = show_stopper() or breakst
    #         if breakst:
    #             break

    #         for c in carbons:
    #             breakst = show_stopper() or breakst
    #             if breakst:
    #                 break

    #             print 'Loop over carbons number!'

    #             SWAP(SAMPLE + '_carbon' + str(c) + '_elState'+str(e)+'_swapRO_'+str(r)+'_positive', 
    #                 el_RO= 'positive', carbon = c
    #                 ,debug = debug, elec_init_state = e, RO_after_swap = RO_after_swap,
    #                 carbon_init_thresholds = c_i_t)


    #             SWAP(SAMPLE + '_carbon' + str(c) + '_elState'+str(e)+'_swapRO_'+str(r)+'_negative', 
    #                 el_RO= 'negative', carbon = c
    #                  ,debug = debug, elec_init_state = e, RO_after_swap = RO_after_swap,
    #                  carbon_init_thresholds = c_i_t)

    print 'Done with loop part' 
  
else: 
    print 'Fail'
