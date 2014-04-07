cfg={}
sample_name = 'Fritz'
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

### General settings for AdwinSSRO
cfg['protocols']['AdwinSSRO']={
		'AWG_done_DI_channel':          17,
		'AWG_event_jump_DO_channel':    8,
		'AWG_start_DO_channel':         9,
		'counter_channel':              1,
		'cycle_duration':               300,
		'green_off_amplitude':          0.0,
		'green_repump_amplitude':       10e-6,
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
		'yellow_repump_duration':       500,
		'yellow_CR_repump':             1,
		'green_CR_repump':              1000,
		'CR_probe_max_time':            1000000,
		}

yellow=False
cfg['protocols']['AdwinSSRO']['yellow'] = yellow
if yellow:
    cfg['protocols']['AdwinSSRO']['repump_duration']  =  cfg['protocols']['AdwinSSRO']['yellow_repump_duration']
    cfg['protocols']['AdwinSSRO']['repump_amplitude'] =  cfg['protocols']['AdwinSSRO']['yellow_repump_amplitude']
    cfg['protocols']['AdwinSSRO']['CR_repump']        =  cfg['protocols']['AdwinSSRO']['yellow_CR_repump']
else:
    cfg['protocols']['AdwinSSRO']['repump_duration']  =  cfg['protocols']['AdwinSSRO']['green_repump_duration']
    cfg['protocols']['AdwinSSRO']['repump_amplitude'] =  cfg['protocols']['AdwinSSRO']['green_repump_amplitude']
    cfg['protocols']['AdwinSSRO']['CR_repump']        =  cfg['protocols']['AdwinSSRO']['green_CR_repump']

### General settings for AdwinSSRO+espin
mw_frq = 2.8124e9
cfg['protocols']['AdwinSSRO+espin'] = {
		'mw_frq':                                  mw_frq, 
		'mw_power':                                20,#-20,
		'MW_pulse_mod_risetime':                   20e-9,
		'send_AWG_start':                          1,
	}
### General settings for AdwinSSRO+MBI
cfg['protocols']['AdwinSSRO+MBI'] = {
		'AWG_wait_duration_before_MBI_MW_pulse':    1e-6,
		'AWG_wait_for_adwin_MBI_duration':      15e-6,
		'AWG_MBI_MW_pulse_duration':                2e-6,
		'AWG_wait_duration_before_shelving_pulse':  100e-9,
		'nr_of_ROsequences':                        1,
		'MW_pulse_mod_risetime':                    10e-9,
		'AWG_to_adwin_ttl_trigger_duration':        2e-6,
		'repump_after_MBI_duration':                100,
		'repump_after_MBI_amp':                     15e-9,
		}
cfg['protocols']['AdwinSSRO+PQ'] = {
		'MAX_DATA_LEN':                             int(100e6),
		'BINSIZE':                                  1, #2**BINSIZE*BASERESOLUTION
		'MIN_SYNC_BIN':                             0,
		'MAX_SYNC_BIN':                             1000,
		'measurement_time':                         1200,#sec
		}


###############################
### NV and field parameters ###
###############################

f_msm1_cntr = 2.8087e9# +/-   0.00000018            #Electron spin ms=-1 frquency
f_msp1_cntr = 3e9 #not calib       #Electron spin ms=+1 frequency

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.195e6        #calibrated 20140320/181319

cfg['samples'][sample_name] = {
'ms-1_cntr_frq' :       f_msm1_cntr,
'ms+1_cntr_frq' :       f_msp1_cntr,
'N_0-1_splitting_ms-1': N_frq,
'N_HF_frq'      :       N_HF_frq}

cfg['protocols'][name]['AdwinSSRO'] = {
		'A_CR_amplitude':				 5e-9,
		'A_RO_amplitude' :				 0,
		'A_SP_amplitude':				 5e-9,
		'CR_duration' :				 	 100,
		'CR_preselect':					 1000,
		'CR_probe':						 1000,
		'CR_repump':					 1000,
		'Ex_CR_amplitude':				 1.5e-9,
		'Ex_RO_amplitude':				 1.5e-9,
		'Ex_SP_amplitude':				 1.5e-9,
		'SP_duration':					 200,
		'SP_filter_duration':			 0,
		'SSRO_duration':				 50,
		'SSRO_repetitions':				 5000,
		'SSRO_stop_after_first_photon':	 0,
		}


cfg['protocols'][name]['AdwinSSRO-integrated'] = {
'SSRO_duration' : 30}

CORPSE_frq = 6.5e6
cfg['protocols'][name]['pulses'] = {

    	'CORPSE_rabi_frequency' : CORPSE_frq,
    	'CORPSE_amp' : 0.201 ,#m.params['msm1_CORPSE_pi_amp'
    	'CORPSE_pi2_amp':0.236991,
    	'CORPSE_pi_60_duration' : 1./CORPSE_frq/6.,
    	'CORPSE_pi_m300_duration' : 5./CORPSE_frq/6.,
    	'CORPSE_pi_420_duration' : 7./CORPSE_frq/6.,
    	'CORPSE_pi_mod_frq' : f_msm1_cntr - mw_frq,
    	'CORPSE_pi2_mod_frq' : f_msm1_cntr - mw_frq,
}
