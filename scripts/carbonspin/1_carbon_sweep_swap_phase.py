"""
Script allows for a sweep of the swap phase that is applied via dynamical decoupling.
This allows for determining an optimal value that might deviate from theory
"""
import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

# import measurement.scripts.lt2_scripts.tools.stools

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False


def MBE(name, carbon            =   1,               
        
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],  

        el_RO               = 'positive',
        tomo                = 'Z',
        debug               = False):

    m = DD.Sweep_Z_init_phase(name)
    funcs.prepare(m)


    m.params['el_after_init']                = '0'


    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 500
    pts = 20
    m.params['init_phase_list'] = np.linspace(-90,90,pts)


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

    m.params['Tomography Bases'] = [[tomo]]*pts
        
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
    m.params['pts']                 = len(m.params['init_phase_list'])
    m.params['sweep_name']          = 'Init_phases' 
    m.params['sweep_pts']           = m.params['init_phase_list']
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    
    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':
    carbons = [1]
    debug = False
    breakst = False


    
    for c in carbons:
        for tomo in ['Z']:
            breakst = show_stopper()
            if breakst:
                break
            MBE(SAMPLE + 'positive_'+str(c)+'_swap_'+tomo, 
                                el_RO = 'positive', 
                                carbon = c, 
                                carbon_init_list = [c],
                                tomo=tomo,
                                debug = debug,
                                carbon_init_methods = ['swap'], 
                                carbon_init_thresholds  =   [0])
