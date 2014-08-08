import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, nr_mbe = 1 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive', part = None):

    m = DD.Two_QB_Probabilistic_MBE_v2(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Carbons to be used
    m.params['carbon_list']         = [4,      1]

    ### Carbon Initialization settings 
    m.params['init_method_list']    = ['swap', 'swap']    ## 'MBI', 'swap', 'mixed'
    m.params['init_state_list']     = init_states #['up',   'up']    ## 'up' or 'down'


    m.params['Only_init_first_Carbon']      = False
    m.params['Only_init_second_Carbon']     = False

    m.params['electron_readout_orientation'] = el_RO
    # #switch to other frame
    # m.params['C13_X_phase'] = 90
    # m.params['C13_Y_phase'] = 0

    ### RO bases (sweep parameter)
    m.params['reps_per_ROsequence'] = 500 
    #m.params['Tomography Bases'] = 'full'
    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    m.params['Tomography Bases'] = ([
           ['Z','Z']])

    # Alternative bases
    if nr_mbe ==  2 and part == '1_qubit':
        m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z']])

    elif nr_mbe == 2 and part == '2_qubit':   
        m.params['Tomography Bases'] = ([
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    if nr_mbe == 3: 
         m.params['Tomography Bases'] = ([
               ['Z','I'],
               ['I','Z'],
               ['Z','Z']
               ])

    m.params['pts']                 = len(m.params['Tomography Bases'])

    ### MBE settings
    m.params['Nr_MBE']              = nr_mbe #1
    m.params['MBE_bases']           = mbe_bases# ['X',    'X'] 

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

    funcs.finish(m, upload =True, debug=True)

    # ### Optimize position
    # qt.msleep(2)
    # AWG.clear_visa()
    # stools.turn_off_all_lt2_lasers()
    # qt.msleep(1)
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])

if __name__ == '__main__':

    MBE(SAMPLE)

    # MBE(SAMPLE+'0_init_XX_p', nr_mbe =0 ,init_states = ['up','up'], el_RO = 'positive'  )
    # MBE(SAMPLE+'0_init_XX_n', nr_mbe =0 , init_states = ['up','up'], el_RO = 'negative'  )

    # MBE(SAMPLE+'0_init_X-X_p', nr_mbe =0 ,init_states = ['up','down'], el_RO = 'positive'  )
    # MBE(SAMPLE+'0_init_X-X_n', nr_mbe =0 , init_states = ['up','down'], el_RO = 'negative'  )

    # MBE(SAMPLE+'1_init_XX_XX_uu_p', nr_mbe =1 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive'  )
    # MBE(SAMPLE+'1_init_XX_XX_uu_n', nr_mbe =1 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'negative'  )

    # MBE(SAMPLE+'1_X-X_uu_p', nr_mbe =1 , mbe_bases = ['X','-X'], init_states = ['up','up'], el_RO = 'positive'  )
    # MBE(SAMPLE+'2_X-X_uu_n', nr_mbe =2 , mbe_bases = ['X','-X'], init_states = ['up','up'], el_RO = 'negative'  )

    # MBE(SAMPLE+'2_XX_uu_p', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive', part = '2_qubit')
    # MBE(SAMPLE+'2_XX_uu_n', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'negative', part = '2_qubit')

    # MBE(SAMPLE+'2_XX_uu_p', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive', part = '1_qubit')
    # MBE(SAMPLE+'2_XX_uu_n', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'negative', part = '1_qubit')

    # MBE(SAMPLE+'2_XX_ud_p', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','down'], el_RO = 'positive', part = '2_qubit')
    # MBE(SAMPLE+'2_XX_ud_n', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','down'], el_RO = 'negative', part = '2_qubit')

    # MBE(SAMPLE+'2_XX_ud_p', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','down'], el_RO = 'positive', part = '1_qubit')
    # MBE(SAMPLE+'2_XX_ud_n', nr_mbe =2 , mbe_bases = ['X','X'], init_states = ['up','down'], el_RO = 'negative', part = '1_qubit')
  
    # MBE(SAMPLE+'3_XX_uu_p', nr_mbe =3 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive'  )
    # MBE(SAMPLE+'3_XX_uu_n', nr_mbe =3 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'negative'  )

    # MBE(SAMPLE+'4_XX_uu_p', nr_mbe =4 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive'  )
    # MBE(SAMPLE+'4_XX_uu_n', nr_mbe =4 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'negative'  )
  
    # MBE(SAMPLE+'1_XX_uu_p', nr_mbe =1 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'positive'  )
    # MBE(SAMPLE+'1_XX_uu_n', nr_mbe =1 , mbe_bases = ['X','X'], init_states = ['up','up'], el_RO = 'negative'  )
   
    # MBE(SAMPLE+'1_XX_ud_p', nr_mbe =1 , mbe_bases = ['X','X'], init_states = ['up','down'], el_RO = 'positive'  )
    # MBE(SAMPLE+'1_XX_ud_n', nr_mbe =1 , mbe_bases = ['X','X'], init_states = ['up','down'], el_RO = 'negative'  )
