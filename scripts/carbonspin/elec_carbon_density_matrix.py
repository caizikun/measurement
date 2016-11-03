"""
This script initializes a joint  bell state of electron and 13C.
One then subsequently performs tomograph 
"""

import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

        
def MBE(name, carbon_list   = [1],      

        carbon_init_list        = [1],
        carbon_init_states      = ['up'], 
        carbon_init_methods     = ['MBI'], 
        carbon_init_thresholds  = [1],  

        number_of_MBE_steps = 1,
        mbe_bases           = ['Y'],
        MBE_threshold       = 1,
        number_of_parity_msmnts = 0,
        parity_msmnts_threshold = 1, 
        e_RO_pulse = 'none',

        el_RO               = 'positive',
        debug               = False):

    m = DD.electron_carbon_density_matrix(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 4000 

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

    m.params['Tomography Bases'] = ([
            ['X'],['Y'],['Z']
            ])
    m.params['electron_RO_pulse'] = e_RO_pulse


    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = number_of_MBE_steps
    m.params['MBE_bases']           = mbe_bases
    m.params['MBE_threshold']       = MBE_threshold
    m.params['logical_state'] = 'X'
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = parity_msmnts_threshold
    

    ### Derive other parameters
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0])

    print m.params['sweep_pts']        
  
    funcs.finish(m, upload =True, debug=debug)


def show_stopper(breakst):
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or breakst:
        return True
    else: return False    
    
if __name__ == '__main__':

    breakst = False
    el_RO_pulse = ['mx']#,'x','y','my','none','X']
    el_RO_directions = ['positive','negative']

    for pulse in el_RO_pulse:

        breakst = show_stopper(breakst)
        if breakst:
            break
        for el_RO in el_RO_directions:

            breakst = show_stopper(breakst)
            if breakst:
                break

            # MBE(SAMPLE + 'el_13C_full_sequence_dm_'+pulse+'_'+el_RO, el_RO= el_RO,carbon_list = [4],
            #                     carbon_init_list = [4,4],number_of_MBE_steps=1,
            #                     carbon_init_methods=['swap','MBI'],e_RO_pulse=pulse,
            #                     carbon_init_thresholds = [0,1],debug=False)


            MBE(SAMPLE + 'el_13C_full_sequence_dm_noMBE'+'_'+el_RO, el_RO= el_RO,carbon_list = [4],
                                carbon_init_list = [4,4],number_of_MBE_steps=0,
                                carbon_init_methods=['swap','MBI'],e_RO_pulse=pulse,
                                carbon_init_thresholds = [0,1],debug=False)



