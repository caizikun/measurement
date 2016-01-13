import numpy as np

cfg={}

#############################
### Set current NV center ###
#############################

cfg['samples']      = {'current':'111_1_sil18'}
cfg['protocols']    = {'current':'111_1_sil18'}

# cfg['samples']      = {'current':'Hans_sil1'}
# cfg['protocols']    = {'current':'Hans_sil1'}

cfg['protocols']['Hans_sil1'] = {}
cfg['protocols']['Hans_sil4'] = {}
cfg['protocols']['111_1_sil18'] = {}

print 'updating msmt params lt2 for {}'.format(cfg['samples']['current'])


###################################
### General settings for magnet ###
###################################

### Assumes a cylindrical magnet
cfg['magnet']={
'nm_per_step'       :   22.68, ## Z-movement, for 18 V and 200 Hz 
'radius'            :   5.,     ## millimeters
'thickness'         :   4.,     ## millimeters
'strength_constant' :   1.3}    ## Tesla

######################################
######################################
### General Settings for Protocols ###
######################################
######################################

    ######################################
    ### General settings for AdwinSSRO ###
    ######################################

cfg['protocols']['AdwinSSRO']={
'AWG_done_DI_channel'       :       16,
'AWG_event_jump_DO_channel' :       6,
'AWG_start_DO_channel'      :       1,
'counter_channel'           :       1,
'cycle_duration'            :       300,
'green_off_amplitude'       :       0.0,
'green_repump_amplitude'    :       12e-6,#40e-6#70#50e-6, #200e-6,
'green_repump_duration'     :       40,#20#10, #50 
'send_AWG_start'            :       0,
'sequence_wait_time'        :       1,
'wait_after_RO_pulse_duration':     3,   
'wait_after_pulse_duration' :       3,      ## Wait time after turning off the lasers (E, A pump, etc)
'cr_wait_after_pulse_duration':     2,
'wait_for_AWG_done'         :       0,
'green_off_voltage'         :       0,
'Ex_off_voltage'            :       0.,
'A_off_voltage'             :       -0.0,
'repump_off_voltage'        :       0,
'yellow_repump_amplitude'   :       60e-9,
'yellow_repump_duration'    :       500,
'yellow_CR_repump'          :       1,
'green_CR_repump'           :       1000,
'CR_probe_max_time'         :       1000000,
'Shutter_channel'           :       4,
'use_shutter'               :       0,
'Shutter_opening_time'  :       3000,
'Shutter_safety_time'   :      200000, ### used for cooling down the sample over time.
}

cfg['protocols']['AdwinSSRO']['cr_mod'] = False
cfg['protocols']['cr_mod'] = {}
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

    ############################################
    ### General settings for AdwinSSRO+espin ###
    ############################################

cfg['protocols']['AdwinSSRO+espin'] = {
'send_AWG_start'        :          1,
'MW_switch_risetime'    :   500e-9, # 500 XXXX
'MW_pulse_mod_risetime' :      10e-9,
'MW2_pulse_mod_risetime' :     20e-9,
'use_shutter'           :          0,
'Shutter_channel'       :          4,
'Shutter_opening_time'  :       3000,
'Shutter_safety_time'   :      200000,
}

    ##########################################
    ### General settings for AdwinSSRO+MBI ###
    ##########################################

### General settings for AdwinSSRO+MBI
cfg['protocols']['AdwinSSRO+MBI'] = {
'send_AWG_start'                        :    1,
'AWG_wait_duration_before_MBI_MW_pulse' :    1e-6,
'AWG_wait_for_adwin_MBI_duration'       :    15e-6,
'AWG_wait_duration_before_shelving_pulse':   100e-9,
'nr_of_ROsequences'                     :    1, #setting this on anything except on 1 crahses the adwin?
'MW_pulse_mod_risetime'                 :    10e-9,
'MW2_pulse_mod_risetime'                :    10e-9,
'MW_switch_risetime'                    :    500e-9, #500e-9  XXXX
'AWG_to_adwin_ttl_trigger_duration'     :    5e-6,
'max_MBI_attempts'                      :    1,
'N_randomize_duration'                  :    50,
'Ex_N_randomize_amplitude'              :    13e-9,#15e-9, #15e-9
'A_N_randomize_amplitude'               :    15e-9,
'repump_N_randomize_amplitude'          :    0e-9} #Green or yellow. Probably should be 0 when using Green

cfg['protocols']['Magnetometry']={
'ch1'                                   :   8,
'ch2'                                   :   9,
'ch3'                                   :   10,
'ch4'                                   :   11,
'ch5'                                   :   12,
'ch6'                                   :   13,
'ch7'                                   :   14,
'ch8'                                   :   15,
'AWG_to_adwin_ttl_trigger_duration'     :   1e-6,
'threshold_majority_vote'               :   1}






######################
### 111 No1 SIL 18 ###
######################

    ##################################################
    ### 111 No1 SIL 18: V and frequency parameters ###
    ##################################################

mw_power  = 20
mw2_power = 20
f_msm1_cntr =   1.746668e9#2.01579e9#1.755020e9            #Electron spin ms=-1 frquency 
f_msp1_cntr =   4.008622e9#3.73636e9#4.002669e9 #3.676464e9             #Electron spin ms=+1 frequency 
                
zero_field_splitting = 2.877623e9   # not calibrated #contains + 2*N_hf
                                 

N_frq    = 7.13429e6      # not calibrated
N_HF_frq = 2.182e6 # was2.196e6       
Q        = 4.938e6        # not calibrated



electron_transition = '-1'

if electron_transition == '-1':
    electron_transition_string = '_m1'
    pulse_shape = 'Hermite' # alternatively 'Hermite', or 'Square'
    if pulse_shape == 'Square':
        mw_mod_frequency = 250e6       #40e6 #250e6    # MW modulation frequency. 250 MHz to ensure phases are consistent between AWG elements
        N_MBI_threshold = 1
    elif pulse_shape == 'Hermite':
        mw_mod_frequency = 0*1e6 
        N_MBI_threshold = 0

    mw_freq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
    mw_freq_MBI = f_msm1_cntr - mw_mod_frequency - N_HF_frq    # Initialized frequency
    AWG_MBI_MW_pulse_amp = 0.00824 #0.01525
    
    Hermite_pi_length = 160e-9    
    Hermite_pi_amp = 0.487 #0.481 #for 150 ns

    Hermite_pi2_length = 65e-9#56e-9 # divsible by 2
    Hermite_pi2_amp = 0.501

    Square_pi_length = 116e-9   #250 MHz slow
    Square_pi_amp = 0.231503  #0.407630#0.385# 0.3875#0.406614#0.406614  #250 MHz, slow

    Square_pi2_length = 56e-9 #should be divisible by 4, slow
    Square_pi2_amp =  0.242622    #0.493036,

    BB1_pi_length = 150e-9
    BB1_pi_amplitude = 0.955

# # For ms = +1
elif electron_transition == '+1':
    electron_transition_string = '_p1'
    pulse_shape = 'Hermite' # alternatively 'Hermite', or 'Square'
    if pulse_shape == 'Square':
        mw_mod_frequency = 0       #40e6 #250e6    # MW modulation frequency. 250 MHz to ensure phases are consistent between AWG elements
        N_MBI_threshold = 1
    elif pulse_shape == 'Hermite':
        mw_mod_frequency = 0*1e6 
        N_MBI_threshold = 0

    mw_freq             = f_msp1_cntr - mw_mod_frequency                # Center frequency
    mw_freq_MBI         = f_msp1_cntr - mw_mod_frequency# - N_HF_frq    # Initialized frequency
    AWG_MBI_MW_pulse_amp = 0.03

    Hermite_pi_length = 220e-9
    Hermite_pi_amp = 0.92

    Hermite_pi2_length = 220e-9#56e-9, #should be divisible by 4, slow
    Hermite_pi2_amp = 0.678533   

    Square_pi_length = 60e-9 #180e-9   #250 MHz slow
    Square_pi_amp =  0.7 #0.694552  #0.407225 #without switch #0.469424,with switch  #250 MHz, slow

    Square_pi2_length = 92e-9 #56e-9, #should be divisible by 4, slow
    Square_pi2_amp =  0.738335 #0.493036, # slow, only calibrated with 2 pulses

    BB1_pi_length = 50e-9
    BB1_pi_amplitude = 0.9




print '*****************************************************'
print ' pulse shape is ' + pulse_shape +' and MBI_threshold is '+str(N_MBI_threshold) + ' and el transition is ' + electron_transition
print '*****************************************************'



##   Second microwave source
### Comment: frequency should be selected automatically depending on source 1...

mw2_freq             = f_msp1_cntr   # Center frequency
mw2_pulse_shape = 'Hermite'

if mw2_freq == f_msm1_cntr:
    mw2_Hermite_pi_length = 90e-9    
    mw2_Hermite_pi_amp = 0.414
    mw2_Hermite_pi2_length = 70e-9
    mw2_Hermite_pi2_amp = .5  
    mw2_Square_pi2_amp =  .5
    mw2_Square_pi_amp =  .414
    mw2_Square_pi_length = 90e-9#180e-9   #250 MHz slow
    mw2_Square_pi2_length = 11e-9#180e-9   #250 MHz slow
    mw2_electron_transition_string = '_m1'
else:
    mw2_Hermite_pi_length = 160e-9    
    mw2_Hermite_pi_amp = 0.616
    mw2_Hermite_pi2_length = 70e-9
    mw2_Hermite_pi2_amp = .5  
    mw2_Square_pi2_amp =  .5
    mw2_Square_pi_amp =  .616
    mw2_Square_pi_length = 160e-9#180e-9   #250 MHz slow
    mw2_Square_pi2_length = 28e-9#180e-9   #250 MHz slow
    mw2_electron_transition_string = '_p1'

cfg['samples']['111_1_sil18'] = {
'electron_transition' : electron_transition_string,
'mw_mod_freq'   :       mw_mod_frequency,
'mw_frq'        :       mw_freq_MBI, # this is automatically changed to mw_freq if hermites are selected.
'mw2_frq'        :      mw2_freq,
'mw_power'      :       mw_power,
'mw2_power'      :      mw2_power,
'ms-1_cntr_frq' :       f_msm1_cntr,
'ms+1_cntr_frq' :       f_msp1_cntr,
'zero_field_splitting': zero_field_splitting,
'Q_splitting'   :       Q,
'g_factor'      :       2.8025e6, #Hz/Gauss
'g_factor_C13'  :       1.0705e3, #Hz/Gauss
'g_factor_N14'  :       0.3077e3, #Hz/Gauss
'N_0-1_splitting_ms-1': N_frq,
'N_HF_frq'      :       N_HF_frq,

    ###########################################
    ### 111 No1 Sil 18: nuclear spin params ###
    ###########################################
'Carbon_LDE_phase_correction_list'      : np.array([0.0]*10),#np.array([0.0] + [16.4] + [17.4] + [17.3] + [0.0] + [17.5] + [16.7] + [0.0] + [0.0] + [0.0]),
'Carbon_LDE_init_phase_correction_list' : np.array([0.0]*10),#np.array([0.0] + [-26.5] + [-143.6] + [-45.3] + [0.0] + [-60.9] + [-91.2] + [0.0] + [0.0] + [0.0]),
    ################
    ### Carbon 1 ###
    ################


'C1_freq_m1'        :  450166.28,##+-104.6 #450301.0, 
'C1_freq_0' : 432027.63,
'C1_freq_1_m1' : 469076.2,
# 'C1_gate_optimize_tau_list_m1' : [4.994e-6,4.994e-6,4.994e-6,4.996e-6,4.996e-6,
#                                4.996e-6,4.998e-6,4.998e-6,4.998e-6],

'C1_gate_optimize_tau_list_m1' : [7.218e-6,4.994e-6,4.994e-6,4.996e-6,4.996e-6,
                               4.996e-6,4.998e-6,4.998e-6,7.214e-6],

# 'C1_gate_optimize_N_list_m1': [32,34,36,32,34,36,34,36,38],
'C1_gate_optimize_N_list_m1': [40,34,36,32,34,36,34,36,42],


# 'C1_Ren_tau'    :   [4.994e-6],
# 'C1_Ren_N'      :   [34],
# 'C1_Ren_extra_phase_correction_list' :  np.array([0] + [-15.28] + [42.26]+[0]*2+[63.88]+ 4*[0]),

# 'C1_Ren_tau'    :   [4.998e-6],
# 'C1_Ren_N'      :   [34],
# 'C1_Ren_extra_phase_correction_list' :  np.array([0] + [54.9] + [26.3]+[0]*2+[61.7]+ 4*[0]),

'C1_Ren_tau_m1'    :   [4.996e-6],
'C1_Ren_N_m1'      :   [36],
'C1_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [32.1] + [106.05] + [8.26] + [0.0] + [36.11] + [-4.49] + [0.0] + [0.0] + [0.0]),

    ################
    ### Carbon 2 ###
    ################

'C2_freq_m1'       :  421891.91,## +-81.2 #421.814e3,  #XXXXXXXXXXXXX
'C2_freq_0' : 431978.19,
'C2_freq_1_m1' : 413523.92,
'C2_gate_optimize_tau_list_m1' :  [13.612e-6,13.612e-6,13.614e-6,13.614e-6,13.614e-6,13.616e-6
                                ,13.616e-6,13.616e-6,13.616e-6],
'C2_gate_optimize_N_list_m1': [28,30,30,32,34,32,34,36,38],           


# 'C2_Ren_tau_m1'    :   [13.614e-6],
# 'C2_Ren_N_m1'      :   [30],
# 'C2_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [43.26] + [169.41] + [135.85] + [0.0] + [78.79] + [87.22] + [0.0] + [0.0] + [0.0]),

'C2_Ren_tau_m1'    :   [13.614e-6],
'C2_Ren_N_m1'      :   [32],
'C2_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [123.81] + [181.0] + [-3.17] + [0.0] + [97.92] + [-15.85] + [0.0] + [0.0] + [0.0]),


    ################
    ### Carbon 3 ###
    ################

'C3_freq_m1'       :   (432014.8+447243.8)/2,  
'C3_freq_0' : 431878.24,
'C3_freq_1_m1' : 446616.1,

'C3_gate_optimize_tau_list_m1' :  [11.942e-6, 11.942e-6, 11.942e-6, 11.944e-6, 11.944e-6
                                    , 11.944e-6, 11.946e-6, 11.946e-6,11.946e-6],
'C3_gate_optimize_N_list_m1': [12,14,16,12,14,16,12,14,16],      

'C3_uncond_tau_m1' :   [(9.098)*1e-6],
'C3_uncond_pi_N_m1':   [44],
# 'C3_uncond_tau' :   [(6.824)*1e-6],
# 'C3_uncond_pi_N':   [64],    
# 'C3_uncond_tau' :   [(7.962)*1e-6],
# 'C3_uncond_pi_N':   [72],   
# 'C3_uncond_tau' :   [(5.688)*1e-6],

# 'C3_uncond_pi_N':   [94],   

'C3_Ren_tau_m1'    :   [11.942e-6],
'C3_Ren_N_m1'      :   [12],
'C3_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [38.19] + [93.46] + [-16.1] + [0.0] + [1.62] + [-10.12] + [0.0] + [0.0] + [0.0]),


    ################
    ### Carbon 5 ###
    ################

'C5_freq_m1' :    420021.01,### +-85.5 # 419.894e3,#XXXXXXXXXX
'C5_freq_0' : 432044.23,
'C5_freq_1_m1' : 408455.5,

# 'C5_gate_optimize_tau_list' :  [8.928e-6,8.928e-6,8.928e-6,8.930e-6,8.930e-6,
#                                 8.930e-6,8.932e-6,8.932e-6,8.932e-6],
# 'C5_gate_optimize_N_list': [38,40,42,34,36,38,34,36,38],           
# 'C5_gate_optimize_tau_list' :  [8.924e-6,8.924e-6,8.924e-6,8.926e-6,8.926e-6,
                                # 8.926e-6,8.928e-6,8.928e-6,8.928e-6],
# 'C5_gate_optimize_N_list': [36,38,40,36,38,40,36,38,40],           

# 'C5_gate_optimize_tau_list' :  [6.536e-6,6.536e-6,6.536e-6,6.538e-6,6.538e-6,
#                                 6.538e-6,6.540e-6,6.540e-6,6.540e-6],
# 'C5_gate_optimize_N_list': [30,32,34,30,32,34,30,32,34],    


'C5_gate_optimize_tau_list_m1' :  [11.308e-6, 11.308e-6, 11.308e-6, 11.310e-6, 11.310e-6, 11.310e-6, 11.312e-6, 11.312e-6, 11.312e-6],
'C5_gate_optimize_N_list_m1': [44,46,48,46,48,50,46,48,50],   

# 'C5_gate_optimize_tau_list' :  [11.310e-6, 11.310e-6],
# 'C5_gate_optimize_N_list': [48,50], 
# 'C5_Ren_tau'    :   [6.538e-6],
# 'C5_Ren_N'      :   [32],
# 'C5_Ren_extra_phase_correction_list' : np.array([0]+[43.7]+[92.5]+[0]*2+[-79.188]+[0]*4), 
'C5_geo_cond_N_m1':    [36],
'C5_geo_uncond_N_m1':  [28],
'C5_uncond_tau_m1' :   [(9.52)*1e-6],
'C5_uncond_pi_N_m1':   [94],
'C5_Ren_tau_m1'    :   [11.308e-6],
'C5_Ren_N_m1'      :   [48],
'C5_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [155.13] + [4.19] + [30.87] + [0.0] + [159.52] + [-13.79] + [0.0] + [0.0] + [0.0]),

'C6_gate_optimize_tau_list_m1' :  [4.93e-6,4.93e-6,4.93e-6,4.932e-6,4.932e-6,4.932e-6],
'C6_gate_optimize_N_list_m1': [88,92,96,88,92,96],   
    ### Carbon 6
'C6_freq_m1'       :   456280.,         #Only roughly calibrated
'C6_freq_0' : 431954.86,
'C6_freq_1_m1' : 480608.97,

'C6_Ren_tau_m1'    :   [4.932e-6],
'C6_Ren_N_m1'      :   [92],
'C6_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [91.03] + [251.57] + [3.75] + [0.0] + [1.96] + [36.92] + [0.0] + [0.0] + [0.0]),

########## dummy carbon 7
'C7_freq_m1'       :   456e3,         #Only roughly calibrated
'C7_freq_0' : 431959.87,
'C7_freq_1_m1' : 480615.5,

'C7_Ren_tau_m1'    :   [2.315e-6],
'C7_Ren_N_m1'      :   [12],
'C7_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),



###########################################
### 111 No1 Sil 18: nuclear spin params ms = +1 ###
###########################################

################
### Carbon 1 ###
################



'C1_freq_p1'       :   450.301e3,
'C1_freq_1_p1' : 468994.63,
'C1_gate_optimize_tau_list_p1' : [7.218e-6,4.994e-6,4.994e-6,4.996e-6,4.996e-6,
                               4.996e-6,4.998e-6,4.998e-6,7.214e-6],
'C1_gate_optimize_N_list_p1': [40,34,36,32,34,36,34,36,42],


'C1_Ren_tau_p1'    :   [4.994e-6],
'C1_Ren_N_p1'      :   [34],
'C1_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [41.76] + [120.91] + [-12.02] + [0.0] + [34.09] + [31.0] + [0.0] + [0.0] + [0.0]),

    ################
    ### Carbon 2 ###
    ################

'C2_freq_p1'       :   421.814e3,  
'C2_freq_1_p1' : 413500.47,
'C2_gate_optimize_tau_list_p1' :  [13.612e-6,13.612e-6,13.612e-6,13.614e-6,13.614e-6,13.614e-6,13.616e-6
                                ,13.616e-6,13.616e-6],
'C2_gate_optimize_N_list_p1': [26,28,30,30,32,34,32,34,36],           


'C2_Ren_tau_p1'    :   [13.616e-6],
'C2_Ren_N_p1'      :   [34],
'C2_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [50.14] + [170.36] + [135.85] + [0.0] + [83.42] + [87.22] + [0.0] + [0.0] + [0.0]),

    ################
    ### Carbon 3 ###
    ################

'C3_freq_p1'       :   421.814e3,  
'C3_freq_1_p1' : 447205.81,

'C3_gate_optimize_tau_list_p1' :  [11.942e-6, 11.942e-6, 11.942e-6, 11.944e-6, 11.944e-6
                                    , 11.944e-6, 11.946e-6, 11.946e-6,11.946e-6],
'C3_gate_optimize_N_list_p1': [12,14,16,12,14,16,12,14,16],      

'C3_uncond_tau_p1' :   [(9.098)*1e-6],
'C3_uncond_pi_N_p1':   [44],

'C3_Ren_tau_p1'    :   [11.090e-6],#[11.942e-6],
'C3_Ren_N_p1'      :   [12],#[14],
'C3_Ren_extra_phase_correction_lis_p1t' : np.array([0.0] + [15.11] + [114.74] + [-6.59] + [0.0] + [34.77] + [29.26] + [0.0] + [0.0] + [0.0]),


    ################
    ### Carbon 5 ###
    ################

'C5_freq_p1'       :   419.894e3,
'C5_freq_1_p1' : 408334.78,

'C5_gate_optimize_tau_list_p1' :  [11.308e-6, 11.308e-6, 11.308e-6, 11.310e-6, 11.310e-6, 11.310e-6, 11.312e-6, 11.312e-6, 11.312e-6],
'C5_gate_optimize_N_list_p1': [44,46,48,46,48,50,46,48,50],   

# 'C5_gate_optimize_tau_list' :  [11.310e-6, 11.310e-6],
# 'C5_gate_optimize_N_list': [48,50], 
# 'C5_Ren_tau'    :   [6.538e-6],
# 'C5_Ren_N'      :   [32],
# 'C5_Ren_extra_phase_correction_list' : np.array([0]+[43.7]+[92.5]+[0]*2+[-79.188]+[0]*4), 
'C5_geo_cond_N_p1':    [36],
'C5_geo_uncond_N_p1':  [28],
'C5_uncond_tau_p1' :   [(9.52)*1e-6],
'C5_uncond_pi_N_p1':   [94],
'C5_Ren_tau_p1'    :   [11.312e-6],
'C5_Ren_N_p1'      :   [48],
'C5_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [60.93] + [39.07] + [80.13] + [0.0] + [103.24] + [104.98] + [0.0] + [0.0] + [0.0]),


    ### Carbon 6
'C6_freq_p1'       :   456e3,         #Only roughly calibrated
'C6_freq_1_p1' : 480623.11,

'C6_Ren_tau_p1'    :   [4.932e-6],
'C6_Ren_N_p1'      :   [92],
'C6_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [35.43] + [-63.73] + [-6.02] + [0.0] + [88.17] + [35.69] + [0.0] + [0.0] + [0.0]),

########## dummy carbon 7
'C7_freq_p1'       :   456e3,         #Only roughly calibrated
'C7_freq_1_p1' : 480615.5,

'C7_Ren_tau_p1'    :   [2.315e-6],
'C7_Ren_N_p1'      :   [12],
'C7_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

}

    #####################################
    ###111 No1 SIL 18 SSRO parameters ###
    #####################################

cfg['protocols']['111_1_sil18']['AdwinSSRO'] = {
'SSRO_repetitions'  : 5000,
'SSRO_duration'     :  150,
'SSRO_stop_after_first_photon' : 1,
'A_CR_amplitude' : 100e-9, #8e-9,   #20e-9
'A_RO_amplitude' : 0.,
'A_SP_amplitude' : 100e-9,   #30e-9 
'CR_duration'    : 50,     # 50
'CR_preselect'   : 1000,
'CR_probe'       : 1000,
'CR_repump'      : 1000,
'Ex_CR_amplitude': 10e-9,    # 5e-9 
'Ex_RO_amplitude': 2.0e-9, #1.5e-9,    #3e-9,    # 15e-9,   0.5e-9
'Ex_SP_amplitude': 0e-9,    # THT 100716 changing this away from zero breaks most singleshot scripts, please inform all if we want to change this convention
'SP_duration'    : 50,     # 400 THT: Hardcoded in the ADWIN to be maximum 500 
'SP_duration_ms0': 500,     # only for specific scripts
'SP_duration_ms1': 500,     # only for specific scripts
'SP_filter_duration' : 0 }

    ##################################
    ### Integrated SSRO parameters ###
    ##################################

cfg['protocols']['111_1_sil18']['AdwinSSRO-integrated'] = {
'SSRO_duration' : 45, #30 previously NK 30-09-15
'Ex_SP_amplitude': 0 }


    ###########################
    ### pulse parameters    ###
    ###########################

    ################ predefs for the params. Select pulse shape!

## decide which parameters to use.
if pulse_shape == 'Hermite':
    fast_pi_length, fast_pi_amp, fast_pi2_length, fast_pi2_amp = Hermite_pi_length, Hermite_pi_amp, Hermite_pi2_length, Hermite_pi2_amp
    cfg['samples']['111_1_sil18']['mw_mod_frq'] = (0)*1e6
else:
    if pulse_shape != 'Square':
        print 'no valid pulses defined, using Square pulse params'
    fast_pi_length, fast_pi_amp, fast_pi2_length, fast_pi2_amp = Square_pi_length, Square_pi_amp, Square_pi2_length, Square_pi2_amp
    cfg['samples']['111_1_sil18']['mw_mod_frq'] = (0)*1e6

if mw2_pulse_shape == 'Hermite':
    print 'using hermites on mw2'
    mw2_fast_pi_length, mw2_fast_pi_amp, mw2_fast_pi2_length, mw2_fast_pi2_amp = mw2_Hermite_pi_length, mw2_Hermite_pi_amp, mw2_Hermite_pi2_length, mw2_Hermite_pi2_amp
else:
    if mw2_pulse_shape != 'Square':
        print 'no valid pulses defined, using Square pulse params'
    mw2_fast_pi_length, mw2_fast_pi_amp, mw2_fast_pi2_length, mw2_fast_pi2_amp = mw2_Square_pi_length, mw2_Square_pi_amp, mw2_Square_pi2_length, mw2_Square_pi2_amp
    


cfg['samples']['111_1_sil18']['mw_frq'] = mw_freq
cfg['samples']['111_1_sil18']['mw2_frq'] = mw2_freq
f_mod_0     = cfg['samples']['111_1_sil18']['mw_mod_freq']

cfg['protocols']['111_1_sil18']['pulses'] ={
    'MW_modulation_frequency'   :   f_mod_0,
    'MW_switch_channel'     :   'None', ### if you want to activate the switch, put to MW_switch

    'X_phase'                   :   90,
    'Y_phase'                   :   0,

    # 'C13_X_phase' :0,
    # 'C13_Y_phase' :90,

    'C13_X_phase' :0,
    'C13_Y_phase' :270,
    ############
    #Pulse type
    ###########
    'pulse_shape': pulse_shape,

    'MW_pulse_mod_frequency' : f_mod_0,

    'fast_pi_mod_frq'           :  f_mod_0,
    'fast_pi2_mod_frq'          :  f_mod_0,
    'Hermite_fast_pi_mod_frq'   :  f_mod_0,
    'Hermite_fast_pi2_mod_frq'  :  f_mod_0,

    ###############
    #
    #   General pulses used
    #
    #######

    # Pulses short with switch 
    # #     ### Pi pulses, fast & hard 
    'fast_pi_duration'              : fast_pi_length, 
    'mw2_fast_pi_duration'          :  mw2_Square_pi_length,    

    ### Pi/2 pulses, fast & hard 
    'fast_pi2_duration'         :  fast_pi2_length,
    'mw2_fast_pi2_duration'     :  mw2_fast_pi2_length,

    #####################
    #                   #
    #   HERMITE         #
    #                   #
    #####################

    'Hermite_pi_length'                 :  Hermite_pi_length,    
    'Hermite_pi_amp'                    :  Hermite_pi_amp,
    'mw2_Hermite_pi_length'             :  mw2_Hermite_pi_length,
    'mw2_Hermite_pi_amp'                :  mw2_Hermite_pi_amp,
    'BB1_fast_pi_duration'              :  BB1_pi_length,
    'BB1_fast_pi_amp'                   :  BB1_pi_amplitude,
    'Hermite_pi2_length'                :  Hermite_pi2_length,#56e-9, #should be divisible by 4, slow
    'Hermite_pi2_amp'                   :  Hermite_pi2_amp, # slow, only calibrated with 2 pulses
    'mw2_Hermite_pi2_length'            :  mw2_Hermite_pi2_length,
    'mw2_Hermite_pi2_amp'               :  mw2_Hermite_pi2_amp,


    #####################
    #                   #
    #   Square pulses   #
    #                   #
    #####################

    'Square_pi_length'                 :  Square_pi_length,    
    'Square_pi_amp'                    :  Square_pi_amp,
    'mw2_Square_pi_length'             :  mw2_Square_pi_length,
    'mw2_Square_pi_amp'                :  mw2_Square_pi_amp,
    'Square_pi2_length'                :  Square_pi2_length,#56e-9, #should be divisible by 4, slow
    'Square_pi2_amp'                   :  Square_pi2_amp, # slow, only calibrated with 2 pulses
    'mw2_Square_pi2_length'            :  mw2_Square_pi2_length,
    'mw2_Square_pi2_amp'               :  mw2_Square_pi2_amp,

    ### MBI pulses ###
    'AWG_MBI_MW_pulse_mod_frq'  :   f_mod_0,
    'AWG_MBI_MW_pulse_ssbmod_frq':  f_mod_0,
    'AWG_MBI_MW_pulse_amp'      :   AWG_MBI_MW_pulse_amp,  #0.01353*1.122  <-- pre-switch era  ## f_mod = 250e6 (msm1)
    # 'AWG_MBI_MW_pulse_amp'      :   0.01705,#0.0075,     ## f_mod = 125e6 (msm1)
    'AWG_MBI_MW_pulse_duration' :   3000e-9}

    ###############################
    ### Nitrogen MBI parameters ###
    ###############################

cfg['protocols']['111_1_sil18']['AdwinSSRO+MBI'] ={

    #Spin pump before MBI
'Ex_SP_amplitude'           :           15e-9,   #15e-9,#15e-9,    #18e-9
'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet?
'SP_E_duration'             :           250,     #Duration for both Ex and A spin pumping
    #MBI readout power and duration
'Ex_MBI_amplitude'          :           0.65e-9,
'MBI_duration'              :           40,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [200],
'repump_after_MBI_A_amplitude':         [40e-9],  #18e-9
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI parameters
'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
'MBI_threshold'             :           N_MBI_threshold, #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
'AWG_wait_for_adwin_MBI_duration':      10e-6+65e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          15e-9,

#Shutter
'use_shutter':                          0, 
'Shutter_channel':                      4, 
'Shutter_rise_time':                    2500,    
'Shutter_fall_time':                    2500,
'Shutter_safety_time':                  200000
}



    ###############################
    ### Nitrogen MBI parameters ###
    ###############################

cfg['protocols']['111_1_sil18']['AdwinSSRO+MBI_shutter'] ={

    #Spin pump before MBI
'Ex_SP_amplitude'           :           15e-9,  #15e-9,#15e-9,    #18e-9
'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet?
'SP_E_duration'             :           250,     #Duration for both Ex and A spin pumping

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           0.55e-9,
'MBI_duration'              :           40,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [150],
'repump_after_MBI_A_amplitude':         [30e-9],  # was 40 JC 151102 #18e-9
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI parameters
'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
'MBI_threshold'             :           N_MBI_threshold,
'AWG_wait_for_adwin_MBI_duration':      10e-6+65e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          15e-9,

#Shutter
'use_shutter':                          0, 
'Shutter_channel':                      4, 
'Shutter_rise_time':                    2500,    
'Shutter_fall_time':                    2500,
'Shutter_safety_time':                  200000
}


    #############################
    ### C13  init and control ###
    #############################

cfg['protocols']['111_1_sil18']['AdwinSSRO+C13'] = {


### wait to mitigate heating?
#'wait_between_runs':                    0, ### bool operator, set to one to wait for the 'Shutter_safety_time'

#C13-MBI  
'C13_MBI_threshold_list':               [1],
'C13_MBI_RO_duration':                  50,  
'E_C13_MBI_RO_amplitude':               0.7e-9, #this was 0.3e-9 NK 20150316
'SP_duration_after_C13':                250, #300 in case of swap init! 
'A_SP_amplitude_after_C13_MBI':         30e-9, # was 15e-9
'E_SP_amplitude_after_C13_MBI':         0e-9,
'C13_MBI_RO_state':                     0, # 0 sets the C13 MBI success condition to ms=0 (> 0 counts), if 1 to ms = +/-1 (no counts)
                
#C13-MBE  
'MBE_threshold':                        1,
'MBE_RO_duration':                      40, # was 40 20150329
'E_MBE_RO_amplitude':                   0.5e-9, #this was 0.35e-9 NK 20150316
'SP_duration_after_MBE':                30,
'A_SP_amplitude_after_MBE':             15e-9,
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
'Shutter_safety_time':                  200000, #Sets the time after each msmts, the ADwin waits for next msmt to protect shutter (max freq is 20Hz)

'min_phase_correct'   :     2,      # minimum phase difference that is corrected for by phase gates
'min_dec_tau'         :     20e-9 + cfg['protocols']['111_1_sil18']['pulses']['fast_pi_duration'],#20e-9 + cfg['protocols']['111_1_sil18']['pulses']['fast_pi_duration'], 
'max_dec_tau'         :     0.4e-6,#2.5e-6,#Based on measurement for fingerprint at low tau
'dec_pulse_multiple'  :     4,      #4.

# Memory entanglement sequence parameters
'optical_pi_AOM_amplitude' :     0.5,
'optical_pi_AOM_duration' :      200e-9,
'optical_pi_AOM_delay' :         300e-9,
'do_optical_pi' :                True,
'initial_MW_pulse':           'pi' #'pi', 'no_pulse'
}




























#################
### Hans sil1 ###
#################

    #############################################
    ### Hans sil1: V and frequency parameters ###
    #############################################

mw_power = 20
mw2_power = 20

f_msm1_cntr =   2.0249065e9            #Electron spin ms=-1 frquency  DO NOT CHANGE THIS!
f_msp1_cntr =   3.730069e9             #Electron spin ms=+1 frequency DO NOT CHANGE THIS!

zero_field_splitting = 2.877480e9   # Lowest value obtained for average ms+1 and -1 fregs.
                                    # As measured by Tim & Julia on 20140403 2.877480(5)e9

N_frq    = 7.13429e6      # not calibrated
N_HF_frq = 2.196e6        # calibrated 20140320/181319
Q        = 4.938e6        # from above values. 20140530

mw_mod_frequency = 250e6       #40e6 #250e6    # MW modulation frequency. 250 MHz to ensure phases are consistent between AWG elements

# For ms = +1
mw_freq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
mw_freq_MBI = f_msm1_cntr - mw_mod_frequency #- N_HF_frq    # Initialized frequency

# # For ms = -1
# mw_freq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
# mw_freq_MBI = f_msm1_cntr - mw_mod_frequency #- N_HF_frq    # Initialized frequency

cfg['samples']['Hans_sil1'] = {
'mw_mod_freq'   :       mw_mod_frequency,
'mw_frq'        :       mw_freq_MBI,
'mw_power'      :       mw_power,
'mw2_power'      :      mw2_power,
'ms-1_cntr_frq' :       f_msm1_cntr,
'ms+1_cntr_frq' :       f_msp1_cntr,
'zero_field_splitting': zero_field_splitting,
'Q_splitting'   :       Q,
'g_factor'      :       2.8025e6, #Hz/Gauss
'g_factor_C13'  :       1.0705e3, #Hz/Gauss
'g_factor_N14'  :       0.3077e3, #Hz/Gauss
'N_0-1_splitting_ms-1': N_frq,
'N_HF_frq'      :       N_HF_frq,

    ######################################
    ### Hans sil1: nuclear spin params ###
    ######################################

'C1_freq'       :   345.124e3,   
'C1_freq_0' : 432027.63,
'C1_freq_1' : 468994.63,
'C1_Ren_extra_phase_correction_list' : np.array([0.0] + [41.76] + [120.91] + [-12.02] + [0.0] + [34.09] + [31.0] + [0.0] + [0.0] + [0.0]),
'C1_Ren_tau'    :   [9.420e-6, 6.522e-6],
'C1_Ren_N'      :   [18      , 10],

'C2_freq'       :   339.955e3,
'C2_Ren_tau'    :   [6.62e-6, 8.088e-6, 9.560e-6],   
'C2_Ren_N'      :   [26     , 28      , 32],

'C3_freq'       :   302.521e3,
'C3_freq_0' : 431878.24,
'C3_freq_1' : 447205.81,
'C3_Ren_extra_phase_correction_list' : np.array([0.0] + [15.11] + [114.74] + [-6.59] + [0.0] + [34.77] + [29.26] + [0.0] + [0.0] + [0.0]),
'C3_Ren_tau'    :   [18.564e-6, 15.328e-6, 16.936e-6],
'C3_Ren_N'      :   [14      , 54       , 46],

'C4_freq'       :   348.574e3,   
'C4_freq_0'     :   325.787e3, 
'C4_freq_1'     :   370.115e3,  
'C4_Ren_extra_phase_correction_list' : np.array([0] +[-90] + [0]*8),
'C4_Ren_tau'    :   [6.456e-6   ],
'C4_Ren_N'      :   [40         ]}


    ##################################
    ### Hans Sil01 SSRO parameters ###
    ##################################

cfg['protocols']['Hans_sil1']['AdwinSSRO'] = {
'SSRO_repetitions'  : 10000,
'SSRO_duration'     :  50,
'SSRO_stop_after_first_photon' : 1,
'A_CR_amplitude' : 10e-9, # was 3 e-9 -Machiel25-06-14
'A_RO_amplitude' : 0,
'A_SP_amplitude' : 50e-9,
'CR_duration'    : 50,
'CR_preselect'   : 1000,
'CR_probe'       : 1000,
'CR_repump'      : 1000,
'Ex_CR_amplitude': 10e-9,   # was 5e-9 -Machiel 25-06-14
'Ex_RO_amplitude': 10e-9,   #15e-9,   # was 10 e-9 -Machiel 25-06-14
'Ex_SP_amplitude': 0e-9,    #THT 100716 changing this away from zero breaks most singleshot scripts, please inform all if we want to change this convention
'SP_duration'    : 50,
'SP_duration_ms0': 50,
'SP_duration_ms1': 200,
'SP_filter_duration' : 0 }

    ##################################
    ### Integrated SSRO parameters ###
    ##################################

cfg['protocols']['Hans_sil1']['AdwinSSRO-integrated'] = {
'SSRO_duration' : 20, 
'Ex_SP_amplitude':0}

    ###########################
    ### pulse parameters ###
    ###########################

f_mod_0     = cfg['samples']['Hans_sil1']['mw_mod_freq']
CORPSE_frq=  5.305e6

cfg['protocols']['Hans_sil1']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,

'pulse_shape'   :   pulse_shape,

'X_phase'                   :   90,
'Y_phase'                   :   0,

# 'C13_X_phase' :0,
# 'C13_Y_phase' :90,

'C13_X_phase' :0,
'C13_Y_phase' :270,

### nescessary to use the new standard espin script (140729 - Julia, not checked fully yet) 
'CORPSE_rabi_frequency' : CORPSE_frq,
# 'CORPSE_amp' : 0.201 ,
# 'CORPSE_pi2_amp': 1,
# 'CORPSE_pulse_delay': 0e-9,
# 'CORPSE_pi_amp': 0.517,
'MW_pi_amp': 0.8,
'MW_pi_length': 98e-9,
'Hermite_pi_length': 154e-9, 
'Hermite_pi_amp': 0.8,
'Hermite_pi2_length': 78e-9,
'Hermite_pi2_amp': 0.8,
# 'IQ_Hermite_pi_length': 154e-9, 
'IQ_Hermite_pi_amp': 0.8,
# 'IQ_Hermite_pi2_length': 78e-9,
'IQ_Hermite_pi2_amp': 0.8,
# 'Hermite_pi4_length': 45e-9,
# 'Hermite_pi4_amp': 0.385,
'Square_pi_length' : 98e-9, 
'Square_pi_amp' : 0.8 , 
'IQ_Square_pi_amp' : 0.8 , 
'Square_pi2_length' : 50e-9, 
'Square_pi2_amp'  : 0.8, 
'IQ_Square_pi2_amp'  : 0.8,
# 'extra_wait_final_pi2' : -30e-9,
'MW_pulse_mod_frequency' : f_mod_0,


# #     ### Pi pulses, fast & hard ### for msp1
'fast_pi_duration'          :   160e-9, #116e-9
'fast_pi_amp'               :   0.816691, 
'fast_pi_mod_frq'           :   f_mod_0,

    ### Pi pulses, fast & hard ### for msm1
# 'fast_pi_duration'          :   98e-9, ## fmod = 250
# 'fast_pi_duration'          :   32e-9, ## fmod = 0
# 'fast_pi_amp'               :   0.783,
# 'fast_pi_mod_frq'           :   f_mod_0,

    ### Pi/2 pulses, fast & hard ### for msp1
'fast_pi2_duration'         :   84e-9, 
'fast_pi2_amp'              :   0.772490,
'fast_pi2_mod_frq'          :   f_mod_0,

     ### Pi/2 pulses, fast & hard ### for msm1
# 'fast_pi2_duration'         :   50e-9, #fmod = 250
# 'fast_pi2_duration'         :   16e-9, #fmod = 0 
# 'fast_pi2_amp'              :   0.729,
# 'fast_pi2_mod_frq'          :   f_mod_0,

    ### MBI pulses ###
'AWG_MBI_MW_pulse_mod_frq'  :   f_mod_0,
'AWG_MBI_MW_pulse_ssbmod_frq':  f_mod_0,
#'AWG_MBI_MW_pulse_amp'      :  0.0128,     ## f_mod = 0e6 
#'AWG_MBI_MW_pulse_amp'      :  0.0141,     ## f_mod = 40e6 
'AWG_MBI_MW_pulse_amp'     :  0.0219,     ## f_mod = 250e6 (msp1)
# 'AWG_MBI_MW_pulse_amp'      :   0.0135,     ## f_mod = 250e6 (msm1)
'AWG_MBI_MW_pulse_duration' :   5500e-9,

    ### Corpse pulses ###
'CORPSE_pi2_amp'    :           1,
'CORPSE_frq'  :  CORPSE_frq,
'CORPSE_pi_60_duration' :  1./CORPSE_frq/6.,
'CORPSE_pi_m300_duration': 5./CORPSE_frq/6.,
'CORPSE_pi_420_duration':  7./CORPSE_frq/6.,
'CORPSE_pi2_24p3_duration': 24.3/CORPSE_frq/360.,
'CORPSE_pi2_m318p6_duration': 318.6/CORPSE_frq/360.,
'CORPSE_pi2_384p3_duration':  384.3/CORPSE_frq/360.}

    ###############################
    ### Nitrogen MBI parameters ###
    ###############################

cfg['protocols']['Hans_sil1']['AdwinSSRO+MBI'] ={

    #Spin pump before MBI
'Ex_SP_amplitude'           :           18e-9,
'A_SP_amplitude_before_MBI' :           0e-9,    #does not seem to work yet
'SP_E_duration'             :           250,     #Duration for both Ex and A spin pumping

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           1e-9,
'MBI_duration'              :           30,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [20],
'repump_after_MBI_A_amplitude':         [15e-9],
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI parameters
'max_MBI_attempts'          :           10,    # The maximum number of MBI attempts before going back to CR check
'MBI_threshold'             :           1,
'AWG_wait_for_adwin_MBI_duration':      10e-6+15e-6, # Added to AWG tirgger time to wait for ADWIN event. THT: this should just MBI_Duration + 10 us

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          15e-9}


    #############################
    ### C13  init and control ###
    #############################

cfg['protocols']['Hans_sil1']['AdwinSSRO+C13'] = {

#C13-MBI  
'C13_MBI_threshold':                    1,
'C13_MBI_RO_duration':                  30, 
'SP_duration_after_C13':                50,
'A_SP_amplitude_after_C13_MBI':         15e-9,
'E_SP_amplitude_after_C13_MBI':         0e-9 ,

#C13-MBE  
'MBE_threshold':                        1,
'MBE_RO_duration':                      30,
'E_MBE_RO_amplitude':                   3e-9,
'SP_duration_after_MBE':                50,
'E_C13_MBI_RO_amplitude':               1e-9,
'A_SP_amplitude_after_MBE':             15e-9,
'E_SP_amplitude_after_MBE':             0e-9 ,

#C13-parity msmnts
'Parity_threshold':                     1,
'Parity_RO_duration':                   50,
'E_Parity_RO_amplitude':                3e-9,

'min_phase_correct'   : 2,      # minimum phase difference that is corrected for by phase gates
'min_dec_tau'         : 20e-9 + cfg['protocols']['Hans_sil1']['pulses']['fast_pi_duration'],
'max_dec_tau'         : 0.4e-6, #0.35e-6, #Based on measurement for fingerprint at low tau
'dec_pulse_multiple'  : 4 #lowest multiple of 4 pulses
}






















    ###############################
    ### Rep Ramsey Magnetometry####
    ###############################


########################
### MAGNETOMETRY #######
########################

CORPSE_frq=  6.8e6
MW_mod_magnetometry=30e6
f_msm1_cntr = 2.024900e9             #Electron spin ms=-1 frquency
f_msp1_cntr = 3.730069e9              #Electron spin ms=+1 frequency

cfg['protocols']['Hans_sil1']['Magnetometry'] ={
'MW_modulation_frequency'   :   MW_mod_magnetometry,
'mw_frq'        :      f_msp1_cntr - MW_mod_magnetometry-N_HF_frq,
'mw_power'      :       20,
'ms-1_cntr_frq':       f_msm1_cntr,
'ms+1_cntr_frq':       f_msp1_cntr,


### Laser duration and powers etc ###
'SSRO_duration'     :  25.,
'Ex_RO_amplitude':  20e-9,
'Ex_SP_amplitude'  : 20e-9,
'A_CR_amplitude': 25e-9,
'Ex_CR_amplitude': 15e-9,
'A_SP_amplitude': 15e-9,
'A_SP_repump_amplitude':.5e-9,
'SP_duration': 100, #!!!! 10
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
'AWG_MBI_MW_pulse_mod_frq'  :   MW_mod_magnetometry+N_HF_frq,#conventional MBI init line (?)
'AWG_MBI_MW_pulse_ssbmod_frq':  MW_mod_magnetometry+N_HF_frq,#conventional MBI init line 
'AWG_MBI_MW_pulse_amp'      :   0.022,#0.0165,
'AWG_MBI_MW_pulse_duration' :   2000e-9,#3300e-9,

#MBI readout power and duration
'do_MBI'                    :           True,
'Ex_MBI_amplitude'          :           5e-9,
'MBI_duration'              :           7,
'AWG_wait_for_adwin_MBI_duration': (4+10)*1e-6,

#'pi2pi_mI0_mod_frq':MW_mod_magnetometry,#+N_HF_frq,
'pi2pi_mIm1_amp':0.180,
'pi2pi_mIp1_amp':0.168,
'pi2pi_mI0_amp':0.1755,
'pi2pi_mI0_duration':394e-9,
'MW_pi_pulse_amp': 0.9,
'AWG_pi2_duration': 40e-9,
'fpga_pi2_duration': 39e-9,
'init_repetitions':100, 
}








#################
### Hans sil4 ###
#################


CORPSE_frq=  11.7e6
N_HF_frq = 2.191e6 # measured on 2014-05-15 fit accuracy of 5 KHz
MW_mod_magnetometry=43e6
f_msm1_cntr = 2.024860e9             #Electron spin ms=-1 frquency
f_msp1_cntr = 3.730069e9              #Electron spin ms=+1 frequency
cfg['protocols']['Hans_sil4']['Magnetometry'] ={
'MW_modulation_frequency'   :   MW_mod_magnetometry,
'mw_frq'        :      f_msm1_cntr - MW_mod_magnetometry,
'mw_power'      :       20,
'ms-1_cntr_frq':       f_msm1_cntr,
'ms+1_cntr_frq':       f_msp1_cntr,
'N_HF_frq'      :       N_HF_frq,
### Laser duration and powers etc ###
'SSRO_duration'     :  18,
'CR_duration':      150,
'Ex_RO_amplitude':  30e-9,
'Ex_SP_amplitude'  : 40e-9,
'A_CR_amplitude': 20e-9,
'Ex_CR_amplitude': 20e-9,
'A_SP_amplitude': 40e-9,
'A_SP_repump_amplitude':40e-9,#.5e-9,
'SP_duration': 21, #!!!! 10
'SP_repump_duration': 50,
'wait_after_RO_pulse_duration':2,
'wait_after_pulse_duration':2,
'A_SP_repump_voltage':0.3, # bit of a detour to avoid putting this variable in ssro.autoconfig.

'SSRO_stop_after_first_photon':0,
#    ### Corpse pulses ###
'CORPSE_pi2_amp'    :           0.811,
'CORPSE_frq'  :  CORPSE_frq,
'CORPSE_pi_60_duration' :  1./CORPSE_frq/6.,
'CORPSE_pi_m300_duration': 5./CORPSE_frq/6.,
'CORPSE_pi_420_duration':  7./CORPSE_frq/6.,
'CORPSE_pi2_24p3_duration': 384.3/CORPSE_frq/360.,
'CORPSE_pi2_m318p6_duration': 318.6/CORPSE_frq/360.,
'CORPSE_pi2_384p3_duration':  384.3/CORPSE_frq/360.}












    ###############################
    ### NV and field parameters ###
    ###############################
'''


mw_freq  = 3.65e9    #MW source frequency
mw_power = 20        #MW power

zero_field_splitting = 2.87747e9    # As measured by Julia on 20140227 2.87747(5)e9

N_frq    = 7.13429e6        #not calibrated
N_HF_frq = 2.195e6        #calibrated 20140320/181319
'''


cfg['samples']['Hans_sil4'] = {
'mw_frq'        :       mw_freq,
'mw_power'      :       mw_power,
'ms-1_cntr_frq' :       f_msm1_cntr,
'ms+1_cntr_frq' :       f_msp1_cntr,
'zero_field_splitting': zero_field_splitting,
'g_factor'      :       2.8e6, #2.8 MHz/Gauss
'N_0-1_splitting_ms-1': N_frq,
'N_HF_frq'      :       N_HF_frq}

    #######################
    ### SSRO parameters ###
    #######################

cfg['protocols']['Hans_sil4']['AdwinSSRO'] = {
'SSRO_repetitions'  : 5000,
'SSRO_duration'     :  50,
'SSRO_stop_after_first_photon' : 0,
'A_CR_amplitude': 20e-9,
'A_RO_amplitude': 0,
'A_SP_amplitude': 40e-9,
'CR_duration' :  100,
'CR_preselect':  1000,
'CR_probe':      1000,
'CR_repump':     1000,
'Ex_CR_amplitude':  20e-9,
'Ex_RO_amplitude':  50e-9,
'Ex_SP_amplitude':  0e-9,
'SP_duration'        : 48,
'SP_filter_duration' : 0 }


    ##################################
    ### Integrated SSRO parameters ###
    ##################################

cfg['protocols']['Hans_sil4']['AdwinSSRO-integrated'] = {
'SSRO_duration' : 25}

    ########################
    ### Pulse parameters ###
    ########################

#f_0 = cfg['samples']['Hans_sil4']['ms-1_cntr_frq'] - cfg.get['samples']['Hans_sil4']['mw_frq']
f_mod_0     = cfg['samples']['Hans_sil4']['ms+1_cntr_frq'] - cfg['samples']['Hans_sil4']['mw_frq']
N_hf_split  = cfg['samples']['Hans_sil4']['N_HF_frq']
f_MBI = f_mod_0 - N_hf_split

cfg['protocols']['Hans_sil4']['pulses'] ={
'MW_modulation_frequency'   :   f_mod_0,

'pulse_shape'   :   pulse_shape,
'X_phase'                   :   90,
'Y_phase'                   :   0,

    ### Pi pulses, hard ###
'fast_pi_duration'          :   110e-9,   #should be divisible by 2
'fast_pi_amp'               :   .77*0.857767, #140324
'fast_pi_mod_frq'           :   f_MBI,

    ### Pi/2 pulses, hard ###
'fast_pi2_duration'         :   60e-9,    #should be divisible by 2
'fast_pi2_amp'              :   .77*0.809057, #0.777847, #140324
'fast_pi2_mod_frq'          :   f_MBI,

    ### MBI pulses ###
'AWG_MBI_MW_pulse_mod_frq'  :   f_MBI,
'AWG_MBI_MW_pulse_ssbmod_frq':  f_MBI,
'AWG_MBI_MW_pulse_amp'      :   .77*0.03,
'AWG_MBI_MW_pulse_duration' :   2500e-9}

#    ### Corpse pulses ###
# cfg.set(branch+'CORPSE_pi2_amp',0.4)
# CORPSE_frq = 8.15e6
# cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)

    ###########
    ### MBI ###
    ###########

cfg['protocols']['Hans_sil4']['AdwinSSRO+MBI'] ={

    #Spin pump before MBI
'Ex_SP_amplitude'           :           10e-9,
'SP_E_duration'             :           300,

    #MBI readout power and duration
'Ex_MBI_amplitude'          :           5e-9,
'MBI_duration'              :           4,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           300,
'repump_after_MBI_A_amplitude':         [15e-9],
'repump_after_MBI_E_amplitude':         [0e-9],

    #MBI paramters
'max_MBI_attempts'          :           100,
'MBI_threshold'             :           1,
'AWG_wait_duration_before_MBI_MW_pulse':50e-9,
'AWG_wait_for_adwin_MBI_duration':      15e-6,

'repump_after_E_RO_duration':           15,
'repump_after_E_RO_amplitude':          15e-9}
############################
### END: save everything ###
############################




































#################
### Hans sil4 ###
#################

# branch='samples/Hans_sil4/'

# f_msm1_cntr = 1.99074e9#2.000052e9#1.642e9
# f_msp1_cntr = 3.7641e9#3.7541e9#4.218e9    #calibrated
# N_frq = 7.13429e6           #not calibrated
# N_HF_frq = 2.16042e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

# branch='protocols/Hans_sil4-default/AdwinSSRO/'

# cfg.set(branch+'A_CR_amplitude', 40e-9)
# cfg.set(branch+'A_RO_amplitude' , 0)
# cfg.set(branch+'A_SP_amplitude', 63e-9)#70e-9)
# cfg.set(branch+'CR_duration' , 100)
# cfg.set(branch+'CR_preselect', 100)
# cfg.set(branch+'CR_probe', 100)
# cfg.set(branch+'CR_repump', 1000)
# cfg.set(branch+'Ex_CR_amplitude', 20e-9) #10e-9
# cfg.set(branch+'Ex_RO_amplitude', 20e-9) #10e-9
# cfg.set(branch+'Ex_SP_amplitude', 0e-9)
# cfg.set(branch+'SP_duration', 150) #300
# cfg.set(branch+'SP_filter_duration', 0)
# cfg.set(branch+'SSRO_duration', 168) #93
# cfg.set(branch+'SSRO_repetitions', 5000)
# cfg.set(branch+'SSRO_stop_after_first_photon', 0)
# cfg.set(branch+'mw_frq',2.2e9) #Probably Redundant, better to read out from AWG
# cfg.set(branch+'mw_power',20)
# cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

# branch='protocols/Hans_sil4-default/AdwinSSRO-integrated/'
# cfg.set(branch+'SSRO_duration', 117)

#     #Pulses, not yet calibrated.
# branch='protocols/Hans_sil4-default/pulses/'
# f0 = cfg['samples']['Hans_sil4']['ms-1_cntr_frq'] - cfg['protocols']['Hans_sil4-default']['AdwinSSRO']['mw_frq']
# cfg.set(branch+'MW_modulation_frequency', f0)
# cfg.set(branch+'Pi_pulse_duration', 80e-9)#40e-9)
# cfg.set(branch+'Pi_pulse_amp',  0.530)#0.6296)

# #Lines added to implement different phase pulses in decoupling sequence
# cfg.set(branch+'X_phase',  90)
# cfg.set(branch+'Y_phase',  0)

# #cfg.set(branch+'CORPSE_pi2_amp',0.4)
# #CORPSE_frq = 8.15e6
# #cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# #cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# #cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# #cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# #cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# #cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)

##############
### sil 10 ###
##############

# branch='samples/sil10/'

# f_msm1_cntr = 2.828855e9
# f_msp1_cntr = 2.925884e9    #not calibrated
# N_frq = 7.13429e6           #not calibrated
# N_HF_frq = 2.16042e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

# branch='protocols/sil10-default/AdwinSSRO/'

# cfg.set(branch+'A_CR_amplitude', 40e-9)
# cfg.set(branch+'A_RO_amplitude' , 0)
# cfg.set(branch+'A_SP_amplitude', 40e-9)
# cfg.set(branch+'CR_duration' , 50)
# cfg.set(branch+'CR_preselect', 15)
# cfg.set(branch+'CR_probe', 2)
# cfg.set(branch+'CR_repump', 1000)
# cfg.set(branch+'Ex_CR_amplitude', 6e-9)
# cfg.set(branch+'Ex_RO_amplitude', 8e-9)
# cfg.set(branch+'Ex_SP_amplitude', 0e-9)
# cfg.set(branch+'SP_duration', 250)
# cfg.set(branch+'SP_filter_duration', 0)
# cfg.set(branch+'SSRO_duration', 50)
# cfg.set(branch+'SSRO_repetitions', 5000)
# cfg.set(branch+'SSRO_stop_after_first_photon', 0)
# cfg.set(branch+'mw_frq',2.8e9) #-100e6)  #Probably Redundant, better to read out from AWG
# cfg.set(branch+'mw_power',20)
# cfg.set(branch+'MW_pulse_mod_risetime',10e-9)

# branch='protocols/sil10-default/AdwinSSRO-integrated/'
# cfg.set(branch+'SSRO_duration', 40)

# ### sil 10 pulses ### !!!NOT CALIBRATED

# branch='protocols/sil10-default/pulses/'

# f0 = cfg['samples']['sil10']['ms-1_cntr_frq'] - cfg['protocols']['sil10-default']['AdwinSSRO']['mw_frq']
# cfg.set(branch+'MW_modulation_frequency', f0)
# cfg.set(branch+'Pi_pulse_duration', 50e-9)
# cfg.set(branch+'Pi_pulse_amp',  0.49)
# cfg.set(branch+'CORPSE_pi2_amp',0.4)
# CORPSE_frq = 8.15e6
# cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
# cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)

# cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
# cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)



# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protoMW_pulse_frequencycols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)




# ### sil 15 ###
# branch='samples/sil15/'

# f_msm1_cntr = 2.828992e9
# f_msp1_cntr = 2.925693e9
# N_frq = 7.13429e6
# N_HF_frq = 2.193e6

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


# ### sil 1 ###
# branch='samples/sil1/'

# f_msm1_cntr = 2.829e9
# f_msp1_cntr = 2.925693e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)

# ### sil 5 ###
# branch='samples/sil5/'

# f_msm1_cntr = 2.829e9 #not calibrated
# f_msp1_cntr = 2.925747e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


### sil 7 ###
# branch='samples/sil7/'

# f_msm1_cntr = 2.829e9 #not calibrated
# f_msp1_cntr = 2.925871e9
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)


### sil 11 ###
# branch='samples/sil11/'

# f_msm1_cntr = 2.829e9
# f_msp1_cntr = 2.926e9 #not calibrated
# N_frq = 7.13429e6#not calibrated
# N_HF_frq = 2.193e6#not calibrated

# cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
# cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
# cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
# cfg.set(branch+'N_HF_frq', N_HF_frq)



#### sil9 ###
#### sil9, AdwinSSRO ###
#
#
#### sil 9 ###
#branch='samples/sil9/'
#
#f_msm1_cntr = 2.828825e9
#f_msp1_cntr = 2.925884e9 #not calibrated
#N_frq = 7.13429e6 #not calibrated
#N_HF_frq = 2.189e6
#
#cfg.set(branch+'ms-1_cntr_frq', f_msm1_cntr)
#cfg.set(branch+'ms+1_cntr_frq', f_msp1_cntr)
#cfg.set(branch+'N_0-1_splitting_ms-1', N_frq)
#cfg.set(branch+'N_HF_frq', N_HF_frq)
#
#
#branch='protocols/sil9-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 10e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 40e-9)
#cfg.set(branch+'CR_duration' , 50)
#cfg.set(branch+'CR_preselect', 15)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 1000)
#cfg.set(branch+'Ex_CR_amplitude', 10e-9)
#cfg.set(branch+'Ex_RO_amplitude', 10e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'mw_frq',2.8e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil9, AdwinSSRO integrated ###
#branch='protocols/sil9-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 23)
#
## # MBI
#branch='protocols/sil9-default/AdwinSSRO+MBI/'
#cfg.set(branch+        'Ex_MBI_amplitude',              10e-9)
#cfg.set(branch+        'Ex_SP_amplitude',               10e-9)
#cfg.set(branch+        'MBI_duration',                  4)
#cfg.set(branch+        'MBI_steps',                     1)
#cfg.set(branch+        'MBI_threshold',                 1)
#cfg.set(branch+        'SP_E_duration',                 200)
#cfg.set(branch+        'repump_after_MBI_duration',     10)
#cfg.set(branch+        'repump_after_MBI_amplitude',    5e-9)
#cfg.set(branch+        'repump_after_E_RO_duration',    10)
#cfg.set(branch+        'repump_after_E_RO_amplitude',   5e-9)
#
## MBI pulse
#cfg.set(branch+        'AWG_wait_duration_before_MBI_MW_pulse',     50e-9)
#cfg.set(branch+        'AWG_wait_for_adwin_MBI_duration',           15e-6)
#
#
#### sil 9 pulses
#f0 = cfg['samples']['sil9']['ms-1_cntr_frq'] - cfg['protocols']['sil9-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil9-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.677)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
#finit = f0 - N_HF_frq
#fmIp1 = f0 + N_HF_frq
#
#cfg.set(branch+'mIm1_mod_frq',finit)
#cfg.set(branch+'mI0_mod_frq',f0)
#cfg.set(branch+'mIp1_mod_frq',fmIp1)
#
#CORPSE_frq = 8.15e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.438)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.474)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.69e-6)
#
##################NOT CALIBRATED!!
#
#cfg.set(branch+        'selective_pi_duration',     2500e-9)
#cfg.set(branch+        'selective_pi_amp',          0.011)
#cfg.set(branch+        'selective_pi_mod_frq',      finit)
#
#cfg.set(branch+        'pi2pi_mIm1_duration',        395e-9)
#cfg.set(branch+        'pi2pi_mIm1_amp',             0.0827)
#cfg.set(branch+        'pi2pi_mIm1_mod_frq',         finit)
#
#cfg.set(branch+        'AWG_MBI_MW_pulse_mod_frq',    finit)
#cfg.set(branch+        'AWG_MBI_MW_pulse_ssbmod_frq', finit)
#cfg.set(branch+        'AWG_MBI_MW_pulse_amp',        cfg.get(branch+        'selective_pi_amp'))
#cfg.set(branch+        'AWG_MBI_MW_pulse_duration',   cfg.get(branch+        'selective_pi_duration'))
#
#cfg.set(branch+        'AWG_shelving_pulse_duration', cfg.get(branch+        '8MHz_pi_duration'))
#cfg.set(branch+        'AWG_shelving_pulse_amp',     cfg.get(branch+        '8MHz_pi_amp'))
#




### Specific protocol settings ###

### sil15 ###
### sil15, AdwinSSRO ###
#branch='protocols/sil15-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 20e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 12)
#cfg.set(branch+'CR_probe', 12)
#cfg.set(branch+'CR_repump', 100)
#cfg.set(branch+'Ex_CR_amplitude', 20e-9)
#cfg.set(branch+'Ex_RO_amplitude', 20e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.9e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil15, AdwinSSRO integrated ###
#branch='protocols/sil15-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#### sil 15 pulses
#f0 = cfg['samples']['sil15']['ms+1_cntr_frq'] - cfg['protocols']['sil15-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil15-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.677)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
# cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)

# cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
# cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
# cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)

#CORPSE_frq = 8.035e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.605)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.639)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.75e-6)



### sil1 ###
### sil1, AdwinSSRO ###
#branch='protocols/sil1-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 20e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 12)
#cfg.set(branch+'CR_probe', 12)
#cfg.set(branch+'CR_repump', 100)
#cfg.set(branch+'Ex_CR_amplitude', 20e-9)
#cfg.set(branch+'Ex_RO_amplitude', 10e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.8e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil1, AdwinSSRO integrated ###
#branch='protocols/sil1-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#
#### sil5 ###
#### sil5, AdwinSSRO ###
#branch='protocols/sil5-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 20e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 30e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 15)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 1000)
#cfg.set(branch+'Ex_CR_amplitude', 10e-9)
#cfg.set(branch+'Ex_RO_amplitude', 5e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.9e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil5, AdwinSSRO integrated ###
#branch='protocols/sil5-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
## pulses
#f0 = cfg['samples']['sil5']['ms+1_cntr_frq'] - cfg['protocols']['sil5-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil5-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.545)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)
#
## cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
## cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
## cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)
#
#CORPSE_frq = 8.050e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.547)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.577)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.61e-6)
#
#### sil7 ###
#### sil7, AdwinSSRO ###
#branch='protocols/sil7-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 15e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 150)
#cfg.set(branch+'CR_preselect', 8)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 1000)
#cfg.set(branch+'Ex_CR_amplitude', 15e-9)
#cfg.set(branch+'Ex_RO_amplitude', 20e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.9e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil7, AdwinSSRO integrated ###
#branch='protocols/sil7-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#### sil 7 pulses
#f0 = cfg['samples']['sil7']['ms+1_cntr_frq'] - cfg['protocols']['sil7-default']['AdwinSSRO']['mw_frq']
#
#branch='protocols/sil7-default/pulses/'
#cfg.set(branch+'f0', f0)
#cfg.set(branch+'8MHz_pi_duration', 63e-9)
#cfg.set(branch+'8MHz_pi_amp',  0.677)
#cfg.set(branch+'8MHz_pi_mod_frq',  f0)
#
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_duration',  tof + 45e-9)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_amp',  0.698)
## cfg.set('protocols/sil15-default/pulses/4MHz_pi2_mod_frq',  finit)
#
## cfg.set('protocols/sil15-default/pulses/hard_pi_duration',  80e-9)
## cfg.set('protocols/sil15-default/pulses/hard_pi_amp',  0.809)
## cfg.set('protocols/sil15-default/pulses/hard_pi_frq',  f0)
#
#CORPSE_frq = 8.102e6
#cfg.set(branch+'CORPSE_pi_60_duration', 1./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_m300_duration', 5./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_420_duration',  7./CORPSE_frq/6.)
#cfg.set(branch+'CORPSE_pi_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi_amp',  0.640)
#
#cfg.set(branch+'CORPSE_pi2_24p3_duration', 24.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_m318p6_duration', 318.6/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_384p3_duration',  384.3/CORPSE_frq/360.)
#cfg.set(branch+'CORPSE_pi2_mod_frq', f0)
#cfg.set(branch+'CORPSE_pi2_amp',  0.698)
#
##for dynamical decoupling pulses:
#cfg.set(branch+'first_C_revival', 53.61e-6)
#
#
#
#
#
#### sil11 ###
#### sil11, AdwinSSRO ###
#branch='protocols/sil11-default/AdwinSSRO/'
#cfg.set(branch+'A_CR_amplitude', 15e-9)
#cfg.set(branch+'A_RO_amplitude' , 0)
#cfg.set(branch+'A_SP_amplitude', 20e-9)
#cfg.set(branch+'CR_duration' , 100)
#cfg.set(branch+'CR_preselect', 6)
#cfg.set(branch+'CR_probe', 2)
#cfg.set(branch+'CR_repump', 100)
#cfg.set(branch+'Ex_CR_amplitude', 10e-9)
#cfg.set(branch+'Ex_RO_amplitude', 10e-9)
#cfg.set(branch+'Ex_SP_amplitude', 0e-9)
#cfg.set(branch+'SP_duration', 250)
#cfg.set(branch+'SP_filter_duration', 0)
#cfg.set(branch+'SSRO_duration', 50)
#cfg.set(branch+'SSRO_repetitions', 5000)
#cfg.set(branch+'SSRO_stop_after_first_photon', 0)
#cfg.set(branch+'repump_after_repetitions',1)
#cfg.set(branch+'mw_frq',2.8e9)
#cfg.set(branch+'mw_power',20)
#cfg.set(branch+'MW_pulse_mod_risetime',10e-9)
#
#### sil11, AdwinSSRO integrated ###
#branch='protocols/sil11-default/AdwinSSRO-integrated/'
#cfg.set(branch+'SSRO_duration', 50)
#
#


