import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def NuclearT1_2(name, carbon            =   1,               
        
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],
        el_after_init = '1', 

        el_RO               = 'positive',
        debug               = False):

    m = DD.NuclearT1_2(name)
    funcs.prepare(m)


    m.params['el_after_init']                = el_after_init
    m.params['add_wait_gate'] = True

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 250

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

    m.params['free_evolution_time'] = np.r_[15e-3, 250e-3, 500e-3, 1., 2., 5.]
    # m.params['free_evolution_time'] = np.r_[10e-4, 50e-4,50e-3,100e-3, 200e-3, 500e-3, 1., 2.,5.]
    m.params['use_shutter'] = 1

    if el_after_init == '0':
        m.params['free_evolution_time'] = np.linspace(1e-3, 400e-3,8)
        m.params['use_shutter'] = False
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
    m.params['pts']                 = len(m.params['free_evolution_time'])
    m.params['sweep_name']          = 'Free_evolution_time' 
    m.params['sweep_pts']           = m.params['free_evolution_time']
    m.params['Tomography Bases'] = [['Z']]*m.params['pts']
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    
    funcs.finish(m, upload =True, debug=debug)


def MBE(name, carbon            =   1,               
        
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],  

        el_RO               = 'positive',
        debug               = False):

    m = DD.Two_QB_Probabilistic_MBE_v3(name)
    funcs.prepare(m)


    m.params['el_after_init']                = '1'


    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 250

    ### Carbons to be used
    m.params['carbon_list']         = [carbon]

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)
    m.params['use_shutter'] = 1
    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['Tomography Bases'] = TD.get_tomo_bases(nr_of_qubits = 1)
    # m.params['Tomography Bases'] = [['X'],['Y'],['Z']]
    m.params['Tomography Bases'] = [['Z']]
        
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

def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    
    if RO_power != None: 
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None: 
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')
    
    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 15e-9#20e-9
    m.run()
    m.save('ms1')

    m.finish()

    
if __name__ == '__main__':


    # for el_after_init in el_after_init_list:
    #     for el_RO in el_RO_list:
    #         NuclearT1_2(SAMPLE + el_RO + '_C5_el' + el_after_init, el_RO= el_RO, carbon = 5, carbon_init_list = [5],
    #             carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0], el_after_init= el_after_init)
    reps=250
    el0list = np.linspace(1e-3, 400e-3,8)
    el1list = np.r_[10e-3, 500e-3, 1., 2., 5., 10.]

    print ((len(el1list) + len(el0list))*50e-3 + (np.sum(el0list)+np.sum(el1list)))*2*reps / 3600

    # NuclearT1_2(SAMPLE + 'positive_5_swap', el_RO= 'positive', carbon = 5, carbon_init_list = [5], el_after_init= '1')

    carbon_list = [5,1,2]
    el_RO_list = ['positive','negative']
    el_after_init_list = ['0','1']

    carbon_list = [2]
    el_RO_list = ['positive','negative']
    el_after_init_list = ['1']

    for carbon in carbon_list:
        for el_RO in el_RO_list:
            for el_after_init in el_after_init_list:
                print '--------------------------------'
                print 'press q to stop measurement loop'
                print '--------------------------------'
                qt.msleep(5)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break
                adwin.start_set_dio(dio_no=4,dio_val=0)
                ssrocalibration(SAMPLE)
                GreenAOM.set_power(25e-6)
                adwin.start_set_dio(dio_no=4,dio_val=0)
                optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
                adwin.start_set_dio(dio_no=4,dio_val=0)
                ssrocalibration(SAMPLE)
                adwin.start_set_dio(dio_no=4,dio_val=0)
                # MBE(SAMPLE + '_'+ el_RO +'_' + str(carbon) +'_el' + el_after_init +'swap', el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon]
                #                          ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])  
                NuclearT1_2(SAMPLE + '_'+ el_RO +'_' + str(carbon) +'_el' + el_after_init, el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon]
                                         ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0], el_after_init = el_after_init)


    # execfile(r'D:\measuring\measurement\scripts\QEC\1Carbon_XY4_C2.py')

    # NuclearT1_2(SAMPLE + 'positive_5_swap', el_RO= 'positve', carbon = 5, carbon_init_list = [5],
    #             carbon_init_methods     =   ['swap'], carbon_init_thresholds  =  [0], el_after_init= '1')

    # el_after_init_list = ['1']
    # el_RO_list = ['positive','negative']
     
    # for el_after_init in el_after_init_list:
    #     for el_RO in el_RO_list:
    #         print '--------------------------------'
    #         print 'press q to stop measurement loop'
    #         print '--------------------------------'
    #         qt.msleep(5)
    #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #             break
    #         GreenAOM.set_power(20e-6)
    #         optimiz0r.optimize(dims=['x','y','z'])
    #         MBE(SAMPLE + 'positive_5_swap', el_RO= 'positive', carbon = 5, carbon_init_list = [5]
    #                                     ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])
    #         NuclearT1_2(SAMPLE + el_RO + '_C5_el' + el_after_init, el_RO= el_RO, carbon = 5, carbon_init_list = [5],
    #             carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0], el_after_init= el_after_init)
    #         MBE(SAMPLE + 'positive_5_swap', el_RO= 'positive', carbon = 5, carbon_init_list = [5]
    #                                     ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])           
