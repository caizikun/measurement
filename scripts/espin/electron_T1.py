"""
Script for e-spin T1 using the pulsar sequencer.
"""
import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from analysis.lib.m2.ssro import ssro as ssroanal

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

class ElectronT1_without_AWG(ssro.IntegratedSSRO):

    mprefix = 'ElectronT1'
    adwin_process = 'T1_without_AWG_SHUTTER'

def T1(name, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', 
        pump_to_1 = False, wait_times = np.linspace(1e3,200e3,15),
        debug = False):
    print 'Hello1'
    m = pulsar_msmt.ElectronT1(name)
    ####dirty hack to switch our lasers around
    # E_aom = m.E_aom
    # A_aom = m.A_aom
    # m.E_aom = A_aom
    # m.A_aom = E_aom
    print 'Hello2'
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    '''set experimental paramqeters'''
        #T1 experiment

    # Measurement settings
    m.params['pts'] = len(wait_times)

    m.params['T1_initial_state'] = T1_initial_state #currently 'ms=0' or 'ms=-1'
    m.params['T1_readout_state'] = T1_readout_state #currently 'ms=0' or 'ms=-1'
    # m.params['wait_times'] =  np.linspace(1e3,1.5e3,16) #in us, values must be divisible by the repeat element
    # m.params['wait_times'] =  np.r_[1000,np.linspace(1e6,5.0e6,5),10e6,15e6,30e6,60e6] #in us, values must be divisible by the repeat element
    # m.params['wait_times'] =  np.r_[1000,np.linspace(1e6,5.0e6,5),60e6] 
    m.params['wait_times'] =  wait_times
    m.params['wait_time_repeat_element'] = 10 #in us, this element is repeated to create the wait times max of 6 seconds
    m.params['repetitions'] = 150
    m.params['use_shutter'] = 0
        #Plot parameters
    m.params['sweep_name'] = 'Times (us)'
    m.params['sweep_pts'] = m.params['wait_times']

        #Set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0

        #Optional: To prepare in ms=-1/+1 by laser pumping
    if pump_to_1:
        m.params['A_SP_amplitude']  = 0
        m.params['Ex_SP_amplitude'] = 15e-9

    m.autoconfig()

    print 'initial_state: ' + m.params['T1_initial_state']
    print 'readout_state: ' + m.params['T1_readout_state']
    print m.params['sweep_pts']
    '''generate sequence'''
    m.generate_sequence(upload=True, debug=debug)
    print 'Hello3'
    m.run()
    m.save()
    m.finish()
    print 'Hello4'

def T1_without_AWG(name, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', pump_to_1 = False, wait_times = np.r_[0.2,0.5]):
    print 'Hello1'
    m = ElectronT1_without_AWG(name)
    print 'Hello2'
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    '''set experimental paramqeters'''
        #T1 experiment

    m.params['T1_wait_times'] = wait_times
    wait_times_AWG = wait_times*1e6
    adwin.set_T1_without_AWG_SHUTTER_var(T1_wait_times= wait_times_AWG.astype(int))
    m.params['repetitions'] = 3
    m.params['Shutter_opening_time']=2500
    m.params['use_shutter'] = 0

        #Plot parameters
    m.params['sweep_name'] = 'Times (s)'
    m.params['sweep_pts'] = m.params['T1_wait_times']
    m.params['pts'] = len(m.params['sweep_pts'])    

        #Set sequence wait time for AWG triggering
    m.params['sequence_wait_time'] = 0

        #Optional: To prepare in ms=-1/+1 by laser pumping
    if pump_to_1:
        m.params['A_SP_amplitude']  = 0
        m.params['Ex_SP_amplitude'] = 15e-9

    #m.autoconfig()

    # print 'initial_state: ' + m.params['T1_initial_state']
    # print 'readout_state: ' + m.params['T1_readout_state']
    print m.params['sweep_pts']
    '''generate sequence'''
    #m.generate_sequence(upload=True, debug=False)
    print 'Hello3'
    m.run()
    m.save()
    m.finish()
    print 'Hello4'


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

    times = np.linspace(1e2,50e3,7)
    ii = 999
    # T1(SAMPLE+'_'+'init_m1_RO_m1', T1_initial_state = 'ms=-1',wait_times = times, 
    #                 T1_readout_state = 'ms=-1', debug=True)
    T1(SAMPLE+'_'+'init_0_RO_0', T1_initial_state = 'ms=0',wait_times = times, 
                    T1_readout_state = 'ms=0', debug=False)
    
    # times = np.r_[1e5,1e6,3e6,10e6,30e6, 60e6]
    

    # T1(SAMPLE+'_'+'init_0_RO_0', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0')
    # T1(SAMPLE+'_'+'init_1_RO_0', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', pump_to_1 = True)

    # T1(SAMPLE+'_'+'init_0_RO_0_SWITCH', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', wait_times = np.r_[1e5,3e5, 1e6])

    # T1(SAMPLE+'_'+'TEST_DONT_USE', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', wait_times = [1e6])
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims = ['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    # ssrocalibration(SAMPLE_CFG)


    # times = np.r_[1e5,1e6,10e6,30e6,60e6]
    # for ii in range(200):
    #     qt.msleep(2)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break
    #     T1(SAMPLE+'_'+'init_0_RO_0_rep_'+str(ii)+'_SHUTTER', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', wait_times = times)
    #     if (ii+1) % 40 == 0:
    #         ssrocalibration(SAMPLE_CFG)
    #         GreenAOM.set_power(20e-6)
    #         optimiz0r.optimize(dims = ['x','y','z'])
    #         stools.turn_off_all_lt2_lasers()
    #         ssrocalibration(SAMPLE_CFG)



    # T1_without_AWG(SAMPLE + 'T1_test_without_AWG') 







    # times = np.r_[10e6]#,600e6]

    # for ii in range(7):

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(2)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break
    #     T1(SAMPLE+'_'+'init_1_RO_0_tau_5min_'+str(ii)+'_TEST', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', pump_to_1 = True, wait_times = times)
    #     T1(SAMPLE+'_'+'init_0_RO_0_tau_5min_+'+str(ii)+'+_TEST', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', wait_times = times)

    #     break
    #     ssrocalibration(SAMPLE_CFG)
    #     # ssroanal.ssrocalib()
    #     GreenAOM.set_power(20e-6)
    #     optimiz0r.optimize(dims = ['x','y','z'])
    #     stools.turn_off_all_lt2_lasers()
    #     ssrocalibration(SAMPLE_CFG)
    #     # ssroanal.ssrocalib()

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(2)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

        
    #     ssrocalibration(SAMPLE_CFG)
    #     # ssroanal.ssrocalib()
    #     GreenAOM.set_power(20e-6)
    #     optimiz0r.optimize(dims = ['x','y','z'])
    #     stools.turn_off_all_lt2_lasers()
    #     ssrocalibration(SAMPLE_CFG)
    #     # ssroanal.ssrocalib()

    #     # print '-----------------------------------'            
    #     # print 'press q to stop measurement cleanly'
    #     # print '-----------------------------------'
    #     # qt.msleep(2)
    #     # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #     #     break


    #     # T1(SAMPLE+'_'+'init_1_RO_0_Ord_1_'+str(ii)+'_SHUTTER', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', pump_to_1 = True, wait_times = np.roll(times,ii))  
    #     # T1(SAMPLE+'_'+'init_0_RO_0_Ord_1_'+str(ii)+'_SHUTTER', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', wait_times = np.roll(times,ii))
    #     # ssrocalibration(SAMPLE_CFG)
    #     # ssroanal.ssrocalib()
    #     # GreenAOM.set_power(20e-6)
    #     # # counters.set_is_running(1)
    #     # optimiz0r.optimize(dims = ['x','y','z'])
    #     # stools.turn_off_all_lt2_lasers()
    #     # ssrocalibration(SAMPLE_CFG)
    #     # ssroanal.ssrocalib()



