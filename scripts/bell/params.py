"""
This file contains all the joint and lt3 measurement parameters.
"""

joint_params = {}

### default process settings
joint_params['RO_during_LDE'] = 1

joint_params['opt_pi_pulses'] = 2
joint_params['LDE_attempts_before_CR'] = 250 # 1000 for tpqi seems ok
joint_params['initial_delay']           = 10e-9
joint_params['opt_pulse_separation']    = 600e-9

joint_params['LDE_element_length']              = 16e-6 # 9e-6 for TPQI with 5 pulses
joint_params['LDE_RO_duration'] = 3e-6

joint_params['MAX_DATA_LEN'] =       int(100e6)
joint_params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
joint_params['MIN_SYNC_BIN'] =       0
joint_params['MAX_SYNC_BIN'] =       1000
joint_params['measurement_abort_check_interval']    = 1. #sec

bs_params = {}
bs_params['MAX_DATA_LEN']        =   joint_params['MAX_DATA_LEN']
bs_params['BINSIZE']             =   1  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
bs_params['MIN_SYNC_BIN']        =   0 
bs_params['MAX_SYNC_BIN']        =   1000 
bs_params['measurement_time']    =   24*60*60 #sec = 24H
bs_params['measurement_abort_check_interval']    = joint_params['measurement_abort_check_interval'] #sec

params_lt3 = {}
### Hardware stuff
# params['HH_binsize_T3'] = 8
#CR:
params_lt3['counter_channel'] = 1
params_lt3['repump_duration'] = 10 # 10 for green, 500 for yellow
params_lt3['CR_duration'] = 100
params_lt3['cr_wait_after_pulse_duration'] = 1
params_lt3['CR_preselect'] = 2500
params_lt3['CR_probe'] = 20
params_lt3['CR_repump'] = 1000 # 1 for yellow, 1000 for green

#CR check modulation pars:
#to be implemented

#bell adwin:
params_lt3['AWG_start_DO_channel'] = 16
params_lt3['AWG_done_DI_channel'] = 8
params_lt3['SP_duration'] = 50
params_lt3['wait_after_pulse_duration'] = 1
params_lt3['remote_CR_DI_channel'] = 9
params_lt3['PLU_DI_channel'] = 10
params_lt3['do_sequences'] = 1
params_lt3['SSRO_duration'] = 50
params_lt3['wait_for_AWG_done'] = 0
params_lt3['sequence_wait_time'] = 10 #NOTE gets set in autoconfig

#adwin powers
params_lt3['Ex_CR_amplitude'] = 2e-9#10e-9#6e-9             
params_lt3['A_CR_amplitude'] =5e-9#10e-9#16e-9              
params_lt3['Ex_SP_amplitude'] = 0e-9              
params_lt3['A_SP_amplitude'] = 10e-9             
params_lt3['Ex_RO_amplitude'] = 5e-9
params_lt3['A_RO_amplitude'] = 0
params_lt3['repump_amplitude'] = 200e-6 

####################
### pulses and MW stuff LT3
#####################
## general
f_msm1_cntr_lt3 = 2.828827e9 
mw0_lt3 = f_msm1_cntr_lt3
#f0_lt3 = f_msm1_cntr_lt3 - mw0_lt3
#params_lt3['ms-1_cntr_frq'] = f_msm1_cntr_lt3
params_lt3['mw_frq'] = mw0_lt3
params_lt3['mw_power'] = 20
params_lt3['MW_pulse_mod_risetime'] = 10e-9

params_lt3['CORPSE_rabi_frequency'] = 8.15e6
params_lt3['CORPSE_pi_amp'] = 0.382
params_lt3['CORPSE_pi2_amp'] = 0.419864
params_lt3['CORPSE_RND_amp'] = 0.5

params_lt3['RND_angle_0'] = 45
params_lt3['RND_angle_1'] = 315

params_lt3['RND_duration'] = 100e-9

#params_lt3['CORPSE_mod_frq'] = f0_lt3

# LDE Sequence in the AWGs
params_lt3['MW_during_LDE']           = 0 #NOTE:gets set automatically

params_lt3['AWG_SP_power']            = params_lt3['A_SP_amplitude']
params_lt3['AWG_RO_power']            = params_lt3['Ex_RO_amplitude']
params_lt3['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT2
params_lt3['LDE_SP_duration']         = 5e-6
params_lt3['LDE_yellow_duration']     = -1. # if this is < 0, no yellow pulse is added to the sequence


params_lt3['MW_opt_puls1_separation'] = 100e-9 #distance between the end of the MW and the start of opt puls1
params_lt3['MW_1_separation'] = joint_params['opt_pulse_separation']
params_lt3['MW_RND_wait'] = 50e-9 #wait start RND MW after end of RND halt pulse
params_lt3['MW_12_offset'] = 0.

params_lt3['PLU_gate_duration']       = 70e-9
params_lt3['PLU_gate_3_duration']     = 40e-9
params_lt3['PLU_1_delay']             = 1e-9
params_lt3['PLU_2_delay']             = 1e-9
params_lt3['PLU_3_delay']             = 50e-9
params_lt3['PLU_4_delay']             = 150e-9

params_lt3['RO_wait'] = 50e-9 #wait start RO after end of RND MW pulse
params_lt3['AWG_wait_for_lt1_start'] = 8e-6 #= dt(f,BC)
params_lt3['sync_during_LDE'] = 1
params_lt3['opt_pulse_start'] = params_lt3['LDE_SP_duration'] +  500e-9

params_lt3['MAX_DATA_LEN'] =       joint_params['MAX_DATA_LEN']
params_lt3['BINSIZE'] =            joint_params['BINSIZE'] #2**BINSIZE*BASERESOLUTION 
params_lt3['MIN_SYNC_BIN'] =       joint_params['MIN_SYNC_BIN']
params_lt3['MAX_SYNC_BIN'] =       joint_params['MAX_SYNC_BIN']
params_lt3['measurement_abort_check_interval']    = joint_params['measurement_abort_check_interval']

params_lt3['measurement_time'] =   20*60,#sec = 20 mins

joint_params['RND_start'] = params_lt3['opt_pulse_start']+joint_params['opt_pulse_separation'] + 3.3e-6 # = dt(f,BC)-dt(AC) + margin