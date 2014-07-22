"""
This file contains all the lt1 measurement parameters.
"""
import qt
import params
params_lt1 = {}


### Hardware stuff
# params['HH_binsize_T3'] = 8
#CR:
params_lt1['counter_channel'] 	= qt.exp_params['protocols']['AdwinSSRO']['counter_channel']
params_lt1['repump_duration'] 	= qt.exp_params['protocols']['AdwinSSRO']['repump_duration'] #500 # 10 for green, 500 for yellow
params_lt1['repump_amplitude'] 	= qt.exp_params['protocols']['AdwinSSRO']['repump_amplitude']# 30e-9 
params_lt1['cr_wait_after_pulse_duration'] = qt.exp_params['protocols']['AdwinSSRO']['cr_wait_after_pulse_duration']
params_lt1['CR_duration'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_duration']
params_lt1['CR_preselect'] 		= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_preselect']
params_lt1['CR_probe'] 			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_probe']
params_lt1['CR_repump']			= qt.exp_params['protocols'][name]['AdwinSSRO']['CR_repump']

params_lt1['cr_mod'] = True
params_lt1['cr_mod_control_offset']     =  0.0
params_lt1['cr_mod_control_amp']        =  0.05 #V
params_lt1['repump_mod_control_offset'] =  7.2
params_lt1['repump_mod_control_amp']    =  .5 #V

#bell adwin:
params_lt1['AWG_done_DI_channel'] = 20
params_lt1['AWG_success_DI_channel'] = 21
params_lt1['SP_duration'] = 10
params_lt1['wait_after_pulse_duration'] = 1
params_lt1['remote_CR_DO_channel'] = 9
params_lt1['SSRO_duration'] = 30
params_lt1['wait_for_AWG_done'] = 1
params_lt1['sequence_wait_time'] = 10 #NOTE gets set in Bell.autoconfig

#adwin powers
params_lt1['Ex_CR_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_CR_amplitude'] 
params_lt1['A_CR_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_CR_amplitude']          
params_lt1['A_SP_amplitude']  = qt.exp_params['protocols'][name]['AdwinSSRO']['A_SP_amplitude']	        
params_lt1['Ex_RO_amplitude'] = qt.exp_params['protocols'][name]['AdwinSSRO']['Ex_RO_amplitude']
params_lt1['A_RO_amplitude']  = 0
params_lt1['Ex_SP_amplitude'] = 0e-9  


####################
### pulses and MW stuff LT1
#####################
## general
params_lt1['mw_frq'] 				= qt.exp_params['samples'][sample_name]['ms-1_cntr_frq']
params_lt1['mw_power'] 				= qt.exp_params['protocols']['AdwinSSRO+espin']['mw_power']
params_lt1['MW_pulse_mod_risetime'] = qt.exp_params['protocols']['AdwinSSRO+espin']['MW_pulse_mod_risetime']

params_lt1['MW_pi_amp_I']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp'] #0.895 # 2014-07-09
params_lt1['MW_pi_amp_Q']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_amp'] #0.895 # 2014-07-09
params_lt1['MW_pi_duration']   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi_length']# 180e-9 # 2014-07-09
params_lt1['MW_pi2_amp_I']	   = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']
params_lt1['MW_pi2_amp_Q']     = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_amp']# XXXXXXXXXXXXX
params_lt1['MW_pi2_duration']  = qt.exp_params['protocols'][name]['pulses']['Hermite_pi2_length']#90e-9 # 2014-07-09
params_lt1['MW_RND_amp_I']	   = params_lt1['MW_pi2_amp_I']#TODO Calibrate  -0.487 
params_lt1['MW_RND_duration_I']= params_lt1['MW_pi2_duration'] #TODO Calibrate 50e-9
params_lt1['MW_RND_amp_Q']	   = -params_lt1['MW_pi2_amp_Q']# 0.487 
params_lt1['MW_RND_duration_Q']= params_lt1['MW_pi2_duration'] #50e-9

params_lt1['echo_offset'] = 0e-9
params_lt1['free_precession_time_1st_revival'] = 73.2e-6
params_lt1['free_precession_offset'] = 0.
#adwin wait time after PLU signal:
params_lt1['wait_before_RO'] = params.joint_params['wait_for_1st_revival']*params_lt1['free_precession_time_1st_revival']*1e6+10


# LDE Sequence in the AWG
params_lt1['eom_pulse_amplitude']		= 1.9
params_lt1['eom_pulse_duration']        = 2e-9
params_lt1['eom_off_duration']          = 150e-9
params_lt1['eom_off_amplitude']         = -.255
params_lt1['eom_overshoot_duration1']   = 10e-9
params_lt1['eom_overshoot1']            = -0.05
params_lt1['eom_overshoot_duration2']   = 4e-9
params_lt1['eom_overshoot2']            = -0.00
params_lt1['aom_risetime']              = 38e-9
params_lt1['aom_amplitude']             = 1.0

params_lt1['MW_during_LDE']           = 0 #NOTE:gets set automatically

params_lt1['AWG_SP_power']            = params_lt1['A_SP_amplitude']
params_lt1['AWG_RO_power']            = params_lt1['Ex_RO_amplitude']
params_lt1['AWG_yellow_power']        = 30e-9 #yellow power during SP in LDE on LT
params_lt1['LDE_SP_duration']         = 5e-6
params_lt1['LDE_yellow_duration']     = 3e-6 # if this is < 0, no yellow pulse is added to the sequence

params_lt1['MW_opt_puls1_separation'] = 100e-9 #distance between the end of the MW and the start of opt puls1
params_lt1['MW_1_separation'] 	= params.joint_params['opt_pulse_separation']
params_lt1['MW_RND_wait'] 		= 160e-9 #wait start RND MW after end of RND halt pulse
params_lt1['RND_duration']	 	= 250e-9
params_lt1['RO_wait'] 			= 75e-9 #wait start RO after end of RND MW pulse
params_lt1['sync_during_LDE'] 	= 1#sync is only for lt3
params_lt1['plu_during_LDE'] 	= 0 
params_lt1['opt_pulse_start']	= params.params_lt3['opt_pulse_start'] - 143e-9 #1.5e-6 = dt(f,BC)-dt(f,AC)

params_lt1['MAX_DATA_LEN'] =       params.joint_params['MAX_DATA_LEN']
params_lt1['BINSIZE'] =            params.joint_params['BINSIZE'] #2**BINSIZE*BASERESOLUTION 
params_lt1['MIN_SYNC_BIN'] =       params.joint_params['MIN_SYNC_BIN']
params_lt1['MAX_SYNC_BIN'] =       params.joint_params['MAX_SYNC_BIN']
params_lt1['TTTR_read_count'] =    params.joint_params['TTTR_read_count']
params_lt1['measurement_abort_check_interval']    = params.joint_params['measurement_abort_check_interval']

params_lt1['measurement_time'] =   24*60*60 #sec = 24 H
