'''
dummy file with local parameters for AWG sequence generation

NK 2016
'''
import qt
import joint_params

name = qt.exp_params['protocols']['current']

params_lt1 = {}

#general sequence things
params_lt1['MW_during_LDE'] = 1

# LDE element
params_lt1['AWG_SP_power']              = 5e-9
params_lt1['LDE_SP_duration']           = 2e-6


# define adwin channels here #XXXXX

#eom pulse
params_lt1['eom_pulse_amplitude']       = 2.0 # (for long pulses it is 1.45, for short:2.0)calibration from 19-03-2014
params_lt1['eom_pulse_duration']        = 2e-9
params_lt1['eom_off_amplitude']         = -0.02 # to be calibrated
params_lt1['eom_off_duration']          = 50e-9 
params_lt1['eom_overshoot_duration1']   = 20e-9
params_lt1['eom_overshoot1']            = -0.03 # to be calibrated
params_lt1['eom_overshoot_duration2']   = 10e-9
params_lt1['eom_overshoot2']            = 0
params_lt1['aom_risetime']              = 40e-9#10e-9 # try to minimize by realigning!
params_lt1['aom_amplitude']             = 0.65 # on CR 31

#timings
params_lt1['opt_pulse_start']           = 2.5e-6 #2215e-9 - 46e-9 + 4e-9 +1e-9 
params_lt1['MW_opt_puls1_separation']   = 22e-9


params_lt1['average_repump_time'] = 400e-9 + 700e-9 # put repump AOM delay here!
params_lt1['LDE_decouple_time'] = 2.32e-6

# probably not necessary
params_lt1['AWG_wait_for_lt3_start'] =  9347e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt1['sync_during_LDE']           = 1

params_lt1['PLU_during_LDE']          = 1
params_lt1['PLU_gate_duration']       = 200e-9#70e-9
params_lt1['PLU_gate_3_duration']     = 40e-9
params_lt1['PLU_1_delay']             = 1e-9
params_lt1['PLU_2_delay']             = 1e-9
params_lt1['PLU_3_delay']             = 50e-9
params_lt1['PLU_4_delay']             = 150e-9

params_lt1['mw_first_pulse_amp']      = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt1['mw_first_pulse_length']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']

### Everything carbon
params_lt1['carbon']                    = 1
params_lt1['carbon_init_method']        = 'swap'

### Everything about the sequence/logic

params_lt1['phase_correct_max_reps']    = 10 