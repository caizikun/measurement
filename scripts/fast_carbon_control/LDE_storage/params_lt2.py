'''
dummy file with local parameters for AWG sequence generation

NK 2016
'''
import qt
import joint_params

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt2 = {}


#general sequence things. All of these are set automatically.
params_lt2['do_general_sweep']          = False
params_lt2['is_two_setup_experiment']   = 1
params_lt2['do_N_MBI']                  = 0 #practically not in use
params_lt2['do_carbon_init']            = 1
params_lt2['MW_before_LDE1']            = 0
params_lt2['LDE_1_is_init']             = 0
params_lt2['do_LDE_1']                  = 1 # we always do this.
params_lt2['LDE_1_is_el_init']          = 0
params_lt2['do_swap_onto_carbon']       = 1
params_lt2['do_LDE_2']                  = 1 # TODO finish the LDE element for non local operation
params_lt2['do_phase_correction']       = 1 
params_lt2['do_purifying_gate']         = 1
params_lt2['do_carbon_readout']         = 1 #if 0 then RO of the electron via an adwin trigger.

# LDE element
params_lt2['MW_during_LDE']             = 1 
params_lt2['AWG_SP_power']              = 1350e-9#1000e-9
params_lt2['LDE_SP_duration']           = 2e-6
params_lt2['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt2['average_repump_time'] 		= 0.5e-6#0.3e-6#250e-9#250e-9#350e-9#213e-9 
params_lt2['LDE_decouple_time']         = round(1/qt.exp_params['samples'][sample_name]['C4_freq_0'],9)#-50e-9
params_lt2['opt_pulse_start']           = 2.5e-6 #2215e-9 - 46e-9 + 4e-9 +1e-9 
params_lt2['MW_opt_puls1_separation']   = 100e-9#220e-9

#adwin params defs:
params_lt2['SP_duration'] = 30 #10
params_lt2['wait_after_pulse_duration'] = 1
params_lt2['do_sequences'] = 1
params_lt2['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt2['E_RO_durations']  = [params_lt2['Dynamical_stop_ssro_duration']] # only necessary for analysis
params_lt2['Dynamical_stop_ssro_threshold'] = 1
params_lt2['MBI_attempts_before_CR'] = 1 

params_lt2['phase_per_sequence_repetition'] =0.
params_lt2['phase_per_compensation_repetition'] =0.
params_lt2['total_phase_offset_after_sequence'] =0.
params_lt2['phase_correct_max_reps']    = 80

# channels
# params_lt2['wait_for_AWG_done'] = 1 # not used in adwin script
params_lt2['PLU_event_di_channel'] = 21
params_lt2['PLU_which_di_channel'] = 20
# params_lt2['AWG_start_DO_channel'] = 1 defined in msmt params
# params_lt2['AWG_done_DI_channel']= 1 defined in msmt params
params_lt2['wait_for_awg_done_timeout_cycles'] = 1000000000  # 10ms
# params_lt2['AWG_event_jump_DO_channel'] = 1 defined in msmt params
params_lt2['AWG_repcount_DI_channel'] = 19
params_lt2['remote_adwin_di_success_channel'] = 22
params_lt2['remote_adwin_di_fail_channel'] = 23
params_lt2['remote_adwin_do_success_channel'] = 14
params_lt2['remote_adwin_do_fail_channel'] = 15
params_lt2['adwin_comm_safety_cycles'] = 15
params_lt2['adwin_comm_timeout_cycles'] = 200000 # 1 ms
params_lt2['remote_awg_trigger_channel'] = 13
params_lt2['invalid_data_marker_do_channel'] = 1 # currently not used
params_lt2['master_slave_awg_trigger_delay'] = 9 # times 10ns, minimum is 9.

#eom pulse went to msmt params but might come back.
params_lt2['eom_pulse_amplitude']		= 1.9 
params_lt2['eom_pulse_duration']        = 2e-9
params_lt2['eom_off_duration']          = 50e-9
params_lt2['eom_off_amplitude']         = -0.293 # calibration 2015-11-04 <--> should be calibrated 
params_lt2['eom_overshoot_duration1']   = 20e-9
params_lt2['eom_overshoot1']            = -0.04 # calibrate!
params_lt2['eom_overshoot_duration2']   = 4e-9
params_lt2['eom_overshoot2']            = -0.00 # calibrate!
params_lt2['aom_risetime']              = 17e-9
params_lt2['aom_amplitude']             = 0.57 #calibrate!


params_lt2['AWG_wait_for_lt3_start']    =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt2['sync_during_LDE']           = 1

params_lt2['PLU_during_LDE']          = 1
params_lt2['PLU_gate_duration']       = 200e-9#70e-9 # 200e-9
params_lt2['PLU_gate_3_duration']     = 40e-9
params_lt2['PLU_1_delay']             = 1e-9
params_lt2['PLU_2_delay']             = 1e-9
params_lt2['PLU_3_delay']             = 50e-9
params_lt2['PLU_4_delay']             = 200e-9

params_lt2['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp'] #### needs to be changed back to regular pi/2 for most calibrations
params_lt2['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']
params_lt2['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt2['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']

### Everything carbon
params_lt2['dps_carbons']                    = [2,4]
params_lt2['carbon_init_method']            =  ['swap']
params_lt2['carbon_readout_orientation']    = 'positive'
# we don't want the old feedback crap
params_lt2['dynamic_phase_tau']			= 2.298e-6#2.298e-6
params_lt2['dynamic_phase_N']			= 2
params_lt2['phase_feedback_resolution']	= 4.5

### Everything HydraHarp
TH_HH_selector = 1e3 #set to 1 for HH
params_lt2['MAX_DATA_LEN']        =   int(100e6)/TH_HH_selector
params_lt2['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
params_lt2['MIN_SYNC_BIN']        =   int(1.6e6)/TH_HH_selector #5 us 
params_lt2['MAX_SYNC_BIN']        =   int(2.0e6)/TH_HH_selector#15 us # XXX was 15us 
params_lt2['MIN_HIST_SYNC_BIN']   =   int(0e6)/TH_HH_selector #XXXX was 5438*1e3
params_lt2['MAX_HIST_SYNC_BIN']   =   int(6*1e6)/TH_HH_selector
params_lt2['count_marker_channel'] = 1

params_lt2['pulse_start_bin'] = 2769e3 -params_lt2['MIN_SYNC_BIN'] #2490e3 BK 
params_lt2['pulse_stop_bin'] = 2792e3 - params_lt2['MIN_SYNC_BIN'] # 2499e3 BK 
params_lt2['tail_start_bin'] = 2792e3 - params_lt2['MIN_SYNC_BIN'] # 2499e3 BK 
params_lt2['tail_stop_bin'] = 2836e3 - params_lt2['MIN_SYNC_BIN']  # 2570e3 BK
params_lt2['PQ_ch1_delay'] = 0

params_lt2['measurement_time']    =   24*60*60 #sec = 24H
params_lt2['measurement_abort_check_interval']    = 1 #sec
params_lt2['wait_for_late_data'] = 0 #in units of measurement_abort_check_interval
params_lt2['TTTR_read_count'] = 131072#qt.instruments['HH_400'].get_T2_READMAX()
params_lt2['TTTR_RepetitiveReadouts'] =  1

params_lt2['measurement_time'] = 24.*60.*60. 