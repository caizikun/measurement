"""
This file contains all the joint and lt4 measurement parameters.
"""
import qt
import joint_params

params_lt4 = {}

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

#CR:
params_lt4['counter_channel']   = qt.exp_params['protocols']['AdwinSSRO']['counter_channel']
params_lt4['repump_duration']   = qt.exp_params['protocols']['AdwinSSRO']['repump_duration']#10#500# 10 for green, 500 for yellow
params_lt4['repump_amplitude']  = qt.exp_params['protocols']['AdwinSSRO']['repump_amplitude']#50e-6#30e-9 
params_lt4['cr_wait_after_pulse_duration'] = qt.exp_params['protocols']['AdwinSSRO']['cr_wait_after_pulse_duration']
params_lt4['CR_duration'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_duration']
params_lt4['CR_preselect'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_preselect']
params_lt4['CR_probe'] 			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_probe']
params_lt4['CR_repump']			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_repump'] # 1 for yellow, 1000 for green

params_lt4['cr_mod'] 				    =  True # qt.exp_params['protocols']['AdwinSSRO']['cr_mod']
params_lt4['cr_mod_control_dac']		=  qt.exp_params['protocols']['cr_mod']['cr_mod_control_dac']
params_lt4['cr_mod_control_offset']     =  qt.exp_params['protocols']['cr_mod']['cr_mod_control_offset']
params_lt4['cr_mod_control_amp']        =  qt.exp_params['protocols']['cr_mod']['cr_mod_control_amp'] 
params_lt4['cr_mod_control_avg_pts']    =  qt.exp_params['protocols']['cr_mod']['cr_mod_control_avg_pts']
params_lt4['repump_mod_control_amp']    =  qt.exp_params['protocols']['cr_mod']['repump_mod_control_amp'] 
params_lt4['repump_mod_control_dac']	=  qt.exp_params['protocols']['cr_mod']['repump_mod_control_dac']

#bell adwin:
params_lt4['AWG_start_DO_channel'] = 9
params_lt4['AWG_done_DI_channel'] = 18
params_lt4['SP_duration'] = 10
params_lt4['wait_after_pulse_duration'] = 3
params_lt4['remote_CR_DI_channel'] = 19
params_lt4['PLU_DI_channel'] = 21
params_lt4['do_sequences'] = 1
params_lt4['SSRO_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt4['wait_for_AWG_done'] = 0
params_lt4['sequence_wait_time'] = 10 #NOTE gets set in autoconfig
params_lt4['wait_for_remote_CR'] = 1  #NOTE gets set in bell script

#adwin powers
params_lt4['Ex_CR_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_CR_amplitude'] #1e-9#0.5e-9#10e-9#6e-9             
params_lt4['A_CR_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_CR_amplitude'] #1e-9#10e-9#16e-9              
params_lt4['A_SP_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_SP_amplitude']	#3e-9             
params_lt4['Ex_RO_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_RO_amplitude']	# 4e-9
params_lt4['A_RO_amplitude']  = 0
params_lt4['Ex_SP_amplitude'] = 0e-9   

####################
### pulses and MW stuff lt4
#####################
## general
params_lt4['mw_frq'] 				= qt.exp_params['samples'][sample_name]['ms-1_cntr_frq']
params_lt4['mw_power'] 				= qt.exp_params['protocols']['AdwinSSRO+espin']['mw_power']
params_lt4['MW_pulse_mod_risetime'] = qt.exp_params['protocols']['AdwinSSRO+espin']['MW_pulse_mod_risetime']

params_lt4['square_MW_pulses']    = False
#params_lt4['MW_pi_amp']	   	   = qt.exp_params['protocols'][name]['pulses']['Square_pi_amp'] #0.895 # 2014-07-09
#params_lt4['MW_pi_duration']   = qt.exp_params['protocols'][name]['pulses']['Square_pi_length']# 180e-9 # 2014-07-09
#params_lt4['MW_pi2_amp']	   = qt.exp_params['protocols'][name]['pulses']['Square_pi2_amp']
#params_lt4['MW_pi2_duration']  = qt.exp_params['protocols'][name]['pulses']['Square_pi2_length']#90e-9 # 2014-07-09
params_lt4['MW_pi_amp']	  	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp'] #0.895 # 2014-07-09
params_lt4['MW_pi_duration']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']# 180e-9 # 2014-07-09
params_lt4['MW_pi2_amp']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt4['MW_pi2_duration']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']#90e-9 # 2014-07-09
#params_lt4['MW_Npi4_amp']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_Npi4_amp'] 
#params_lt4['MW_Npi4_duration']  = qt.exp_params['protocols'][name]['pulses']['Hermite_Npi4_length']#90e-9 # 2014-07-09

params_lt4['MW_RND_amp_I']	   = params_lt4['MW_pi2_amp']#TODO Calibrate  -0.487 
params_lt4['MW_RND_duration_I']= params_lt4['MW_pi2_duration'] #TODO Calibrate 50e-9
params_lt4['MW_RND_amp_Q']	   = params_lt4['MW_pi2_amp']# 0.487 
params_lt4['MW_RND_duration_Q']= params_lt4['MW_pi2_duration'] #50e-9

params_lt4['MW_BellStateOffset'] = 0 # Sam should be rotated by 0.53 pi  AR 2015-02-26

params_lt4['echo_offset'] = -85e-9 #50 ns
params_lt4['free_precession_time_1st_revival'] = 73.2e-6 # this is the total free precession time
params_lt4['free_precession_offset'] = 0
#adwin wait time after PLU signal:
params_lt4['wait_before_RO'] = joint_params.joint_params['wait_for_1st_revival']*params_lt4['free_precession_time_1st_revival']*1e6+10


# LDE Sequence in the AWGs # params taken from the previous LT1 params
params_lt4['eom_pulse_amplitude']		= 1.9 
params_lt4['eom_pulse_duration']        = 2e-9
params_lt4['eom_off_duration']          = 70e-9
params_lt4['eom_off_amplitude']         = -.25 
params_lt4['eom_overshoot_duration1']   = 20e-9
params_lt4['eom_overshoot1']            = -0.04
params_lt4['eom_overshoot_duration2']   = 4e-9
params_lt4['eom_overshoot2']            = -0.00
params_lt4['aom_risetime']              = 15e-9
params_lt4['aom_amplitude']             = 0.47   #2015-02-22

params_lt4['MW_during_LDE']           = 0 #NOTE:gets set automatically

params_lt4['AWG_SP_power']            = params_lt4['A_SP_amplitude']
params_lt4['AWG_RO_power']            = 4e-9 # 2014-11-18
params_lt4['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT2
params_lt4['LDE_SP_duration']         = 5.e-6 #DONT CHANGE THIS
params_lt4['LDE_yellow_duration']     = -1. # if this is < 0, no yellow pulse is added to the sequence

params_lt4['MW_opt_puls1_separation'] = 10e-9 #distance between the end of the MW and the start of opt puls1
params_lt4['MW_1_separation'] 		  = joint_params.joint_params['opt_pulse_separation']
params_lt4['MW_RND_wait'] 			  = 160e-9 #wait start RND MW after end of RND halt pulse
params_lt4['RND_duration'] 			  = 250e-9
params_lt4['RO_wait'] 				  = 75e-9 #wait start RO after end of RND MW pulse
params_lt4['sync_during_LDE']   	  = 1
params_lt4['plu_during_LDE']    	  = 1
params_lt4['opt_pulse_start']   	  = params_lt4['LDE_SP_duration'] +  500e-9 #DONT CHANGE THIS
params_lt4['AWG_wait_for_lt3_start'] =  9347e-9+1e-9#8.768e-6+787e-9#1787e-9#1487e-9#1487e-9#8e-6 = dt(f,AB) ###2014-06-07: Somehow both 1487 and 1486 produce 1487, Hannes -> i think because of multiple of 4 -> i chnged the start of the pulse 

params_lt4['PLU_gate_duration']       = 200e-9#70e-9
params_lt4['PLU_gate_3_duration']     = 40e-9
params_lt4['PLU_1_delay']             = 1e-9
params_lt4['PLU_2_delay']             = 1e-9
params_lt4['PLU_3_delay']             = 50e-9
params_lt4['PLU_4_delay']             = 150e-9

params_lt4['MAX_DATA_LEN'] 			=       joint_params.joint_params['MAX_DATA_LEN']
params_lt4['BINSIZE'] 				=       joint_params.joint_params['BINSIZE'] #2**BINSIZE*BASERESOLUTION 
params_lt4['MIN_SYNC_BIN'] 			=       joint_params.joint_params['MIN_SYNC_BIN']
params_lt4['MAX_SYNC_BIN'] 			=       joint_params.joint_params['MAX_SYNC_BIN']
params_lt4['MIN_HIST_SYNC_BIN'] 	=  		joint_params.joint_params['MIN_HIST_SYNC_BIN']
params_lt4['MAX_HIST_SYNC_BIN'] 	=  		joint_params.joint_params['MAX_HIST_SYNC_BIN']
params_lt4['TTTR_RepetitiveReadouts']=	 	joint_params.joint_params['TTTR_RepetitiveReadouts']
params_lt4['TTTR_read_count'] 		=    	joint_params.joint_params['TTTR_read_count']
params_lt4['measurement_abort_check_interval'] = joint_params.joint_params['measurement_abort_check_interval']
params_lt4['wait_for_late_data'] 	= 		joint_params.joint_params['wait_for_late_data']
params_lt4['entanglement_marker_number'] = 4
params_lt4['tail_start_bin'] = 5350
params_lt4['tail_stop_bin'] = 5350 + 200

params_lt4['measurement_time'] =   2*60*60#sec = 60 mins

