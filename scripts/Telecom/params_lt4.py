import qt
# import joint_params

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt4 = {}

#general sequence things. All of these are set automatically.
params_lt4['do_general_sweep']          = False
params_lt4['is_two_setup_experiment']   = 1
params_lt4['do_N_MBI']                  = 0 #practically not in use
params_lt4['MW_before_LDE1']            = 0
params_lt4['do_LDE_1']                  = 1 # we always do this.

# LDE element
params_lt4['MW_during_LDE']             = 1 
params_lt4['AWG_SP_power']              = 100e-9#1000e-9
params_lt4['LDE_SP_duration']           = 1.5e-6
params_lt4['LDE_SP_delay']              = 0e-6 ### don't change this.
params_lt4['average_repump_time']       = 0.22e-6#0.27e-6#0.254e-6 # XXX put repump AOM delay here!
params_lt4['LDE_decouple_time']         = 400e-9
params_lt4['MW_opt_puls1_separation']   = 430e-9 #


#adwin params defs:
params_lt4['SP_duration'] = 30#10 #10
params_lt4['wait_after_pulse_duration'] = 1
params_lt4['do_sequences'] = 1
params_lt4['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt4['E_RO_durations']  = [params_lt4['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt4['Dynamical_stop_ssro_threshold'] = 1
params_lt4['MBI_attempts_before_CR'] = 1 

#### stuff the purification script requires but not useful for us
params_lt4['phase_correct_max_reps'] = 72
params_lt4['phase_feedback_resolution'] = 4.5

params_lt4['Phase_stab_duration'] = 100000 # How many microseconds to phase stabilise for
params_lt4['Phase_stab_interval'] = 1000000 # Time between phase stabilisations in microseconds
params_lt4['phase_stab_signal_channel'] = 7 # Channel to signal on

# channels
#params_lt4['wait_for_AWG_done'] = 1 # not used in adwin script
params_lt4['PLU_event_di_channel'] = 21 
params_lt4['PLU_which_di_channel'] = 20 # not used on slave
#params_lt4['AWG_start_DO_channel'] =  defined in msmt params
#params_lt4['AWG_done_DI_channel']= defined in msmt params
params_lt4['wait_for_awg_done_timeout_cycles'] = 1e7  # 10ms
#params_lt4['AWG_event_jump_DO_channel'] =  defined in msmt params
params_lt4['AWG_repcount_DI_channel'] = 19 
params_lt4['remote_adwin_di_success_channel'] = 22 
params_lt4['remote_adwin_di_fail_channel'] = 23
params_lt4['remote_adwin_do_success_channel'] = 14
params_lt4['remote_adwin_do_fail_channel'] = 15
params_lt4['adwin_comm_safety_cycles'] = 15
params_lt4['adwin_comm_timeout_cycles'] = 200000 # 1ms 
params_lt4['remote_awg_trigger_channel'] = 13 # not used on slave
params_lt4['invalid_data_marker_do_channel'] = 5 # currently not used
params_lt4['master_slave_awg_trigger_delay'] = 9 # times 10ns
params_lt4['sync_during_LDE']           = 1

params_lt4['PLU_during_LDE']          = 1
params_lt4['PLU_gate_duration']       = 50e-9#70e-9
params_lt4['PLU_gate_3_duration']     = 40e-9
params_lt4['PLU_1_delay']             = 88e-9 - 200e-9
params_lt4['PLU_2_delay']             = 88e-9 - 200e-9
params_lt4['PLU_3_delay']             = 50e-9
params_lt4['PLU_4_delay']             = 2500e-9 # don't change this

params_lt4['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_amp']
params_lt4['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_length']
params_lt4['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt4['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt4['LDE_final_mw_phase']      = qt.exp_params['protocols'][name]['pulses']['X_phase']

params_lt4['mw_second_pulse_amp']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp']
params_lt4['mw_second_pulse_length']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']

params_lt4['MAX_DATA_LEN']        =   int(100e6)
params_lt4['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
params_lt4['MIN_SYNC_BIN']        =   int(3e6)
params_lt4['MAX_SYNC_BIN']        =   int(6e6)#15 us # XXX was 15us 
params_lt4['MIN_HIST_SYNC_BIN']   =   int(3e6) #XXXX was 5438*1e3
params_lt4['MAX_HIST_SYNC_BIN']   =   int(6e6)
params_lt4['count_marker_channel'] = 1

params_lt4['pulse_start_bin'] = 2810e3 -params_lt4['MIN_HIST_SYNC_BIN'] #2490e3 BK  #XXX
params_lt4['pulse_stop_bin'] = 2826e3 - params_lt4['MIN_HIST_SYNC_BIN'] # 2499e3 BK #XXX
params_lt4['tail_start_bin'] = 2826e3 - params_lt4['MIN_HIST_SYNC_BIN'] # 2499e3 BK #XXX
params_lt4['tail_stop_bin'] = 2856e3 - params_lt4['MIN_HIST_SYNC_BIN']  # 2570e3 BK #XXX
params_lt4['PQ_ch1_delay'] = 18e3

params_lt4['measurement_time']    =   24.*60*60 #sec = 24H
params_lt4['measurement_abort_check_interval']    = 1 #sec
params_lt4['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
params_lt4['TTTR_read_count'] = 131072#qt.instruments['HH_400'].get_T2_READMAX()
params_lt4['TTTR_RepetitiveReadouts'] =  1


params_lt4['use_live_marker_filter']=True
params_lt4['maximum_meas_time_in_min'] = 60
params_lt4['do_green_reset'] = False

params_lt4['live_filter_queue_length'] = 10

### parameters for LDE timing:
params_lt4['TPQI_normalisation_measurement'] = False
params_lt4['initial_delay']           = 10e-9 #DONT CHANGE THIS
params_lt4['do_final_mw_LDE']         = 0 # only used for B&K

params_lt4['opt_pi_pulses'] = 1
params_lt4['opt_pulse_separation']    = 0.2e-6#250e-9 #350e-9 changed for higher visibility of 

params_lt4['LDE1_attempts'] = 1000 
params_lt4['LDE2_attempts'] = 500

params_lt4['LDE_element_length'] = 6.0e-6 #DO NOT CHANGE THIS


#### added for the adwin process
params_lt4['is_master'] = 1