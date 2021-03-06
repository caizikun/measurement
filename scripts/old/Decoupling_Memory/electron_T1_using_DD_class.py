"""
MAB 24-4-2015
ElectronT1 using dynamicaldecoupling class
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

def ElectronT1(name,   
        init_el_state           = 0,
        RO_el_state             = 0,
        free_evolution_time     = np.linspace(10e-3,500e-3,2),
        debug                   = True,
        Shutter_rise_time       = 2500):

    m = DD.Electron_T1(name)
    funcs.prepare(m)

    '''Set parameters'''

    m.params['init_el_state'] = str(init_el_state)
    m.params['RO_el_state'] = str(RO_el_state)
    
    #############################
    ### Option 1; Sweep phase ###
    #############################
    m.params['Shutter_rise_time'] = Shutter_rise_time
    m.params['use_shutter']         = 1
    m.params['Nr_C13_init']         = 0
    m.params['Nr_MBE']              = 0 
    m.params['Nr_parity_msmts']     = 0
    m.params['reps_per_ROsequence'] = 400
    m.params['free_evolution_time'] = free_evolution_time
    # m.params['pts'] = len(m.params['free_evolution_time'])
    m.params['pts'] = 1
    m.params['sweep_name'] = 'Free evolution time (s)'
    m.params['sweep_name'] = 'Shutter_rise_time (ms)'
    # m.params['sweep_pts']  = m.params['free_evolution_time']
    m.params['sweep_pts']  = np.array(m.params['Shutter_rise_time']) / 1000

    ####################################################
    ### Option 3; Sweep assymetric RO evolution time ###
    ####################################################
  
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



if __name__ == '__main__':



    sleep = 2
    optimize = True
    ssrocalib = False
    debug = False
    init_el_state_list = [1]
    RO_el_state_list = [1]
    

    

    FET = [[0.05,10.,30.],[60.],[100.],[250.]]
    
    FET = np.linspace(0.05,40,10)
    FET = [FET[2:9:3],FET[1:9:3],FET[:8:3],np.array([FET[-1]]),np.array([50.])]
    FET = [np.linspace(0.005,1.5,8)]
    # FET = [np.array([0.10])]
    # Total_time = 10*4.*sum(sum(FET))
    # Number_of_Parts = total_measurement_time*3600./Total_time
    Number_of_Parts = len(FET)
    # Number_of_Parts = 5
    # ElectronT1(SAMPLE + 'test',
    #                     init_el_state           = 1,
    #                     RO_el_state             = 1,
    #                     free_evolution_time     = [250.],
    #                     debug                   = False)

    # adwin.start_set_dio(dio_no=4,dio_val=0)
    # ssss
    stopper = 0

    if False:
        for init_el_state in init_el_state_list:
            if stopper == 1 or qstop(sleep=sleep):
                stopper=1
                break
            for RO_el_state in RO_el_state_list:
                if stopper == 1 or qstop(sleep=sleep):
                    stopper=1
                    break
                for reppart in range(1):
                    if stopper == 1 or qstop(sleep=sleep):
                        stopper=1
                        break
                    for FETpart in range(Number_of_Parts):
                            if stopper == 1 or qstop(sleep=sleep):
                                stopper = 1
                                break
                            msmtstring = SAMPLE + 'electronT1'+'_init_el' + str(init_el_state) + '_RO_el' + str(RO_el_state) + '_reppart' + str(reppart+1) + '_FETpart'+ str(FETpart+1)
                            if ssrocalib and not debug:
                                adwin.start_set_dio(dio_no=4,dio_val=0)
                                ssrocalibration(SAMPLE)
                            if optimize and not debug:
                                GreenAOM.set_power(20e-6)
                                adwin.start_set_dio(dio_no=4,dio_val=0)
                                optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=210)
                            # if ssrocalib and not debug:
                            #     adwin.start_set_dio(dio_no=4,dio_val=0)
                            #     ssrocalibration(SAMPLE)
                            adwin.start_set_dio(dio_no=4,dio_val=0)
                            ElectronT1(msmtstring,
                            init_el_state           = init_el_state,
                            RO_el_state             = RO_el_state,
                            free_evolution_time     = FET[FETpart],
                            debug                   = debug)
    
        if ssrocalib and not debug and stopper == 0:
            adwin.start_set_dio(dio_no=4,dio_val=0)
            ssrocalibration(SAMPLE)
        adwin.start_set_dio(dio_no=4,dio_val=0)
    # single_Tomo_basis_list = [['I','X'],['X','I'],['X','X']]
    # FET=np.linspace(0.15/(2*pulses),2.25/(2*pulses),8)

    # mode = 'Sweep evolution time'
    Shutter_rise_times = np.linspace(750,5000,18)
    
    for aa, Shutter_rise_time in enumerate(Shutter_rise_times):
        if stopper == 1 or qstop(sleep=sleep):
            stopper = 1
            break
        msmtstring = SAMPLE + 'electronT1_shutter_test' + '_FETpart'+ str(aa+1).zfill(2)
        ElectronT1(msmtstring,   
        init_el_state           = 0,
        RO_el_state             = 0,
        free_evolution_time     = np.array([50e-3]),
        debug                   = False,
        Shutter_rise_time       = Shutter_rise_time)
        adwin.start_set_dio(dio_no=4,dio_val=0)

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