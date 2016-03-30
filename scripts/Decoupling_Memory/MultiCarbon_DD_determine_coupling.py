"""
Script for a carbon Hahn echo sequence.
Initialization:
- Initializes in the 1 state using Swap
- Can set the electron state by setting the MBI succes condition

Hahn echo
- Applies two pi / 2 pulses along x-axis to apply one pi pulse

Measurement
- Measures Carbon state along X,Y,Z axis. Should allign along Z.
"""
import numpy as np
import qt 
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Multi_C_DD(name,   
        carbon_init_list        = [1,2],
        carbon_init_states      = 2*['up'], 
        carbon_init_methods     = 2*['swap'], 
        carbon_init_thresholds  = 2*[0],   
        el_RO                   = 'positive',
        el_after_init           = 1,
        
        C13_DD_scheme           = 'auto',
        pulses                  = 1,
        wait_gate               = True,
        free_evolution_time     = np.zeros((1)),
        single_Tomo_basis       = ['X','X'],

        number_of_MBE_steps = 1,
        logic_state         ='X',
        classical_state     = ['X','X'],
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,

        mode                    = 'Sweep evolution time',
        debug                   = True):

    m = DD.MultiNuclearDD(name)
    funcs.prepare(m)

    '''Set parameters'''
    print free_evolution_time

    m.params['wait_gate'] = wait_gate
    m.params['C13_DD_Scheme'] = C13_DD_scheme
    m.params['el_after_init'] = el_after_init 
    m.params['Decoupling_pulses']=pulses
    if mode == 'Sweep RO evolution time':
        m.params['reps_per_ROsequence'] = 250
    elif mode == 'Sweep phase':
        m.params['reps_per_ROsequence'] = 350
        m.params['use_shutter'] = 0
    else:
        m.params['reps_per_ROsequence'] = 350
        m.params['use_shutter'] = 1

    m.params['carbon_init_list']        = carbon_init_list
    m.params['init_method_list']        = carbon_init_methods    
    m.params['init_state_list']         = carbon_init_states 
    m.params['C13_MBI_threshold_list']  = carbon_init_thresholds
    m.params['Nr_C13_init']             = len(carbon_init_list) - carbon_init_states.count('M')
    m.params['electron_readout_orientation'] = el_RO

    ####################
    ### MBE settings ###
    ####################
    if logic_state == 'classical':
        m.params['Nr_MBE']                 = 0
        m.params['MBE_threshold']          = 0
    else:
        m.params['Nr_MBE']                 = number_of_MBE_steps
        m.params['MBE_threshold']          = MBE_threshold

    m.params['MBE_bases']              = mbe_bases
    
    if 'p' in logic_state:
        logic_state = logic_state[1]
    m.params['2qb_logical_state']      = logic_state
    m.params['2C_RO_trigger_duration'] = 150e-6

    m.params['Nr_parity_msmts']     = 0
    m.params['classical_state']     = classical_state
    # m.params['use_shutter'] = 1

    #############################
    ### Option 1; Sweep phase ###
    #############################

    if mode == 'Sweep phase':
        m.params['Tomography Bases'] = single_Tomo_basis
        m.params['pts'] = len(m.params['Tomography Bases'])
        m.params['free_evolution_time'] = free_evolution_time*m.params['pts']
        m.params['free_evolution_time_RO'] = free_evolution_time*m.params['pts']
        m.params['sweep_name'] = 'Tomography bases'
        m.params['sweep_pts']  = []
        for BP in m.params['Tomography Bases']:
            m.params['sweep_pts'].append(''.join([str(s) for s in BP]))

    ######################################
    ### Option 2; Sweep evolution time ###
    ######################################


    elif mode == 'Sweep evolution time':
        m.params['free_evolution_time'] = free_evolution_time
        m.params['free_evolution_time_RO'] = free_evolution_time
        m.params['pts'] = len(m.params['free_evolution_time'])
        m.params['sweep_name'] = 'Free evolution time (s)'
        m.params['sweep_pts']  = m.params['free_evolution_time']*2*pulses 
        m.params['Tomography Bases'] = m.params['pts']*single_Tomo_basis

    ####################################################
    ### Option 3; Sweep assymetric RO evolution time ###
    ####################################################
  
    elif mode == 'Sweep RO evolution time':
        Diff_FET = np.linspace(-15e-3,15e-3,9)
        m.params['pts'] = len(Diff_FET)
        m.params['free_evolution_time'] = m.params['pts']*[20e-3]
        m.params['free_evolution_time_RO'] = Diff_FET+20e-3

        m.params['sweep_name'] = 'Delta Free Evolution time (ms)'
        m.params['sweep_pts']  =  Diff_FET*1e3
        m.params['Tomography Bases'] = m.params['pts']*[single_Tomo_basis]

    else:
        raise Exception('Mode not recognized')

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

def qstop(sleep=2):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

def Carbon_DD_mult_msmts(DD_scheme='XY4',carbons=[1],pulses_list=[4],el_ROs=['positive'],optimize=True, ssrocalib=True, 
    Max_FET_Dict = {'1': 1.3,'4': 2.25,'8': 3.0,'16': 5.,'32': 7.}, timepart_Dict ={'1': 1,'4': 2,'8': 4,'16': 8,'32': 8},
    debug=False, datapoints = 8, time_min= 20e-3):
    counter = 0
    for carbon in carbons:
        if qstop():
            break
        for pulses in pulses_list:
            if qstop():
                break
            FET = np.linspace(max(time_min/(2*pulses),1.5e-3),Max_FET_Dict[str(pulses)]/(2*pulses),datapoints)
            print FET
            indexer = datapoints/timepart_Dict[str(pulses)]
            for el_RO in el_ROs:
                if qstop():
                    break
                for timepart in range(timepart_Dict[str(pulses)]):
                    if qstop():
                        break
                    if ssrocalib and not debug:
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        ssrocalibration(SAMPLE)
                    if optimize and not debug:
                        GreenAOM.set_power(20e-6)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
                    if ssrocalib and not debug:
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        ssrocalibration(SAMPLE)
                    counter +=1    
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    msmtstr = SAMPLE+'_'+ DD_scheme +'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses).zfill(2) + '_part' + str(timepart+1)
                    # Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = pulses, C13_DD_scheme=DD_scheme, debug=debug, free_evolution_time=FET[timepart*indexer:(timepart+1)*indexer])
                    print "Counter", counter
        

if __name__ == '__main__':
    if False:
        mode = 'Sweep evolution time'
        DD_scheme = 'auto'
        carbons = [1,2]
        logic_state = 'pX'
        single_Tomo_basis = ['X','X']
        el_RO_list = ['positive']
        pulses = 1
        ii = 0
        el_after_init = 1
        mode = 'Sweep evolution time'
        for el_RO in el_RO_list:
            msmtstring = SAMPLE + '_sweep_evolution_time_'+ DD_scheme + '_C' + '&'.join([str(s) for s in carbons]) + '_Logic' +logic_state    \
                                            + '_Tomo' +  ''.join([str(s) for s in single_Tomo_basis]) +'_RO' + el_RO + '_el' + str(el_after_init)       \
                                            + '_N' + str(pulses).zfill(2) + '_part' +str(ii+1).zfill(2)
            Multi_C_DD(msmtstring,  
                carbon_init_list        = carbons,  
                el_RO                   = el_RO,
                el_after_init           = el_after_init,
                
                C13_DD_scheme           = DD_scheme,
                pulses                  = pulses,
                single_Tomo_basis       = [single_Tomo_basis],
                free_evolution_time     = np.array([2e-3]),
                wait_gate               = True,

                logic_state             = logic_state,

                mode                    = mode,
                debug                   = debug)
            adwin.start_set_dio(dio_no=4,dio_val=0)

    # carbons_init_list = [[1, 2], [1, 3],  [1, 6], [2, 3], [2, 6],  [3, 6], [5, 6], [1, 5], [3, 5]] 
    # carbons_init_list = [[2,5]]
    carbons_init_list = [[1,2]]
    full_Tomo_basis_list = ([['X','X'],['Y','Y'],['Z','Z']])
    # full_Tomo_basis_list = ([['X','X']])
    pulses_list = [4]
    maxtimes_list = [1.1,2.15,2.8]
    maxtimes_list = [1.5]
    FET_parts_list  = [2]
    el_RO_list = ['positive','negative']
    logic_state_list = ['mX']
    TomoCheck = True
    RunMsmt = True
    DD_scheme = 'auto'
    optimize = True
    ssrocalib = True
    debug = False
    sleep = 2
    if True:
        for single_Tomo_basis in full_Tomo_basis_list:
            if qstop(sleep=sleep):
                break
            for carbons in carbons_init_list:
                if qstop(sleep=sleep):
                    break
                for pp, pulses in enumerate(pulses_list):
                    if qstop(sleep=sleep):
                        break
                    FET = np.linspace(max(0.02/(2*pulses),2e-3),maxtimes_list[pp]/(2*pulses),8)
                    FET_parts = FET_parts_list[pp]
                    print FET
                    if ssrocalib and RunMsmt and not debug:
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        ssrocalibration(SAMPLE)
                    for logic_state in logic_state_list:
                        print 

                        if qstop(sleep=sleep):
                            break
                        for el_RO in el_RO_list:
                            if qstop(sleep=sleep*3):
                                break
                            if TomoCheck:
                                if optimize and RunMsmt and not debug:
                                    GreenAOM.set_power(20e-6)
                                    adwin.start_set_dio(dio_no=4,dio_val=0)
                                    optimiz0r.optimize(dims=['x','y','z'], int_time=200)
                                msmtstring = SAMPLE + '_TomoCheck_'+ DD_scheme + '_C' + '&'.join([str(s) for s in carbons]) + '_Logic' +logic_state    \
                                + '_Tomo' +  ''.join([str(s) for s in single_Tomo_basis]) +'_RO' + el_RO + '_el' + str(el_after_init)       \
                                + '_N' + str(pulses).zfill(2) 
                                adwin.start_set_dio(dio_no=4,dio_val=0)
                                Multi_C_DD(msmtstring,  
                                    carbon_init_list        = carbons,  
                                    el_RO                   = el_RO,
                                    el_after_init           = el_after_init,
                                    
                                    C13_DD_scheme           = 'No_DD',
                                    pulses                  = pulses,
                                    single_Tomo_basis       = [single_Tomo_basis],
                                    free_evolution_time     = [0.001],
                                    wait_gate               = False,

                                    logic_state             = logic_state,

                                    mode                    = 'Sweep phase',
                                    debug                   = debug)
                            if RunMsmt:
                                for ii in range(FET_parts):
                                    if qstop(sleep=sleep*3):
                                        break
                                    if optimize and RunMsmt and not debug:
                                        GreenAOM.set_power(20e-6)
                                        adwin.start_set_dio(dio_no=4,dio_val=0)
                                        optimiz0r.optimize(dims=['x','y','z'], int_time=180)
                                    adwin.start_set_dio(dio_no=4,dio_val=0)
                                    msmtstring = SAMPLE + '_sweep_evolution_time_'+ DD_scheme + '_C' + '&'.join([str(s) for s in carbons]) + '_Logic' +logic_state    \
                                    + '_Tomo' +  ''.join([str(s) for s in single_Tomo_basis]) +'_RO' + el_RO + '_el' + str(el_after_init)       \
                                    + '_N' + str(pulses).zfill(2) + '_part' +str(ii+1).zfill(2)
                                    Multi_C_DD(msmtstring,  
                                        carbon_init_list        = carbons,  
                                        el_RO                   = el_RO,
                                        el_after_init           = el_after_init,
                                        
                                        C13_DD_scheme           = DD_scheme,
                                        pulses                  = pulses,
                                        single_Tomo_basis       = [single_Tomo_basis],
                                        free_evolution_time     = FET[ii::FET_parts],
                                        wait_gate               = True,

                                        logic_state             = logic_state,

                                        mode                    = mode,
                                        debug                   = debug)
                                    adwin.start_set_dio(dio_no=4,dio_val=0)


    if ssrocalib and RunMsmt and not debug:
        adwin.start_set_dio(dio_no=4,dio_val=0)
        ssrocalibration(SAMPLE)
    all_carbons = [1,2,3,5,6]
    carbons_init_list = []
    for carbon in all_carbons:
        for carbon2 in all_carbons:
            if carbon != carbon2 and [carbon2, carbon] not in carbons_init_list:
                carbons_init_list.append([carbon,carbon2])

    carbons_init_list = [[1, 2], [1, 3],  [1, 6], [2, 3], [2, 6],  [3, 6], [5, 6], [1, 5], [3, 5]]
    max_time = [0.5,0.35,0.72,0.3,0.5,0.45,0.3]

    pulses = 4
    # carbons_init_list = [[3,6],[1,3],[2,6]]
    # FET = np.linspace(0.005,1./(2.*pulses),10)
    FET_parts = 5

    DD_scheme = 'auto'
    el_after_init = 1
    optimize = True
    ssrocalib = True
    # FET = [0.015/(2.*pulses)]
    # FET = np.linspace(0.016/(2.*pulses),0.5/(2.*pulses),12)
    # FET_parts = 12
    # logic_state_list = ['mX','pX']
    # logic_state_list = ['mX']
    TomoCheck = True
    RunMsmt = True
    debug = False
    sleep = 2
    #full_Tomo_basis_list = ([['X','X'], ['Y','Y'], ['Z','Z']])

    # FET = np.linspace(0.04/(2.*pulses),0.8/(2.*pulses),9)
    # FET_parts = 8
    # carbons_init_list = [[1,5]]
    full_Tomo_basis_list = ([['I','X']])

    # TomoCheck = True
    # FET = np.array([0.004])
    # FET_parts = 1
    # pulses = 4
    # carbons_init_list = [[1,2]]
    # ssrocalib = False
    # optimize = False
    # full_Tomo_basis_list = ([['X','X']])

    # full_Tomo_basis_list = ([['DFS']])
    # el_RO_list = ['positive','negative']
    el_RO_list = ['positive','negative']
    if False:
        for single_Tomo_basis in full_Tomo_basis_list:
            if qstop(sleep=sleep):
                break
            for cc,carbons in enumerate(carbons_init_list):
                FET = np.linspace(0.005,max_time[cc]/(2.*pulses),10)
                if qstop(sleep=sleep):
                    break
                if ssrocalib and not debug and RunMsmt:
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    ssrocalibration(SAMPLE)
                for el_RO in el_RO_list:
                    if qstop(sleep=sleep):
                        breaks
                    if optimize and not debug and RunMsmt:
                        GreenAOM.set_power(20e-6)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        optimiz0r.optimize(dims=['x','y','z'], int_time=180)
                    if TomoCheck:
                        msmtstring = SAMPLE + '_TomoCheck_No_DD_C' + '&'.join([str(s) for s in carbons])  \
                        + '_initXX_TomoXX_RO' + el_RO + '_el' + str(el_after_init)        \
                        + '_N' + str(0).zfill(2) 
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        Multi_C_DD(msmtstring,  
                            carbon_init_list        = carbons,  
                            el_RO                   = el_RO,
                            el_after_init           = el_after_init,
                            
                            C13_DD_scheme           = 'No_DD',
                            pulses                  = pulses,
                            single_Tomo_basis       = [['X','X']],
                            free_evolution_time     = [0.005],
                            wait_gate               = False,

                            logic_state             = 'classical',
                            classical_state         = ['X','X'],

                            mode                    = 'Sweep phase',
                            debug                   = debug)
                        # Multi_C_DD(msmtstring,  
                        #     carbon_init_list        = carbons,  
                        #     el_RO                   = el_RO,
                        #     el_after_init           = el_after_init,
                            
                        #     C13_DD_scheme           = 'No_DD',
                        #     pulses                  = 0,
                        #     single_Tomo_basis       = [['X','X']],
                        #     free_evolution_time     = [0.01],
                        #     wait_gate               = False,

                        #     logic_state             = 'classical',
                        #     classical_state         = ['X','X'],

                        #     mode                    = 'Sweep phase',
                        #     debug                   = debug)
                    if RunMsmt:
                        for ii in range(FET_parts):
                            if qstop(sleep=sleep):
                                break
                            msmtstring = SAMPLE + '_sweep_evolution_time_'+ DD_scheme + '_C' + '&'.join([str(s) for s in carbons])    \
                            + '_Tomo' +  ''.join([str(s) for s in single_Tomo_basis]) +'_RO' + el_RO + '_el' + str(el_after_init)     \
                            + '_N' + str(pulses).zfill(2) + '_part' + str(ii+1).zfill(2) 
                            adwin.start_set_dio(dio_no=4,dio_val=0)
                            Multi_C_DD(msmtstring,  
                                carbon_init_list        = carbons,  
                                el_RO                   = el_RO,
                                el_after_init           = el_after_init,
                                
                                C13_DD_scheme           = DD_scheme,
                                pulses                  = pulses,
                                single_Tomo_basis       = [single_Tomo_basis],
                                free_evolution_time     = FET[ii::FET_parts],
                                wait_gate               = True,

                                logic_state             = 'classical',
                                classical_state         = ['X','X'],

                                mode                    = mode,
                                debug                   = debug)





                # single_Tomo_basis_list = [['I','X'],['X','I'],['X','X']]
            # FET=np.linspace(0.15/(2*pulses),2.25/(2*pulses),8)

            # mode = 'Sweep evolution time'

            # for single_Tomo_basis in single_Tomo_basis_list:
            #     if qstop():
            #         break
            #     for el_RO in el_RO_list:
            #         if qstop():
            #             break
            #         for ii in range(4):
            #             msmtstring = SAMPLE + '_Hahn_sweep_FET_'+ DD_scheme + '_C' + '&'.join([str(s) for s in carbon_init_list])   \
            #             + '_Tomo' +  ''.join([str(s) for s in single_Tomo_basis]) +'_RO' + el_RO + '_el' + str(el_after_init)       \
            #             + '_N' + str(pulses).zfill(2) + '_part' +str(ii+1)
            #             if ssrocalib and not debug:
            #                 adwin.start_set_dio(dio_no=4,dio_val=0)
            #                 ssrocalibration(SAMPLE)
            #             if optimize and not debug:
            #                 GreenAOM.set_power(20e-6)
            #                 adwin.start_set_dio(dio_no=4,dio_val=0)
            #                 optimiz0r.optimize(dims=['x','y','z'], int_time=200)
            #             if ssrocalib and not debug:
            #                 adwin.start_set_dio(dio_no=4,dio_val=0)
            #                 ssrocalibration(SAMPLE)
            #             adwin.start_set_dio(dio_no=4,dio_val=0)
            #             Multi_C_DD(msmtstring,  
            #                 carbon_init_list        = carbon_init_list,  
            #                 el_RO                   = el_RO,
            #                 el_after_init           = el_after_init,
                            
            #                 C13_DD_scheme           = DD_scheme,
            #                 pulses                  = pulses,
            #                 single_Tomo_basis       = single_Tomo_basis,
            #                 free_evolution_time     = FET[ii*2:(ii+1)*2],

            #                 mode                    = mode,
            #                 debug                   = debug)

    adwin.start_set_dio(dio_no=4,dio_val=0)

    # mode = 'Sweep RO evolution time'

    # for single_Tomo_basis in single_Tomo_basis_list:
    #     if qstop():
    #         break
    #     for el_RO in el_RO_list:
    #         if qstop():
    #             break
    #         msmtstring = SAMPLE + '_Assymetric_Hahn_'+ DD_scheme + '_C' + '&'.join([str(s) for s in carbon_init_list])  \
    #         + '_Tomo' +  ''.join([str(s) for s in single_Tomo_basis]) +'_RO' + el_RO + '_el' + str(el_after_init)       \
    #         + '_N' + str(pulses).zfill(2) + '_part1'
    #         if ssrocalib and not debug:
    #             adwin.start_set_dio(dio_no=4,dio_val=0)
    #             ssrocalibration(SAMPLE)
    #         if optimize and not debug:
    #             GreenAOM.set_power(20e-6)
    #             adwin.start_set_dio(dio_no=4,dio_val=0)
    #             optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #         if ssrocalib and not debug:
    #             adwin.start_set_dio(dio_no=4,dio_val=0)
    #             ssrocalibration(SAMPLE)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         Multi_C_DD(msmtstring,  
    #             carbon_init_list        = carbon_init_list,  
    #             el_RO                   = el_RO,
    #             el_after_init           = el_after_init,
                
    #             C13_DD_scheme           = DD_scheme,
    #             pulses                  = pulses,
    #             single_Tomo_basis       = single_Tomo_basis,

    #             mode                    = mode,
    #             debug                   = debug)

    # adwin.start_set_dio(dio_no=4,dio_val=0)

    execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')