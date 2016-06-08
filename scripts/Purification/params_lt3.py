import qt
import joint_params

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt3 = {}

#general sequence things. All of these are set automatically.
params_lt3['do_general_sweep']          = False
params_lt3['is_two_setup_experiment']   = 1
params_lt3['do_N_MBI']                  = 0 #practically not in use
params_lt3['do_carbon_init']            = 1
params_lt3['MW_before_LDE1']            = 0
params_lt3['LDE_1_is_init']             = 0
params_lt3['do_LDE_1']                  = 1 # we always do this.
params_lt3['LDE_1_is_el_init']          = 0
params_lt3['do_swap_onto_carbon']       = 1
params_lt3['do_LDE_2']                  = 1 # TODO finish the LDE element for non local operation
params_lt3['do_phase_correction']       = 1 
params_lt3['do_purifying_gate']         = 1
params_lt3['do_carbon_readout']         = 1 #if 0 then RO of the electron via an adwin trigger.

# LDE element
params_lt3['MW_during_LDE']             = 1 
params_lt3['AWG_SP_power']              = 1000e-9
params_lt3['LDE_SP_duration']           = 1.5e-6
params_lt3['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt3['average_repump_time'] 		= 0.254e-6 # XXX put repump AOM delay here!
params_lt3['LDE_decouple_time']         = 1/qt.exp_params['samples'][sample_name]['C1_freq_0']
params_lt3['MW_opt_puls1_separation']   = 50e-9 # was 22 e-9. needs to be adjusted.


#adwin params defs:
params_lt3['SP_duration'] = 30#10 #10
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['do_sequences'] = 1
params_lt3['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt3['E_RO_durations']  = [params_lt3['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt3['Dynamical_stop_ssro_threshold'] = 1
params_lt3['MBI_attempts_before_CR'] = 1 

# params_lt3['phase_per_sequence_repetition'] =0.
# params_lt3['phase_per_compensation_repetition'] =0.
# params_lt3['total_phase_offset_after_sequence'] =0.
params_lt3['phase_correct_max_reps']    = 80 


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
params_lt3['adwin_comm_safety_cycles'] = 3
params_lt3['adwin_comm_timeout_cycles'] = 1000 # 1ms 
params_lt3['remote_awg_trigger_channel'] = 1 # not used on slave
params_lt3['invalid_data_marker_do_channel'] = 5 # currently not used
params_lt3['master_slave_awg_trigger_delay'] = 9 # times 10ns


# #eom pulse
# params_lt3['eom_pulse_amplitude']		= 1.9 
# params_lt3['eom_pulse_duration']        = 2e-9
# params_lt3['eom_off_duration']          = 50e-9
# params_lt3['eom_off_amplitude']         = -0.293 # calibration 2015-11-04 <--> should be calibrated 
# params_lt3['eom_overshoot_duration1']   = 20e-9
# params_lt3['eom_overshoot1']            = -0.04 # calibrate!
# params_lt3['eom_overshoot_duration2']   = 4e-9
# params_lt3['eom_overshoot2']            = -0.00 # calibrate!
# params_lt3['aom_risetime']              = 17e-9
# params_lt3['aom_amplitude']             = 0.57 #calibrate!


params_lt3['AWG_wait_for_lt3_start'] =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt3['sync_during_LDE']           = 1

params_lt3['PLU_during_LDE']          = 1
params_lt3['PLU_gate_duration']       = 100e-9#70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 1e-9
params_lt3['PLU_2_delay']             = 1e-9
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 2000e-9 # don't change this

params_lt3['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt3['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']
params_lt3['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt3['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']

### Everything carbon

params_lt3['carbon']                        = 1
params_lt3['carbon_init_method']            = 'swap'
params_lt3['carbon_readout_orientation']    = 'positive'
params_lt3['dynamic_phase_tau'] = 2.310e-6
params_lt3['dynamic_phase_N'] = 2 

### Everything TimeHarp / this is imported from Bell.joint_params
params_lt3['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
params_lt3['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
params_lt3['MIN_SYNC_BIN'] =       2000
params_lt3['MAX_SYNC_BIN'] =       3500
params_lt3['MIN_HIST_SYNC_BIN'] =  2000
params_lt3['MAX_HIST_SYNC_BIN'] =  3500
params_lt3['TTTR_RepetitiveReadouts'] =  10 #
params_lt3['TTTR_read_count'] = 	1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
params_lt3['measurement_abort_check_interval']    = 2. #sec
params_lt3['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
params_lt3['use_live_marker_filter']=True
params_lt3['entanglement_marker_number'] = 4 ##### put plu marker on HH here! needs to be kept!

params_lt3['pulse_start_bin'] = 3014 - 55 -params_lt3['MIN_SYNC_BIN']
params_lt3['pulse_stop_bin'] = 3014+9-55 -params_lt3['MIN_SYNC_BIN']
params_lt3['tail_start_bin'] = 3014+9-55 -params_lt3['MIN_SYNC_BIN']
params_lt3['tail_stop_bin'] = 3014+9-55+50 -params_lt3['MIN_SYNC_BIN']
params_lt3['PQ_ch1_delay'] = 55

params_lt3['live_filter_queue_length'] = 10

params_lt3['measurement_time'] = 24.*60.*60. 