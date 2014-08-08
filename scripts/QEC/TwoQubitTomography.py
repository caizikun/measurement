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
        method_A = 'swap', method_B = 'swap', 
        Only_init_first_Carbon = True, Only_init_second_Carbon= False, 
        probabilistic =0):

    m = DD.Two_QB_Tomography(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = 15
    # Carbon Initialization 
    m.params['Carbon A']        = Carbon_A
    m.params['C_A_init_method'] = method_A
    m.params['C_A_init_state']  = Init_A

    m.params['Carbon B']        = Carbon_B  
    m.params['C_B_init_method'] = method_B
    m.params['C_B_init_state']  = Init_B

    m.params['Only_init_first_Carbon']  = Only_init_first_Carbon
    m.params['Only_init_second_Carbon'] = Only_init_second_Carbon

    # Initial state for Carbon Parity measurement 
    m.params['Phases_C_A'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_A']= [False]*m.params['pts'] 
    m.params['Phases_C_B'] = np.ones(m.params['pts'])*0
    m.params['measZ_C_B']= [False]*m.params['pts'] 

    # Tomography Readout stuff 
    m.params['Tomography Bases'] = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])

    #m.params['Tomography Bases'] = ([['X','Z']])

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

    #Thresholds 
    m.params['MBI_threshold']           = 1
    m.params['C13_MBI_threshold']       = probabilistic #Must be same for both. THT: add functionality to combine methods 

    # Durations 
    m.params['C13_MBI_RO_duration']     = 30 
    m.params['SP_duration_after_C13']   = 50

    # Amplitudes 
    m.params['E_C13_MBI_RO_amplitude']     = 1e-9
    m.params['A_SP_amplitude_after_C13_MBI']  = 15e-9
    m.params['E_SP_amplitude_after_C13_MBI']  = 0e-9 



    ### For faking that the same carbon is initialized 2 times
    #m.params['C4_freq'    ]=m.params['C1_freq'    ]  #NOTE: based on old measurements 
    #m.params['C4_freq_0'  ]=m.params['C1_freq_0'  ]
    #m.params['C4_freq_1'  ]=m.params['C1_freq_1'  ] 
    #m.params['C4_freq_dec']=m.params['C1_freq_dec']

    #m.params['C4_Ren_tau'] =m.params['C1_Ren_tau']   
    #m.params['C4_Ren_N']   =m.params['C1_Ren_N']     

    funcs.finish(m, upload =True, debug=True)

if __name__ == '__main__':

    Two_QB_Tomo(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'up', Init_B = 'up',method_A = 'swap',method_B ='swap', probabilistic =1)
   

    # Two_QB_Tomo(SAMPLE,Carbon_A = 1, Carbon_B = 4, Init_A = 'up', Init_B = 'down',method_A = 'swap',method_B ='swap', probabilistic = 0 )
    # Two_QB_Tomo(SAMPLE,Carbon_A = 1, Carbon_B = 4, Init_A = 'down', Init_B = 'up',method_A = 'swap',method_B ='swap', probabilistic = 0 )
    # Two_QB_Tomo(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'up', Init_B = 'up',method_A = 'swap',method_B ='swap', probabilistic = 0 )
    # Two_QB_Tomo(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'up', Init_B = 'down',method_A = 'swap',method_B ='swap', probabilistic = 0 )
    # Two_QB_Tomo(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'down', Init_B = 'up',method_A = 'swap',method_B ='swap', probabilistic = 0 )
    # Two_QB_Tomo(SAMPLE,Carbon_A = 1, Carbon_B = 4, Init_A = 'up', Init_B = 'up',method_A = 'swap',method_B ='swap', probabilistic = 1 )

    # Two_QB_Tomo(SAMPLE,Carbon_A = 1, Carbon_B = 4, Init_A = 'down', Init_B = 'down',Only_init_second_Carbon=True)

    # # Two_QB_Tomo(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'up', Init_B = 'up',Only_init_second_Carbon=True)

    # Two_QB_Tomo(SAMPLE,Carbon_A = 4, Carbon_B = 1, Init_A = 'down', Init_B = 'down',Only_init_second_Carbon=True)

