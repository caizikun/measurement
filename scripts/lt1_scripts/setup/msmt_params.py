
cfg={}

sample_name = 'Gretel'
sil_name = 'sil1'
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
    'AWG_done_DI_channel'       :       23,
    'AWG_event_jump_DO_channel' :       2,
    'AWG_start_DO_channel'      :       1,
    'counter_channel'           :       1,
    'cycle_duration'            :       300,
    'green_off_amplitude'       :       0.0,
    'green_repump_amplitude'    :       5e-6,
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
    'Ex_N_randomize_amplitude'              :    4e-9,
    'A_N_randomize_amplitude'               :    4e-9,
    'repump_N_randomize_amplitude'          :    4e-9}


cfg['protocols']['AdwinSSRO+PQ'] = {
        'MAX_DATA_LEN':                             int(100e6),
        'BINSIZE':                                  1, #2**BINSIZE*BASERESOLUTION
        'MIN_SYNC_BIN':                             0,
        'MAX_SYNC_BIN':                             1000,
        'TTTR_read_count':                          1000, 
        'measurement_time':                         1200,#sec
        'measurement_abort_check_interval':         1#sec

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

f_msm1_cntr = 2.8078e9#2014-07-17- SIL1            #Electron spin ms=-1 frquency
f_msp1_cntr = 3.753180e9            #Electron spin ms=+1 frequency

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.189e6 # from FM calibration msmnts#2.189e6        #calibrated 20140918/202617 # for Gretel
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
    'A_CR_amplitude': 5e-9,#3nW
    'A_RO_amplitude': 0,
    'A_SP_amplitude': 20e-9,
    'CR_duration' :  1,
    'CR_preselect':  1000,
    'CR_probe':      1000,
    'CR_repump':     1000,
    'Ex_CR_amplitude':  3e-9,#5nW
    'Ex_RO_amplitude':  2e-9, #15e-9,
    'Ex_SP_amplitude':  5e-9,
    'SP_duration'        : 1,
    'SP_duration_ms0' : 1,
    'SP_duration_ms1' : 1,
    'SP_filter_duration' : 0 
    }
    

cfg['protocols'][name]['AdwinSSRO-integrated'] = {
    'SSRO_duration' : 1}


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







######################
#### SIL 1 ##########
######################

MW_mod_magnetometry=31.234e6
f_msm1_cntr = 2.83796e9         #Electron spin ms=-1 frquency
#f_msp1_cntr = 2.900e9        #NOT CALIBRATED
cfg['protocols']['Gretel_sil1']['pulses'] ={
'MW_modulation_frequency'   :   MW_mod_magnetometry,
'mw_frq'        :      f_msm1_cntr - MW_mod_magnetometry,#-N_HF_frq,

}



######################
#### SIL 10 ##########
######################
'''
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
'''