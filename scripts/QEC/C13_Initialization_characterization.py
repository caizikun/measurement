"""
Script which performs an electron ramsey experiment after initializing a carbon in the vicinity
"""

import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)



SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


def electronramsey_WithNuclearInit(name,
    Addressed_Carbon=1,
    C_13_init_state='up',
    el_RO_result=0,
    electron_RO='positive',
    no_carbon_init = False):

    m = DD.ElectronRamseyWithNuclearInit(name)

    funcs.prepare(m)

    pts = 20
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['wait_times'] = np.linspace(2000e-9,8000e-9,pts)

    # MW pulses
    m.params['detuning']  = 0.5e6

    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = np.ones(pts) * 360 * m.params['wait_times'] * m.params['detuning']
    m.params['pi2_lengths'] = np.ones(pts) * 16e-9


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['wait_times']/1e-9

    #define everything carbon related
    m.params['Addressed_Carbon']             = Addressed_Carbon
    m.params['C13_init_state']               = C_13_init_state
    m.params['electron_readout_orientation'] = electron_RO
    m.params['C13_MBI_RO_state']             = el_RO_result


    m.params['no_carbon_init']=no_carbon_init 
    if no_carbon_init:
        m.params['Nr_C13_init']                  = 0
        m.params['C13_MBI_threshold_list']      = []
    else:
        m.params['Nr_C13_init']                  = 1
        m.params['C13_MBI_threshold_list']      = [0]


    ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['Nr_parity_msmts']     = 0

    ##########
    # Overwrite certain params to test their influence on the sequence. 
        

    funcs.finish(m, upload=True, debug=False)

def electronramsey_C13Init_Characterization(name,
    Addressed_Carbon=1,
    C_13_init_state='up',
    el_RO_result=0,
    electron_RO='positive'):

    m = DD.ElectronRamseyWithNuclearInit(name)

    funcs.prepare(m)

    pts = 32
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['wait_times'] = np.linspace(0,10000e-9,pts)

    # MW pulses
    m.params['detuning']  = 0.5e6

    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = np.ones(pts) * 360 * m.params['wait_times'] * m.params['detuning']
    m.params['pi2_lengths'] = np.ones(pts) * 16e-9


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['wait_times']/1e-9

    #define everything carbon related
    m.params['Addressed_Carbon']             = Addressed_Carbon
    m.params['C13_init_state']               = C_13_init_state
    m.params['electron_readout_orientation'] = electron_RO
    m.params['C13_MBI_RO_state']             = el_RO_result

    m.params['no_carbon_init']=no_carbon_init # if True, this flag circumvents any carbon initialization. (does not work yet)
    
    if no_carbon_init:
        m.params['Nr_C13_init']                  = 0
        m.params['C13_MBI_threshold_list']      = []
    else:
        m.params['Nr_C13_init']                  = 1
        m.params['C13_MBI_threshold_list']      = [0]


    ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['Nr_parity_msmts']     = 0


    funcs.finish(m, upload=True, debug=False)


def MBE(name, carbon            =   1,               
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],  

        el_RO               = 'positive',
        debug               = False):

    m = DD.Two_QB_Probabilistic_MBE_v3(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 500 

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
    m.params['Tomography Bases'] = TD.get_tomo_bases(nr_of_qubits = 1)
        
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
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0])
    
    funcs.finish(m, upload =True, debug=debug)
   



if __name__ == '__main__':


    for ii in range(50):

        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(4)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        GreenAOM.set_power(5e-6)
        ins_counters.set_is_running(0)  
        optimiz0r.optimize(dims=['x','y','z'])

        
        MBE(SAMPLE+'_init_up_C1_pos', carbon = 1, carbon_init_list =  [1], carbon_init_states = ['up'],  el_RO = 'positive')
        MBE(SAMPLE+'_init_up_C1_neg', carbon = 1, carbon_init_list =  [1], carbon_init_states = ['up'],  el_RO = 'negative')
        
        MBE(SAMPLE+'_init_down_C1_pos', carbon = 1, carbon_init_list =  [1], carbon_init_states = ['down'],  el_RO = 'positive')
        MBE(SAMPLE+'_init_down_C1_neg', carbon = 1, carbon_init_list =  [1], carbon_init_states = ['down'],  el_RO = 'negative')

        MBE(SAMPLE+'_init_no_C1_pos', carbon = 1, carbon_init_list =  [2], carbon_init_states = ['down'],  el_RO = 'positive')
        MBE(SAMPLE+'_init_no_C1_neg', carbon = 1, carbon_init_list =  [2], carbon_init_states = ['down'],  el_RO = 'negative')


        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(4)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        electronramsey_WithNuclearInit(SAMPLE+'_C1_up',
        Addressed_Carbon=1,
        C_13_init_state='up',
        el_RO_result=0,
        electron_RO='positive', no_carbon_init=False)

        electronramsey_WithNuclearInit(SAMPLE+'_C1_down',
        Addressed_Carbon=1,
        C_13_init_state='down',
        el_RO_result=0,
        electron_RO='positive', no_carbon_init=False)

        electronramsey_WithNuclearInit(SAMPLE+'_C1_noInit',
        Addressed_Carbon=1,
        C_13_init_state='up',
        el_RO_result=0,
        electron_RO='positive', no_carbon_init=True)

        ssrocalibration(SAMPLE_CFG)    

    # for ii in range(10):

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     GreenAOM.set_power(5e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z'])    

    #     MBE(SAMPLE+'_init_up_C5_pos', carbon = 5, carbon_init_list =  [5], carbon_init_states = ['up'],  el_RO = 'positive')
    #     MBE(SAMPLE+'_init_up_C5_neg', carbon = 5, carbon_init_list =  [5], carbon_init_states = ['up'],  el_RO = 'negative')
        
    #     MBE(SAMPLE+'_init_down_C5_pos', carbon = 5, carbon_init_list =  [5], carbon_init_states = ['down'],  el_RO = 'positive')
    #     MBE(SAMPLE+'_init_down_C5_neg', carbon = 5, carbon_init_list =  [5], carbon_init_states = ['down'],  el_RO = 'negative')

    #     electronramsey_WithNuclearInit(SAMPLE+'_C5_up',
    #     Addressed_Carbon=5,
    #     C_13_init_state='up',
    #     el_RO_result=0,
    #     electron_RO='positive', no_carbon_init=False)

    #     electronramsey_WithNuclearInit(SAMPLE+'_C5_down',
    #     Addressed_Carbon=5,
    #     C_13_init_state='down',
    #     el_RO_result=0,
    #     electron_RO='positive', no_carbon_init=False)

    #     electronramsey_WithNuclearInit(SAMPLE+'_C5_noInit',
    #     Addressed_Carbon=5,
    #     C_13_init_state='down',
    #     el_RO_result=0,
    #     electron_RO='positive', no_carbon_init=True)

    #     ssrocalibration(SAMPLE_CFG) 

    # for ii in range(10):

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(4)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     GreenAOM.set_power(5e-6)
    #     ins_counters.set_is_running(0)  
    #     optimiz0r.optimize(dims=['x','y','z'])    

    #     MBE(SAMPLE+'_init_up_C2_pos', carbon = 2, carbon_init_list =  [2], carbon_init_states = ['up'],  el_RO = 'positive')
    #     MBE(SAMPLE+'_init_up_C2_neg', carbon = 2, carbon_init_list =  [2], carbon_init_states = ['up'],  el_RO = 'negative')
        
    #     MBE(SAMPLE+'_init_down_C2_pos', carbon = 2, carbon_init_list =  [2], carbon_init_states = ['down'],  el_RO = 'positive')
    #     MBE(SAMPLE+'_init_down_C2_neg', carbon = 2, carbon_init_list =  [2], carbon_init_states = ['down'],  el_RO = 'negative')

    #     electronramsey_WithNuclearInit(SAMPLE+'_C2_up',
    #     Addressed_Carbon = 2,
    #     C_13_init_state ='up',
    #     el_RO_result = 0,
    #     electron_RO='positive', no_carbon_init=False)

    #     electronramsey_WithNuclearInit(SAMPLE+'_C2_down',
    #     Addressed_Carbon=2,
    #     C_13_init_state='down',
    #     el_RO_result=0,
    #     electron_RO='positive', no_carbon_init=False)

    #     electronramsey_WithNuclearInit(SAMPLE+'_C2_noInit',
    #     Addressed_Carbon=2,
    #     C_13_init_state='down',
    #     el_RO_result=0,
    #     electron_RO='positive', no_carbon_init=True)

    #     ssrocalibration(SAMPLE_CFG) 
    
