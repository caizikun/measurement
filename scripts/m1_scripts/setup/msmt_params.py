import numpy as np

#### M1 Params ####


cfg={}

#############################
### Set current NV center ###
#############################

sample_name         = '111_1_sil18'

cfg['samples']      = {'current':sample_name}
cfg['protocols']    = {'current':sample_name}
cfg['protocols'][sample_name] = {}

print 'updating msmt params M1 for {}'.format(cfg['samples']['current'])

###################################
### General settings for magnet ###
###################################

### Assumes a cylindrical magnet
cfg['magnet']={
'nm_per_step'       :   38.85, ## Z-movement, for 18 V and 200 Hz 
'radius'            :   5.,     ## millimetersy
'thickness'         :   4.,     ## millimeters
'strength_constant' :   1.3}    ## Tesla

#################
### Protocols ###
#################

cfg['protocols']['AdwinSSRO']={
'AWG_done_DI_channel'       :       16,
'AWG_event_jump_DO_channel' :       14,
'AWG_start_DO_channel'      :       15,
'counter_channel'           :       1,
'cycle_duration'            :       1000,   ## in units of the ADWIN processor clock
'green_off_amplitude'       :       0.0,
'green_repump_amplitude'    :       30e-6, #5,
'green_repump_duration'     :       50,
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
'Shutter_opening_time'      :       3000,
'Shutter_safety_time'       :      200000, ### used for cooling down the sample over time.
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
'MW_switch_risetime'    :    50e-9,
'MW_pulse_mod_risetime' :      10e-9,#10
'MW2_pulse_mod_risetime':    10e-9,#10
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
'MW_pulse_mod_risetime'                 :    10e-9,#10
'MW2_pulse_mod_risetime'                :    10e-9,
'MW_switch_risetime'                    :    50e-9, #500e-9  XXXX
'AWG_to_adwin_ttl_trigger_duration'     :    5e-6, 
'max_MBI_attempts'                      :    1,
'N_randomize_duration'                  :    200,#50,
'Ex_N_randomize_amplitude'              :    1e-9,#15e-9, #15e-9
'A_N_randomize_amplitude'               :    10e-9,#15e-9,
'repump_N_randomize_amplitude'          :    0e-9} #Green or yellow. Probably should be 0 when using Green

############### ######################
### SAMPLES ### ### 111 No1 SIL 18 ###
############### ######################

    #####################################
    ###111 No1 SIL 18 SSRO parameters ###
    #####################################

cfg['protocols']['111_1_sil18']['AdwinSSRO'] = {
'A_CR_amplitude' : 8e-9, #8
'A_RO_amplitude' :0e-9,
'A_SP_amplitude' : 8e-9, #8  
'CR_duration'    : 150,     
'CR_preselect'   : 1000,

'CR_probe'       : 1000,
'CR_repump'      : 1000,
'Ex_CR_amplitude': 0.5e-9, #0.5e-9  
'Ex_RO_amplitude': 1.5e-9, #2
'Ex_SP_amplitude': 0e-9,   # THT 100716 changing this away from zero breaks most singleshot scripts, please inform all if we want to change this convention
'SP_duration'    : 100,    #50 # THT: Hardcoded in the ADWIN to be maximum 500 
'SP_duration_ms0': 100,    # only for specific scripts
'SP_duration_ms1': 100,    # only for specific scripts
'SP_filter_duration':  0,
'SSRO_repetitions'  :  5000,
'SSRO_duration'     :  50,#50
'SSRO_stop_after_first_photon' : 0} 

    ##################################
    ### Integrated SSRO parameters ###
    ##################################

cfg['protocols']['111_1_sil18']['AdwinSSRO-integrated'] = {
'SSRO_duration'  : 40,
'Ex_SP_amplitude': 0 }

    ##################################################
    ### 111 No1 SIL 18: V and frequency parameters ###
    ##################################################

mw_power  = 20
mw2_power = -20
f_msm1_cntr =   1.746666e9#1.766536e9  #Electron spin ms=-1 frequency
f_msp1_cntr =   4.008650e9#4.008621e9  #Electron spin ms=+1 frequency 

zero_field_splitting = 2.877623e9#2.877623e9  # not calibrated # contains + 2*N_hf?

N_frq    = 7.13429e6      # not calibrated
N_HF_frq = 2.182e6        # was 2.196e6       
Q        = 4.938e6        # not calibrated

electron_transition = '-1'
multiple_source = False

# pulse_shape = 'Square' # alternatively 'Hermite', or 'Square'
pulse_shape = 'Hermite' # alternatively 'Hermite', or 'Square'

if electron_transition == '-1':
    electron_transition_string = '_m1'
    if pulse_shape == 'Square':
        mw_mod_frequency = 43e6 # MJD set to 43e6 for N MBI quick sweeping in 10 MHz regime # MW modulation frequency. 250 MHz to ensure phases are consistent between AWG elements
        N_MBI_threshold = 1
        Ex_SP_amplitude = 16e-9
    elif pulse_shape == 'Hermite':
        mw_mod_frequency = 0*1e6 
        N_MBI_threshold = 0#0
        Ex_SP_amplitude = 0

    mw_freq     = f_msm1_cntr - mw_mod_frequency                # Center frequency
    mw_freq_MBI = f_msm1_cntr - mw_mod_frequency #- N_HF_frq  MJD commented out to set the MBI freq to the center freq     # Initialized frequency
    
    AWG_MBI_MW_pulse_amp = 0.009#0.00824 #0.01525
    
    Hermite_pi_length   = 220e-9#200e-9    
    Hermite_pi_amp      = 0.704#0.716 #0.704 # 0.729 #0.856 #0.9#0.8175 #0.3564 #0.737 #0.442 # 0.445 for 160ns #0.481 #for 150 ns

    Hermite_pi2_length  = 100e-9 # 56e-9 # divsible by 2
    Hermite_pi2_amp     = 0.637#0.660 #0.777 #0.62 # 0.501

    Square_pi_length    = 602e-9   #250 MHz slow
    Square_pi_amp       = 0.73 #0.231503  #0.407630#0.385# 0.3875#0.406614#0.406614  #250 MHz, slow

    Square_pi2_length   = 56e-9 #should be divisible by 4, slow
    Square_pi2_amp      =  0.242622    #0.493036,

    BB1_pi_length       = 150e-9
    BB1_pi_amplitude    = 0.955


elif electron_transition == '+1':
    electron_transition_string = '_p1'
    pulse_shape = 'Hermite' # alternatively 'Hermite', or 'Square'
    if pulse_shape == 'Square':
        mw_mod_frequency = 0       #40e6 #250e6    # MW modulation frequency. 250 MHz to ensure phases are consistent between AWG elements
        N_MBI_threshold = 1
        Ex_SP_amplitude = 16e-9
    elif pulse_shape == 'Hermite':
        mw_mod_frequency = 0*1e6 
        N_MBI_threshold = 0
        Ex_SP_amplitude = 0
    mw_freq             = f_msp1_cntr - mw_mod_frequency                # Center frequency
    mw_freq_MBI         = f_msp1_cntr - mw_mod_frequency# - N_HF_frq    # Initialized frequency
    AWG_MBI_MW_pulse_amp = 0#0.00824

    Hermite_pi_length = 200e-9
    Hermite_pi_amp = 0.869 #0.92

    Hermite_pi2_length = 100e-9#120e-9#56e-9, #should be divisible by 4, slow
    Hermite_pi2_amp = 0.493 #0.678533   

    Square_pi_length = 60e-9 #180e-9   #250 MHz slow
    Square_pi_amp =  0.7 #0.694552  #0.407225 #without switch #0.469424,with switch  #250 MHz, slow

    Square_pi2_length = 92e-9 #56e-9, #should be divisible by 4, slow
    Square_pi2_amp =  0.738335 #0.493036, # slow, only calibrated with 2 pulses

    BB1_pi_length = 50e-9
    BB1_pi_amplitude = 0.9


print '*************************************************************************'
print ' pulse shape is ' + pulse_shape +' and MBI_threshold is '+str(N_MBI_threshold) + ' and el transition is ' + electron_transition
print '*************************************************************************'

##   Second microwave source
### Comment: frequency should be selected automatically depending on source 1...

mw2_freq            = f_msp1_cntr   # Center frequency
mw2_pulse_shape     = 'Hermite'

if mw2_freq == f_msm1_cntr:
    mw2_Hermite_pi_duration = 90e-9  
    mw2_Hermite_pi_amp = 0.414
    mw2_Hermite_pi2_length = 70e-9
    mw2_Hermite_pi2_amp = .5  
    mw2_Square_pi2_amp =  .5
    mw2_Square_pi_amp =  .414
    mw2_Square_pi_length = 90e-9    #180e-9   #250 MHz slow
    mw2_Square_pi2_length = 11e-9   #180e-9   #250 MHz slow
    mw2_electron_transition_string = '_m1'
else:
    mw2_Hermite_pi_length = 160e-9    
    mw2_Hermite_pi_amp = 0.616
    mw2_Hermite_pi2_length = 70e-9
    mw2_Hermite_pi2_amp = .5  
    mw2_Square_pi2_amp =  .5
    mw2_Square_pi_amp =  .616
    mw2_Square_pi_length = 160e-9   #180e-9   #250 MHz slow
    mw2_Square_pi2_length = 28e-9   #180e-9   #250 MHz slow
    mw2_electron_transition_string = '_p1'

cfg['samples']['111_1_sil18'] = {
'electron_transition' : electron_transition_string,
'electron_transition_used' : electron_transition_string,
'multiple_source'   :   multiple_source,
'mw_mod_freq'   :       mw_mod_frequency,
'mw_frq'        :       mw_freq, 
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

    #####################################################
    ###define which transitions to use for each carbon###
    #####################################################
'C1_dec_trans'  :   '_m1',
'C2_dec_trans'  :   '_m1',
'C3_dec_trans'  :   '_m1',
'C4_dec_trans'  :   '_p1',
'C5_dec_trans'  :   '_m1',
'C6_dec_trans'  :   '_m1',
'C7_dec_trans'  :   '_p1',
'C8_dec_trans'  :   '_m1',
'Cm1_dec_trans' :   '_m1',
'Cp1_Dec_trans' :   '_p1',


'C1_freq_m1'    : 450877,       ##+-104.6 #450301.0, 
'C1_freq_0'     : 432012.57,
'C1_freq_1_m1'  : 469066.38,

# 'C1_gate_optimize_tau_list_m1' : [4.994e-6,4.994e-6,4.994e-6,4.996e-6,4.996e-6,
#                                4.996e-6,4.998e-6,4.998e-6,4.998e-6],

'C1_gate_optimize_tau_list_m1' : [7.218e-6,4.994e-6,4.994e-6,4.996e-6,4.996e-6,
                               4.996e-6,4.998e-6,4.998e-6,7.214e-6],

# 'C1_gate_optimize_N_list_m1': [32,34,36,32,34,36,34,36,38],
'C1_gate_optimize_N_list_m1': [40,34,36,32,34,36,34,36,42],


# 'C1_Ren_tau'    :   [4.994e-6],
# 'C1_Ren_N'      :   [34],
# 'C1_Ren_extra_phase_correction_list' :  np.array([0] + [-15.28] + [42.26]+[0]*2+[63.88]+ 4*[0]),

'C1_Ren_tau_m1'    :  [7.220e-6],
'C1_Ren_N_m1'      :  [44],
'C1_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [179.44] + [106.05] + [8.26] + [0.0] + [36.11] + [-4.49] + [0.0] + [0.0] + [0.0]),

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

'C5_freq_m1' :   419999,### +-85.5 # 419.894e3,#XXXXXXXXXX
'C5_freq_0' :    432044.23,
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
'C5_Ren_tau_m1'    :   [6.544e-6],
'C5_Ren_N_m1'      :   [28],
'C5_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [42.41] + [4.19] + [30.87] + [0.0] + [11.08] + [-13.79] + [0.0] + [0.0] + [0.0]),

    ################
    ### Carbon 6 ###
    ################

'C6_gate_optimize_tau_list_m1' :  [4.93e-6,4.93e-6,4.93e-6,4.932e-6,4.932e-6,4.932e-6],
'C6_gate_optimize_N_list_m1': [88,92,96,88,92,96],   

'C6_freq_m1'       :   456280.,         # Only roughly calibrated
'C6_freq_0' : 431954.86,
'C6_freq_1_m1' : 480608.97,

'C6_Ren_tau_m1'    :   [4.932e-6],
'C6_Ren_N_m1'      :   [92],
'C6_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [91.03] + [251.57] + [3.75] + [0.0] + [1.96] + [25.65] + [0.0] + [0.0] + [0.0]),

    ################
    ### Dummy C7 ###
    ################

'C7_freq_m1'        :   456e3,          # Only roughly calibrated
'C7_freq_0'         : 431959.87,
'C7_freq_1_m1'      : 480615.5,

'C7_Ren_tau_m1'    :   [2.315e-6],
'C7_Ren_N_m1'      :   [12],
'C7_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

    ################
    ### Dummy C8 ###
    ################
## 120 us, 2kHz, C13 cluster
'C8_freq_m1'        : 2.082e3,#2.0846e3,          # Only roughly calibrated
'C8_freq_0'         : 2.082e3,#2.0846e3, 
'C8_freq_1_m1'      : 2.082e3,#2.0846e3,

'C8_Ren_tau_m1'    :   [122.685e-6],
'C8_Ren_N_m1'      :   [22],
'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# # 75 us, 6800kHz, C13 cluster
# 'C8_freq_m1'        : 6.60e3,          # Only roughly calibrated
# 'C8_freq_0'         : 6.60e3,
# 'C8_freq_1_m1'      : 6.60e3,

# 'C8_Ren_tau_m1'    :   [76.545e-6],
# 'C8_Ren_N_m1'      :   [12],#[12],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# 63 us, 7800kHz, C13 cluster
# 'C8_freq_m1'        : 7.9e3,          # Only roughly calibrated
# 'C8_freq_0'         : 7.9e3,#239,
# 'C8_freq_1_m1'      : 7.9e3,

# 'C8_Ren_tau_m1'    :   [63.65e-6],#[62.4969e-6],
# 'C8_Ren_N_m1'      :   [32],#[16],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),


# # 63 us, 7800kHz, C13 cluster
# 'C6_freq_m1'        : 6.6e3,          # Only roughly calibrated
# 'C6_freq_0'         : 6.6e3,#239,
# 'C6_freq_1_m1'      : 6.6e3,

# 'C6_Ren_tau_m1'    :   [76.545e-6],#[63.65e-6],
# 'C6_Ren_N_m1'      :   [12],
# 'C6_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# # #165 us, C13 cluster
# 'C8_freq_m1'        : 2816,#2816,#0.189e3,          # Only roughly calibrated
# 'C8_freq_0'         : 2816,#0.189e3,
# 'C8_freq_1_m1'      : 2816,#2.816e3,#0.189e3,

# 'C8_Ren_tau_m1'    :   [172.445e-6],
# 'C8_Ren_N_m1'      :   [8],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# 111 us, 80 Hz, C13 cluster
# 'C8_freq_m1'        : 4.422e3,          # Only roughly calibrated
# 'C8_freq_0'         : 4.422e3, 
# 'C8_freq_1_m1'      : 4.422e3,

# 'C8_Ren_tau_m1'    :   [112.22e-6],
# 'C8_Ren_N_m1'      :   [26],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# #260 us, 2kHz, C13 cluster
# 'C8_freq_m1'        : 1.821e3,          # Only roughly calibrated
# 'C8_freq_0'         : 1.821e3,#130,#1.821e3, 
# 'C8_freq_1_m1'      : 1.821e3,#1.821e3,

# 'C8_Ren_tau_m1'    :   [276.8e-6],
# 'C8_Ren_N_m1'      :   [6],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# #260 us, 2kHz, C13 cluster
# 'C8_freq_m1'        : 2.77e3,          # Only roughly calibrated
# 'C8_freq_0'         : 2.77e3, 
# 'C8_freq_1_m1'      : 2.77e3,

# 'C8_Ren_tau_m1'    :   [256.8e-6],
# 'C8_Ren_N_m1'      :   [8],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),


# #260 us, 2kHz, C13 cluster
# 'C8_freq_m1'        : 2.77e3,          # Only roughly calibrated
# 'C8_freq_0'         : 2.77e3, 
# 'C8_freq_1_m1'      : 2.77e3,

# 'C8_Ren_tau_m1'    :   [4.371e-6],
# 'C8_Ren_N_m1'      :   [1600],
# 'C8_Ren_extra_phase_correction_list_m1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),


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


# #63 us, 7800kHz, C13 cluster
# 'C8_freq_p1'        : 8.23e3,          # Only roughly calibrated
# 'C8_freq_0'         : 8.23e3,
# 'C8_freq_1_p1'      : 8.23e3,

# 'C8_Ren_tau_p1'    :   [60.182e-6],#[63.65e-6],
# 'C8_Ren_N_p1'      :   [12],
# 'C8_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

#75 us, 6600kHz, C13 cluster
# 'C8_freq_p1'        : 6.6e3,          # Only roughly calibrated
# 'C8_freq_0'         : 6.6e3,
# 'C8_freq_1_p1'      : 6.6e3,

# 'C8_Ren_tau_p1'    :   [76.545e-6],#[63.65e-6],
# 'C8_Ren_N_p1'      :   [10],
# 'C8_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

#75 us, 6600kHz, C13 cluster
# 'C8_freq_p1'        : 4.465e3,          # Only roughly calibrated
# 'C8_freq_0'         : 4.465e3,
# 'C8_freq_1_p1'      : 4.465e3,

# 'C8_Ren_tau_p1'    :   [111.22e-6],#[63.65e-6],
# 'C8_Ren_N_p1'      :   [24],
# 'C8_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),

# #165 us, 7800kHz, C13 cluster
# 'C8_freq_p1'        : 2.777e3,          # Only roughly calibrated
# 'C8_freq_0'         : 2.777e3,
# 'C8_freq_1_p1'      : 2.777e3,

# 'C8_Ren_tau_p1'    :   [172.445e-6],
# 'C8_Ren_N_p1'      :   [8],
# 'C8_Ren_extra_phase_correction_list_p1' : np.array([0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0] + [0.0]),
}



    ###########################################
    ### 111 No1 SIL 18: pulse parameters    ###
    ###########################################

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
    # print 'using hermites on mw2'
    mw2_fast_pi_length, mw2_fast_pi_amp, mw2_fast_pi2_length, mw2_fast_pi2_amp = mw2_Hermite_pi_length, mw2_Hermite_pi_amp, mw2_Hermite_pi2_length, mw2_Hermite_pi2_amp
else:
    if mw2_pulse_shape != 'Square':
        print 'no valid pulses defined, using Square pulse params'
    mw2_fast_pi_length, mw2_fast_pi_amp, mw2_fast_pi2_length, mw2_fast_pi2_amp = mw2_Square_pi_length, mw2_Square_pi_amp, mw2_Square_pi2_length, mw2_Square_pi2_amp
    

f_mod_0  = cfg['samples']['111_1_sil18']['mw_mod_freq']

cfg['protocols']['111_1_sil18']['pulses'] ={
    'MW_modulation_frequency'   :   f_mod_0,
    'MW_switch_channel'         :  'MW_switch',#'None',  ### if you want to activate the switch, put to MW_switch

    'DESR_pulse_duration'       : 3e-6,
    'DESR_pulse_amplitude'      : 0.01,
    'X_phase'                   :   90,
    'Y_phase'                   :    0,

    # 'C13_X_phase' :0,
    # 'C13_Y_phase' :90,

    'C13_X_phase' :0,
    'C13_Y_phase' :270,

    ##############
    # Pulse type #
    ##############
    
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
'Ex_SP_amplitude'           :           Ex_SP_amplitude,   #15e-9,#15e-9,    #18e-9
'A_SP_amplitude_before_MBI' :           0,    #does not seem to work yet?
'SP_E_duration'             :           50, #50     #Duration for both Ex and A spin pumping
    #MBI readout power and duration
'Ex_MBI_amplitude'          :           0.65e-9,
'MBI_duration'              :           10,

    #Repump after succesfull MBI
'repump_after_MBI_duration' :           [200], 
'repump_after_MBI_A_amplitude':         [12e-9],#8 #12 #18e-9
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

    #############################
    ### C13  init and control ###
    #############################

cfg['protocols']['111_1_sil18']['AdwinSSRO+C13'] = {


### wait to mitigate heating?
#'wait_between_runs':                    0, ### bool operator, set to one to wait for the 'Shutter_safety_time'

#C13-MBI  
'C13_MBI_threshold_list':               [1],
'C13_MBI_RO_duration':                  40,#160,  
'E_C13_MBI_RO_amplitude':               0.05e-9, #this was 0.3e-9 NK 20150316
'SP_duration_after_C13':                30, #300 in case of swap init! 
'A_SP_amplitude_after_C13_MBI':         8e-9, # was 15e-9
'E_SP_amplitude_after_C13_MBI':         0*3e-9,
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
'min_dec_tau'         :     cfg['protocols']['111_1_sil18']['pulses']['fast_pi_duration'],#20e-9 + cfg['protocols']['111_1_sil18']['pulses']['fast_pi_duration'], 
'max_dec_tau'         :     0.4e-6, #2.5e-6,#Based on measurement for fingerprint at low tau
'dec_pulse_multiple'  :     4,      #4.

# Memory entanglement sequence parameters
'optical_pi_AOM_amplitude' :     0.5,
'optical_pi_AOM_duration' :      200e-9,
'optical_pi_AOM_delay' :         300e-9,
'do_optical_pi' :                True,
'initial_MW_pulse':           'pi' #'pi', 'no_pulse'            
}

    #############################
        ### RF control ###
    #############################

cfg['protocols']['111_1_sil18']['RFTest'] = {
'RF_pulse_frequency': 400e3
}

