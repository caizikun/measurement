import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Two_QB_Tomo(name,tau = None,
        Carbon_A = 1, Carbon_B = 4, 
        Init_A = 'up', Init_B = 'up',
        Only_init_first_Carbon = False, Only_init_second_Carbon= False):

    m = DD.Two_QB_Tomography(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 15
    # Carbon Initialization 
    m.params['Carbon A'] = Carbon_A
    m.params['C_A_init_method'] = 'swap'
    m.params['C_A_init_state'] = Init_A

    m.params['Carbon B'] = Carbon_B  
    m.params['C_B_init_method'] = 'swap'
    m.params['C_B_init_state'] = Init_B

    m.params['Only_init_first_Carbon'] = Only_init_first_Carbon
    m.params['Only_init_second_Carbon'] = Only_init_second_Carbon



    # Initial state for Carbon Parity measurement 
    m.params['Phases_C_A'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_A']= [False]*m.params['pts'] 
    m.params['Phases_C_B'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_B']= [False]*m.params['pts'] 


    # Tomography Readout stuff 
    m.params['MBE_Bases'] = ['X','X'] 

    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    m.params['sweep_name'] = 'Tomography Bases' 
    m.params['sweep_pts'] =[]
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0]+BP[1])

    print m.params['sweep_pts']        




    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to test
    if m.params['Only_init_first_Carbon'] or m.params['Only_init_second_Carbon']: 
        m.params['Nr_C13_init']= 1
    else :
        m.params['Nr_C13_init']= 2
    m.params['Nr_MBE'] =0
    m.params['Nr_parity_msmts']=0

    #Thresholds 
    m.params['MBI_threshold']           = 1
    m.params['C13_MBI_threshold']       = 0 #Must be same for both. 

    m.params['MBE_threshold']           = 1
    m.params['Parity_threshold']        = 1


    # Durations 
    m.params['C13_MBI_RO_duration']     = 30 
    m.params['SP_duration_after_C13']   = 50

    m.params['MBE_RO_duration']=  10
    m.params['SP_duration_after_MBE'] =  25

    m.params['Parity_RO_duration'] =  10


    # Amplitudes 
    m.params['E_C13_MBI_RO_amplitude']     = 1e-9
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 

    m.params['E_MBE_RO_amplitude']     = 1e-9
    m.params['A_SP_amplitude_after_MBE']  = 15e-9
    m.params['E_SP_amplitude_after_MBE']  = 0e-9 

    m.params['E_Parity_RO_amplitude']     = 1e-9


    # m.params['C4_freq'    ]=m.params['C1_freq'    ]  #NOTE: based on old measurements 
    # m.params['C4_freq_0'  ]=m.params['C1_freq_0'  ]
    # m.params['C4_freq_1'  ]=m.params['C1_freq_1'  ] 
    # m.params['C4_freq_dec']=m.params['C1_freq_dec']

    # m.params['C4_Ren_tau'] =m.params['C1_Ren_tau']   
    # m.params['C4_Ren_N'] =m.params['C1_Ren_N']     

    



    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    Two_QB_Tomo(SAMPLE,Carbon_A = 1, Carbon_B = 4, Init_A = 'up', Init_B = 'up' )
