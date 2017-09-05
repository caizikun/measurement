'''
dummy file with local parameters for AWG sequence generation

NK 2016
'''
import qt
import joint_params

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt4 = {}

#general sequence things. All of these are set automatically.
params_lt4['do_general_sweep']          = False
params_lt4['is_two_setup_experiment']   = 0
params_lt4['do_N_MBI']                  = 0 #practically not in use
params_lt4['do_carbon_init']            = 1
params_lt4['MW_before_LDE1']            = 0
params_lt4['LDE_1_is_init']             = 0
params_lt4['do_LDE_1']                  = 1 # we always do this.
params_lt4['LDE_1_is_el_init']          = 0
params_lt4['simple_el_init']            = 0
params_lt4['do_swap_onto_carbon']       = 1
params_lt4['do_LDE_2']                  = 1 # TODO finish the LDE element for non local operation
params_lt4['do_phase_correction']       = 1 
params_lt4['do_purifying_gate']         = 1
params_lt4['do_carbon_readout']         = 1 #if 0 then RO of the electron via an adwin trigger.
params_lt4['do_sweep_delay_cycles'] 	= 0
params_lt4['do_dd_phase_correction_calibration'] = 0
params_lt4['do_phase_offset_sweep'] = 0
params_lt4['do_phase_per_seqrep_sweep'] = 0
params_lt4['repump_instead_of_LDE_2'] = 0

params_lt4['LDE1_attempts'] = 10
params_lt4['LDE2_attempts'] = 10

# LDE element
params_lt4['MW_during_LDE']             = 1 
params_lt4['AWG_SP_power']              = 500e-9
params_lt4['LDE_SP_duration']           = 2e-6
params_lt4['LDE_SP_delay']			    = 0e-6 ### don't change this.
params_lt4['average_repump_time'] 		= 350e-9#90e-9 
params_lt4['use_avg_repump_time_from_msmt_params'] = 0
params_lt4['LDE_decouple_time']         = 2.256e-6 #round(1/qt.exp_params['samples'][sample_name]['C4_freq_0'],9) + #-50e-9
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
params_lt4['wait_for_awg_done_timeout_cycles'] = 1000000000  # 10ms
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

#eom pulse went to msmt params but might come back.
# params_lt4['eom_pulse_amplitude']		= 1.9 
# params_lt4['eom_pulse_duration']        = 2e-9
# params_lt4['eom_off_duration']          = 50e-9
# params_lt4['eom_off_amplitude']         = -0.293 # calibration 2015-11-04 <--> should be calibrated 
# params_lt4['eom_overshoot_duration1']   = 20e-9
# params_lt4['eom_overshoot1']            = -0.04 # calibrate!
# params_lt4['eom_overshoot_duration2']   = 4e-9
# params_lt4['eom_overshoot2']            = -0.00 # calibrate!
# params_lt4['aom_risetime']              = 17e-9
# params_lt4['aom_amplitude']             = 0.57 #calibrate!


params_lt4['AWG_wait_for_lt3_start']    =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt4['sync_during_LDE']           = 0

params_lt4['PLU_during_LDE']          = 1
params_lt4['PLU_gate_duration']       = 200e-9#70e-9 # 200e-9
params_lt4['PLU_gate_3_duration']     = 40e-9
params_lt4['PLU_1_delay']             = 1e-9
params_lt4['PLU_2_delay']             = 1e-9
params_lt4['PLU_3_delay']             = 50e-9
params_lt4['PLU_4_delay']             = 200e-9

params_lt4['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp'] #### needs to be changed back to regular pi/2 for most calibrations
params_lt4['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']
params_lt4['mw_first_pulse_phase']    = qt.exp_params['protocols'][name]['pulses']['X_phase']
params_lt4['LDE_final_mw_amplitude']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']

### Everything carbon
params_lt4['carbons']                       = [2]
params_lt4['reverse_carbon_inits']          = True
params_lt4['carbon_swap_el_states']         = ['Z']
params_lt4['carbon_init_method']            = 'swap'
params_lt4['carbon_readout_orientation']    = 'positive'
# carbon_encoding: serial_swap or MBE
params_lt4['carbon_encoding']               = 'serial_swap'
params_lt4['sequence_type']                 = params_lt4['carbon_encoding']
params_lt4['dps_MBE_bases']                 = ['Y','Y']
params_lt4['dps_MBE_readout_orientation']   = 'positive'
params_lt4['delay_feedback_N']              = 1
params_lt4['delay_feedback_target_phase']   = params_lt4['delay_feedback_N']*8*360.0 # making sure that we have enough delay time
params_lt4['delay_feedback_pulse_seq']      = ['X','mX']

params_lt4['delay_feedback_use_calculated_phase_offsets'] = 1
params_lt4['delay_feedback_single_phase_offset'] = 1

params_lt4['delay_feedback_initial_static_dec_block_pulse_seq'] = ['X', 'Y', 'X', 'Y']
params_lt4['delay_feedback_initial_static_dec_block_duration'] = 8*2.2e-6 #20e-6

params_lt4['delay_feedback_final_static_dec_block_pulse_seq'] = ['X', 'mX', 'X', 'mX']
params_lt4['delay_feedback_final_static_dec_block_elflip_insert_after'] = 2
params_lt4['delay_feedback_final_static_dec_block_duration'] = 8*2.2e-6 #20e-6

params_lt4['delay_feedback_static_dec_duration'] = (
    params_lt4['delay_feedback_initial_static_dec_block_duration']
    + params_lt4['delay_feedback_final_static_dec_block_duration']
)

params_lt4['delay_feedback_adwin_trigger_channel'] = 'adwin_count'
params_lt4['delay_feedback_adwin_trigger_length'] = 3e-6
params_lt4['delay_feedback_adwin_trigger_delay'] = 1e-6
params_lt4['delay_feedback_HHsync_delay'] = params_lt4['delay_feedback_initial_static_dec_block_duration'] - 1e-6

# we don't want the old feedback crap
params_lt4['use_old_feedback']			= 0 
params_lt4['dynamic_phase_tau']			= 2.296e-6#2.298e-6
params_lt4['dynamic_phase_N']			= 2
params_lt4['phase_feedback_resolution']	= 4.5

### Everything HydraHarp
do_PQ_msmt = 0

params_lt4['do_PQ_msmt'] = do_PQ_msmt
params_lt4['do_delay_HH_trigger'] = do_PQ_msmt
params_lt4['delay_feedback_HHsync_include'] = do_PQ_msmt

TH_HH_selector = 1 #set to 1 for HH
params_lt4['MAX_DATA_LEN']        =   int(100e6)/TH_HH_selector
params_lt4['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
params_lt4['MIN_SYNC_BIN']        =   int(4e6)/TH_HH_selector #5 us 
params_lt4['MAX_SYNC_BIN']        =   int(8.0e6)/TH_HH_selector#15 us # XXX was 15us
params_lt4['MIN_HIST_SYNC_BIN']   =   int(4e6)/TH_HH_selector #XXXX was 5438*1e3
params_lt4['MAX_HIST_SYNC_BIN']   =   int(8e6)/TH_HH_selector
params_lt4['count_marker_channel'] = 1

params_lt4['PQ_ch1_delay'] = 0

params_lt4['measurement_time']    =   24*60*60 #sec = 24H
params_lt4['measurement_abort_check_interval']    = 1 #sec
params_lt4['wait_for_late_data'] = 0 #in units of measurement_abort_check_interval
params_lt4['TTTR_read_count'] = 131072#qt.instruments['HH_400'].get_T2_READMAX()
params_lt4['TTTR_RepetitiveReadouts'] =  1

params_lt4['measurement_time'] = 24.*60.*60. 