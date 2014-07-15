
cfg={}

sample_name = 'THe111_no1'
sil_name = 'SIL1'
name=sample_name+'_'+sil_name
cfg['samples'] = {'current':sample_name}
cfg['protocols'] = {'current':name}

cfg['protocols'][name] = {}


cfg['protocols']['The111_no1_SIL1'] = {}
cfg['protocols']['Hans_sil1'] = {}
cfg['protocols']['Hans_sil4'] = {}


print 'updating msmt params lt1 for {}'.format(cfg['samples']['current'])



##############################################################################
##############################################################################
### General Settings for Protocols
##############################################################################
##############################################################################

    ######################################
    ### General settings for AdwinSSRO ###
    ######################################

cfg['protocols']['AdwinSSRO']={
    'AWG_done_DI_channel'       :       20,
    'AWG_event_jump_DO_channel' :       14,
    'AWG_start_DO_channel'      :       10,
    'counter_channel'           :       1,
    'cycle_duration'            :       300,
    'green_off_amplitude'       :       0.0,
    'green_repump_amplitude'    :       100e-6,
    'green_repump_duration'     :       15,
    'send_AWG_start'            :       0,
    'sequence_wait_time'        :       1,
    'wait_after_RO_pulse_duration':     3,
    'wait_after_pulse_duration' :       3,
    'cr_wait_after_pulse_duration':     1,
    'wait_for_AWG_done'         :       0,
    'green_off_voltage'         :       0,
    'Ex_off_voltage'            :       0.,
    'A_off_voltage'             :       -0.0,
    'repump_off_voltage'        :       0,
    'yellow_repump_amplitude'   :       30e-9,
    'yellow_repump_duration'    :       500,
    'yellow_CR_repump'          :       1,
    'green_CR_repump'           :       1000,
    'CR_probe_max_time'         :       1000000,
    'SSRO_stop_after_first_photon': 0,}

cfg['protocols']['AdwinSSRO']['cr_mod'] = True
cfg['protocols']['cr_mod']={
    'cr_mod_control_offset'     :   0.0,
    'cr_mod_control_amp'        :   0.05, #V
    'repump_mod_control_amp'    :   .5, #V
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

mw_frq = 2.78e9
mw_power = 20 
cfg['protocols']['AdwinSSRO+espin'] = {
        'mw_frq'                :     mw_frq, 
        'mw_power'              :     mw_power,
        'send_AWG_start'        :     1,
        'MW_pulse_mod_risetime' :     20e-9,
        'MW_pulse_mod_frequency':     46e6,
        }

##########################################
### General settings for AdwinSSRO+MBI ###
##########################################


cfg['protocols']['AdwinSSRO+MBI'] = {
    'send_AWG_start'                        :    1,
    'AWG_wait_duration_before_MBI_MW_pulse' :    1e-6,
    'AWG_wait_for_adwin_MBI_duration'       :    15e-6,
    'AWG_wait_duration_before_shelving_pulse':   100e-9,
    'nr_of_ROsequences'                     :    1, #setting this on anything except on 1 crahses the adwin?
    'MW_pulse_mod_risetime'                 :    10e-9,
    'AWG_to_adwin_ttl_trigger_duration'     :    5e-6,
    'max_MBI_attempts'                      :    1,
    'N_randomize_duration'                  :    50,
    'Ex_N_randomize_amplitude'              :    20e-9,
    'A_N_randomize_amplitude'               :    20e-9,
    'repump_N_randomize_amplitude'          :    20e-9}


cfg['protocols']['AdwinSSRO+PQ'] = {
        'MAX_DATA_LEN':                             int(100e6),
        'BINSIZE':                                  1, #2**BINSIZE*BASERESOLUTION
        'MIN_SYNC_BIN':                             0,
        'MAX_SYNC_BIN':                             1000,
        'TTTR_read_count':                          1000, 
        'measurement_time':                         1200,#sec
        'measurement_abort_check_interval':         1#sec

        }



####################################################
### NV and field parameters for a general sample ###
####################################################

f_msm1_cntr = 2.807745e9#2.807214e9 #2014-07-15- SIL1            #Electron spin ms=-1 frquency
f_msp1_cntr = 3.753180e9            #Electron spin ms=+1 frequency

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.19e6        #calibrated 20140320/181319
C_split  = 0.847e6 

cfg['samples'][sample_name] = {
    'ms-1_cntr_frq' :       f_msm1_cntr,
    'ms+1_cntr_frq' :       f_msp1_cntr,
    'N_0-1_splitting_ms-1': N_frq,
    'N_HF_frq'      :       N_HF_frq,
    'C_split'       :       C_split}

cfg['protocols'][name]['AdwinSSRO'] = {
    'SSRO_repetitions'  : 5000,
    'SSRO_duration'     :  50,
    'SSRO_stop_after_first_photon' : 0,
    'A_CR_amplitude': 3e-9,#3nW
    'A_RO_amplitude': 0,
    'A_SP_amplitude': 3e-9,
    'CR_duration' :  100,
    'CR_preselect':  1000,
    'CR_probe':      1000,
    'CR_repump':     1000,
    'Ex_CR_amplitude':  2e-9,#5nW
    'Ex_RO_amplitude':  10e-9, #15e-9,
    'Ex_SP_amplitude':  10e-9,
    'SP_duration'        : 100,
    'SP_duration_ms0' : 100,
    'SP_duration_ms1' : 100,
    'SP_filter_duration' : 0 
    }
    

cfg['protocols'][name]['AdwinSSRO-integrated'] = {
    'SSRO_duration' : 30}


CORPSE_frq = 9e6
cfg['protocols'][name]['pulses'] = {
        'CORPSE_rabi_frequency' : CORPSE_frq,
        'CORPSE_amp' : 0.201 , #N.C.
        'CORPSE_pi2_amp':0.770, #N.C.
        'CORPSE_pulse_delay': 0e-9, #N.C.
        'CORPSE_pi_amp': 0.713, #N.C. 
        'Square_pi_amp': 0.9,#N.C.
        'Square_pi_length': 2000e-9,#N.C.
        'Square_pi2_amp': 0.4,#N.C.
        'Square_pi2_length': 15e-9,#N.C.
        'IQ_Square_pi_amp': 0.015,#N.C.
        'IQ_Square_pi2_amp': 0.09,#N.C.
        'Hermite_pi_length': 180e-9,
        'Hermite_pi_amp': 0.452578,#0.455, #0.775, # calib. 2014-07-15
        'Hermite_pi2_length': 90e-9,
        'Hermite_pi2_amp': 0.295318,#0.300, #0.673 calib. 2014-07-11
        'IQ_Hermite_pi_amp': 0.83398,#0.455, #0.775, # calib. 2014-07-15
        'IQ_Hermite_pi2_amp': 0.415623,#0.455, #0.775, # calib. 2014-07-15
        'extra_wait_final_pi2' : -30e-9
        }

