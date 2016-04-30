'''
dummy file with local parameters for AWG sequence generation

NK 2016
'''
import qt
import joint_params

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

params_lt3 = {}

#general sequence things. All of this are set automatically.
params_lt3['MW_during_LDE'] 	= 1 
params_lt3['do_general_sweep']    = False
params_lt3['is_two_setup_experiment'] = 0
params_lt3['do_N_MBI']            = 0
params_lt3['do_carbon_init']         = 0
params_lt3['do_LDE_1']            = 1 # we always do this.
params_lt3['do_swap_onto_carbon']    = 0
params_lt3['do_LDE_2']            = 0 # TODO finish the LDE element for non local operation
params_lt3['do_phase_correction']       = 0 
params_lt3['do_purifying_gate']              = 0
params_lt3['do_carbon_readout']   = 0 #if 0 then RO of the electron via an adwin trigger.


#adwin params defs:
params_lt3['SP_duration'] = 10 #10
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['do_sequences'] = 1
params_lt3['Dynamical_stop_ssro_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt3['Dynamical_stop_ssro_threshold'] = 1
params_lt3['MBI_attempts_before_CR'] = 1 

params_lt3['phase_per_sequence_repetition'] =0.
params_lt3['phase_per_compensation_repetition'] =0.
params_lt3['total_phase_offset_after_sequence'] =0.


# channels
#params_lt3['wait_for_AWG_done'] = 1 # not used in adwin script
params_lt3['PLU_event_di_channel'] = 20 
params_lt3['PLU_which_di_channel'] = 20 # not used on slave
#params_lt3['AWG_start_DO_channel'] =  defined in msmt params
#params_lt3['AWG_done_DI_channel']= defined in msmt params
params_lt3['wait_for_awg_done_timeout_cycles'] = 10000  # 10ms
#params_lt3['AWG_event_jump_DO_channel'] =  defined in msmt params
params_lt3['AWG_repcount_DI_channel'] = 16 
params_lt3['remote_adwin_di_success_channel'] = 19 
params_lt3['remote_adwin_di_fail_channel'] = 18
params_lt3['remote_adwin_do_success_channel'] = 13
params_lt3['remote_adwin_do_fail_channel'] = 8
params_lt3['adwin_comm_safety_cycles'] = 2 
params_lt3['adwin_comm_timeout_cycles'] = 1000 # 1ms 
params_lt3['remote_awg_trigger_channel'] = 1 # not used on slave
params_lt3['invalid_data_marker_do_channel'] = 5 # currently not used

# LDE element
params_lt3['AWG_SP_power']              = 500e-9 #insert appropriate repump power.
params_lt3['LDE_SP_duration']           = 2e-6
params_lt3['LDE_decouple_time']         = 2.32e-6
params_lt3['average_repump_time'] = 400e-9 + 700e-9 # XXX put repump AOM delay here!

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

#timings
params_lt3['opt_pulse_start']           = 2.5e-6 #2215e-9 - 46e-9 + 4e-9 +1e-9 
params_lt3['MW_opt_puls1_separation']   = -22e-9
#params_lt3['MW_1_separation']           = joint_params.joint_params['opt_pulse_separation'] #or alternatively tau_larmor
params_lt3['AWG_wait_for_lt3_start'] =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt3['sync_during_LDE']           = 1

params_lt3['PLU_during_LDE']          = 1
params_lt3['PLU_gate_duration']       = 200e-9#70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 1e-9
params_lt3['PLU_2_delay']             = 1e-9
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 150e-9
params_lt3['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt3['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']
### Everything carbon
params_lt3['carbon']                    = 1

### Everything about the sequence/logic

params_lt3['phase_correct_max_reps']    = 10 # should really be joint params. move later