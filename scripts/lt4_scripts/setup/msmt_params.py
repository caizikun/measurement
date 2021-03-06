import numpy as np

cfg={}
sample_name = '111no2'
sil_name = 'SIL2'
name=sample_name+'_'+sil_name
cfg['samples'] = {'current':sample_name}
cfg['protocols'] = {'current':name}

cfg['protocols'][name] = {}

print 'updating msmt params lt4 for {}'.format(cfg['samples']['current'])

##############################################################################
##############################################################################
### Protocols
##############################################################################
##############################################################################

mw_mod_frequency = 0
mw_power = 20

f_msm1_cntr = 1.718064e9 #by JS #Electron spin ms=-1 frquency   ##Calib 2017-XX-XX
f_msp1_cntr = 4.038204e9 #by JS #4.038781e9 #4.044206e9  #Electron spin ms=+1 frequency

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.19e6        #calibrated 20140320/181319
C_split  = 0.847e6 
pulse_shape = 'Hermite'
electron_transition = '-1'


if electron_transition == '+1':
	electron_transition_string = '_p1'
	mw_frq     = f_msp1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msp1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 220e-9#100e-9 #Not calibrated
	hermite_pi_amp = 0.84

	square_pi_length = 20e-9 #Not calibrated
	square_pi_amp = 0.6 #Not calibrated

	hermite_pi2_length = 100e-9 #Not calibrated
	hermite_pi2_amp = 0.764

elif electron_transition == '-1':
	electron_transition_string = '_m1'
	mw_frq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msm1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 126e-9 # divisible by 2
	hermite_pi_amp =  0.824#0.956#0.867 #0.863

	square_pi_length = 50e-9
	square_pi_amp = 0.291

	hermite_pi2_length = 60e-9 # divisible by 2
	hermite_pi2_amp = 0.618 # 0.632


### General settings for AdwinSSRO
cfg['protocols']['AdwinSSRO']={
		'AWG_done_DI_channel':          18,
		'AWG_event_jump_DO_channel':    8,
		'AWG_start_DO_channel':         9,
		'counter_channel':              1,
		'cycle_duration':               300,
		'green_off_amplitude':          0.0,
		'green_repump_amplitude':       4.5e-6,
		'green_repump_duration':        100,#20,
		'send_AWG_start':               0,
		'sequence_wait_time':           0,
		'wait_after_RO_pulse_duration': 3,
		'wait_after_pulse_duration':    3,
		'cr_wait_after_pulse_duration': 3,
		'wait_for_AWG_done':            0,
		'Ex_off_voltage':               -0.01,
		'A_off_voltage':                -0.26,
		'yellow_repump_amplitude':      32e-9,#30e-9,#30e-9,
		'yellow_repump_duration':       300,#300,
		'yellow_CR_repump':             1,
		'green_CR_repump':              1000,
		'CR_probe_max_time':            1000000,
		'SSRO_stop_after_first_photon':	0,
		}

cfg['protocols']['AdwinSSRO']['cr_mod'] = True
cfg['protocols']['cr_mod']={
	'cr_mod_control_dac'		:   'gate_mod',
	'cr_mod_control_offset'     :   0.0,
	'cr_mod_control_amp'        :   0.1, #V
	'cr_mod_control_avg_pts'	:   200000.,
	'repump_mod_control_offset' :   5., #note gets set automatically
	'repump_mod_control_amp'    :   0.5, #V 1.
	'repump_mod_control_dac'	:   'yellow_aom_frq',
	}

yellow = False


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
		'MW_pulse_mod_risetime':                   10e-9,
		'send_AWG_start':                          1,
		'MW_pulse_mod_frequency' : 				   43e6,
		'MW_switch_risetime':					   450e-9, # 500e-9
	}

##########################################
### General settings for AdwinSSRO+MBI ###
##########################################

cfg['protocols']['AdwinSSRO+MBI'] = {
		'send_AWG_start'                        :   1,
		'AWG_wait_duration_before_MBI_MW_pulse':    1e-6,
		'AWG_wait_for_adwin_MBI_duration':          15e-6,
		'AWG_MBI_MW_pulse_duration':                2e-6,
		'AWG_MBI_MW_pulse_amp'      			:   0.00,#0.0165,
		'AWG_MBI_MW_pulse_mod_frq'  			:   0,
		'AWG_MBI_MW_pulse_ssbmod_frq'			:  	0,
		'AWG_wait_duration_before_shelving_pulse':  100e-9,
		'nr_of_ROsequences':                        1,
		'MW_pulse_mod_risetime':                    10e-9,
		'mw2_pulse_mod_risetime':					10e-9,
		
		'AWG_to_adwin_ttl_trigger_duration':        2e-6,
		'repump_after_MBI_duration':                150, 
		'repump_after_MBI_amp':                     15e-9,
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
		'TTTR_read_count':							1000, #s
		'TTTR_RepetitiveReadouts':					10,
		'measurement_time':                         1200,#sec
		'measurement_abort_check_interval':			1,#sec
		'MIN_HIST_SYNC_BIN': 	  					0,
	    'MAX_HIST_SYNC_BIN': 					 	1000,
	    'count_marker_channel':						1,
		}

############################################
### General settings for AdwinSSRO+delay ###
############################################

dl_physical_delay_time_offset	= 1294e-9 #1820e-9
dl_delayed_element_run_up_time  = 800e-9

# dl_minimal_delay_time = dl_minimal_delay_time_bare + dl_delayed_element_run_up_time

cfg['protocols']['AdwinSSRO+delay'] = {
    'delay_trigger_DI_channel':                 20,
    'delay_trigger_DO_channel':                 12,
    'delay_HH_trigger_DO_channel':				11,
    'do_tico_delay_control':                    1,
    'do_delay_HH_trigger':			   			0,
    # 'minimal_delay_time_bare':                  dl_minimal_delay_time_bare,
    # JS: the following parameter shouldn't be defined and isn't used anywhere anymore
    # I hope I got rid of all left-over occurrences.
    # "awg_delay':                                0, # this parameter is not dfined@!!!!! dl_awg_delay,
    'delayed_element_run_up_time':              dl_delayed_element_run_up_time,
    'self_trigger_pulse_timing_offset':			0e-9,
    # 'minimal_delay_time':                       dl_minimal_delay_time,
	'physical_delay_time_offset':				dl_physical_delay_time_offset,
	'delay_time_offset':						dl_physical_delay_time_offset + dl_delayed_element_run_up_time,
    'minimal_delay_cycles':                     15,
    'delay_clock_cycle_time':                   20e-9,
    'self_trigger_duration':                    100e-9,
	'delay_HH_sync_duration':					50e-9,
	'delay_HH_sync_offset':						500e-9,
	'delay_HH_trigger_duration':				20e-9,
}

###############################
### NV and field parameters ###
###############################

cfg['samples'][sample_name] = {
	'electron_transition' : electron_transition_string,
	'mw_mod_freq'   :       mw_mod_frequency,
	'mw_frq'        :       mw_frq_MBI, # this is automatically changed to mw_freq if hermites are selected.
	'mw_power'      :       mw_power,
	'mw2_mod_freq'   :      0,
	'mw2_frq'        :      0, 
	'mw2_power'      :      0,
	'multiple_source':      False,
	'ms-1_cntr_frq' :       f_msm1_cntr,
	'ms+1_cntr_frq' :       f_msp1_cntr,
	'N_0-1_splitting_ms-1': N_frq,
	'N_HF_frq'      :       N_HF_frq,
	'C_split'		:		C_split,


###############
### Carbons ###
###############
	'Carbon_LDE_phase_correction_list' : np.array([0.0]*4+[0]+[0.0]*7),
	'Carbon_LDE_init_phase_correction_list' : np.array([0.0]*4+[0.]+[0.0]*7),
    'phase_per_sequence_repetition'    : 59.691, # 360.0 - 60.818, # 15.23+0.07+0.1+0.1-0.03+0.43, #adwin needs positive values
    'phase_per_compensation_repetition': 78.057, #360.0 - 78.291, # 18.298,# adwin needs positive values
    'total_phase_offset_after_sequence': 301.63, # 101.63-1.3+1.7-1.1-1.5+2.5, #adwin needs positive values
###############
### SIL2    ###
###############

	'number_of_carbon_params':	8, # JS: should match with the list below

	# ###############
	# # C1 (A~ -376)#
	# ###############
	'C1_T2star_0'		: 10.76e-3,
	'C1_T2star_1_m1'	: 9.16e-3,

	'C1_freq_m1'        : (443317.88 + 819798.18)/2,
	'C1_freq_0' 		: 443317.88,
	'C1_freq_1_m1' 		: 819798.18,

	'C1_Ren_tau_m1'    :   [5.936e-6],
	'C1_Ren_N_m1'      :   [20],
	'C1_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-12.78] + [-5.54] + [2.57] + [1.19] + [6.55] + [2.0] + [-3.79] + [0.0] + [0.0] + [0.0]),

	'C1_phase_per_LDE_sequence_m1'	: 344.184,
	'C1_init_phase_correction_m1': 0.0,
	# 'C1_init_phase_correction_serial_swap_m1': 0.0,
	'C1_freq_p1'        : (443349.05 + 88091.98)/2,
	'C1_freq_1_p1' 		: 88066.83,

	'C1_Ren_tau_p1'    :   [10.28e-6],
	'C1_Ren_N_p1'      :   [4],
	'C1_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [-12.92] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C1_phase_per_LDE_sequence_p1'	:	0.0,
	'C1_init_phase_correction_p1': 0.0,

	'C1_LDE_phase_matching_time_m1' : 95e-9,
	###############
	# C2(A ~ -32)  #
	###############
	'C2_T2star_0'		: 11.79e-3,
	'C2_T2star_1_m1'	: 10.76e-3,

	'C2_freq_m1'        : (443010.86 + 475456.31)/2,
	'C2_freq_0' 		: 443010.86,
	'C2_freq_1_m1' 		: 475456.31,

	'C2_Ren_tau_m1'    :   [4.892e-06], #3.87
	'C2_Ren_N_m1'      :   [46], #36
	'C2_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.48] + [208.57] + [1.88] + [-2.37] + [6.73] + [-0.38] + [-11.9] + [223.37] + [0.0]),

	'C2_phase_per_LDE_sequence_m1'	: 60.883,
	'C2_init_phase_correction_m1': 0.0,
	# 'C2_init_phase_correction_serial_swap_m1': 0.0, #182.740, # C2,C4 serial swap sequence offset
	# 'C2_init_phase_correction_m1': 252.779, # single carbon sequence offset
	# offsets for the LDE calibration, not really interesting #178.552, #184.075, #181.041, # 185.919, #270.0,
	
	'C2_freq_p1'        : (442986.36 + 412434.56)/2,
	'C2_freq_1_p1' 		: 412584.87,

	'C2_Ren_tau_p1'    :   [8.762e-06], #3.87
	'C2_Ren_N_p1'      :   [44], #36
	'C2_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [-8.99] + [0.13] + [0.82] + [-4.02] + [-9.21] + [2.53] + [3.66] + [223.37] + [0.0]),

	'C2_phase_per_LDE_sequence_p1'	: 0.0,
	'C2_init_phase_correction_p1': 0.0,

	'C2_LDE_phase_matching_time_m1' : 366e-9,
	###############
	# C3 (A ~ -58)#
	###############
	'C3_T2star_0'		: 10.05e-3,
	'C3_T2star_1_m1'	: 9.71e-3,

	'C3_freq_m1'        : (442980.35 + 505394.68)/2,
	'C3_freq_0' 		: 442974.49,
	'C3_freq_1_m1' 		: 505367.01,

	'C3_Ren_tau_m1'    :   [3.692e-6],
	'C3_Ren_N_m1'      :   [66],
	'C3_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.26] + [-9.16] + [44.29] + [-3.89] + [-2.17] + [2.44] + [-0.92] + [0.0] + [0.0] + [0.0]),

	'C3_phase_per_LDE_sequence_m1'	: 84.63,
	'C3_init_phase_correction_m1': 0.0,

	'C3_freq_p1'        : (442993.52 + 382245.66)/2,
	'C3_freq_1_p1' 		: 382234.24,

	'C3_Ren_tau_p1'    :   [11.512e-6],
	'C3_Ren_N_p1'      :   [60],
	'C3_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [1.98] + [27.37] + [-4.54] + [0.2] + [5.62] + [-9.44] + [0.0] + [0.0] + [0.0]),

	'C3_phase_per_LDE_sequence_p1'	: 0.0, #84.126,
	'C3_init_phase_correction_p1': 0.0,

	'C3_LDE_phase_matching_time_m1' : 250e-9,
	###############
	# C4 (A ~ 33) #
	###############
	'C4_T2star_0'		: 18.98e-3,
	'C4_T2star_1_m1'	: 16.05e-3,

	'C4_freq_m1'        : (442805.46 + 416193.95)/2,
	'C4_freq_0' 		: 442805.46,
	'C4_freq_1_m1' 		: 416193.95,

	'C4_Ren_tau_m1'    :   [6.402e-6],#[1.745e-6],##[6.386e-6],
	'C4_Ren_N_m1'      :   [28],#[56], #28
	'C4_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [7.15] + [-2.45] + [7.68] + [-2.22] + [7.64] + [2.39] + [-2.62] + [0.0] + [0.0]),

	'C4_phase_per_LDE_sequence_m1'	: 14.616,
	'C4_init_phase_correction_m1'	: 0.0,

	'C4_freq_p1'        : (441374.13 + 464341.28)/2,
	'C4_freq_1_p1' 		: 464341.28,


	'C4_Ren_tau_p1'    :   [11.558e-6],#[1.745e-6],##[6.386e-6],
	'C4_Ren_N_p1'      :   [40],#[56], #28
	'C4_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [2.8] + [3.12] + [48.35] + [-0.6] + [1.87] + [5.39] + [0.0] + [0.0]),

	'C4_phase_per_LDE_sequence_p1'	: 0.0, #15.795,
	'C4_init_phase_correction_p1'	: 0.0,

	'C4_LDE_phase_matching_time_m1' : 0e-9,#305e-9,
	###############
	# C5 (A ~ 26) #
	###############
	'C5_T2star_0'		: 4.46e-3,
	'C5_T2star_1_m1'	: 4.53e-3,

	'C5_freq_m1'        : (443714.55 + 422758.50)/2,
	'C5_freq_0' 		: 443714.55,
	'C5_freq_1_m1' 		: 422758.5,

	'C5_Ren_tau_m1'    :   [8.656e-6], #[10.964e-6], #8.826
	'C5_Ren_N_m1'      :   [40], # [46],  #,
	'C5_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-9.09] + [-5.32] + [7.72] + [-5.84] + [9.7] + [0.79] + [-0.04] + [0.0] + [0.0]),

	'C5_phase_per_LDE_sequence_m1'	: 21.329,
	'C5_init_phase_correction_m1': 0.0,

	'C5_freq_p1'        : (442792.00 + 472344.32)/2,
	'C5_freq_1_p1' 		: 472344.32,

	'C5_Ren_tau_p1'    :   [11.474e-6], #[10.964e-6], #8.826
	'C5_Ren_N_p1'      :   [60], # [46],  #,
	'C5_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [-8.99] + [-1.11] + [1.59] + [-10.62] + [-19.97] + [1.39] + [6.16] + [0.0] + [0.0]),

	'C5_phase_per_LDE_sequence_p1'	: 0.0, #22.336,
	'C5_init_phase_correction_p1': 0.0,

	'C5_LDE_phase_matching_time_m1' : 0e-9,#272e-9,
	###############
	# C6(A ~ -72) #
	###############
	'C6_T2star_0'		: 9.89e-3,
	'C6_T2star_1_m1'	: 9.20e-3,

	'C6_freq_m1'        : (443857.94 + 520853.65)/2,
	'C6_freq_0' 		: 443857.94,
	'C6_freq_1_m1' 		: 520853.65,

	'C6_Ren_tau_m1'    :   [3.632e-6],
	'C6_Ren_N_m1'      :   [52],
	'C6_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [3.89] + [-2.53] + [-4.81] + [-0.87] + [1.04] + [95.54] + [-18.99] + [0.0] + [0.0] + [0.0]),

	'C6_phase_per_LDE_sequence_m1'	: 100.51,
	'C6_init_phase_correction_m1': 0.0,

	'C6_freq_p1'        : (443849.06 + 367087)/2,
	'C6_freq_1_p1' 		: 367053.62,

	'C6_Ren_tau_p1'    :   [9.238e-6],
	'C6_Ren_N_p1'      :   [24],
	'C6_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [-1.12] + [-3.57] + [-3.73] + [-0.81] + [-15.32] + [-5.92] + [0.0] + [0.0] + [0.0]),

	'C6_phase_per_LDE_sequence_p1'	: 0.0, #97.5,
	'C6_init_phase_correction_p1': 0.0,

	'C6_LDE_phase_matching_time_m1' : 250e-9,
	###############
	# C7(A ~ -11)  #
	###############
	'C7_T2star_0'		: 7.65e-3,
	'C7_T2star_1_m1'	: 6.45e-3,

	'C7_freq_m1'        : (443247.28 + 455460.10)/2,
	'C7_freq_0' 		: 443247.28,
	'C7_freq_1_m1' 		: 455460.1,

	'C7_Ren_tau_m1'    :   [11.678e-6],
	'C7_Ren_N_m1'      :   [60],
	'C7_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-0.47] + [-6.33] + [9.12] + [15.65] + [10.23] + [1.08] + [226.6] + [0.0] + [0.0]),

	'C7_phase_per_LDE_sequence_m1'	: 46.813,
	'C7_init_phase_correction_m1': 0.0,

	'C7_freq_p1'        : (443245.18 + 431633.03)/2,
	'C7_freq_1_p1' 		: 431635.32,

	'C7_Ren_tau_p1'    :   [10.866e-6],
	'C7_Ren_N_p1'      :   [54],
	'C7_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [-8.99] + [2.98] + [4.54] + [18.25] + [16.01] + [1.79] + [-14.02] + [0.0] + [0.0]),

	'C7_phase_per_LDE_sequence_p1'	: 0.0, #46.184,
	'C7_init_phase_correction_p1': 0.0,

	'C7_LDE_phase_matching_time_m1' : 413e-9,

	###############
	# C8(A ~ -10)  #
	############### ### only low control fidelity.
	'C8_freq_m1'        : (443338.55 + 453503.83)/2.,
	'C8_freq_0' 		: 443338.55,
	'C8_freq_1_m1' 		: 453503.83,
	'C8_Ren_tau_m1'    :   [17.282e-6],
	'C8_Ren_N_m1'      :   [94],
	'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-8.99] + [63.23] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C8_phase_per_LDE_sequence_m1'	:	0.0,
	'C8_init_phase_correction_m1': 0.0,


	'C8_freq_p1'        : (443338.55 + 453503.83)/2.,

	'C8_freq_1_p1' 		: 453503.83,
	'C8_Ren_tau_p1'    :   [17.282e-6],
	'C8_Ren_N_p1'      :   [94],
	'C8_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [-8.99] + [63.23] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C8_phase_per_LDE_sequence_p1'	:	0.0,
	'C8_init_phase_correction_p1': 0.0,

	'C8_LDE_phase_matching_time_m1' : 100e-9,
	}


cfg['protocols'][name]['AdwinSSRO'] = {
		'A_CR_amplitude':			 	 4.5e-9,#4.5e-9, #4e-9
		'A_RO_amplitude' :				 0,
		'A_SP_amplitude':				 100e-9,
		'CR_duration' :				 	 60, 
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.8e-9,#1.5e-9, #2e-9 
		'Ex_RO_amplitude':				 4.5e-9,#4.5e-9,#used to be 8e-9
		'Ex_SP_amplitude':				 0,
		'Ex_SP_calib_amplitude':		 14.0e-9,
		'SP_duration':					 100,
		'SP_duration_ms0':				 100,
		'SP_duration_ms1':				 1000,
		'SP_filter_duration':			 0,
		'SSRO_duration':				 40,
		'SSRO_repetitions':				 5000,
		'AWG_controlled_readout':		 0, 
		}

###


###


cfg['protocols'][name]['AdwinSSRO+MBI']={
	#Spin pump before MBI
	'Ex_SP_amplitude'           :           0e-9,   #15e-9,#15e-9,    #18e-9
	'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet?
	'SP_E_duration'             :           5,     #Duration for both Ex and A spin pumping
	 
	 #MBI readout power and duration
	'Ex_MBI_amplitude'          :           0.0e-9,
	'MBI_duration'              :           10,

	#Repump after succesfull MBI
	'repump_after_MBI_duration' :           [50],
	'repump_after_MBI_A_amplitude':         [30e-9],  #18e-9
	'repump_after_MBI_E_amplitude':         [0e-9],

	#MBI parameters
	'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
	'MBI_threshold'             :           0, 
	'AWG_wait_for_adwin_MBI_duration':      10e-6+15e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

	'repump_after_E_RO_duration':           15,
	'repump_after_E_RO_amplitude':          15e-9,

	#Shutter
	'use_shutter':                          0, # we don't have a shutter in the setup right now
}

cfg['protocols'][name]['AdwinSSRO+C13']={
	### Comment NK 2016-02-27 these parameters have been directly ported to LT4 from LT3 and still need testing!
	#'wait_between_runs':                    0, ### bool operator, set to one to wait for the 'Shutter_safety_time'

		#C13-MBI  
		'C13_MBI_threshold_list':               [1],
		'C13_MBI_RO_duration':                  40,  #25
		'E_C13_MBI_RO_amplitude':               0.15e-9, #0.02e-9
		'SP_duration_after_C13':                20, #use long repumping in case of swap init
		'A_SP_amplitude_after_C13_MBI':         25e-9,
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
		'min_dec_tau'         :     2.0e-6,#2.1e-6,#16e-9 + cfg['protocols'][name]['pulses']['Hermite_pi_length'],#2.05e-6,#16e-9 + cfg['protocols'][name]['pulses']['Hermite_pi_length'], 
		'max_dec_tau'         :     2.5e-6,#2.4e-6,#0.2e-6,#2.5e-6
		'dec_pulse_multiple'  :     4,      #4.
		# 'min_dec_duration'	  :		2.0e-6,
		# 'max_dec_duration'	  :		2.5e-6,
		# Memory entanglement sequence parameters
		'optical_pi_AOM_amplitude' :     0.5,
		'optical_pi_AOM_duration' :      200e-9,
		'optical_pi_AOM_delay' :         300e-9,
		'do_optical_pi' :                False,
		'initial_MW_pulse':           	 'pi2' #'pi', 'no_pulse'

}

cfg['protocols'][name]['AdwinSSRO-integrated'] = {
	'SSRO_duration' : 10}

cfg['protocols'][name]['pulses'] = {

		'X_phase'               :90,
		'Y_phase'               :0,

		'C13_X_phase' 			:0,
		'C13_Y_phase' 			:270,

		'pulse_shape': pulse_shape,
		'MW_switch_channel'		:	'mw_switch', ###'None', if you want to activate the switch, put to MW_switch
		'mw2_modulation_frequency'   :  0,
		'MW_modulation_frequency'   :  0,
    	'CORPSE_rabi_frequency' :   9e6,
    	'CORPSE_amp' :		 		0.201,
    	'CORPSE_pi2_amp':			0.543,
    	'CORPSE_pulse_delay':		0e-9,
    	'CORPSE_pi_amp':			0.517,
    	'Hermite_pi_length': 		hermite_pi_length,#150e-9, ## bell duration
        'Hermite_pi_amp': 			hermite_pi_amp,#0.938,#0.901, # 2015-12-17 ## bell duration
        'Hermite_pi2_length':		hermite_pi2_length,
        'Hermite_pi2_amp': 			hermite_pi2_amp, 
        'Hermite_Npi4_length':		90e-9, #pi/4 45e-9
        'Hermite_Npi4_amp':			0.844 + 0.0185,#2015-12-28
        'Hermite_theta_amp':		hermite_pi_amp, #0.84,#0.83/3+0.07,
		'Hermite_theta_length':		hermite_pi_length, #50e-9,


        'Square_pi_length' :		square_pi_length, # 2014-12-01
      	'Square_pi_amp' :			square_pi_amp , #  2014-12-01
      	'IQ_Square_pi_amp' :		0.03 , # calib. for 2 us pi pulse, 2014-07-25 
      	'Square_pi2_length' :		25e-9, # XXXXXXX not calibrated
    	'Square_pi2_amp'  :			0.735,#0.71104, # XXXXXXX not calibrated
    	'IQ_Square_pi2_amp'  :		0.015, # XXXXXXX not calibrated
    	'extra_wait_final_pi2' :	-30e-9,
    	'DESR_pulse_duration' :		5e-6,
    	'DESR_pulse_amplitude' :	0.02, #should not be larger than 0.05

    	### composite pulses

    	'BB1_fast_pi_amp':			0.88,
    	'BB1_fast_pi_duration':		104e-9,#hermite_pi_length,

    	### AXY4 pulses

    	'AXY_f3DD':					0.1,

    	# Second mw source
    	'mw2_Hermite_pi_length': 	0,
        'mw2_Hermite_pi_amp': 		0,
        'mw2_Hermite_pi2_length':	0,
        'mw2_Hermite_pi2_amp': 		0,
        'mw2_Square_pi_length' :	0,
      	'mw2_Square_pi_amp' :		0,
      	'mw2_Square_pi2_length' :   0,
    	'mw2_Square_pi2_amp' :		0,

    	'eom_pulse_amplitude'		 : -2.0, # calibration PH 2017-02-24
    	'eom_pulse_duration'         : 2e-9,
    	'eom_off_duration'           : 50e-9,
    	'eom_off_amplitude'          : 0.32,#0.522, # calibration PH 2017-10-10
    	'eom_overshoot_duration1'    : 20e-9,
    	'eom_overshoot1'             : -0.04,
    	'eom_overshoot_duration2'    : 4e-9,
    	'eom_overshoot2'             : -0.00,
    	'aom_risetime'               : 20e-9, #17e-9
    	'aom_amplitude'              : 0.7, 
}

cfg['protocols'][name]['cr_linescan'] = {
		'A_CR_amplitude':				 2.2e-9,
		'CR_duration' :				 	 80,
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.0e-9,
		}
