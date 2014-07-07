"""
This file contains all the lt1 measurement parameters.
"""
import params
params_lt1 = {}


### Hardware stuff
# params['HH_binsize_T3'] = 8
#CR:
params_lt1['counter_channel'] = 1
params_lt1['repump_duration'] = 500 # 10 for green, 500 for yellow
params_lt1['CR_duration'] = 100
params_lt1['cr_wait_after_pulse_duration'] = 1
params_lt1['CR_preselect'] = 2500
params_lt1['CR_probe'] = 20
params_lt1['CR_repump'] = 1000 # 1 for yellow, 1000 for green
params_lt1['cr_mod'] = True
params_lt1['cr_mod_control_offset']     =  0.0
params_lt1['cr_mod_control_amp']        =  0.05 #V
params_lt1['repump_mod_control_offset'] =  7.0
params_lt1['repump_mod_control_amp']    =  .5 #V

#CR check modulation pars:
#to be implemented

#bell adwin:
params_lt1['AWG_done_DI_channel'] = 20
params_lt1['AWG_success_DI_channel'] = 21
params_lt1['SP_duration'] = 50
params_lt1['wait_after_pulse_duration'] = 1
params_lt1['remote_CR_DO_channel'] = 9
params_lt1['SSRO_duration'] = 50
params_lt1['wait_for_AWG_done'] = 1
params_lt1['sequence_wait_time'] = 10 #NOTE gets set in Bell.autoconfig

#adwin powers
params_lt1['Ex_CR_amplitude'] = 5e-9#10e-9#6e-9             
params_lt1['A_CR_amplitude'] =5e-9#10e-9#16e-9              
params_lt1['Ex_SP_amplitude'] = 0e-9              
params_lt1['A_SP_amplitude'] = 5e-9             
params_lt1['Ex_RO_amplitude'] = 6e-9
params_lt1['A_RO_amplitude'] = 0
params_lt1['repump_amplitude'] = 30e-9 

####################
### pulses and MW stuff LT1
#####################
## general
f_msm1_cntr_lt1 = 2.828827e9 
mw0_lt1 = f_msm1_cntr_lt1
#f0_lt1 = f_msm1_cntr_lt1 - mw0_lt1
#params_lt1['ms-1_cntr_frq'] = f_msm1_cntr_lt1
params_lt1['mw_frq'] = mw0_lt1
params_lt1['mw_power'] = 20
params_lt1['MW_pulse_mod_risetime'] = 10e-9

params_lt1['CORPSE_rabi_frequency'] = 8.15e6
params_lt1['CORPSE_pi_amp'] = 0.382
params_lt1['CORPSE_pi2_amp'] = 0.419864
params_lt1['CORPSE_RND_amp'] = 0.5

params_lt1['RND_angle_0'] = 45
params_lt1['RND_angle_1'] = 315

params_lt1['RND_duration'] = 300e-9

params_lt1['RND_during_LDE'] = 1 

params_lt1['do_echo'] = 1
params_lt1['do_final_MW_rotation'] = 1

params_lt1['wait_for_PLU'] = 0
params_lt1['free_precession_time_1st_revival'] = 73.9e-6

#params_lt1['CORPSE_mod_frq'] = f0_lt1

# LDE Sequence in the AWG
# calibration from 2014-05-30


params_lt1['eom_pulse_duration']        = 2e-9
params_lt1['eom_pulse_amplitude']		= 1.9
params_lt1['eom_off_duration']          = 150e-9
params_lt1['eom_off_amplitude']         = -.255
params_lt1['eom_overshoot_duration1']   = 10e-9
params_lt1['eom_overshoot1']            = -0.05
params_lt1['eom_overshoot_duration2']   = 4e-9
params_lt1['eom_overshoot2']            = -0.00
params_lt1['aom_risetime']              = 38e-9
params_lt1['eom_aom_on']                = True
params_lt1['aom_amplitude']             = 1.0

params_lt1['MW_during_LDE']           = 0 #NOTE:gets set automatically

params_lt1['AWG_SP_power']            = params_lt1['A_SP_amplitude']
params_lt1['AWG_RO_power']            = params_lt1['Ex_RO_amplitude']
params_lt1['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT2
params_lt1['LDE_SP_duration']         = 5e-6
params_lt1['LDE_yellow_duration']     = -1. # if this is < 0, no yellow pulse is added to the sequence

params_lt1['MW_opt_puls1_separation'] = 100e-9 #distance between the end of the MW and the start of opt puls1
params_lt1['MW_1_separation'] = params.joint_params['opt_pulse_separation']
params_lt1['MW_RND_wait'] = 50e-9 #wait start RND MW after end of RND halt pulse
params_lt1['echo_offset'] = 0.

params_lt1['RO_wait'] = 50e-9 #wait start RO after end of RND MW pulse
params_lt1['sync_during_LDE'] = 1#sync is only for lt3
params_lt1['plu_during_LDE'] = 0 
params_lt1['opt_pulse_start'] = params.params_lt3['opt_pulse_start'] - 143e-9 #1.5e-6 = dt(f,BC)-dt(f,AC)

params_lt1['MAX_DATA_LEN'] =       params.joint_params['MAX_DATA_LEN']
params_lt1['BINSIZE'] =            params.joint_params['BINSIZE'] #2**BINSIZE*BASERESOLUTION 
params_lt1['MIN_SYNC_BIN'] =       params.joint_params['MIN_SYNC_BIN']
params_lt1['MAX_SYNC_BIN'] =       params.joint_params['MAX_SYNC_BIN']
params_lt1['TTTR_read_count'] =    params.joint_params['TTTR_read_count']

params_lt1['measurement_abort_check_interval']    = params.joint_params['measurement_abort_check_interval']

params_lt1['measurement_time'] =   24*60*60 #sec = 24 H
