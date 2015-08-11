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

def Single_C_DD(name, 
        carbon_nr             = 1,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        C13_DD_scheme         = 'XY4',
        pulses                = 4,
        el_after_init         = 1,
        C13_init_method       = 'MBI',
        C13_MBI_threshold     = [1],
        C13_RO_phase          = ['X'],
        reps                  = 400,
        free_evolution_time = np.zeros((1))):

    m = DD.NuclearDD(name)
    funcs.prepare(m)

    '''Set parameters'''

    m.params['C13_DD_Scheme'] = C13_DD_scheme
    if pulses == 1:
        m.params['C13_DD_Scheme'] = 'X'


    m.params['el_after_init'] = el_after_init 
    m.params['Decoupling_pulses']=pulses
    ### Sweep parameters
    m.params['reps_per_ROsequence'] = reps
    # if pulses > 31:
    #     m.params['reps_per_ROsequence'] = 450

    # if pulses > 33:
    #     m.params['reps_per_ROsequence'] = 800
    m.params['C13_MBI_RO_state'] = 0 
    m.params['C13_MBI_threshold_list'] = C13_MBI_threshold
    # m.params['C13_MBI_RO_duration'] = 100 

    m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    m.params['use_shutter'] = 1
    ### overwritten from msmnt params
           
     # Free evolution time in the order of

    #############################
    ### Option 1; Sweep phase ###
    #############################

    if False:
        m.params['C_RO_phase'] = ['X','Y','Z']
        m.params['pts'] = len(m.params['C_RO_phase'])
        m.params['free_evolution_time'] = [0.001e-3]*len(m.params['C_RO_phase'])
        m.params['sweep_name'] = 'phase'
        m.params['sweep_pts']  = m.params['C_RO_phase']
    
    ######################################
    ### Option 2; Sweep evolution time ###
    ######################################
    
    if True:
        if sum(free_evolution_time) > 1e-3:
            m.params['free_evolution_time'] = free_evolution_time
        else:
            if pulses == 1:
                m.params['free_evolution_time'] = np.linspace(10e-3,1.3/(2.),8) 
            elif pulses == 2:
                m.params['free_evolution_time'] = np.linspace(5e-3,120e-3,8)
            elif pulses == 4:
                m.params['free_evolution_time'] = np.linspace(2.5e-3,2.0/(2.*pulses),8)
            else:
                m.params['free_evolution_time'] = np.linspace(1.5e-3,200e-3,6)
        m.params['pts'] = len(m.params['free_evolution_time'])
        m.params['C_RO_phase'] = C13_RO_phase*len(m.params['free_evolution_time'])
        m.params['sweep_name'] = 'Free evolution time (s)'
        m.params['sweep_pts']  = m.params['free_evolution_time']*2*pulses

    
  
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

def qstop(sleep):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(2)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

def Carbon_DD_mult_msmts(DD_scheme='XY4',carbons=[1],pulses_list=[4],el_ROs=['positive'],optimize=True, ssrocalib=False, 
    Max_FET_Dict = {'1': 1.3,'4': 2.25,'8': 3.0,'16': 5.,'32': 7.}, timepart_Dict ={'1': 1,'4': 1,'8': 4,'16': 8,'32': 8},
    debug=False, datapoints = 10, time_min= 50e-3, repitions = 500,el_after_init=1,tau_min =1.5e-3):
    stopper = False
    Calc_time = False
    sleep = 2
    if Calc_time == True:
        debug =True
        sleep = 0
        Totaltime = 0
    for carbon in carbons:
        if stopper:
            break
        for pulses in pulses_list:
            if stopper:
                break
            FET = np.linspace(max(time_min/(2*pulses),tau_min),Max_FET_Dict[str(pulses)]/(2*pulses),datapoints)
            if Calc_time:
                Total_time += FET*2*pulses*2*repitions
                print carbon, pusles, Totaltime
            indexer = datapoints/timepart_Dict[str(pulses)]
            for el_RO in el_ROs:
                if stopper:
                    break
                for timepart in range(timepart_Dict[str(pulses)]):
                    if stopper or qstop(sleep):
                        stopper = True
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
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    msmtstr = SAMPLE+'_'+ DD_scheme +'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses).zfill(2) + '_part' + str(timepart+1)
                    if not Calc_time:
                        Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = pulses, 
                            C13_DD_scheme=DD_scheme, debug=debug, free_evolution_time=FET[timepart*indexer:(timepart+1)*indexer],
                            C13_init_method = 'MBI', C13_MBI_threshold = [1], el_after_init=el_after_init, C13_RO_phase = ['X'],reps=repitions)

                    
if __name__ == '__main__':

    tau=4.996e-6
    N=36
    t_pi = 2*tau*N
    # t_min = t_pi+10e-6#1,2,4,8,16,32,
    # Carbon_DD_mult_msmts(DD_scheme='auto',carbons=[1],pulses_list=[1,2,4,8,16,32],el_ROs=['positive','negative'],debug=False, ssrocalib=False,el_after_init=0
    #     ,Max_FET_Dict = {'1': 0.13, '2':0.2, '4': 0.28,'8': 0.45,'16': 0.73,'32': 1.1, '64':56},tau_min=t_min,
    #     timepart_Dict ={'1':1, '2':2, '4': 2,'8': 4,'16': 10,'32': 20,'64': 20},datapoints=20)

    Carbon_DD_mult_msmts(DD_scheme='auto',carbons=[1],pulses_list=[1],el_ROs=['positive'],debug=False, ssrocalib=False,el_after_init=1
        ,Max_FET_Dict = {'1': 50e-3, '2':0.2, '4': 0.28,'8': 0.45,'16': 0.73,'32': 1.1, '64':56},tau_min=t_min,
        timepart_Dict ={'1':1, '2':2, '4': 2,'8': 4,'16': 10,'32': 20,'64': 20},datapoints=9)

    # DD_scheme = 'auto'
    # carbons = [1,2]
    # el_ROs = ['positive','negative']
    # pulses = 1
    # debug = False
    # FET=np.linspace(2.5e-3,1.4/(2*pulses),7)
    # for carbon in carbons:
    #     for el_RO in el_ROs:
    #         if qstop():
    #             break
    #         GreenAOM.set_power(20e-6)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         msmtstr = SAMPLE+'_'+ DD_scheme +'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses).zfill(2) + '_part1'
    #         Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = pulses, C13_DD_scheme=DD_scheme, debug=debug, free_evolution_time=FET)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)

    # execfile(r'D:\measuring\measurement\scripts\QEC\NuclearT1_2.py')
    # Carbon_DD_mult_msmts(DD_scheme='XY4',carbons=[carbon],pulses_list=[1,4],el_ROs=['positive','negative'],optimize=True)
    
    # Max_FET_Dict = {'1': 1.3,'4': 2.25,'8': 3.0,'16': 5.,'32': 7.}
    # timepart_Dict ={'1': 1,'4': 2,'8': 4,'16': 8,'32': 8}

    # for pulses in [1,4,8,16,32]
    #     linsp = np.linspace(max(10e-3/(2*pulses),1.5e-3),Max_FET_Dict[str(pulses)],8)
    #     len(linsp)*
    
    # time_min = 20e-3


    # FET = np.linspace(1.5e-3,200e-3,8)
    # for el_RO in el_ROs:
    #     if qstop():
    #         break 
    #     for timepart in range(2):
    #         if qstop():
    #             break     
    #         msmtstr = SAMPLE+'_'+ 'XY4' +'_C'+str(carbon) +'_RO' + el_RO + '_N8' + '_part' + str(timepart+1) 
    #         GreenAOM.set_power(25e-6)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         ssrocalibration(SAMPLE)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = 8, C13_DD_scheme='XY4', free_evolution_time= FET[timepart*4:timepart*4+4])
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         ssrocalibration(SAMPLE)

    # FET = np.linspace(1.5e-3,5.0/(2.*16),8)
    # for el_RO in el_ROs:
    #     if qstop():
    #         break 
    #     for timepart in range(4):
    #         if qstop():
    #             break     
    #         msmtstr = SAMPLE+'_'+ 'XY4' +'_C'+str(carbon) +'_RO' + el_RO + '_N16' + '_part' + str(timepart+1) 
    #         GreenAOM.set_power(25e-6)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         ssrocalibration(SAMPLE)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = 16, C13_DD_scheme='XY4', free_evolution_time= FET[timepart*2:timepart*2+2])
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         ssrocalibration(SAMPLE)

    # FET = np.linspace(1.5e-3,6.5/(2.*32),8)
    # for el_RO in el_ROs:
    #     if qstop():
    #         break 
    #     for timepart in range(8):
    #         if qstop():
    #             break     
    #         msmtstr = SAMPLE+'_'+ 'XY4' +'_C'+str(carbon) +'_RO' + el_RO + '_N32' + '_part' + str(timepart+1) 
    #         GreenAOM.set_power(25e-6)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         ssrocalibration(SAMPLE)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = 32, C13_DD_scheme='XY4', free_evolution_time= np.ones((1))*FET[timepart])
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         ssrocalibration(SAMPLE)

    # if carbon == 3:
    #     FET = np.linspace(1.5e-3,8.5/(2.*64),8)
    #     for el_RO in el_ROs:
    #         if qstop():
    #             break 
    #         for timepart in range(8):
    #             if qstop():
    #                 break     
    #             msmtstr = SAMPLE+'_'+ 'XY4' +'_C'+str(carbon) +'_RO' + el_RO + '_N64' + '_part' + str(timepart+1) 
    #             GreenAOM.set_power(25e-6)
    #             adwin.start_set_dio(dio_no=4q,dio_val=0)
    #             optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #             adwin.start_set_dio(dio_no=4,dio_val=0)
    #             ssrocalibration(SAMPLE)
    #             adwin.start_set_dio(dio_no=4,dio_val=0)
    #             Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = 64, C13_DD_scheme='XY4', free_evolution_time= np.ones((1))*FET[timepart])
    #             adwin.start_set_dio(dio_no=4,dio_val=0)
    #             ssrocalibration(SAMPLE)

    adwin.start_set_dio(dio_no=4,dio_val=0)
    

    # execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')