import qt
import sce_expm_joint_params
import numpy as np

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt3 = {}

#general sequence things. All of these are set automatically.
params_lt3['do_general_sweep']          = False
params_lt3['is_two_setup_experiment']   = 1
params_lt3['do_N_MBI']                  = 0 #practically not in use
params_lt3['MW_before_LDE']            = 0
params_lt3['LDE_is_init']             = 0
params_lt3['do_LDE']                  = 1 # we always do this.
params_lt3['record_expm_params']  = False # by default we dont record this, only useful if a long run
    

# LDE element
params_lt3['MW_during_LDE']             = 1 
params_lt3['AWG_SP_power']              = 20e-9#1000e-9
params_lt3['LDE_SP_duration']           = 1.5e-6
params_lt3['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt3['MW_opt_puls1_separation']   = 120e-9 #
params_lt3['MW_repump_distance']		= 1200e-9
params_lt3['LDE_decouple_time']         = 2.2e-6
params_lt3['MW_final_delay_offset']		= 0e-9
params_lt3['first_mw_pulse_is_pi2']     = 0
params_lt3['LDE_attempts_before_yellow']  = 2000
params_lt3['Yellow_AWG_duration']			= 300e-6
params_lt3['Yellow_AWG_power']			= 50e-9


#adwin params defs:
params_lt3['SP_duration'] = 30#10 #10
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['do_sequences'] = 1
params_lt3['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt3['E_RO_durations']  = [params_lt3['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt3['Dynamical_stop_ssro_threshold'] = 1
params_lt3['MBI_attempts_before_CR'] = 1 

# channels
#params_lt3['wait_for_AWG_done'] = 1 # not used in adwin script
params_lt3['PLU_event_di_channel'] = 20 
params_lt3['PLU_which_di_channel'] = 21 # not used on slave
params_lt3['wait_for_awg_done_timeout_cycles'] = 1e7  # 10ms
params_lt3['AWG_repcount_DI_channel'] = 16 
params_lt3['remote_adwin_di_success_channel'] = 19 
params_lt3['remote_adwin_di_fail_channel'] = 18
params_lt3['remote_adwin_do_success_channel'] = 13
params_lt3['remote_adwin_do_fail_channel'] = 8
params_lt3['adwin_comm_safety_cycles'] = 15
params_lt3['adwin_comm_timeout_cycles'] = 50000 # 10ms 
params_lt3['remote_awg_trigger_channel'] = 1 # not used on slave
params_lt3['invalid_data_marker_do_channel'] = 5 # currently not used
params_lt3['master_slave_awg_trigger_delay'] = 9 # times 10ns

# dynamical decoupling
params_lt3['max_decoupling_reps'] = 200
params_lt3['dynamic_decoupling_N'] = 8
params_lt3['dynamic_decoupling_tau'] = 36.156e-6-8e-9 # 16 th larmor revival gives: 200*4*32 = 25.6 ms.
params_lt3['tomography_basis'] = 'Y' ### sets RELATIVE phase and amplitude of the last pi/2 pulse when doing decoupling.
params_lt3['decoupling_element_duration'] = 2*params_lt3['dynamic_decoupling_tau']*params_lt3['dynamic_decoupling_N']

params_lt3['sync_during_LDE']           = 1

params_lt3['PLU_during_LDE']          = 1
params_lt3['PLU_gate_duration']       = 100e-9#70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 28e-9#18e-9#+18e-9 ### optimized to deselect the pulse w. plu
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 250e-9 # it was 150e-9 for bell 

params_lt3['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_amp']
params_lt3['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']
params_lt3['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt3['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt3['LDE_final_mw_phase']      = 0.0

params_lt3['sin2_theta']			= 0.5
params_lt3['sin2_theta_fit_of']		= 0.99290825310801334
params_lt3['sin2_theta_fit_a']		= 1.7624629794004711
params_lt3['sin2_theta_fit_x0']		= 0.8893242344254747

### Everything TimeHarp / this is copied from Bell.joint_params
params_lt3['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
params_lt3['BINSIZE'] =            8 #2**BINSIZE*BASERESOLUTION 
params_lt3['MIN_SYNC_BIN'] =       2600 #2500
params_lt3['MAX_SYNC_BIN'] =       3400 ### XXXX change me!
params_lt3['MIN_HIST_SYNC_BIN'] =  1600#2500
params_lt3['MAX_HIST_SYNC_BIN'] =  2400 ### XXXX change me!
params_lt3['TTTR_RepetitiveReadouts'] =  10 #
params_lt3['TTTR_read_count'] = 	1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
params_lt3['measurement_abort_check_interval']    = 2. #sec
params_lt3['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
params_lt3['use_live_marker_filter']=True
params_lt3['count_marker_channel'] = 4 ##### put plu marker on HH here! needs to be kept!

params_lt3['pulse_start_bin'] = 2700-params_lt3['MIN_SYNC_BIN']       #### Puri: 2550 BK: 2950
params_lt3['pulse_stop_bin'] = 2900-params_lt3['MIN_SYNC_BIN']    #### BK: 2950
params_lt3['tail_start_bin'] = 2700 -params_lt3['MIN_SYNC_BIN']       #### BK: 2950
params_lt3['tail_stop_bin'] = 2900 -params_lt3['MIN_SYNC_BIN']    #### BK: 2950
params_lt3['PQ_ch1_delay'] = 55

params_lt3['live_filter_queue_length'] = 10

params_lt3['measurement_time'] = 24.*60.*60. 



################ all of the parameters below are not in use on LT3 as it does not run the fibre stretcher
params_lt3['Phase_msmt_DAC_channel'] = 0 ### not in use at LT3. This will throw an error on the adwin if used accidentally (there is no dac channel 0)
params_lt3['Phase_Msmt_voltage'] = 0.0
params_lt3['Phase_Msmt_off_voltage'] = 0.0
params_lt3['Phase_stab_DAC_channel'] = 0 ### not in use at LT3. This will throw an error on the adwin if used accidentally (channel 0 does not exist)
params_lt3['zpl1_counter_channel'] = 4 ## not in use
params_lt3['zpl2_counter_channel'] = 4 ## not in use
params_lt3['modulate_stretcher_during_phase_msmt'] = 0

params_lt3['stretcher_V_2pi'] = 11
params_lt3['stretcher_V_max'] = 9.5
params_lt3['Phase_Msmt_g_0'] = 1 # Scaling factor to match APD channels
params_lt3['Phase_Msmt_Vis'] = 1 # Vis of interference'

params_lt3['PID_GAIN'] = 1.0
params_lt3['PID_Kp'] = 0.000
params_lt3['PID_Ki'] = 0.0
params_lt3['PID_Kd'] = 0.0
params_lt3['phase_setpoint'] = np.pi/2

params_lt3['count_int_time_stab'] = 10000 # How long to integrate counts for in microseconds
params_lt3['count_int_time_meas'] = 200 # How long to integrate counts for in microseconds
params_lt3['pid_points'] = 4 # How many points to sample the phase at during the PID loop
params_lt3['pid_points_to_store'] = 4 # How many points to store
params_lt3['sample_points'] = 20 # How many points to sample the phase at during the expm part
params_lt3['phase_stab_max_time'] = 300000 # How long in microseconds to run the expm for after phase stabilisation



