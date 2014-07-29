import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name):

    m = DD.Two_QB_Probabilistic_MBE_v2(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Carbons to be used
    m.params['carbon_list']         = [1,      3]

    ### Carbon Initialization settings 
    m.params['init_method_list']    = ['swap', 'swap']    ## 'MBI', 'swap', 'no'
    m.params['init_state_list']     = ['up',   'down']    ## 'up' or 'down'

    m.params['Only_init_first_Carbon']      = False
    m.params['Only_init_second_Carbon']     = True

    ### RO bases (sweep parameter)
    m.params['reps_per_ROsequence'] = 1000 
    #m.params['Tomography Bases'] = 'full'
    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    ## Alternative bases
    # m.params['Tomography Bases'] = ([['I','X'],
    #        ['I','Y'],
    #        ['I','Z']])

         ## Alternative bases
    m.params['Tomography Bases'] = ([['X','I'],
            ['Y','I'],
            ['Z','I'], 
            ['I','X'],
            ['I','Y'],
            ['I','Z']])
    m.params['pts']                 = len(m.params['Tomography Bases'])

    ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['MBE_bases']           = ['X',    'X'] 

    ### Parity measurement settings  
    m.params['Nr_parity_msmts'] = 0
    m.params['Phases_C_A'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_A']= [False]*m.params['pts'] 
    m.params['Phases_C_B'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_B']= [False]*m.params['pts'] 
    




 

    ### Derive other parameters

    ### number of Carbon spins to initialize
    if m.params['Only_init_first_Carbon'] or m.params['Only_init_second_Carbon']: 
        m.params['Nr_C13_init'] = 1
    else :
        m.params['Nr_C13_init'] = 2
    
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0]+BP[1])
    print m.params['sweep_pts']        

    


    ### Overwrite certain values in msmt_params to test
    
    ### Thresholds 
    m.params['MBI_threshold']           = 1
    m.params['C13_MBI_threshold']       = 1  
    m.params['MBE_threshold']           = 1
    m.params['Parity_threshold']        = 1

    ### Durations 
    m.params['C13_MBI_RO_duration']     = 30 
    m.params['SP_duration_after_C13']   = 50

    m.params['MBE_RO_duration']         = 30
    m.params['SP_duration_after_MBE']   = 50

    m.params['Parity_RO_duration']      = 10

    ### Amplitudes 
    m.params['E_C13_MBI_RO_amplitude']        = 1e-9
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 

    m.params['E_MBE_RO_amplitude']        = 1e-9
    m.params['A_SP_amplitude_after_MBE']  = 15e-9
    m.params['E_SP_amplitude_after_MBE']  = 0e-9 

    m.params['E_Parity_RO_amplitude']     = 1e-9

    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    MBE(SAMPLE)
   
    
