cfg={}
sample_name = 'Pippin'
sil_name = 'SIL1'
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

f_msm1_cntr = 1.705249e9 #1.669252e9#1.713316e9 #1.7#2.809073e9#2.809328e9#2.80888e9#2.75375e9# +/-   0.000018           #Electron spin ms=-1 frquency 

f_msp1_cntr = 4.051020e9#4.087882e9#2.810e9 #not calib       #Electron spin ms=+1 frequency
mw_mod_frequency = 0
mw_power = 20

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.198e6        #calibrated 2014-03-20/181319
C_split  = 0.847e6 

pulse_shape = 'Hermite'
electron_transition = '-1'

if electron_transition == '+1':
	electron_transition_string = '_p1'
	mw_frq     = f_msp1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msp1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 100e-9
	hermite_pi_amp = 0.76

	hermite_pi2_length = 36e-9
	hermite_pi2_amp = 0.833

else:
	electron_transition_string = '_m1'
	mw_frq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
	mw_frq_MBI = f_msm1_cntr - mw_mod_frequency # - N_HF_frq    # Initialized frequency

	hermite_pi_length = 100e-9
	hermite_pi_amp = 0.395#0.887

	hermite_pi2_length = 36e-9
	hermite_pi2_amp = 0.437


### General settings for AdwinSSRO
cfg['protocols']['AdwinSSRO']={
		'AWG_done_DI_channel':          17,
		'AWG_start_DO_channel':         9,
		'AWG_event_jump_DO_channel'	:   10,
		'counter_channel':              1,
		#'counter_ch_input_pattern':		0,
		'cycle_duration':               300,
		'green_off_amplitude':          0.0,
		'green_repump_amplitude':       45e-6, #XXXX 50e-6
		'green_repump_duration':        10,
		'send_AWG_start':               0,
		'sequence_wait_time':           1,
		'wait_after_RO_pulse_duration': 3,
		'wait_after_pulse_duration':    3,
		'cr_wait_after_pulse_duration': 3,
		'wait_for_AWG_done':            0,
		'Ex_off_voltage':               0.,
		'A_off_voltage':                -0.0,
		'yellow_repump_amplitude':      50e-9,
		'yellow_repump_duration':       300,
		'yellow_CR_repump':             1,
		'green_CR_repump':              1000,
		'CR_probe_max_time':            1000000,
		'SSRO_stop_after_first_photon':	0,
		}

cfg['protocols']['AdwinSSRO']['cr_mod'] = True
cfg['protocols']['cr_mod']={
	'cr_mod_control_dac'		:	'gate_mod',
	'cr_mod_control_offset'     :   0.0,
	'cr_mod_control_amp'        :   0.1, #V
	'cr_mod_control_avg_pts'	:   500000.,
	'repump_mod_control_offset' :   5.4, #not gets set automatically
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
		'mw_power':                                20,#-20,
		'MW_pulse_mod_risetime':                   20e-9,
		'send_AWG_start':                          1,
		'MW_pulse_mod_frequency' : 				   43e6,
	}


##########################################
### General settings for AdwinSSRO+MBI ###
##########################################

cfg['protocols']['AdwinSSRO+MBI'] = {

		'send_AWG_start'                        :   1,
		'AWG_wait_duration_before_MBI_MW_pulse'	:   1e-6,
		'AWG_wait_for_adwin_MBI_duration'		:   15e-6,
		'AWG_MBI_MW_pulse_duration'				:   0.02e-6,
		'AWG_MBI_MW_pulse_amp'      			:   0.022,#0.0165,
		'AWG_MBI_MW_pulse_mod_frq'  			:   0,
		'AWG_MBI_MW_pulse_ssbmod_frq'			:  	0,
		'AWG_wait_duration_before_shelving_pulse':  100e-9,
		'nr_of_ROsequences'						:   1,  #setting this on anything except on 1 crahses the adwin?
		'MW_pulse_mod_risetime'					:   20e-9,
		'MW_switch_risetime'                    :   500.0e-9, #This was 100e-9, seemed not long enough NK 20150319
		'AWG_to_adwin_ttl_trigger_duration'		:   2e-6,
		'repump_after_MBI_duration'				:   100, 
		'repump_after_MBI_amp'					:   15e-9,
		'max_MBI_attempts'                      :   1,
		'N_randomize_duration'                  :   50,
		'Ex_N_randomize_amplitude'				:	15e-9,
		'A_N_randomize_amplitude'               :   15e-9,
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
	'mw_frq'        :       mw_frq_MBI, # this is automatically changed to mw_freq if hermites are selected.
	'mw_power'      :       mw_power,
	'ms-1_cntr_frq' :       f_msm1_cntr,
	'ms+1_cntr_frq' :       f_msp1_cntr,
	'N_0-1_splitting_ms-1': N_frq,
	'N_HF_frq'      :       N_HF_frq,
	'C_split'		:		C_split}

cfg['protocols'][name]['AdwinSSRO'] = {
		'A_CR_amplitude':				 1e-9,
		'A_RO_amplitude' :				 0,
		'A_SP_amplitude':				 25e-9,   #2015-06-27 was 30 
		'CR_duration' :				 	 50, 
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 3e-9,
		'Ex_RO_amplitude':				 5e-9, #5e-9
		'Ex_SP_amplitude':				 0e-9,  #2015-05-25
		'Ex_SP_calib_amplitude':		 5e-9, ## used for ssro calib.
		'SP_duration':					 100,
		'SP_duration_ms0':				 50,
		'SP_duration_ms1':				 1000, #2015-05-25
		'SP_filter_duration':			 0,
		'SSRO_duration':				 50,
		'SSRO_repetitions':				 5000,
		}
cfg['protocols'][name]['AdwinSSRO+MBI']={
	#Spin pump before MBI
	'Ex_SP_amplitude'           :           0e-9,   #15e-9,#15e-9,    #18e-9
	'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet?
	'SP_E_duration'             :           10,     #Duration for both Ex and A spin pumping
	 
	 #MBI readout power and duration
	'Ex_MBI_amplitude'          :           0.65e-9,
	'MBI_duration'              :           40,

	#Repump after succesfull MBI
	'repump_after_MBI_duration' :           [150],
	'repump_after_MBI_A_amplitude':         [25e-9],  #18e-9
	'repump_after_MBI_E_amplitude':         [0e-9],

	#MBI parameters
	'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
	'MBI_threshold'             :           0, #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	'AWG_wait_for_adwin_MBI_duration':      10e-6+40e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

	'repump_after_E_RO_duration':           15,
	'repump_after_E_RO_amplitude':          15e-9,

	#Shutter
	'use_shutter':                          0, # we don't have a shutter in the setup right now
}

cfg['protocols'][name]['AdwinSSRO+C13']={}

cfg['protocols'][name]['AdwinSSRO-integrated'] = {
	'SSRO_duration' : 10} #18

CORPSE_frq = 9e6

cfg['protocols'][name]['pulses'] = {
		

		'X_phase'                   :   90,
		'Y_phase'                   :   0,

		'C13_X_phase' :0,
		'C13_Y_phase' :270,

		'pulse_shape': pulse_shape,

		'MW_switch_risetime'	:	500e-9,
		'MW_switch_channel'		:	'None', ### if you want to activate the switch, put to MW_switch
    	'CORPSE_rabi_frequency' : CORPSE_frq,
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
        'Square_pi_length' :		100e-9,#2000e-9, # calib. 2014-07-25
      	'Square_pi_amp' :			0.731, 
      	'Square_pi2_length' :		25e-9, # XXXXXXX not calibrated
    	'Square_pi2_amp'  :			0.684, # XXXXXXX not calibratedrepump
      	'IQ_Square_pi_amp' :		0.068,#632 , # calib. for 1 us pi pulse, 2015-05-12 
      	'IQ_Square_pi2_amp'  :		0.6967, # 
    	'extra_wait_final_pi2' :	-30e-9,
    	'DESR_pulse_duration' :		4e-6,
    	'DESR_pulse_amplitude' :	0.15,#0.194,
}


cfg['protocols'][name]['cr_linescan'] = {
		'A_CR_amplitude':				 4e-9,
		'CR_duration' :				 	 100,
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.5e-9,
		}