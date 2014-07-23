import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, tau = None,
        Carbon_A = 1, Carbon_B = 4, 
        Init_A = 'down', Init_B = 'up',
        Only_init_first_Carbon = False, 
        Only_init_second_Carbon= False):

    m = DD.Two_QB_Probabilistic_MBE(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    #### Carbon Initialization settings 
    m.params['Carbon A']            = Carbon_A
    m.params['C_A_init_method']     = 'swap'
    m.params['C_A_init_state']      = Init_A

    m.params['Carbon B']            = Carbon_B  
    m.params['C_B_init_method']     = 'swap'
    m.params['C_B_init_state']      = Init_B

    m.params['Only_init_first_Carbon']      = Only_init_first_Carbon
    m.params['Only_init_second_Carbon']     = Only_init_second_Carbon
    m.params['no_C13_init']                 = 0 # TODO_THT: this does not appear functional yet


    ### Sweep parameters: the readout basis
    m.params['reps_per_ROsequence'] = 1000 #Repetitions of each data point
    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    ### Alternative bases
    m.params['Tomography Bases'] = ([
            ['X','X'],
            ['Y','Y'],
            ['Z','Z']])

    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0]+BP[1])
    print m.params['sweep_pts']        

    ### Parity measurement settings  
    m.params['Phases_C_A'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_A']= [False]*m.params['pts'] 
    m.params['Phases_C_B'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_B']= [False]*m.params['pts'] 

    m.params['MBE_Bases'] = ['X','X'] 
    
    ### Overwrite certain values in msmt_params to test
    
    ### number of Carbon spins to initialize
    if m.params['Only_init_first_Carbon'] or m.params['Only_init_second_Carbon']: 
        m.params['Nr_C13_init'] = 1
    elif m.params['no_C13_init']:
        m.params['Nr_C13_init'] = 0
    else :
        m.params['Nr_C13_init'] = 2
    
    ### number of MBE steps
    m.params['Nr_MBE']          =   1
    m.params['Nr_parity_msmts'] =   0

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

    funcs.finish(m, upload =True, debug=True)

if __name__ == '__main__':
    MBE(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'up', Init_B = 'up' )
