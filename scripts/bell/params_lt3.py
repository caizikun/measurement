"""
This file contains all the lt3 measurement parameters.
"""
import qt
import joint_params

params_lt3 = {}

### Hardware stuff
name = qt.exp_params['protocols']['current']
sample_name = qt.exp_params['samples']['current']

#CR
params_lt3['counter_channel'] 	= qt.exp_params['protocols']['AdwinSSRO']['counter_channel']
params_lt3['repump_duration'] 	= qt.exp_params['protocols']['AdwinSSRO']['repump_duration'] #500 # 10 for green, 500 for yellow
params_lt3['repump_amplitude'] 	= qt.exp_params['protocols']['AdwinSSRO']['repump_amplitude']# 30e-9 
params_lt3['cr_wait_after_pulse_duration'] = qt.exp_params['protocols']['AdwinSSRO']['cr_wait_after_pulse_duration']
params_lt3['CR_duration'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_duration']
params_lt3['CR_preselect'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_preselect']
params_lt3['CR_probe'] 			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_probe']
params_lt3['CR_repump']			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_repump']

params_lt3['cr_mod'] 				    =  True#qt.exp_params['protocols']['AdwinSSRO']['cr_mod']
params_lt3['cr_mod_control_dac']		=  qt.exp_params['protocols']['cr_mod']['cr_mod_control_dac']
params_lt3['cr_mod_control_offset']     =  qt.exp_params['protocols']['cr_mod']['cr_mod_control_offset'] #XXX this should be true in case of cr mod!!
params_lt3['cr_mod_control_amp']        =  qt.exp_params['protocols']['cr_mod']['cr_mod_control_amp'] 
params_lt3['cr_mod_control_avg_pts']    =  qt.exp_params['protocols']['cr_mod']['cr_mod_control_avg_pts'] 
params_lt3['repump_mod_control_amp']    =  qt.exp_params['protocols']['cr_mod']['repump_mod_control_amp'] 
params_lt3['repump_mod_control_dac']	=  qt.exp_params['protocols']['cr_mod']['repump_mod_control_dac']


#bell adwin:
params_lt3['AWG_done_DI_channel'] = 17
params_lt3['AWG_success_DI_channel'] = 9
params_lt3['SP_duration'] = 10
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['remote_CR_DO_channel'] = 12
params_lt3['SSRO_duration'] = qt.exp_params['protocols'][name]['AdwinSSRO-integrated']['SSRO_duration'] #15 
params_lt3['wait_for_AWG_done'] = 1
params_lt3['sequence_wait_time'] = 10 #NOTE gets set in Bell.autoconfig

#adwin powers
params_lt3['Ex_CR_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_CR_amplitude'] 
params_lt3['A_CR_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_CR_amplitude']          
params_lt3['A_SP_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_SP_amplitude']	        
params_lt3['Ex_RO_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_RO_amplitude']
params_lt3['A_RO_amplitude']  = 0
params_lt3['Ex_SP_amplitude'] = 0e-9  


####################
### pulses and MW stuff lt3
#####################
## general
params_lt3['mw_frq'] 				= qt.exp_params['samples'][sample_name]['ms-1_cntr_frq']
params_lt3['mw_power'] 				= qt.exp_params['protocols']['AdwinSSRO+espin']['mw_power']
params_lt3['MW_pulse_mod_risetime'] = qt.exp_params['protocols']['AdwinSSRO+espin']['MW_pulse_mod_risetime']

params_lt3['MW_pi_amp']	   	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp'] #0.895 # 2014-07-09
params_lt3['MW_pi_duration']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']# 180e-9 # 2014-07-09
params_lt3['MW_pi2_amp']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt3['MW_pi2_duration']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']#90e-9 # 2014-07-09
params_lt3['MW_RND_amp_I']	   = params_lt3['MW_pi2_amp']#TODO Calibrate  -0.487 
params_lt3['MW_RND_duration_I']= params_lt3['MW_pi2_duration'] #TODO Calibrate 50e-9
params_lt3['MW_RND_amp_Q']	   = params_lt3['MW_pi_amp']# 0.487 
params_lt3['MW_RND_duration_Q']= params_lt3['MW_pi_duration'] #50e-9

params_lt3['echo_offset'] = 0e-9
params_lt3['free_precession_time_1st_revival'] = 73.2e-6
params_lt3['free_precession_offset'] = 0.
#adwin wait time after PLU signal:
params_lt3['wait_before_RO'] = joint_params.joint_params['wait_for_1st_revival']*params_lt3['free_precession_time_1st_revival']*1e6+10


# LDE Sequence in the AWG
params_lt3['eom_pulse_amplitude']        = 2.0 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
params_lt3['eom_pulse_duration']         = 2e-9
params_lt3['eom_off_amplitude']          = -0.055 # calibration from 2014-07-23
params_lt3['eom_off_duration']           = 150e-9
params_lt3['eom_overshoot_duration1']    = 20e-9
params_lt3['eom_overshoot1']             = -0.03 # calibration from 19-03-2014# 
params_lt3['eom_overshoot_duration2']    = 10e-9
params_lt3['eom_overshoot2']             = 0
params_lt3['aom_risetime']				 = 15e-9
params_lt3['aom_amplitude']				 = 0.52 # 2014

params_lt3['MW_during_LDE']           = 0 #NOTE:gets set automatically

params_lt3['AWG_SP_power']            = params_lt3['A_SP_amplitude']
params_lt3['AWG_RO_power']            = 10e-9#params_lt3['Ex_RO_amplitude']
params_lt3['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT
params_lt3['LDE_SP_duration']         = 5e-6
params_lt3['LDE_yellow_duration']     = -1 # if this is < 0, no yellow pulse is added to the sequence

params_lt3['MW_opt_puls1_separation'] = 200e-9 #distance between the end of the MW and the start of opt puls1
params_lt3['MW_1_separation'] 	= joint_params.joint_params['opt_pulse_separation']
params_lt3['MW_RND_wait'] 		= 160e-9 #wait start RND MW after end of RND halt pulse
params_lt3['RND_duration']	 	= 250e-9
params_lt3['RO_wait'] 			= 75e-9 #wait start RO after end of RND MW pulse
params_lt3['sync_during_LDE'] 	= 1#sync is only for lt4
params_lt3['plu_during_LDE'] 	= 0 
params_lt3['opt_pulse_start']	= 5.5e-6 + 2.423e-6 #SP duration + 500 ns - some diff in optical pathlength --> 1.5e-6 = dt(f,BC)-dt(f,AC)

params_lt3['MAX_DATA_LEN'] =       joint_params.joint_params['MAX_DATA_LEN']
params_lt3['BINSIZE'] =            joint_params.joint_params['BINSIZE'] #2**BINSIZE*BASERESOLUTION 
params_lt3['MIN_SYNC_BIN'] =       joint_params.joint_params['MIN_SYNC_BIN']
params_lt3['MAX_SYNC_BIN'] =       joint_params.joint_params['MAX_SYNC_BIN']
params_lt3['MIN_HIST_SYNC_BIN'] =  joint_params.joint_params['MIN_HIST_SYNC_BIN']
params_lt3['MAX_HIST_SYNC_BIN'] =  joint_params.joint_params['MAX_HIST_SYNC_BIN']
params_lt3['TTTR_read_count'] =    joint_params.joint_params['TTTR_read_count']
params_lt3['measurement_abort_check_interval']    = joint_params.joint_params['measurement_abort_check_interval']

params_lt3['measurement_time'] =   24*60*60 #sec = 24 H


