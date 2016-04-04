import numpy as np

cfg={}

sample_name = 'Gretel'
# sil_name = 'sil3'
sil_name = 'sil2'
name=sample_name+'_'+sil_name
cfg['samples'] = {'current':sample_name}
cfg['protocols'] = {'current':name}

cfg['protocols'][name] = {}


cfg['protocols']['The111_no1_SIL1'] = {}
cfg['protocols']['Hans_sil1'] = {}
cfg['protocols']['Gretel_sil3'] = {}
cfg['protocols']['Gretel_sil2'] = {}
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
    'AWG_done_DI_channel'       :       23,
    'AWG_event_jump_DO_channel' :       2,
    'AWG_start_DO_channel'      :       1,
    'counter_channel'           :       1,
    'cycle_duration'            :       300,
    'green_off_amplitude'       :       0.0,
    'green_repump_amplitude'    :       30e-6, # Previously 15e-6
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
    'yellow_repump_amplitude'   :       245e-9,#300e-9 if possible
    'yellow_repump_duration'    :       500,
    'yellow_CR_repump'          :       1,
    'green_CR_repump'           :       1000,
    'CR_probe_max_time'         :       1000000,
    'SSRO_stop_after_first_photon': 0,}

cfg['protocols']['AdwinSSRO']['cr_mod'] = False
cfg['protocols']['cr_mod']={
    'cr_mod_control_offset'     :   0.0,
    'cr_mod_control_amp'        :   0.05, #V
    'repump_mod_control_amp'    :   .5, #V
    'repump_mod_DAC_channel'    :0,
    'cr_mod_DAC_channel'    :0,
    'repump_mod_control_offset'    :0,

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

mw_frq = 2.78e9
mw_power = 20 
cfg['protocols']['AdwinSSRO+espin'] = {
        'mw_frq'                :     mw_frq, 
        'mw_power'              :     mw_power,
        'MW_switch_risetime'    :     500.00e-9, # Taken from LT2 msmt params (KvB 26-5-2015)
        'send_AWG_start'        :     1,
        'MW_pulse_mod_risetime' :     10e-9,
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
    'Ex_N_randomize_amplitude'              :    4e-9,
    'A_N_randomize_amplitude'               :    4e-9,
    'repump_N_randomize_amplitude'          :    4e-9,
    
    }


cfg['protocols']['AdwinSSRO+PQ'] = {
        'MAX_DATA_LEN':                             int(100e6),
        'BINSIZE':                                  1, #2**BINSIZE*BASERESOLUTION
        'MIN_SYNC_BIN':                             0,
        'MAX_SYNC_BIN':                             1000,
        'TTTR_read_count':                          1000, 
        'measurement_time':                         1200,#sec
        'measurement_abort_check_interval':         1,#sec
        'pq_sync_length':                           75e-9,
        'time_between_syncs':                       50e-9,
        'syncs_per_sweep':                          2,
        'summed_binsize':                           250,
        'RO_start':                                 700,#ns
        'RO_stop':                                  700+2110, # in ns, should be start of RO + integration time
        'do_spatial_optimize':                      False,
        }

cfg['protocols']['GreenRO+PQ'] = {
        'sync_counter_idx':4,   # counter channel on ADwin that recieves pulse from AWG everytime a sync is sent to PQ, to compare sync nr's
        }
cfg['protocols']['Magnetometry']={
'ch1'                                   :   7,
'ch2'                                   :   8,
'ch3'                                   :   9,
'ch4'                                   :   10,
'ch5'                                   :   11,
'ch6'                                   :   12,
'ch7'                                   :   13,
'ch8'                                   :   14,
'AWG_to_adwin_ttl_trigger_duration'     :   5e-6,
'threshold_majority_vote'               :   1}
####################################################
### NV and field parameters for a general sample ###
####################################################

# NOTE: F_MSM1_CNTR = SIL 2!!!
f_msm1_cntr = (2.814333) *1e9#2.816464e9 #2.817393e9 #2.81558e9#2.817419e9#2.84628e9#2.845609e9#2.848291e9#2.847321e9 #2.845634e9 # 2.845256e9#2014-07-17- SIL1            #Electron spin ms=-1 frquency
f_msp1_cntr = 2.941343e9#2.926302e9#3.753180e9            #Electron spin ms=+1 frequency

zero_field_splitting = 2.877336e9
N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.189e6 # from FM calibration msmnts#2.189e6        #calibrated 20140918/202617 # for Gretel
C_split  = 0.847e6 

cfg['samples'][sample_name] = {
    'ms-1_cntr_frq' :       f_msm1_cntr,
    'ms+1_cntr_frq' :       f_msp1_cntr,
    'N_0-1_splitting_ms-1': N_frq,
    'N_HF_frq'      :       N_HF_frq,
    'C_split'       :       C_split,
    'zero_field_splitting': zero_field_splitting,
    'g_factor'      :       2.8025e6, #Hz/Gauss
    'g_factor_C13'  :       1.0705e3, #Hz/Gauss
    'g_factor_N14'  :       0.3077e3, #Hz/Gauss
}





cfg['protocols'][name]['AdwinSSRO'] = {
    'SSRO_repetitions'  : 5000,
    'SSRO_duration'     :  200,
    'SSRO_stop_after_first_photon' : 0,
    'A_CR_amplitude': 7e-9,# 13 nW #8nW
    'A_RO_amplitude': 0,
    'A_SP_amplitude': 20e-9,#20e-9, # Previously 20
    'CR_duration' :  250,
    'CR_preselect':  1000,
    'CR_probe':      1000,
    'CR_repump':     1000,
    'Ex_CR_amplitude':  0.75e-9,#2.5e-9,#2.5e-9,#1nW
    'Ex_RO_amplitude':  0.5e-9, #15e-9,
    'Ex_SP_amplitude':  0.4e-9,
    'SP_duration'        : 300, # was 300 with proper alignment of NewFocus
    'SP_duration_ms0' : 300,
    'SP_duration_ms1' : 300,
    'SP_filter_duration' : 0 
    }
    

cfg['protocols'][name]['AdwinSSRO-integrated'] = {
    'SSRO_duration' : 50,
    'Ex_SP_amplitude':  0e-9,}


MBI_duration = 10
cfg['protocols'][name]['AdwinSSRO+MBI'] ={
    #Spin pump before MBI
'Ex_SP_amplitude'           :           0.3e-9,
'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet
'SP_E_duration'             :           300,     #Duration for both Ex and A spin pumping

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           0e-9,#NOTE 
'MBI_duration'              :           MBI_duration,
#'AWG_wait_for_adwin_MBI_duration': (4+10)*1e-6,

#    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [300],   # repump duration + 4 us should always be larger than AWG MBI element duration
'repump_after_MBI_A_amplitude':         [20e-9],#5nW NOTE
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI parameters
'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
'MBI_threshold'             :           0,
'AWG_wait_for_adwin_MBI_duration':      10e-6+MBI_duration*1e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          4e-9,

}
cfg['protocols'][name]['AdwinSSRO+C13'] = {

#C13-MBI  
'C13_MBI_threshold_list':               [1],
'C13_MBI_RO_duration':                  40,  
'E_C13_MBI_RO_amplitude':               0.5e-9, #this was 0.3e-9 NK 20150316
'SP_duration_after_C13':                10, #300 in case of swap init! 
'A_SP_amplitude_after_C13_MBI':         0*10e-9, # was 15e-9
'E_SP_amplitude_after_C13_MBI':         0e-9,
'C13_MBI_RO_state':                     0, # 0 sets the C13 MBI success condition to ms=0 (> 0 counts), if 1 to ms = +/-1 (no counts)
                
#C13-MBE  
'MBE_threshold':                        1,
'MBE_RO_duration':                      40, # was 40 20150329
'E_MBE_RO_amplitude':                   0.5e-9, #this was 0.35e-9 NK 20150316
'SP_duration_after_MBE':                30,
'A_SP_amplitude_after_MBE':             0*10e-9,
'E_SP_amplitude_after_MBE':             0e-9 ,

#C13-parity msmnts
'Parity_threshold':                     1,
'Parity_RO_duration':                   108,
'E_Parity_RO_amplitude':                0.3e-9,

#Shutter
'use_shutter':                          0, 
'Shutter_channel':                      4, 
'Shutter_rise_time':                    2500,    
'Shutter_fall_time':                    2500,
'Shutter_safety_time':                  50000, #Sets the time after each msmts, the ADwin waits for next msmt to protect shutter (max freq is 20Hz)

'min_phase_correct'   : 2,      # minimum phase difference that is corrected for by phase gates
'min_dec_tau'         : 20e-9 + 140e-9,#140e-9 = fast_pi_duration (check pulselib below)
'max_dec_tau'         : 2.4e-6,#2.5e-6,#Based on measurement for fingerprint at low tau
'dec_pulse_multiple'  : 4      #4. 


}

###########
# is this still used?
###########
'''
CORPSE_frq = 9e6
cfg['protocols'][name]['pulses'] = {
        'CORPSE_rabi_frequency' : CORPSE_frq,
        'CORPSE_amp' : 0.201 , #N.C.
        'CORPSE_pi2_amp':0.770, #N.C.
        'CORPSE_pulse_delay': 0e-9, #N.C.
        'CORPSE_pi_amp': 0.713, #N.C. 
        'Square_pi_amp': 0.406,# calib. 2014-07-17
        'Square_pi_length': 40e-9,# calib. 2014-07-17
        'Square_pi2_amp': 0.412,# calib 2014-07-17
        'Square_pi2_length': 20e-9,# calib. 2014-07-17
        'IQ_Square_pi_amp': 0.015,#N.C.
        'IQ_Square_pi2_amp': 0.09,#N.C.
        'Hermite_pi_length': 180e-9, 
        'Hermite_pi_amp': 0.42018, #0.4645, # calib. 2014-07-24
        'Hermite_pi2_length': 90e-9,
        'Hermite_pi2_amp': 0.273,# 0.304276,# calib. 2014-07-24
        'IQ_Hermite_pi_amp': 0.83398,#0.455, #0.775, # calib. 2014-07-15
        'IQ_Hermite_pi2_amp': 0.415623,#0.455, #0.775, # calib. 2014-07-15
        'extra_wait_final_pi2' : -30e-9
        }
'''






######################
#### SIL 2 ##########
######################



##### Pulses#######

f_mod_0= 0 * 250e6#31e6


# NOTE: ONLY FAST PI/2 PULSE (SQUARE) NOT CALIBRATED YET!!
Hermite_fast_pi_duration   =  140e-9#137e-9#140e-9 
Hermite_fast_pi_amp        =  0.2261#0.226#0.5735#0.218#0.202, #0.122140
Hermite_fast_Xpi_amp        =  0.257#0.256
Hermite_fast_pi_mod_frq    =  f_mod_0
Hermite_fast_pi2_duration  =  72e-9
Hermite_fast_pi2_amp       =  0.191#0.1794#0.184566 #0.092117
Hermite_fast_pi2_mod_frq   =  f_mod_0 # NOTE: Hermite Pi pulse calibrated for 0 mod freq


cfg['protocols']['Gretel_sil2']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'mw_power'      : 20,
'Square_pi2_amp': 0.6,
'Square_pi2_length': 1.219e-6,
'RO_stop':          700+1940,
'GreenAOM_pulse_length':3e-6,

'X_phase'                   :   90,
'Y_phase'                   :   0,

# 'C13_X_phase' :0,
# 'C13_Y_phase' :90,

'C13_X_phase' :0,
'C13_Y_phase' :270,

'MW_pulse_mod_frequency' : f_mod_0,
'mw_mod_freq' : f_mod_0,

'MW_switch_risetime'    :   500e-9,
'MW_switch_channel'     :   'None', ### if you want to activate the switch, put to MW_switch

############
#Pulse type
###########
'pulse_shape': 'Hermite',
# 'pulse_shape': 'Square',

'Hermite_pi_length'          :  Hermite_fast_pi_duration,#140e-9 # @ 100 MHz,    #250 MHz slow
'Hermite_pi_amp'               :  Hermite_fast_pi_amp, 
'Hermite_fast_Xpi_amp'               :  Hermite_fast_Xpi_amp, 
'Hermite_fast_pi_mod_frq'           :  Hermite_fast_pi_mod_frq,

'Hermite_pi2_length'         :  Hermite_fast_pi2_duration, 
'Hermite_pi2_amp'              :  Hermite_fast_pi2_amp,
'Hermite_fast_pi2_mod_frq'          :  Hermite_fast_pi2_mod_frq, 


'fast_pi_duration'          :  115e-9,#Hermite_fast_pi_duration,
'fast_pi_amp'               :  0.14,#Hermite_fast_pi_amp, 
'fast_pi_mod_frq'           :  0,#Hermite_fast_pi_mod_frq,

    ### Pi/2 pulses, fast & hard 
# 'fast_pi2_duration'         :   32e-9, #should be divisible by 4
'fast_pi2_duration'         :   Hermite_fast_pi2_duration,
'fast_pi2_amp'              :   Hermite_fast_pi2_amp, 
'fast_pi2_mod_frq'          :   Hermite_fast_pi2_mod_frq,
    
    ### DESR pulses ###
'desr_pulse_duration'       :   0.5*2.e-6,#2*2*3.956e-6,#(2.262e-6)/4.,
'desr_pulse_amp'            :   2*0.0154,#0024 for ms+1
'desr_modulation_frequency' : 40e6,
'desr_MW_power'             : 5,#-12,

    ### MBI pulses ###
'AWG_MBI_MW_pulse_mod_frq'  :   f_mod_0,
'AWG_MBI_MW_pulse_ssbmod_frq':  f_mod_0,
'AWG_MBI_MW_pulse_amp'      :   0.017,  #0.01353*1.122  <-- pre-switch era  ## f_mod = 250e6 (msm1)
# 'AWG_MBI_MW_pulse_amp'      :   0.01705,#0.0075,     ## f_mod = 125e6 (msm1)
'AWG_MBI_MW_pulse_duration' :   2500e-9,


### dummy params for second MW source
'mw2_Hermite_pi_length' : 10e-9,
'mw2_Hermite_pi2_length' : 10e-9,
}

###########################################
### Gretel SIL2: nuclear spin params ###
###########################################
cfg['samples']['Gretel_sil2'] ={


#XXXXX
### dummy parameters for purification testing. delete when done.
# 'electron_transition' : '_m1',
# 'C1_freq_m1'       :   440e3,#24.618e3,
# 'C1_freq_1_m1' : 460e3,#24.543e3, 
# 'C1_Ren_tau_m1'    :   [10e-6],#[30.652e-6],#[30.632e-6],#39.424e-6
# 'C1_Ren_N_m1'      :   [4],#[164],#[184],#132
# 'Carbon_LDE_phase_correction_list' : np.array([0]*10),
# 'C1_Ren_extra_phase_correction_list_m1' : np.array([-75] * 10),

#C13-params

'C1_freq'       :   24.618e3, 
'C1_freq_0' : 24.338e3, 
'C1_freq_1' : 24.543e3, 
'C1_Ren_tau'    :   [30.652e-6],#[30.632e-6],#39.424e-6
'C1_Ren_N'      :   [164],#[184],#132
'C1_Ren_extra_phase_correction_list' : np.array([-75] * 10),
'C1_gate_optimize_tau_list' : [30.644e-6,30.652e-6,30.660e-6,30.668e-6,30.676e-6],#[30.668e-6]*5,
'C1_gate_optimize_N_list': [164]*5,

'C2_freq'       :   0*450.301e3, # not yet measured
'C2_freq_0' : 0*431932.22,# not yet measured
'C2_freq_1' : 0*469009.46,# not yet measured
'C2_Ren_tau'    :   [31.440e-6],# NOTE: coarse calibration 2015-08-05
'C2_Ren_N'      :   [300], # NOTE: coarse calibration 2015-08-05
'C2_Ren_extra_phase_correction_list' : np.array([0] * 10),

########
##no C3 defined yet for gretel
'C3_freq'       :   450.301e3,
'C3_freq_0' : 431932.22,
'C3_freq_1' : 469009.46,
'C3_Ren_tau'    :   [11.976E-6],
'C3_Ren_N'      :   [176/4], # NOTE: period actually 174 pulses 
'C3_Ren_extra_phase_correction_list' : np.array([0] * 10)
}




















































######################
#### SIL 1 ##########
######################

f_mod_0=31e6
#f_msm1_cntr = 2.838037e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil1']={}
cfg['protocols']['Gretel_sil1']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.01125,
'Square_pi2_length': 1.219e-6,
'RO_stop':          700+780,
'GreenAOM_pulse_length':2e-6,
}
######################
#### SIL 3 ##########
######################

f_mod_0 = 0 * 250e6
#f_msm1_cntr = 2.845266e9#2.838096e9         #Electron spin ms=-1 frquency, previously (30-01-2015) 2.838056
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED

### center frequencies:
# f_msm1_cntr = 2.817524e9
# f_msp1_cntr = 2.93744e9

# NOTE 24-04-2015: 
# DynamicalDecoupling class has hardcoded pulse durations using the
# keys of the square pulses ('fast_pi_duration', etc.).
# Because SIL3 currently uses HERMITE PULSES, the square pulse keys are now overwritten 
# using the Hermite pulse values

Hermite_fast_pi_duration   =  140e-9 
Hermite_fast_pi_amp        =  0.136 
Hermite_fast_pi_mod_frq    =  f_mod_0
Hermite_fast_pi2_duration  =  70e-9
Hermite_fast_pi2_amp       =  0.10
Hermite_fast_pi2_mod_frq   =  f_mod_0 # NOTE: Hermite Pi pulse calibrated for 0 mod freq





cfg['protocols']['Gretel_sil3']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'mw_power'      : 20,
'Square_pi2_amp': 0.6,
'Square_pi2_length': 1.219e-6,
'RO_stop':          700+1940,
'GreenAOM_pulse_length':3e-6,
'MW_modulation_frequency'   :   f_mod_0,

'X_phase'                   :   90,
'Y_phase'                   :   0,

# 'C13_X_phase' :0,
# 'C13_Y_phase' :90,

'C13_X_phase' :0,
'C13_Y_phase' :270,

'MW_pulse_mod_frequency' : f_mod_0,

############
#Pulse type
###########
'pulse_shape': 'Hermite',

############
#SQUARE pulses
###########



# #     ### Pi pulses, fast & hard 
# 'fast_pi_duration'          :  44e-9,# Previous value on 23-04-205: 200e-9,    #250 MHz slow
# 'fast_pi_amp'               :  0.45,#  Previous value on 23-04-2015: 0.45,  #250 MHz, slow
# 'fast_pi_mod_frq'           :   f_mod_0,

#     ### Pi/2 pulses, fast & hard 
# # 'fast_pi2_duration'         :   32e-9, #should be divisible by 4
# 'fast_pi2_duration'         :   24e-9,#56e-9, #should be divisible by 4, slow
# 'fast_pi2_amp'              :   0.49, # slow, only calibrated with 2 pulses
# 'fast_pi2_mod_frq'          :   f_mod_0,


############
#Hermite pulses
###########
# #     ### Pi pulses, fast & hard 


# Calibrated values for Hermite pulses:
# 1) mod_fr1 = 100 MHz:
# Hermite_fast_pi_duration = 140e-9
# Hermite_fast_pi_amp = 0.196
# RESULTING PI-PULSE FIDELITY: 0.98-0.99
# 2) mod_frq = 250 MHz:
# Hermite_fast_pi_duration = 160e-9
# Hermite_fast_pi_amp = 0.2646
# RESULTING PI-PULSE FIDELITY: 0.95
# 3) mod_frq = 0 MHz
# Hermite_fast_pi_duration = 140e-9
# Hermite_fast_pi_amp = 0.136
# RESULTING PI-PULSE FIDELITY: 0.994


'Hermite_fast_pi_duration'          :  Hermite_fast_pi_duration,#140e-9 # @ 100 MHz,    #250 MHz slow
'Hermite_fast_pi_amp'               :  Hermite_fast_pi_amp, 
'Hermite_fast_pi_mod_frq'           :  Hermite_fast_pi_mod_frq,

'Hermite_fast_pi2_duration'         :  Hermite_fast_pi2_duration, 
'Hermite_fast_pi2_amp'              :  Hermite_fast_pi2_amp,
'Hermite_fast_pi2_mod_frq'          :  Hermite_fast_pi2_mod_frq, 


'fast_pi_duration'          :  Hermite_fast_pi_duration,
'fast_pi_amp'               :  Hermite_fast_pi_amp, 
'fast_pi_mod_frq'           :  Hermite_fast_pi_mod_frq,

    ### Pi/2 pulses, fast & hard 
# 'fast_pi2_duration'         :   32e-9, #should be divisible by 4
'fast_pi2_duration'         :   Hermite_fast_pi2_duration,
'fast_pi2_amp'              :   Hermite_fast_pi2_amp, 
'fast_pi2_mod_frq'          :   Hermite_fast_pi2_mod_frq,


    ### MBI pulses ###
'AWG_MBI_MW_pulse_mod_frq'  :   f_mod_0,
'AWG_MBI_MW_pulse_ssbmod_frq':  f_mod_0,
'AWG_MBI_MW_pulse_amp'      :   0.017,  #0.01353*1.122  <-- pre-switch era  ## f_mod = 250e6 (msm1)
# 'AWG_MBI_MW_pulse_amp'      :   0.01705,#0.0075,     ## f_mod = 125e6 (msm1)
'AWG_MBI_MW_pulse_duration' :   2500e-9}



'''
cfg['protocols']['Gretel_sil3']['AdwinSSRO+MBI'] ={
    #Spin pump before MBI
'Ex_SP_amplitude'           :           0.1e-9,
'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet
'SP_E_duration'             :           300,     #Duration for both Ex and A spin pumping

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           0e-9,#NOTE 
'MBI_duration'              :           MBI_duration,
#'AWG_wait_for_adwin_MBI_duration': (4+10)*1e-6,

#    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [300],   # repump duration + 4 us should always be larger than AWG MBI element duration
'repump_after_MBI_A_amplitude':         [5e-9],#5nW NOTE
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI parameters
'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
'MBI_threshold'             :           0,
'AWG_wait_for_adwin_MBI_duration':      10e-6+MBI_duration*1e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          4e-9,

}
'''
# NOTE (18-05-2015): COPIED & PASTED the AdwinSSRO+MBI data from SIL3 for SIL2



######################
#### SIL 4 ##########
######################

f_mod_0=31e6
f_msm1_cntr = 2.837845e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil4']={}
cfg['protocols']['Gretel_sil4']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.011,
'Square_pi2_length': 0.853e-6,
'RO_stop':          700+1100,
'GreenAOM_pulse_length':2e-6,
}

######################
#### SIL 6 ##########
######################

f_mod_0=31e6
f_msm1_cntr = 2.838015e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil6']={}
cfg['protocols']['Gretel_sil6']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.05/2.,
'Square_pi2_length': 0.806e-6,
'RO_stop':          700+2100,
'GreenAOM_pulse_length': 3e-6
}

######################
#### SIL 10 ##########
######################
f_mod_0=31e6
f_msm1_cntr = 2.843440e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil10']={}
cfg['protocols']['Gretel_sil10']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.04,
'Square_pi2_length': 0.932e-6,
'RO_stop':          700+990,
'GreenAOM_pulse_length': 3e-6
}


######################
#### SIL 11 ##########
######################
f_mod_0=31e6
f_msm1_cntr = 2.843348e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil11']={}
cfg['protocols']['Gretel_sil11']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.02,
'Square_pi2_length': 1.25e-6,
'RO_stop':          700+620,
'GreenAOM_pulse_length': 3e-6
}

######################
#### SIL 12 ##########
######################
f_mod_0=31e6
f_msm1_cntr = 2.843296e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil12']={}
cfg['protocols']['Gretel_sil12']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.0133,
'Square_pi2_length': 1.381e-6,
'RO_stop':          700+520,
'GreenAOM_pulse_length': 3e-6
}

######################
#### SIL 16 ##########
######################
f_mod_0=31e6
f_msm1_cntr = 2.837778e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil16']={}
cfg['protocols']['Gretel_sil16']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.02,
'Square_pi2_length': 1.096e-6,
'RO_stop':          700+1730,
'GreenAOM_pulse_length': 3e-6
}

######################
#### SIL 17 ##########
######################
f_mod_0=31e6
f_msm1_cntr = 2.838088e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil17']={}
cfg['protocols']['Gretel_sil17']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.03,
'Square_pi2_length': 1.005e-6,
'RO_stop':          700+1490,
'GreenAOM_pulse_length': 3e-6
}


######################
#### SIL 20 ##########
######################
f_mod_0=31e6
f_msm1_cntr = 2.837888e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil20']={}
cfg['protocols']['Gretel_sil20']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,
'mw_frq'        :      f_msm1_cntr - f_mod_0,#-N_HF_frq,
'Square_pi2_amp': 0.03,
'Square_pi2_length': 1.005e-6,
'RO_stop':          700+1270,
'GreenAOM_pulse_length': 3e-6
}




######################
#### SIL 10 ##########
######################

MBI_duration = 70

cfg['protocols']['Gretel_sil10']['AdwinSSRO+MBI'] ={
    #Spin pump before MBI
'Ex_SP_amplitude'           :           6.5e-9,
'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet
'SP_E_duration'             :           300,     #Duration for both Ex and A spin pumping

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           0.1e-9,#NOTE 
'MBI_duration'              :           MBI_duration,
#'AWG_wait_for_adwin_MBI_duration': (4+10)*1e-6,

#    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [50],   # repump duration + 4 us should always be larger than AWG MBI element duration
'repump_after_MBI_A_amplitude':         [5e-9],#5nW NOTE
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI parameters
'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
'MBI_threshold'             :           0,
'AWG_wait_for_adwin_MBI_duration':      10e-6+MBI_duration*1e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          4e-9,

}

CORPSE_frq=  6.8e6
MW_mod_magnetometry=31.234e6
f_msm1_cntr = 0.292e6+2.845e9         #Electron spin ms=-1 frquency
f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil10']['Magnetometry'] ={
'MW_modulation_frequency'   :   MW_mod_magnetometry,
'mw_frq'        :      f_msm1_cntr - MW_mod_magnetometry,#-N_HF_frq,
'FM_sensitivity':       ((((2.5e6*2*600/650.)/(2.012/2.188))/(2.191/2.189))/(2.190/2.189))/(2.197/2.189)/(2.193/2.189), # Hz/V, set manually in SMB; factor 2 is because of AWG output, 600/650 is to impedance match the MOD ext of SMB wrt AWG output (50ohm)
'FM_delay'      :       40e-6,
'mw_power'      :       7,
'ms-1_cntr_frq':       f_msm1_cntr,
'ms+1_cntr_frq':       f_msp1_cntr,
'ms+1_mod_frq':        f_msp1_cntr-f_msm1_cntr + MW_mod_magnetometry, 
### Laser duration and powers etc ###

'SSRO_duration'     :  40.,
'CR_duration'       : 120,
'Ex_RO_amplitude': 3e-9,
'A_CR_amplitude': 8e-9,
'Ex_CR_amplitude': 5e-9,
'A_SP_amplitude': 25e-9, #NOte: set back to 30nW?
'A_SP_repump_amplitude':.5e-9,
'SP_duration': 200, #!!!! 10
'SP_repump_duration': 100,
'SP_duration_ms0': 50,
'SP_duration_ms1':300,

'wait_after_RO_pulse_duration':2,
'wait_after_pulse_duration':2,
'A_SP_repump_voltage':0.3, # bit of a detour to avoid putting this variable in ssro.autoconfig.

'SSRO_stop_after_first_photon':0,

### Corpse pulses ###
'CORPSE_pi2_amp'    :           .9,
'CORPSE_frq'  :  CORPSE_frq,
'CORPSE_pi_60_duration' :  1./CORPSE_frq/6.,
'CORPSE_pi_m300_duration': 5./CORPSE_frq/6.,
'CORPSE_pi_420_duration':  7./CORPSE_frq/6.,
'CORPSE_pi2_24p3_duration': 24.3/CORPSE_frq/360.,
'CORPSE_pi2_m318p6_duration': 318.6/CORPSE_frq/360.,
'CORPSE_pi2_384p3_duration':  384.3/CORPSE_frq/360.,

# For nitrogen initialization
'N_0-1_splitting_ms-1': 7.13429e6,
'init_repetitions':1,
'AWG_MBI_MW_pulse_mod_frq'  :   MW_mod_magnetometry+1*N_HF_frq,#conventional MBI init line (?)
'AWG_MBI_MW_pulse_ssbmod_frq':  MW_mod_magnetometry+1*N_HF_frq,#conventional MBI init line 
'AWG_MBI_MW_pulse_amp'      :   0.008, #NOTE!
'AWG_MBI_MW_pulse_duration' :   10788e-9,# NOTE!

#MBI readout power and duration

#RO on ms=0, +1
'MW_pi_msp1_amp': 0.2,
'MW_pi_msp1_dur': 40e-9,

#'pi2pi_mI0_mod_frq':MW_mod_magnetometry,#+N_HF_frq,
'MW_pi_msp1_dur': 40e-9,
'MW_pi_msp1_amp': 0.2,
'pi2pi_mIm1_amp':0.180,
'pi2pi_mIp1_amp':0.168,
'pi2pi_mI0_amp':0.1755,
'pi2pi_mI0_duration':394e-9,
'MW_pi_pulse_amp': 0.02,
'MW_pi2_pulse_amp': 0.02,
'AWG_pi2_duration': 1812e-9,
'fpga_pi2_duration': 1812e-9,
'fpga_phase_offset': 90-15,
}
