import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, carbon_list   = [1,4],               
        
        carbon_init_list        = [1],
        carbon_init_states      = ['up'], 
        carbon_init_methods     = ['MBI'],
        carbon_init_threshold   = 1,  

        number_of_MBE_steps = 0,
        mbe_bases           = ['X','X'],
        MBE_threshold       = 1,
        el_RO               = 'positive',
        debug               = False):

    ### TODO THT: I want the carbon init_threshold to be a list as well so that the 
    ### ADWIN runs with different thresholds

    m = DD.Two_QB_Probabilistic_MBE_v3(name)
    funcs.prepare(m)

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 1000 

    if 0: #JUST FOR NOW TURN OF SPIN PUMPING TO COMPARE TO DETERMINSTIC MBE
        m.params['A_SP_amplitude_after_MBE'] = 0e-9
        m.params['MBE_RO_duration']          = 50            


    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization params 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    ## 'MBI', 'swap', 'mixed'
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ### MBE settings
    m.params['Nr_MBE']              = number_of_MBE_steps 
    m.params['MBE_bases']           = mbe_bases

    ### RO bases (sweep parameter)
    #m.params['Tomography Bases'] = 'full'
    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    m.params['Tomography Bases'] = ([
        ['X','I'],['Y','I'],['Z','I']])

    ### Derive other parameters
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []

    ### Parity measurement settings, not used yet, but needed as ADWIN script already loads this  
    m.params['Nr_parity_msmts'] = 0

    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0]+BP[1])
    print m.params['sweep_pts']        

    m.params['C13_MBI_threshold']       = carbon_init_threshold 
    m.params['MBE_threshold']           = MBE_threshold
    m.params['Parity_threshold']        = 1

    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':

    MBE(SAMPLE)