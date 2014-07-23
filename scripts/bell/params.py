"""
This file contains all the joint and lt3 measurement parameters.
"""
import qt

joint_params = {}

### default process settings
joint_params['RO_during_LDE'] = 0

joint_params['opt_pi_pulses'] = 2
joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok
joint_params['initial_delay']           = 10e-9 ## 2014-06-07 initial delay used to be a joint param. i made it setup specific, to overlap the pulses
joint_params['opt_pulse_separation']    = 600e-9

joint_params['RND_during_LDE'] = 0 
joint_params['do_echo'] = 0
joint_params['do_final_MW_rotation'] = 0
joint_params['wait_for_1st_revival'] = 0
joint_params['DD_number_pi_pulses'] = 2 # the maximum number of pi pulses is 3 !!!

joint_params['LDE_element_length']     = 16.e-6+(joint_params['opt_pi_pulses']-2)*joint_params['opt_pulse_separation']  # 9e-6 for TPQI with 5 pulses
joint_params['LDE_RO_duration'] = 4e-6
joint_params['separate_RO_element'] =  True

joint_params['MAX_DATA_LEN'] =       int(100e6)
joint_params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
joint_params['MIN_SYNC_BIN'] =       0 #WRONG / TODO
joint_params['MAX_SYNC_BIN'] =       7000
joint_params['TTTR_read_count'] = 	 1000 #s
joint_params['measurement_abort_check_interval']    = 1. #sec


params_lt3 = {}

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

#CR:
params_lt3['counter_channel']   = qt.exp_params['protocols']['AdwinSSRO']['counter_channel']
params_lt3['repump_duration']   = qt.exp_params['protocols']['AdwinSSRO']['repump_duration']#10#500# 10 for green, 500 for yellow
params_lt3['repump_amplitude']  = qt.exp_params['protocols']['AdwinSSRO']['repump_amplitude']#50e-6#30e-9 
params_lt3['cr_wait_after_pulse_duration'] = qt.exp_params['protocols']['AdwinSSRO']['cr_wait_after_pulse_duration']
params_lt3['CR_duration'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_duration']
params_lt3['CR_preselect'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_preselect']
params_lt3['CR_probe'] 			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_probe']
params_lt3['CR_repump']			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_repump'] # 1 for yellow, 1000 for green

params_lt3['cr_mod'] 			= False
#CR check modulation pars:
#to be implemented
#
#

#bell adwin:
params_lt3['AWG_start_DO_channel'] = 9
params_lt3['AWG_done_DI_channel'] = 17
params_lt3['SP_duration'] = 10
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['remote_CR_DI_channel'] = 19
params_lt3['PLU_DI_channel'] = 21
params_lt3['do_sequences'] = 1
params_lt3['SSRO_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt3['wait_for_AWG_done'] = 0
params_lt3['sequence_wait_time'] = 10 #NOTE gets set in autoconfig
params_lt3['wait_for_remote_CR'] = 1  #NOTE gets set in bell script

#adwin powers
params_lt3['Ex_CR_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_CR_amplitude'] #1e-9#0.5e-9#10e-9#6e-9             
params_lt3['A_CR_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_CR_amplitude'] #1e-9#10e-9#16e-9              
params_lt3['A_SP_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_SP_amplitude']	#3e-9             
params_lt3['Ex_RO_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_RO_amplitude']	# 4e-9
params_lt3['A_RO_amplitude']  = 0
params_lt3['Ex_SP_amplitude'] = 0e-9   

####################
### pulses and MW stuff LT3
#####################
## general
params_lt3['mw_frq'] 				= qt.exp_params['samples'][sample_name]['ms-1_cntr_frq']
params_lt3['mw_power'] 				= qt.exp_params['protocols']['AdwinSSRO+espin']['mw_power']
params_lt3['MW_pulse_mod_risetime'] = qt.exp_params['protocols']['AdwinSSRO+espin']['MW_pulse_mod_risetime']

params_lt3['MW_pi_amp_I']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp_Imod'] #0.895 # 2014-07-09
params_lt3['MW_pi_amp_Q']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp_Qmod'] #0.895 # 2014-07-09
params_lt3['MW_pi_duration']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']# 180e-9 # 2014-07-09
params_lt3['MW_pi2_amp_I']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp_Imod']
params_lt3['MW_pi2_amp_Q']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp_Qmod'] 
params_lt3['MW_pi2_duration']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']#90e-9 # 2014-07-09
params_lt3['MW_RND_amp_I']	   = params_lt3['MW_pi2_amp_I']#TODO Calibrate  -0.487 
params_lt3['MW_RND_duration_I']= params_lt3['MW_pi2_duration'] #TODO Calibrate 50e-9
params_lt3['MW_RND_amp_Q']	   = params_lt3['MW_pi2_amp_Q']# 0.487 
params_lt3['MW_RND_duration_Q']= params_lt3['MW_pi2_duration'] #50e-9


params_lt3['echo_offset'] = 0e-9 #50 ns
params_lt3['free_precession_time_1st_revival'] = 73.2e-6 # this is the total free precession time
params_lt3['free_precession_offset'] = 0
#adwin wait time after PLU signal:
params_lt3['wait_before_RO'] = joint_params['wait_for_1st_revival']*params_lt3['free_precession_time_1st_revival']*1e6+10


# LDE Sequence in the AWGs
params_lt3['eom_pulse_amplitude']        = 2.0 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
params_lt3['eom_pulse_duration']         = 2e-9
params_lt3['eom_off_amplitude']          = -0.055 # calibration from 2014-07-23
params_lt3['eom_off_duration']           = 150e-9
params_lt3['eom_overshoot_duration1']    = 20e-9
params_lt3['eom_overshoot1']             = -0.03 # calibration from 19-03-2014# 
params_lt3['eom_overshoot_duration2']    = 10e-9
params_lt3['eom_overshoot2']             = 0
params_lt3['aom_risetime']				 = 15e-9
params_lt3['aom_amplitude']				 = 0.65 # 2014-07-23

params_lt3['MW_during_LDE']           = 0 #NOTE:gets set automatically

params_lt3['AWG_SP_power']            = params_lt3['A_SP_amplitude']
params_lt3['AWG_RO_power']            = params_lt3['Ex_RO_amplitude']
params_lt3['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT2
params_lt3['LDE_SP_duration']         = 5.e-6 
params_lt3['LDE_yellow_duration']     = -1. # if this is < 0, no yellow pulse is added to the sequence

params_lt3['MW_opt_puls1_separation'] = 200e-9 #distance between the end of the MW and the start of opt puls1
params_lt3['MW_1_separation'] = joint_params['opt_pulse_separation']
params_lt3['MW_RND_wait'] = 160e-9 #wait start RND MW after end of RND halt pulse
params_lt3['RND_duration'] = 250e-9
params_lt3['RO_wait'] = 75e-9 #wait start RO after end of RND MW pulse
params_lt3['sync_during_LDE'] = 1
params_lt3['plu_during_LDE'] = 1
params_lt3['opt_pulse_start'] = params_lt3['LDE_SP_duration'] +  500e-9
params_lt3['AWG_wait_for_lt1_start'] =  1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt3['PLU_gate_duration']       = 200e-9#70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 1e-9
params_lt3['PLU_2_delay']             = 1e-9
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 150e-9

params_lt3['MAX_DATA_LEN'] =       joint_params['MAX_DATA_LEN']
params_lt3['BINSIZE'] =            joint_params['BINSIZE'] #2**BINSIZE*BASERESOLUTION 
params_lt3['MIN_SYNC_BIN'] =       joint_params['MIN_SYNC_BIN']
params_lt3['MAX_SYNC_BIN'] =       joint_params['MAX_SYNC_BIN']
params_lt3['TTTR_read_count'] =    joint_params['TTTR_read_count']
params_lt3['measurement_abort_check_interval']    = joint_params['measurement_abort_check_interval']

params_lt3['measurement_time'] =   60*60#sec = 60 mins

joint_params['RND_start'] = params_lt3['opt_pulse_start']+(joint_params['opt_pi_pulses']-1)*joint_params['opt_pulse_separation'] + 3.3e-6 # = dt(f,BC)-dt(AC) + margin