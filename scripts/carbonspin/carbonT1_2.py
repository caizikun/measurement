import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
#from measurement.lib.measurement2.adwin_ssro import pulsar_msmt; reload(pulsar_msmt)
#drom measurement.lib.measurement2.adwin_ssro import ssro


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def NuclearT1_2(name, carbon            =   1,               
        
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],
        el_after_init = '1', 
        free_ev_time = np.r_[15e-3, 250e-3, 500e-3, 1., 2., 5.,10.],

        el_RO               = 'positive',
        debug               = False):
    import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
    m = DD.NuclearT1_2(name)
    funcs.prepare(m)


    m.params['el_after_init']                = el_after_init
    m.params['add_wait_gate'] = True

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 400

    ### Carbons to be used
    m.params['carbon_list']         = [carbon]

    ### Carb

    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['free_evolution_time'] = free_ev_time
    # m.params['free_evolution_time'] = np.r_[10e-4, 50e-4,50e-3,100e-3, 200e-3, 500e-3, 1., 2.,5.]
    m.params['use_shutter'] = 0

    # if el_after_init == '0':
        # m.params['free_evolution_time'] = np.linspace(1e-3, 400e-3,8)
        # m.params['use_shutter'] = False
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

    m.params['reps_per_ROsequence'] = 350

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
    #             carbon_init_methods     P=   ['swap'], carbon_init_thresholds  =   [0], el_after_init= el_after_init)
    reps=250
    el0list = np.linspace(1e-3, 400e-3,8)
    el1list = np.r_[10e-3, 500e-3, 1., 2., 5., 10.]

    print ((len(el1list) + len(el0list))*50e-3 + (np.sum(el0list)+np.sum(el1list)))*2*reps / 3600

    # NuclearT1_2(SAMPLE + 'positive_5_swap', el_RO= 'positive', carbon = 5, carbon_init_list = [5], el_after_init= '1')

    # carbon_list = [5,1,2]
    # el_RO_list = ['positive','negative']
    # el_after_init_list = ['0','1']
    #el_RO='negative'
    #carbon = 2
    #el_after_init = '1'
    #NuclearT1_2(SAMPLE + '_'+ el_RO +'_C' + str(carbon) +'_el' + el_after_init +'_partTEST', el_RO= 'negative', carbon = carbon, carbon_init_list = [carbon]
    #                                         ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0], el_after_init = '1',
    #                                         free_ev_time = np.array([50.]))
    #daf
    
    #execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\electron_T1_using_DD_class.py')
    FET_dict = {}
    FET_dict['2'] = [np.linspace(0.0006,0.05,9),np.linspace(0.05,0.5,11)[1::],np.linspace(0.5,1.0,6)[1::],np.linspace(1.0,1.5,4)[1::],np.linspace(1.5,2.0,3)[1::],np.linspace(2.0,3.0,3)[1::]]
    FET_dict['1'] = [np.linspace(0.0006,0.05,9),np.linspace(0.05,0.5,11)[1::],np.linspace(0.5,1.0,6)[1::],np.linspace(1.0,1.5,4)[1::]]
    FET_dict['5'] = [np.linspace(0.0006,0.05,9),np.linspace(0.05,0.5,11)[1::],np.linspace(0.5,1.0,6)[1::]]
    FET_dict['6'] = FET_dict['5']
    FET_dict['3'] = FET_dict['5']
    if True:
        carbon_list = [2,5,6,3,1]
        el_RO_list = ['positive','negative']
        # el_RO_list = ['positive']
        # carbon_list = [1]
        el_after_init_list = ['0']
        #FET = [np.linspace(0.0006,0.05,9),np.linspace(0.05,0.5,11)[1::],np.linspace(0.5,1.0,6)[1::],np.linspace(1.0,1.5,4)[1::],np.linspace(1.5,2.0,3)[1::],np.linspace(2.0,3.0,3)[1::],np.linspace(3.0,3.5,1)[1::]]
        stop = False
        #FET_parts= len(FET)
        #FET = EvoTime_arr=np.r_[np.linspace(500e-6,50e-3,10),60e-3,80e-3]
        for carbon in carbon_list:
            FET = FET_dict[str(carbon)]
            FET_parts = len(FET)
            if stop:
                break
            if carbon == 2:
                el_RO_list = ['negative']
            for el_RO in el_RO_list:
                if stop:
                    break
                for el_after_init in el_after_init_list:
                    if stop:
                        break
                    for ii in range(FET_parts):
                        print '--------------------------------'
                        print 'press q to stop measurement loop'
                        print '--------------------------------'
                        qt.msleep(5)
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            stop=True
                            break
                        GreenAOM.set_power(25e-6)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=180)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        # MBE(SAMPLE + '_'+ el_RO +'_' + str(carbon) +'_el' + el_after_init +'swap', el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon]
                        #                          ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])  
                        NuclearT1_2(SAMPLE + '_'+ el_RO +'_C' + str(carbon) +'_el' + el_after_init +'_part'+str(ii+1), el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon]
                                                ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0], el_after_init = el_after_init,
                                               free_ev_time = FET[ii])
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        #ssrocalibration(SAMPLE)
        adwin.start_set_dio(dio_no=4,dio_val=0)


    if False:
        carbon_list = [2,1]
        el_RO_list = ['positive','negative']
        # el_RO_list = ['positive']
        # carbon_list = [1]
        el_after_init_list = ['1']
        FET = [np.r_[20e-3,250e-3,500e-3,1.,2.,5.],np.r_[20e-3,10.,20.],np.array([20e-3,35.]),np.array([20e-3,50.])]
        FET_parts= len(FET)
        #FET = EvoTime_arr=np.r_[np.linspace(500e-6,50e-3,10),60e-3,80e-3]
        for carbon in carbon_list:
            for el_RO in el_RO_list:
                for el_after_init in el_after_init_list:
                    for ii in range(FET_parts):
                        print '--------------------------------'
                        print 'press q to stop measurement loop'
                        print '--------------------------------'
                        qt.msleep(5)
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            break
                        GreenAOM.set_power(25e-6)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=180)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        # MBE(SAMPLE + '_'+ el_RO +'_' + str(carbon) +'_el' + el_after_init +'swap', el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon]
                        #                          ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])  
                        NuclearT1_2(SAMPLE + '_'+ el_RO +'_C' + str(carbon) +'_el' + el_after_init +'_part'+str(ii+1), el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon]
                                                ,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0], el_after_init = el_after_init,
                                               free_ev_time = FET[ii])
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        execfile('QEC/QEC_ssro_calibration.py')
                        #ssrocalibration(SAMPLE)
        adwin.start_set_dio(dio_no=4,dio_val=0)


    # execfile(r'D:\measuring\measurement\scripts\QEC\NuclearT1_2.py')

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
