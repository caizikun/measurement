"""
Script for a simple Decoupling sequence
"""
import numpy as np
import qt
import msvcrt
import measurement.scripts.QEC as ssro

import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

from analysis.lib.tools import toolbox
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from analysis.lib.m2.ssro import ssro as ssro_analysis
reload(ssro_analysis)

execfile(qt.reload_current_setup)
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
temperature_sensor = qt.instruments['kei2000']

def SimpleDecoupling_swp_tau(name,tau_min=9e-6,tau_max=10e-6,tau_step =50e-9, N =16):

    m = DD.SimpleDecoupling(name+'_tau_'+str(tau_min*1e9))

    # print 'threshold =' + str(m.params['MBI_threshold'])
    # print 'pulse_shape = ' +str(m.params['pulse_shape'])
    # NOTE: ADDED from ElectronT1_Hermite on 23-04-204
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    m.params['temp'] = temperature_sensor.get_readlastval()
    funcs.prepare(m)

    if True: ### if you don't want to do MBI for this script.
        m.params['MBI_threshold'] = 0
        m.params['Ex_SP_amplitude'] = 0
        m.params['Ex_MBI_amplitude'] = 0
        m.params['SP_E_duration'] = 20 #2000
        
        m.params['repump_after_MBI_A_amplitude'] = [25e-9]
        m.params['repump_after_MBI_duration'] = [300] # 50  


    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 250 #250 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    if N%4 == 0: 
        m.params['Final_Pulse'] ='-x'
    else:
        m.params['Final_Pulse'] ='x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    Number_of_pulses = N 
    tau_list = np.arange(tau_min,tau_max,tau_step) 
    print tau_list

    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        = tau_list*1e6
    m.params['sweep_name']       = 'tau (us)'

    # print m.params['fast_pi_duration']
    # print m.params['fast_pi_amp']

    # m.params['fast_pi2_duration'] = pi_dur
    # m.params['fast_pi2_amp'] = pi_amp




    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)


# for ssro measurement
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
    m.params['Ex_SP_amplitude'] = 4e-9
    m.run()
    m.save('ms1')
    m.finish()


def optimize_magnetic_field():

    safemode            = False    # If True then manual confirmation is needed befor each magnet movement
    optimization_target = 15     # Target difference frequency in kHz , first (03.08) was 10 then 7 then 10 again
    field_gradient      = 0.100     
    only_fine           = False

    ### Settings for the first coarse steps
    coarse_range          = 7.5     #Common: 10 MHz
    coarse_pts            = 101     #Common: 121
    coarse_reps           = 750     #Common: 500
    coarse_amplitude      = 0.08
    coarse_pulse_length   = 3e-6
    coarse_MW_power       = -1

    ### Settings for the fine steps
    fine_range          = 0.600
    fine_pts            = 81
    fine_reps           = 2000
    fine_amplitude      = 0.08/3 
    fine_pulse_length   = 9e-6
    fine_MW_power       = -1

    
    
    
    coarse_range   = fine_range     
    coarse_pts     = fine_pts    
    coarse_reps    = fine_reps   
    coarse_pulse_length = fine_pulse_length
    coarse_amplitude    = fine_amplitude 
    coarse_MW_power = fine_MW_power


## Run optimizor ##############
    GreenAOM.set_power(10e-6)
    counters.set_is_running(True)
    optimiz0r.optimize(dims=['x','y','z'], int_time=300)

    GreenAOM.set_power(10e-6)
    counters.set_is_running(True)
    optimiz0r.optimize(dims=['x','y','z'], int_time=300)

    name = 'SSRO_calib'
    ssrocalibration(name)

   ### SSRO Analysis
    ssro_analysis.ssrocalib()

#########################################

    f0 = []; u_f0 = []; delta_f0 =[]; iterations_list =[]; magnet_postion_list =[]; fit_failed_list=[]

    darkesr('magnet_optimize_init', range_MHz=coarse_range, pts=coarse_pts, reps=coarse_reps, 
                power= coarse_amplitude, MW_power = coarse_MW_power, pulse_length=coarse_pulse_length)

    # Do the fitting, returns in MHz, input in GHz
     
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
    delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3    # in kHz

    # Magnet start position
    Start_position = magnet_Z_scanner.GetPosition()

    # List all the measured values
    iterations = 0
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    delta_f0.append(delta_f0_temp)
    magnet_postion_list.append(Start_position)


    while abs(delta_f0_temp) > optimization_target:

            ## Determine new postition
            current_position = magnet_Z_scanner.GetPosition()
            delta_position = delta_f0_temp/field_gradient*1e-6
            move_to_position = current_position + delta_position

            print 'Target frequency =' + str(current_f_msm1)
            print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
            print 'Difference = ' + str(delta_f0_temp) + ' kHz'
            print 'Current magnet position = ' + str(current_position) + ' mm'
            print 'Move to position          ' + str(move_to_position) + ' mm'
            print 'By                        ' + str(delta_position*1e6) + 'nm'
            

            # if u_f0_temp*1e6 > 15:
            #     print 'Uncertainty larger than 15 kHz, fit failed'
            #     fit_failed = 1
            # else: 
            #     fit_failed = 0

            # fit_failed_list.append(fit_failed)
            
            ## Actually move the magnet
          

            if u_f0_temp*1e6 < 15:
       
                ## Limit the maximum movement range
                if move_to_position < 0.042 or move_to_position > 0.072:
                    print 'movement is going out of range, abort!!!'
                    break

                print 'Target frequency =' + str(current_f_msm1)
                print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
                print 'Difference = ' + str(delta_f0_temp) + ' kHz'
                print 'Current magnet position = ' + str(current_position) + ' mm'
                print 'Move to position          ' + str(move_to_position) + ' mm'
                print 'By                        ' + str((move_to_position-current_position)*1e6) + 'nm'

                if safemode == True: 
                    print '\a\a\a' 
                    ri = raw_input ('move magnet? (y/n)')
                    if str(ri) != 'y': 
                        break
                
                ## Actually move the magnet
                magnet_Z_scanner.MoveRelative(delta_position)
                print 'moving magnet...'

            else:
                print 'Uncertainty larger than 15 kHz, fit failed'
                break

            print '--------------------------------'
            print 'press q to stop measurement loop'
            print '--------------------------------'
            qt.msleep(2)

            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or abs(move_to_position-current_position) < 0.000025:
                break

            darkesr('magnet_optimize_step_' + str(iterations), range_MHz=fine_range, pts=fine_pts, reps=fine_reps, 
                power = fine_amplitude, MW_power = fine_MW_power, pulse_length=fine_pulse_length)

            f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
            delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3

            iterations += 1

if __name__ == '__main__':



    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=2.31e-6,tau_max=2.38e-6,tau_step =10e-9, N =2)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=30e-6,tau_max=50e-6,tau_step =40e-9, N =2)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=50e-6,tau_max=70e-6,tau_step =40e-9, N =2)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=70e-6,tau_max=90e-6,tau_step =40e-9, N =2)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=90e-6,tau_max=110e-6,tau_step =40e-9, N =2)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=110e-6,tau_max=130e-6,tau_step =40e-9, N =2)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=130e-6,tau_max=150e-6,tau_step =40e-9, N =2)


    for ii in range(330,340):
        for jj in range(0,5):
            SimpleDecoupling_swp_tau(SAMPLE, tau_min=(ii*1e-6+jj*0.2e-6),tau_max=(ii*1.0e-6+(jj+1)*0.2e-6),tau_step =4e-9, N =32)

        if ii%2 == 0:
            name = 'SSRO_calib'
            ssrocalibration(name)
            ssro_analysis.ssrocalib()
            optimize_magnetic_field()

    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.522e-6-0.02e-6,tau_max=6.522e-6+0.02e-6,tau_step =1e-9, N =20)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=113.4e-6,tau_max=113.5e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=113.5e-6,tau_max=113.6e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=113.6e-6,tau_max=113.7e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=113.7e-6,tau_max=113.8e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=113.8e-6,tau_max=113.9e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=113.9e-6,tau_max=6e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6e-6,tau_max=6.1e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=7e-6,tau_max=7.2e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=7.2e-6,tau_max=7.4e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=7.4e-6,tau_max=7.6e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=7.6e-6,tau_max=7.8e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=7.8e-6,tau_max=8e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8e-6,tau_max=8.2e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8.2e-6,tau_max=8.4e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8.4e-6,tau_max=8.6e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.8e-6,tau_max=6.9e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.9e-6,tau_max=7e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6e-6,tau_max=6.1e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.1e-6,tau_max=6.2e-6,tau_step =4e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.2e-6,tau_max=6.3e-6,tau_step =4e-9, N =32)

    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.8e-6,tau_max=6.9e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.9e-6,tau_max=6e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6e-6,tau_max=6.1e-6,tau_step =10e-9, N =32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.1e-6,tau_max=6.2e-6,tau_step =10e-9, N =32)
    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=4.994e-6-0.1e-6,tau_max=4.994e-6+0.1e-6,tau_step =5e-9, N =32)
    #SimpleDecoupling_swp_tau(SAMPLE, tau_min=4.200e-6,tau_max=4.400e-6,tau_step =4e-9, N =64)
    # stools.turn_off_all_lt2_lasers()
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=6.280e-6,tau_max=6.32e-6,tau_step = 2e-9, N=64)

    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=4.0e-6,tau_max=4.2e-6,tau_step =4e-9, N=64)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=4.2e-6,tau_max=4.4e-6,tau_step =4e-9, N=64)

    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=10.7e-6,tau_max=10.9e-6,tau_step =4e-9, N=64)

    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=11.0e-6,tau_max=11.2e-6,tau_step =4e-9, N=32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=11.2e-6,tau_max=11.4e-6,tau_step =4e-9, N=32)

    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=13.3e-6,tau_max=13.5e-6,tau_step =4e-9, N=32)
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=13.5e-6,tau_max=13.6e-6,tau_step =4e-9, N=32)



    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=4.5e-6,tau_max=4.7e-6,tau_step =10e-9, N=128)
    # stools.turn_off_all_lt2_lasers()
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8.2e-6,tau_max=8.7e-6,tau_step =5e-9, N =32, pi_dur = 136e-9, pi_amp=0.398466, pi2_dur = 68e-9, pi2_amp = 0.398571)
    # stools.turn_off_all_lt2_lasers()
    # GreenAOM.set_power(20e-6)
    # optimiz0r.optimize(dims=['x','y','z'])
    # stools.turn_off_all_lt2_lasers()
    # SimpleDecoupling_swp_tau(SAMPLE, tau_min=8.2e-6,tau_max=8.7e-6,tau_step =5e-9, N =32, pi_dur = 168e-9, pi_amp=0.313663, pi2_dur = 84e-9, pi2_amp = 0.314146)


