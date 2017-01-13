import qt
#import joint_params

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt3 = {}

#general sequence things. All of these are set automatically.
params_lt3['do_general_sweep']          = False
params_lt3['is_two_setup_experiment']   = 1
params_lt3['do_N_MBI']                  = 0 #practically not in use
params_lt3['MW_before_LDE1']            = 0
params_lt3['do_LDE_1']                  = 1 # we always do this.

# LDE element
params_lt3['MW_during_LDE']             = 1 
params_lt3['AWG_SP_power']              = 1000e-9#1000e-9
params_lt3['LDE_SP_duration']           = 1.5e-6
params_lt3['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt3['average_repump_time'] 		= 0.22e-6#0.27e-6#0.254e-6 # XXX put repump AOM delay here!
params_lt3['LDE_decouple_time']         = 1/qt.exp_params['samples'][sample_name]['C1_freq_0']
params_lt3['MW_opt_puls1_separation']   = 70e-9 #

#adwin params defs:
params_lt3['SP_duration'] = 30#10 #10
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['do_sequences'] = 1
params_lt3['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt3['E_RO_durations']  = [params_lt3['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt3['Dynamical_stop_ssro_threshold'] = 1
params_lt3['MBI_attempts_before_CR'] = 1 

#### stuff the purification script requires but not useful for us
params_lt3['phase_correct_max_reps'] = 72
params_lt3['phase_feedback_resolution'] = 4.5

# channels
#params_lt3['wait_for_AWG_done'] = 1 # not used in adwin script
params_lt3['PLU_event_di_channel'] = 20 
params_lt3['PLU_which_di_channel'] = 21 # not used on slave
#params_lt3['AWG_start_DO_channel'] =  defined in msmt params
#params_lt3['AWG_done_DI_channel']= defined in msmt params
params_lt3['wait_for_awg_done_timeout_cycles'] = 1e7  # 10ms
#params_lt3['AWG_event_jump_DO_channel'] =  defined in msmt params
params_lt3['AWG_repcount_DI_channel'] = 16 
params_lt3['remote_adwin_di_success_channel'] = 19 
params_lt3['remote_adwin_di_fail_channel'] = 18
params_lt3['remote_adwin_do_success_channel'] = 13
params_lt3['remote_adwin_do_fail_channel'] = 8
params_lt3['adwin_comm_safety_cycles'] = 15
params_lt3['adwin_comm_timeout_cycles'] = 200000 # 1ms 
params_lt3['remote_awg_trigger_channel'] = 1 # not used on slave
params_lt3['invalid_data_marker_do_channel'] = 5 # currently not used
params_lt3['master_slave_awg_trigger_delay'] = 9 # times 10ns


params_lt3['sync_during_LDE']           = 1

params_lt3['PLU_during_LDE']          = 1
params_lt3['PLU_gate_duration']       = 100e-9#70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 18e-9+18e-9
params_lt3['PLU_2_delay']             = 18e-9+18e-9
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 2500e-9 # don't change this

params_lt3['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_amp']
params_lt3['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_length']
params_lt3['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt3['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt3['LDE_final_mw_phase'] 	  = qt.exp_params['protocols'][name]['pulses']['X_phase']

params_lt3['mw_second_pulse_amp']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp']
params_lt3['mw_second_pulse_length']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']

### Everything TimeHarp / this is copied from Bell.joint_params
params_lt3['TH_260N'] = {
	'MAX_DATA_LEN' :       int(10e6), ## used to be 100e6
	'BINSIZE' :            1, #2**BINSIZE*BASERESOLUTION 
 	'MIN_SYNC_BIN' :       0,#2500
 	'MAX_SYNC_BIN' :       8500,
 	'MIN_HIST_SYNC_BIN' :  0,#2500
 	'MAX_HIST_SYNC_BIN' :  8500,
 	'TTTR_read_count' : 	qt.instruments['TH_260N'].get_T2_READMAX(), #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
 	'count_marker_channel' : 4, ##### put plu marker on HH here! needs to be kept!
}

params_lt3['HH_400'] = {
	'MAX_DATA_LEN' :       int(100e6), ## used to be 100e6
	'BINSIZE' :            8, #2**BINSIZE*BASERESOLUTION 
 	'MIN_SYNC_BIN' :       int(2e6),#2500
 	'MAX_SYNC_BIN' :       int(5.7e6),
 	'MIN_HIST_SYNC_BIN' :  int(2e6),#2500
 	'MAX_HIST_SYNC_BIN' :  int(5.7e6),
 	'TTTR_read_count' : 	 qt.instruments['HH_400'].get_T2_READMAX(), #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
 	'count_marker_channel' : 1, ##### put plu marker on HH here! needs to be kept!
}

params_lt3['selected_PQ_ins'] =  ['TH_260N','HH_400']
params_lt3['measurement_abort_check_interval']    = 2. #sec
params_lt3['TTTR_RepetitiveReadouts']			  =  1
params_lt3['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
params_lt3['use_live_marker_filter']=True
params_lt3['maximum_meas_time_in_min'] = 60
params_lt3['do_green_reset'] = False

params_lt3['TH_260N']['pulse_start_bin'] = 2050-params_lt3['TH_260N']['MIN_SYNC_BIN']       #### Puri: 2550 BK: 2950
params_lt3['TH_260N']['pulse_stop_bin'] = 2050+2000-params_lt3['TH_260N']['MIN_SYNC_BIN']    #### BK: 2950
params_lt3['TH_260N']['tail_start_bin'] = 2050 -params_lt3['TH_260N']['MIN_SYNC_BIN']       #### BK: 2950
params_lt3['TH_260N']['tail_stop_bin'] = 2050+2000 -params_lt3['TH_260N']['MIN_SYNC_BIN']    #### BK: 2950
params_lt3['TH_260N']['PQ_ch1_delay'] = 55

params_lt3['live_filter_queue_length'] = 10

params_lt3['measurement_time'] = 24.*60.*60. 

print params_lt3['LDE_final_mw_phase']

### parameters for LDE timing:
params_lt3['TPQI_normalisation_measurement'] = False
params_lt3['initial_delay']           = 10e-9 #DONT CHANGE THIS
params_lt3['do_final_mw_LDE']         = 0 # only used for B&K

params_lt3['opt_pi_pulses'] = 1
params_lt3['opt_pulse_separation']    = 2.5e-6#250e-9 #350e-9 changed for higher visibility of 

params_lt3['LDE1_attempts'] = 1000 
params_lt3['LDE2_attempts'] = 500

params_lt3['LDE_element_length'] = 7.0e-6 #DO NOT CHANGE THIS


#### added for the adwin process
params_lt3['is_master'] = 1