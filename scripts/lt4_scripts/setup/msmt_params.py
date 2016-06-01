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

f_msm1_cntr = 1.716222e9#1.715936e9 #1.711414e9	#Electron spin ms=-1 frquency   ##Calib 2015-05-06
f_msp1_cntr = 4.039757e9 #4.044206e9  #Electron spin ms=+1 frequency

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.19e6        #calibrated 20140320/181319
C_split  = 0.847e6 
pulse_shape = 'Hermite'
electron_transition = '-1'

if electron_transition == '+1':
	electron_transition_string = '_p1'
	mw_frq     = f_msp1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msp1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 290e-9#100e-9 #Not calibrated
	hermite_pi_amp = 0.873 #Not calibrated

	square_pi_length = 20e-9 #Not calibrated
	square_pi_amp = 0.6 #Not calibrated

	hermite_pi2_length = 76e-9 #Not calibrated
	hermite_pi2_amp = 0.840 #Not calibrated

else:
	electron_transition_string = '_m1'
	mw_frq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msm1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 94e-9
	hermite_pi_amp = 0.911

	square_pi_length = 50e-9
	square_pi_amp = 0.248

	hermite_pi2_length = 50e-9
	hermite_pi2_amp = 0.564#0.608


### General settings for AdwinSSRO
cfg['protocols']['AdwinSSRO']={
		'AWG_done_DI_channel':          18,
		'AWG_event_jump_DO_channel':    8,
		'AWG_start_DO_channel':         9,
		'counter_channel':              1,
		'cycle_duration':               300,
		'green_off_amplitude':          0.0,
		'green_repump_amplitude':       18e-6,
		'green_repump_duration':        20,
		'send_AWG_start':               0,
		'sequence_wait_time':           0,
		'wait_after_RO_pulse_duration': 3,
		'wait_after_pulse_duration':    3,
		'cr_wait_after_pulse_duration': 3,
		'wait_for_AWG_done':            0,
		'Ex_off_voltage':               0.03,
		'A_off_voltage':                -0.2,
		'yellow_repump_amplitude':      35e-9,#80e-9, #50e-9 XXXXXXXXXXXX
		'yellow_repump_duration':       300,
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
		'MW_switch_risetime':						500e-9,
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
	'Carbon_LDE_init_phase_correction_list' : np.array([0.0]*4+[180.]+[0.0]*7),
    'phase_per_sequence_repetition'    :350.776-14.472, #adwin needs positive values
    'phase_per_compensation_repetition':360-6.21, # adwin needs positive values
    'total_phase_offset_after_sequence': -129.1,#180.0,#42.328,
###############
### SIL2    ###
###############

	###############
	# C1 (A~ -350)#
	###############
	'C1_freq_m1'        : (441045.84+8165920)/2.,
	'C1_freq_0' 		: 446128.33,
	'C1_freq_1_m1' 		: 8165920,

	'C1_Ren_tau_m1'    :   [5.97e-6],
	'C1_Ren_N_m1'      :   [28],
	'C1_Ren_extra_phase_correction_list_m1' : np.array([0.0]*11),

	###############
	# C3 (A ~ -55)#
	###############
	'C3_freq_m1'        : (440252.25 + 516843)/2.,
	'C3_freq_0' 		: 440252.25,
	'C3_freq_1_m1' 		: 516843,

	'C3_Ren_tau_m1'    :   [3.66e-6],
	'C3_Ren_N_m1'      :   [50],
	'C3_Ren_extra_phase_correction_list_m1' : np.array([0.0]*11),
	
	###############
	# C4 (A ~ 26) #
	###############
	'C4_freq_m1'        : (416812.23+ 443393.29)/2,
	'C4_freq_0' 		: 443416.22,
	'C4_freq_1_m1' 		: 416815.78,

	'C4_Ren_tau_m1'    :   [6.384e-6],##[6.386e-6],
	'C4_Ren_N_m1'      :   [28], #28
	'C4_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [-100.61] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

	'C4_unc_N_m1'		:  [40],
	'C4_unc_tau_m1'		:  [6.93e-6],
	'C4_unc_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [139.34] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),
	'C4_unc_phase_offset_m1' : 126.74,
	###############
	# C5 (A ~ -26) #
	###############
	'C5_freq_m1'        : (426648.89+447931.8)/2,
	'C5_freq_0' 		: 447931.8,
	'C5_freq_1_m1' 		: 426648.89,

	'C5_Ren_tau_m1'    :   [8.57e-6], #8.826
	'C5_Ren_N_m1'      :   [36], 
	'C5_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-8.99] + [63.23] + [20.11] + [0.0] + [-44.9] + [0.0] + [0.0] + [0.0] + [0.0]),


	###############
	# C6(A ~ -72) #
	###############
	'C6_freq_m1'        : (438746.23 + 500e3)/2.,
	'C6_freq_0' 		: 443762.95,
	'C6_freq_1_m1' 		: 500277.17,

	'C6_Ren_tau_m1'    :   [4.935e-6],
	'C6_Ren_N_m1'      :   [44],
	'C6_Ren_extra_phase_correction_list_m1' : np.array([0.0]*11),

	###############
	# C7(A ~ 11)  #
	###############
	# 'C7_freq_m1'        : (441e3*2 + 55e3)/2.,
	# 'C7_freq_0' 		: 440252.25,
	# 'C7_freq_1_m1' 		: 516843,

	# 'C7_Ren_tau_m1'    :   [5.28e-6],
	# 'C7_Ren_N_m1'      :   [26],
	# 'C7_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-8.99] + [63.23] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [0.0] + [0.0]),

	###############
	# C8(A ~ -33)  #
	###############
	'C8_freq_m1'        : (479173.5+446669.09)/2,
	'C8_freq_0' 		: 446669.09,
	'C8_freq_1_m1' 		: 479173.5,

	'C8_Ren_tau_m1'    :   [4.852e-6], #3.87
	'C8_Ren_N_m1'      :   [44], #36
	'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [-8.99] + [63.23] + [20.11] + [0.0] + [-37.25] + [0.0] + [0.0] + [223.37] + [0.0]),
	
	'C8_unc_N_m1'		:  [40],
	'C8_unc_tau_m1'		:  [6.93e-6],
	'C8_unc_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [41.6] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),
	'C8_unc_phase_offset_m1' : -55.29,


	}


cfg['protocols'][name]['AdwinSSRO'] = {
		'A_CR_amplitude':			 	 5e-9, #4e-9
		'A_RO_amplitude' :				 0,
		'A_SP_amplitude':				 20e-9,
		'CR_duration' :				 	 50, 
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 2e-9, #2e-9 
		'Ex_RO_amplitude':				 4.5e-9, #used to 8e-9
		'Ex_SP_amplitude':				 0,
		'Ex_SP_calib_amplitude':		 1e-9,
		'SP_duration':					 100,
		'SP_duration_ms0':				 100,
		'SP_duration_ms1':				 1000,
		'SP_filter_duration':			 0,
		'SSRO_duration':				 40,
		'SSRO_repetitions':				 5000, 
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
		'E_C13_MBI_RO_amplitude':               0.07e-9, #0.02e-9
		'SP_duration_after_C13':                20, #use long repumping in case of swap init
		'A_SP_amplitude_after_C13_MBI':         52e-9,
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
	'SSRO_duration' : 8}

cfg['protocols'][name]['pulses'] = {

		'X_phase'               :90,
		'Y_phase'               :0,

		'C13_X_phase' 			:0,
		'C13_Y_phase' 			:270,

		'pulse_shape': pulse_shape,
		'MW_switch_risetime'	:	500e-9,
		'MW_switch_channel'		:	'None', ### if you want to activate the switch, put to MW_switch
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

    	'BB1_fast_pi_amp':			0.529,#0.604,
    	'BB1_fast_pi_duration':		130e-9,#200e-9,#hermite_pi_length,


    	# Second mw source
    	'mw2_Hermite_pi_length': 	0,
        'mw2_Hermite_pi_amp': 		0,
        'mw2_Hermite_pi2_length':	0,
        'mw2_Hermite_pi2_amp': 		0,
        'mw2_Square_pi_length' :	0,
      	'mw2_Square_pi_amp' :		0,
      	'mw2_Square_pi2_length' :   0,
    	'mw2_Square_pi2_amp' :		0,

    	'eom_pulse_amplitude'		 : 1.9,
    	'eom_pulse_duration'         : 2e-9,
    	'eom_off_duration'           : 50e-9,
    	'eom_off_amplitude'          : -0.293, # calibration 2015-11-04
    	'eom_overshoot_duration1'    : 20e-9,
    	'eom_overshoot1'             : -0.04,
    	'eom_overshoot_duration2'    : 4e-9,
    	'eom_overshoot2'             : -0.00,
    	'aom_risetime'               : 28e-9, #17e-9
    	'aom_amplitude'              : 0.431, #CR 31   AR 2016-05-26
}

cfg['protocols'][name]['cr_linescan'] = {
		'A_CR_amplitude':				 2e-9,
		'CR_duration' :				 	 80,
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.5e-9,
		}