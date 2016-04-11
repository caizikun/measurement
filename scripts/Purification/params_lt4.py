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

#general sequence things. All of this are set automatically.
params_lt4['MW_during_LDE'] 	= 1 
params_lt4['do_general_sweep']    = False
params_lt4['non_local']           = 1
params_lt4['do_N_MBI']            = 0
params_lt4['init_carbon']         = 0
params_lt4['do_LDE_1']            = 1 # TODO finish the LDE elements for non local operation
params_lt4['swap_onto_carbon']    = 0
params_lt4['do_LDE_2']            = 0 # TODO finish the LDE element for non local operation
params_lt4['phase_correct']       = 0 
params_lt4['purify']              = 0
params_lt4['C13_RO']              = 0 #if 0 then RO of the electron via an adwin trigger.
params_lt4['final_RO_in_adwin']   = 0 # this gets rid of the final RO

#adwin channel defs:
params_lt4['AWG_start_DO_channel'] = 9
params_lt4['AWG_done_DI_channel'] = 18
params_lt4['AWG_event_jump_DO_channel'] = 8
params_lt4['SP_duration'] = 30 #10
params_lt4['wait_after_pulse_duration'] = 3
params_lt4['remote_CR_DI_channel'] = 19
params_lt4['PLU_DI_channel'] = 21
params_lt4['do_sequences'] = 1
params_lt4['SSRO_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt4['wait_for_AWG_done'] = 1
params_lt4['sequence_wait_time'] = 10 #NOTE should be set in autoconfig! Not done yet!
params_lt4['wait_for_remote_CR'] = 1  #NOTE should be set when generating the msmt! Not done yet!
params_lt4['invalid_data_marker_do_channel'] = 5

# LDE element
params_lt4['AWG_SP_power']              = 5e-9 #insert appropriate repump power.
params_lt4['LDE_SP_duration']           = 2e-6

#eom pulse
params_lt4['eom_pulse_amplitude']		= 1.9 
params_lt4['eom_pulse_duration']        = 2e-9
params_lt4['eom_off_duration']          = 50e-9
params_lt4['eom_off_amplitude']         = -0.293 # calibration 2015-11-04 <--> should be calibrated 
params_lt4['eom_overshoot_duration1']   = 20e-9
params_lt4['eom_overshoot1']            = -0.04 # calibrate!
params_lt4['eom_overshoot_duration2']   = 4e-9
params_lt4['eom_overshoot2']            = -0.00 # calibrate!
params_lt4['aom_risetime']              = 17e-9
params_lt4['aom_amplitude']             = 0.57 #calibrate!

#timings
params_lt4['opt_pulse_start']           = 2.5e-6 #2215e-9 - 46e-9 + 4e-9 +1e-9 
params_lt4['MW_opt_puls1_separation']   = -22e-9
params_lt4['MW_1_separation']           = joint_params.joint_params['opt_pulse_separation'] #or alternatively tau_larmor
params_lt4['AWG_wait_for_lt3_start'] =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt4['sync_during_LDE']           = 1

params_lt4['PLU_during_LDE']          = 1
params_lt4['PLU_gate_duration']       = 200e-9#70e-9
params_lt4['PLU_gate_3_duration']     = 40e-9
params_lt4['PLU_1_delay']             = 1e-9
params_lt4['PLU_2_delay']             = 1e-9
params_lt4['PLU_3_delay']             = 50e-9
params_lt4['PLU_4_delay']             = 150e-9

params_lt4['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt4['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']
### Everything carbon
params_lt4['carbon']                    = 1

### Everything about the sequence/logic

params_lt4['phase_correct_max_reps']    = 10 # should really be joint params. move later