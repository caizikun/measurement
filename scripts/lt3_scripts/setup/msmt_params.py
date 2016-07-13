import numpy as np

cfg={}
sample_name = 'Pippin'
sil_name = 'SIL2'
name=sample_name+'_'+sil_name
cfg['samples'] = {'current':sample_name}
cfg['protocols'] = {'current':name}


cfg['protocols'][name] = {}

print 'updating msmt params lt3 for {}'.format(cfg['samples']['current'])

##############################################################################
##############################################################################
### Protocols
##############################################################################
##############################################################################

f_msm1_cntr = 1.705722e9 #Electron spin ms=-1 frquency 
f_msp1_cntr = 4.049479e9 #Electron spin ms=+1 frequency

mw_mod_frequency = 0
mw_power = 20
mw2_mod_frequency = 0
mw2_power = 20

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.198e6        #calibrated 2014-03-20/181319
C_split  = 0.847e6 

pulse_shape = 'Hermite'
#pulse_shape = 'Square'
electron_transition = '+1'
multiple_source = False

mw1_source = ''
if electron_transition == '+1':
	electron_transition_string = '_p1'
	mw_frq     = f_msp1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msp1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 90e-9 #even
	hermite_pi_amp = 0.718#0.681#0.667 # 06-02
	hermite_pi2_length = 46e-9 # even
	hermite_pi2_amp = 0.482 # 06-02 

	square_pi_length = 18e-9 # even
	square_pi_amp = 0.799 # 02-19
	square_pi2_length = 16e-9 # even
	square_pi2_amp = 0.88 # 02-19

else:
	electron_transition_string = '_m1'
	mw_frq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msm1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 100e-9 
	hermite_pi_amp = 0.368
	hermite_pi2_length = 90e-9
	hermite_pi2_amp = 0.189

	square_pi_length = 30e-9
	square_pi_amp = 0.79 
	square_pi2_length = 16e-9
	square_pi2_amp = 0.88 

# Second MW source, currently only up to 3.2GHz, i.e. only -1 transition
mw2_frq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
mw2_frq_MBI = f_msm1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

mw2_hermite_pi_length = 180e-9#100e-9 #100e-9
mw2_hermite_pi_amp = 0.248 # AR 03/29
mw2_hermite_pi2_length  = 50e-9#36e-9 #36e-9
mw2_hermite_pi2_amp  = 0.343
mw2_square_pi_length = 16e-9
mw2_square_pi_amp = 0.477
mw2_square_pi2_length  = 10e-9
mw2_square_pi2_amp  = 0.42

### General settings for AdwinSSRO
cfg['protocols']['AdwinSSRO']={
		'AWG_done_DI_channel':          17,
		'AWG_start_DO_channel':         9,
		'AWG_event_jump_DO_channel'	:   10,
		'counter_channel':              1,
		#'counter_ch_input_pattern':	0,
		'cycle_duration':               300,
		'green_off_amplitude':          0.0,
		'green_repump_amplitude':       15e-6,# 15e-6
		'green_repump_duration':        30, # maximum is 1000 for CR_mod
		'send_AWG_start':               0,
		'sequence_wait_time':           1,
		'wait_after_RO_pulse_duration': 3,
		'wait_after_pulse_duration':    3,
		'cr_wait_after_pulse_duration': 3,
		'wait_for_AWG_done':            0,
		'Ex_off_voltage':               0.,
		'A_off_voltage':                -0.0,
		'yellow_repump_amplitude':      28e-9,#20e-9, #50e-9
		'yellow_repump_duration':       300, # maximum is 1000 for CR_mod
		'yellow_CR_repump':             1, 
		'green_CR_repump':              1000,
		'CR_probe_max_time':            1000000,
		'SSRO_stop_after_first_photon':	1,
		}

cfg['protocols']['AdwinSSRO']['cr_mod'] = True
cfg['protocols']['cr_mod']={
	'cr_mod_control_dac'		:	'gate_mod',
	'cr_mod_control_offset'     :   0.0,
	'cr_mod_control_amp'        :   0.07, #V
	'cr_mod_control_avg_pts'	:   500000.,
	'repump_mod_control_offset' :   5.4, #note, gets set automatically
	'repump_mod_control_amp'    :   .5, #V
	'repump_mod_control_dac'	:   'yellow_aom_frq',
	}

yellow = True
cfg['protocols']['AdwinSSRO']['yellow'] = yellow
if yellow:
    cfg['protocols']['AdwinSSRO']['repump_duration']  =  cfg['protocols']['AdwinSSRO']['yellow_repump_duration']
    cfg['protocols']['AdwinSSRO']['repump_amplitude'] =  cfg['protocols']['AdwinSSRO']['yellow_repump_amplitude']
    cfg['protocols']['AdwinSSRO']['CR_repump']        =  cfg['protocols']['AdwinSSRO']['yellow_CR_repump']
else:
    cfg['protocols']['AdwinSSRO']['repump_duration']  =  cfg['protocols']['AdwinSSRO']['green_repump_duration']
    cfg['protocols']['AdwinSSRO']['repump_amplitude'] =  cfg['protocols']['AdwinSSRO']['green_repump_amplitude']
    cfg['protocols']['AdwinSSRO']['CR_repump']        =  cfg['protocols']['AdwinSSRO']['green_CR_repump']



############################################
### General settings for AdwinSSRO+espin ###
############################################

# mw_frq = 2.78e9
cfg['protocols']['AdwinSSRO+espin'] = {
		'mw_frq':                                  mw_frq, 
		'mw_power':                                mw_power,
		'MW_pulse_mod_risetime':                   8e-9, #20   XXX
		'MW_pulse_mod_frequency' : 				   0e6,
		'mw2_frq':                                 mw2_frq, 
		'mw2_power':                               mw2_power,
		'mw2_pulse_mod_risetime':                  55e-9,
		'mw2_pulse_mod_frequency' : 			   0e6,
		'send_AWG_start':                          1
	}


##########################################
### General settings for AdwinSSRO+MBI ###
##########################################

cfg['protocols']['AdwinSSRO+MBI'] = {

		'send_AWG_start'                        :   1,
		'AWG_wait_duration_before_MBI_MW_pulse'	:   1e-6,
		'AWG_wait_for_adwin_MBI_duration'		:   15e-6,
		'AWG_MBI_MW_pulse_duration'				:   2e-6,
		'AWG_MBI_MW_pulse_amp'      			:   0.00,#0.0165,
		'AWG_MBI_MW_pulse_mod_frq'  			:   0,
		'AWG_MBI_MW_pulse_ssbmod_frq'			:  	0,
		'AWG_wait_duration_before_shelving_pulse':  100e-9,
		'nr_of_ROsequences'						:   1,  #setting this on anything except on 1 crahses the adwin?
		'MW_pulse_mod_risetime'					:   8e-9,  #20
		'mw2_pulse_mod_risetime'				:   55e-9,
		'AWG_to_adwin_ttl_trigger_duration'		:   2e-6,
		'repump_after_MBI_duration'				:   150, 
		'repump_after_MBI_amp'					:   15e-9,
		'max_MBI_attempts'                      :   1,
		'N_randomize_duration'                  :   50,
		'Ex_N_randomize_amplitude'				:	3e-9,
		'A_N_randomize_amplitude'               :   10e-9,
		'repump_N_randomize_amplitude'          :   0e-9,
		#Shutter
		'use_shutter':                          0, 
		'Shutter_channel':                      4, 
		'Shutter_rise_time':                    2500,    
		'Shutter_fall_time':                    2500,
		'Shutter_safety_time':                  50000
		}

cfg['protocols']['AdwinSSRO+PQ'] = {
		'MAX_DATA_LEN':                             int(100e6),
		'BINSIZE':                                  0, #2**BINSIZE*BASERESOLUTION
		'MIN_SYNC_BIN':                             0,
		'MAX_SYNC_BIN':                             1000,
		'TTTR_read_count':							1000,#1000,#1000, #s
		'TTTR_RepetitiveReadouts':					10,
		'measurement_time':                         1200,#sec
		'measurement_abort_check_interval':			1,#sec
		'MIN_HIST_SYNC_BIN':						0,
		'MAX_HIST_SYNC_BIN':						10000,
		'count_marker_channel':						1,
		}


###############################
### NV and field parameters ###
###############################



cfg['samples'][sample_name] = {
	'electron_transition' : electron_transition_string,
	'mw_mod_freq'   :       mw_mod_frequency,
	'mw_frq'        :       mw_frq, # this is automatically changed to mw_freq if hermites are selected.
	'mw_power'      :       mw_power,
	'mw2_mod_freq'   :      mw2_mod_frequency,
	'mw2_frq'        :      mw2_frq, # this is automatically changed to mw_freq if hermites are selected.
	'mw2_power'      :      mw2_power,
	'ms-1_cntr_frq' :       f_msm1_cntr,
	'ms+1_cntr_frq' :       f_msp1_cntr,
	'N_0-1_splitting_ms-1': N_frq,
	'N_HF_frq'      :       N_HF_frq,
	'C_split'		:		C_split,
	'multiple_source' :		False,


###############
### Carbons ###
###############
	### Please uncomment the SIL you are working on
	'Carbon_LDE_phase_correction_list' : np.array([0.0]+[0.0]+[0.0]*2+[0.0]*7),
	'Carbon_LDE_init_phase_correction_list' : np.array([0.0]+[0.0]+[0.0]*2+[180.]+[0.0]*7),
    'phase_per_sequence_repetition'    : 344.6+1.2-17.55+0.214,#329.06,#4.162, #adwin needs positive values
    'phase_per_compensation_repetition': 14.067, # adwin needs positive values
    'total_phase_offset_after_sequence': 67,#222.69, #68.386,#42.328,

	# #########################
	# #####     SIL1      #####
	# #########################
	# ##########
	# ### C2 ###
	# ###########
	# 'C2_freq_m1'        : (446138.+462154.03)/2.,
	# 'C2_freq_0' 		: 445890.53,
	# 'C2_freq_1_m1' 		: 462167.38, #1kHz uncertainty though

	# 'C2_Ren_tau_m1'    :   [7.12e-6],
	# 'C2_Ren_N_m1'      :   [24],
	# 'C2_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [63.23] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	# ###########
	# ### C3 ####
	# ###########
	# # #### C3 ### C8 in up 
	# 'C3_freq_m1'      : (446138. + 462154.03)/2.,
	# 'C3_freq_0' 		: 445890.53,
	# 'C3_freq_1_m1' 	: 462167.38,

	# ## C3 ### C8 in down
	# # 'C3_freq_m1'      	: (447432 + 544247)/2.,
	# # 'C3_freq_0' 		: 447432,
	# # 'C3_freq_1_m1' 		: 544247,

	# #tau, N, phase correction
	# 'C3_Ren_tau_m1'    :   [13.734e-6],#[4.535e-6],
	# 'C3_Ren_N_m1'      :   [38],#[48],
	# 'C3_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [44.33] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	#########################
	#####     SIL2      #####
	#########################
	################
	#### C1 ~ -35 ###
	################
	'C1_freq_m1'        : (447929.95 + 483714)/2., 
	'C1_freq_0' 		: 447834.54,
	'C1_freq_1_m1' 		: 483714,

	'C1_Ren_tau_m1'    :   [4.822e-6],
	'C1_Ren_N_m1'      :   [12],
	'C1_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-55.46] + [44.33] + [0.0] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C1_freq_p1'        : 434615.6,#434257.72, 
	'C1_freq_0' 		: 447834.54,
	'C1_freq_1_p1' 		: 425436.75,

	'C1_Ren_tau_p1'    :   [10.886e-6],#10.886e-6], #8.608e-6
	'C1_Ren_N_p1'      :   [12], #12
	'C1_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [47.18] + [44.33] + [0.0] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C1_unc_tau_p1'    :   [9.132e-6],
	'C1_unc_N_p1'      :   [12],
	'C1_unc_phase_offset_p1' : 82.6,
	'C1_unc_extra_phase_correction_list_p1': np.array([0.0] + [104.32] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

	###############
	#### C2 ~ 15 ###
	###############
	'C2_freq_m1'        : (447774.53+432700)/2.,
	'C2_freq_0' 		: 447725.47,
	'C2_freq_1_m1' 		: 432700, 

	'C2_Ren_tau_m1'    :   [10.786e-6],
	'C2_Ren_N_m1'      :   [24],
	'C2_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [7.12] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C2_freq_p1'        : 456025,
	'C2_freq_0' 		: 447725.47,
	'C2_freq_1_p1' 		: 464353.86,
	
	'C2_Ren_tau_p1'    :   [9.316e-6],#[10.79e-6],
	'C2_Ren_N_p1'      :   [24],#[26],
	'C2_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [5.51] + [-46.89] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	###############
	#### C3 ~ 42 ###
	###############
	'C3_freq_m1'        : (447528.84*2 - 42e3)/2.,
	'C3_freq_0' 		: 447528.84,
	'C3_freq_1_m1' 		: 447e3-42e3, 

	'C3_Ren_tau_m1'    :   [4.11e-6],
	'C3_Ren_N_m1'      :   [32],
	'C3_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [7.12] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	###############
	#### C4 ~ -80 ###
	###############
	'C4_freq_m1'        : (447953.99*2 + 42e3)/2.,
	'C4_freq_0' 		: 447953.99,
	'C4_freq_1_m1' 		: 447e3+82e3, 

	'C4_Ren_tau_m1'    :   [4.51e-6],
	'C4_Ren_N_m1'      :   [66],
	'C4_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [7.12] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	###############
	#### C5 ~-114 ###
	###############
	'C5_freq_m1'        : (446138*2 + 114e3)/2.,
	'C5_freq_0' 		: 447479.34,
	'C5_freq_1_m1' 		: 447e3+114e3, 

	'C5_Ren_tau_m1'    :   [5.445e-6],
	'C5_Ren_N_m1'      :   [38],
	'C5_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [7.12] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	###############
	#### C6 ~ 14 ###
	###############
	'C6_freq_m1'        : (447765.59 +433431)/2.,
	'C6_freq_0' 		: 447765.59,
	'C6_freq_1_m1' 		: 433431, 

	'C6_Ren_tau_m1'    :   [21.895e-6],
	'C6_Ren_N_m1'      :   [26],
	'C6_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [5.51] + [7.12] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	#########################
	#####      SIL3    ######
	#########################

	# ###########
	# #### C1 ###
	# ###########
	# 'C1_freq_m1'        : (447024.+1296429.)/2., # random
	# 'C1_freq_0' 		: 447024.,
	# 'C1_freq_1_m1' 		: 1296429.,

	# 'C1_Ren_tau_m1'    :   [10.786e-6],
	# 'C1_Ren_N_m1'      :   [26],
	# 'C1_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [13.79] + [44.33] + [0.0] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),


}

cfg['protocols'][name]['AdwinSSRO'] = {
		'A_CR_amplitude':				 6e-9,#2.5e-9,
		'A_RO_amplitude' :				 0,
		'A_SP_amplitude':				 12e-9,
		'CR_duration' :				 	 50, 
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.8e-9,#0.7e-9,#1.5e-9,
		'Ex_RO_amplitude':				 4e-9,#5e-9, #5e-9
		'Ex_SP_amplitude':				 0e-9,  #2015-05-25
		'Ex_SP_calib_amplitude':		 12e-9, ## used for ssro calib
		'SP_duration':					 100, ## hardcoded in the adwin to be 500 max.
		'SP_duration_ms0':				 400, ## used for ssro calib
		'SP_duration_ms1':				 1000, ## used for ssro calib
		'SP_filter_duration':			 0,
		'SSRO_duration':				 50,
		'SSRO_repetitions':				 5000
		}

cfg['protocols'][name]['AdwinSSRO+MBI']={
	#Spin pump before MBI
	'Ex_SP_amplitude'           :           0e-9,   #15e-9,#15e-9,    #18e-9
	'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet?
	'SP_E_duration'             :           50,     #Duration for both Ex and A spin pumping
	 
	 #MBI readout power and duration
	'Ex_MBI_amplitude'          :           0.0e-9,
	'MBI_duration'              :           10,

	#Repump after succesfull MBI
	'repump_after_MBI_duration' :           [200],
	'repump_after_MBI_A_amplitude':         [12e-9],  #18e-9
	'repump_after_MBI_E_amplitude':         [0e-9],

	#MBI parameters
	'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
	'MBI_threshold'             :           0, 
	'AWG_wait_for_adwin_MBI_duration':      10e-6+65e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

	'repump_after_E_RO_duration':           15,
	'repump_after_E_RO_amplitude':          15e-9,

	#Shutter
	'use_shutter':                          0, # we don't have a shutter in the setup right now
}

f_mod_0     = cfg['samples'][sample_name]['mw_mod_freq']

cfg['protocols'][name]['pulses'] = {
		
		'X_phase'                   :   90,
		'Y_phase'                   :   0,

		'C13_X_phase' :0,
		'C13_Y_phase' :270,

		'pulse_shape': pulse_shape,
		'MW_modulation_frequency'   :   f_mod_0,
		'mw2_modulation_frequency'   :  0,
		'MW_switch_risetime'	:	10e-9,
		'MW_switch_channel'		:	'None', ### if you want to activate the switch, put to MW_switch
    	'CORPSE_rabi_frequency' :   9e6,
    	'CORPSE_amp' : 				0.201 ,
    	'CORPSE_pi2_amp':			0.543,
    	'CORPSE_pulse_delay': 		0e-9,
    	'CORPSE_pi_amp': 			0.517,
    	'Hermite_pi_length': 		hermite_pi_length,#150e-9, ## bell duration
        'Hermite_pi_amp': 			hermite_pi_amp,#0.938,#0.901, # 2015-12-17 ## bell duration
        'Hermite_pi2_length':		hermite_pi2_length,
        'Hermite_pi2_amp': 			hermite_pi2_amp, 
        'Hermite_Npi4_length':		45e-9,
        'Hermite_Npi4_amp':			0.373683, # 2014-08-21

        'Square_pi_length' :		square_pi_length,
      	'Square_pi_amp' :			square_pi_amp, 
      	'Square_pi2_length' :		square_pi2_length, # XXXXXXX not calibrated
    	'Square_pi2_amp'  :			square_pi2_amp, # XXXXXXX not calibratedrepump
    	'IQ_Square_pi_amp' :		0.068, 
      	'IQ_Square_pi2_amp'  :		0.6967,
      	'extra_wait_final_pi2' :	-30e-9,
    	'DESR_pulse_duration' :		4e-6,
    	'DESR_pulse_amplitude' :	0.0018,#0.194,

    	# Second mw source
    	'mw2_Hermite_pi_length': 	mw2_hermite_pi_length,
        'mw2_Hermite_pi_amp': 		mw2_hermite_pi_amp,
        'mw2_Hermite_pi2_length':	mw2_hermite_pi2_length,
        'mw2_Hermite_pi2_amp': 		mw2_hermite_pi2_amp, 
        'mw2_Square_pi_length' :	mw2_square_pi_length,
      	'mw2_Square_pi_amp' :		mw2_square_pi_amp, 
      	'mw2_Square_pi2_length' :   mw2_square_pi2_length,
    	'mw2_Square_pi2_amp' :		mw2_square_pi_amp,

    	'eom_pulse_duration':				2e-9,
        'eom_off_duration':					50e-9, # 50e-9
        'eom_off_amplitude':				-0.02, #-0.02
        'eom_pulse_amplitude':				2, # (for long pulses it is 1.45, dor short:2.0) calibration from 19-03-2014
        'eom_overshoot_duration1':			18e-9,
        'eom_overshoot1':					-0.03, # calibration from 19-03-2014# 
        'eom_overshoot_duration2':			10e-9,
        'eom_overshoot2':					0,
        'aom_risetime':						12e-9,#40e-9
        'aom_amplitude':					0.4,#0.2
}


cfg['protocols'][name]['AdwinSSRO+C13']={
	### Comment NK 2016-01-13 these parameters have been directly ported to LT3 from LT2 and still need testing!
#'wait_between_runs':                    0, ### bool operator, set to one to wait for the 'Shutter_safety_time'

		#C13-MBI  
		'C13_MBI_threshold_list':               [1],
		'C13_MBI_RO_duration':                  25,  
		'E_C13_MBI_RO_amplitude':               0.2e-9, 
		'SP_duration_after_C13':                30, #use long repumping in case of swap init
		'A_SP_amplitude_after_C13_MBI':         12e-9,
		'E_SP_amplitude_after_C13_MBI':         0e-9,
		'C13_MBI_RO_state':                     0, # 0 sets the C13 MBI success condition to ms=0 (> 0 counts), if 1 to ms = +/-1 (no counts)
		                
		#C13-MBE  
		'MBE_threshold':                        1,
		'MBE_RO_duration':                      40, # was 40 20150329
		'E_MBE_RO_amplitude':                   0.05e-9, 
		'SP_duration_after_MBE':                30,
		'A_SP_amplitude_after_MBE':             12e-9,
		'E_SP_amplitude_after_MBE':             0e-9 ,

		#C13-parity msmnts
		'Parity_threshold':                     1,
		'Parity_RO_duration':                   108,
		'E_Parity_RO_amplitude':                0.05e-9,

		#Shutter
		'use_shutter':                          0, 
		'Shutter_channel':                      4, 
		'Shutter_rise_time':                    2500,    
		'Shutter_fall_time':                    2500,
		'Shutter_safety_time':                  200000, #Sets the time after each msmts, the ADwin waits for next msmt to protect shutter (max freq is 20Hz)

		# phase correction
		'min_phase_correct'   :     2,      # minimum phase difference that is corrected for by phase gates
		'min_dec_tau'         :     30e-9 + cfg['protocols'][name]['pulses']['Hermite_pi_length'],#2.05e-6,#16e-9 + cfg['protocols'][name]['pulses']['Hermite_pi_length'], 
		'max_dec_tau'         :     0.255e-6,#0.35e-6,
		'dec_pulse_multiple'  :     4,      #4.

		# Memory entanglement sequence parameters
		'optical_pi_pulse_sep' :         1000e-9,
		'do_optical_pi' :                False,
		'initial_MW_pulse':           'pi2' #'pi', 'no_pulse'
}

cfg['protocols'][name]['AdwinSSRO-integrated'] = {
	'SSRO_duration' : 10,#13, #18
	'Ex_SP_amplitude': 0 }

# CORPSE_frq = 9e6



cfg['protocols'][name]['cr_linescan'] = {
		'A_CR_amplitude':				 2e-9,
		'CR_duration' :				 	 100,
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.5e-9,
		}