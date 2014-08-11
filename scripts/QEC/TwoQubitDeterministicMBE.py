import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, carbon_list   = [4, 1],               
        
        carbon_init_list        = [4,1],
        carbon_init_states      = ['up','up'], 
        carbon_init_methods     = ['swap','swap'],
        carbon_init_threshold   = 1,  

        mbe_bases           = ['X','X'],
        parity_msmt_basis   = ['X','X'],

        el_RO               = 'positive', 
        debug               = True):

    #TODO_MAR: NOTE: what is the el_RO statement doing in this function?!? 

    ### TODO THT:  Iwant the carbon init_threshold to be a list as well so that the 
    ### ADWIN runs with different thresholds

    m = DD.Two_QB_Det_MBE(name)
   
    funcs.prepare(m)

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 500 
    #m.params['A_SP_amplitude_after_C13_MBE'] = 0e-9 #turn off spin pumping for deterministic
    #m.params['MBE_RO_duration']     = 50            #RO longer for deterministic

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization params 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    ## 'MBI', 'swap', 'mixed'
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ### MBE settings
    m.params['Nr_MBE']              = 0 
    m.params['MBE_bases']           = mbe_bases

        ### Parity measurement settings  
    m.params['Nr_parity_msmts']   = 1     ### Currently just for For ADWIN
    m.params['parity_msmt_basis'] = parity_msmt_basis

    # m.params['Phases_C_A'] = np.ones(m.params['pts'])*0
    # m.params['measZ_C_A']= [False]*m.params['pts'] 
    # m.params['Phases_C_B'] = np.ones(m.params['pts'])*0
    # m.params['measZ_C_B']= [False]*m.params['pts'] 

    ### RO bases (sweep parameter)
    #m.params['Tomography Bases'] = 'full'
    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    m.params['Tomography Bases'] = ([
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    ### Derive other parameters
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []

    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0]+BP[1])
    print 'Tomography bases: %s' %m.params['sweep_pts']        

    ### Overwrite thresholds for quick testing 
    m.params['MBI_threshold']           = 1
    m.params['C13_MBI_threshold']       = carbon_init_threshold 
    m.params['MBE_threshold']           = 1
    m.params['Parity_threshold']        = 1

    funcs.finish(m, upload =True, debug=True)
    
if __name__ == '__main__':

    MBE(SAMPLE)