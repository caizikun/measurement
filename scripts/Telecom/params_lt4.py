'''
dummy file with local parameters for AWG sequence generation

NK 2016
'''
import qt

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt4 = {}
#### added for the adwin process
params_lt4['is_master'] = 1

#general sequence things. All of these are set automatically.
params_lt4['do_general_sweep']          = False
params_lt4['is_two_setup_experiment']   = 1
params_lt4['do_N_MBI']                  = 0 #practically not in use
params_lt4['MW_before_LDE1']            = 0
params_lt4['do_LDE_1']                  = 1 # we always do this.

# LDE element
params_lt4['MW_during_LDE']             = 1 
params_lt4['AWG_SP_power']              = 50e-9#1000e-9
params_lt4['LDE_SP_duration']           = 2e-6
params_lt4['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt4['average_repump_time'] 		= 0.5e-6#0.3e-6#250e-9#250e-9#350e-9#213e-9 
params_lt4['LDE_decouple_time']         = round(1/qt.exp_params['samples'][sample_name]['C4_freq_0'],9)#-50e-9
params_lt4['opt_pulse_start']           = 2.5e-6 #2215e-9 - 46e-9 + 4e-9 +1e-9 
params_lt4['MW_opt_puls1_separation']   = 100e-9#220e-9

#adwin params defs:
params_lt4['SP_duration'] = 30 #10
params_lt4['wait_after_pulse_duration'] = 1
params_lt4['do_sequences'] = 1
params_lt4['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt4['E_RO_durations']  = [params_lt4['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt4['Dynamical_stop_ssro_threshold'] = 1
params_lt4['MBI_attempts_before_CR'] = 1 

# params_lt4['phase_per_sequence_repetition'] =0.
# params_lt4['phase_per_compensation_repetition'] =0.
# params_lt4['total_phase_offset_after_sequence'] =0.
params_lt4['phase_correct_max_reps']    = 80

# channels
# params_lt4['wait_for_AWG_done'] = 1 # not used in adwin script
params_lt4['PLU_event_di_channel'] = 21
params_lt4['PLU_which_di_channel'] = 20
# params_lt4['AWG_start_DO_channel'] = 1 defined in msmt params
# params_lt4['AWG_done_DI_channel']= 1 defined in msmt params
params_lt4['wait_for_awg_done_timeout_cycles'] = 1000000  # 10ms
# params_lt4['AWG_event_jump_DO_channel'] = 1 defined in msmt params
params_lt4['AWG_repcount_DI_channel'] = 19
params_lt4['remote_adwin_di_success_channel'] = 22
params_lt4['remote_adwin_di_fail_channel'] = 23
params_lt4['remote_adwin_do_success_channel'] = 14
params_lt4['remote_adwin_do_fail_channel'] = 15
params_lt4['adwin_comm_safety_cycles'] = 15
params_lt4['adwin_comm_timeout_cycles'] = 200000 # 1 ms
params_lt4['remote_awg_trigger_channel'] = 13
params_lt4['invalid_data_marker_do_channel'] = 1 # currently not used
params_lt4['master_slave_awg_trigger_delay'] = 9 # times 10ns, minimum is 9.


params_lt4['mw_second_pulse_amp']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp']
params_lt4['mw_second_pulse_length']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']
params_lt4['LDE_element_length'] = 7.0e-6 #DO NOT CHANGE THIS
params_lt4['initial_delay']           = 10e-9 #DONT CHANGE THIS


params_lt4['AWG_wait_for_lt3_start']    =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt4['sync_during_LDE']           = 1

params_lt4['PLU_during_LDE']          = 1
params_lt4['PLU_gate_duration']       = 200e-9#70e-9 # 200e-9
params_lt4['PLU_gate_3_duration']     = 40e-9
params_lt4['PLU_1_delay']             = 1e-9
params_lt4['PLU_2_delay']             = 1e-9
params_lt4['PLU_3_delay']             = 50e-9
params_lt4['PLU_4_delay']             = 200e-9

params_lt4['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_amp'] #### needs to be changed back to regular pi/2 for most calibrations
params_lt4['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_theta_length']
params_lt4['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt4['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']

### Everything carbon
params_lt4['carbon']                    = 4
params_lt4['carbon_init_method']            = 'swap'
params_lt4['carbon_readout_orientation']    = 'positive'
params_lt4['dynamic_phase_tau']			= 2.298e-6#2.298e-6
params_lt4['dynamic_phase_N']			= 2
params_lt4['phase_feedback_resolution']	= 4.5

### Everything TimeHarp / this is copied from Bell.joint_params

params_lt4['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
params_lt4['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
params_lt4['MIN_SYNC_BIN'] =       0#2500
params_lt4['MAX_SYNC_BIN'] =       8500
params_lt4['MIN_HIST_SYNC_BIN'] =  0#2500
params_lt4['MAX_HIST_SYNC_BIN'] =  8500
params_lt4['TTTR_RepetitiveReadouts'] =  10 #
params_lt4['TTTR_read_count'] = 	1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
params_lt4['count_marker_channel'] = 4 ##### put plu marker on HH here! needs to be kept!

params_lt4['measurement_abort_check_interval']    = 2. #sec
params_lt4['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
params_lt4['use_live_marker_filter']=True
params_lt4['maximum_meas_time_in_min'] = 60
params_lt4['do_green_reset'] = False

params_lt4['pulse_start_bin'] = 2050-params_lt4['MIN_SYNC_BIN']       #### Puri: 2550 BK: 2950
params_lt4['pulse_stop_bin'] = 2050+2000-params_lt4['MIN_SYNC_BIN']    #### BK: 2950
params_lt4['tail_start_bin'] = 2050 -params_lt4['MIN_SYNC_BIN']       #### BK: 2950
params_lt4['tail_stop_bin'] = 2050+2000 -params_lt4['MIN_SYNC_BIN']    #### BK: 2950
params_lt4['PQ_ch1_delay'] = 55

params_lt4['live_filter_queue_length'] = 10

params_lt4['measurement_time'] = 24.*60.*60. 

### parameters for LDE timing:
params_lt4['TPQI_normalisation_measurement'] = False
params_lt4['initial_delay']           = 10e-9 #DONT CHANGE THIS
params_lt4['do_final_mw_LDE']         = 0 # only used for B&K

params_lt4['opt_pi_pulses'] = 1
params_lt4['opt_pulse_separation']    = 2.5e-6#250e-9 #350e-9 changed for higher visibility of 

params_lt4['LDE1_attempts'] = 1000 
params_lt4['LDE2_attempts'] = 500

params_lt4['LDE_element_length'] = 7.0e-6 #DO NOT CHANGE THIS

