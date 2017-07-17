'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 2
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
' Bookmarks                      = 3,3,16,16,22,22,149,149,151,151,437,437,685,685,686,686,734,734,871,871,937,937,1103,1104,1105,1108,1109
'<Header End>
' Purification sequence, as sketched in the purification/planning folder
' AR2016
'
' We use two setups. Each adwin is connected to its own awg jump trigger.
' Each setup gets a parameter 'is_master' that determines whether it is the Master (who controls communication) or the Slave (who waits for the other guy)
' The master AWG triggers the slave awg. Tpo this end, there's a hardware local <-> nonlocal switch
' Two channels are used for communication between adwins, one to signal success and one to signal failure.
' 
' 
' modes:
' 100 : ADWIN communication
' 200 : dynamical stop SSRO

'   0 : CR check
'   1 : E spin pumping into ms=+/-1
'   2 : MBI of one carbon spin
'   3 : Carbon init successful --> adwin communication?
'   31: Send AWG trigger in case of success on both sides.
'   4 : run entanglement sequence and count reps while waiting for PLU success signal
'   5 : wait for the electron Carbon swap to be done and then read out the electron if this is specified in the msmt parameters. Go to adwin communication in that case
'   51: send awg trigger in case of successful swap.
'   6 : save SSRO after SWAP result, run entanglement sequence and count reps while waiting for PLU success signal
'   7 : Phase synchronisation
'   8 : Purification gate
'   9 : Tomo gate
'  10 : Save result
'  11 : in case of electron RO only
'  12 : Parameter reinitialization


#INCLUDE ADwinPro_All.inc
#INCLUDE ..\adwin_pro_2\configuration.inc
#INCLUDE ..\adwin_pro_2\cr_mod_Bell.inc
#INCLUDE ..\adwin_pro_2\control_tico_delay_line.inc
'#INCLUDE .\cr.inc
'#INCLUDE .\cr_mod_Bell.inc
#INCLUDE math.inc

' #DEFINE max_repetitions is defined as 500000 in cr check. Could be reduced to save memory
#DEFINE max_purification_repetitions    500000 ' high number needed to have good statistics in the repump_speed calibration measurement
#DEFINE max_SP_bins                     2000  
#DEFINE max_nuclei                      6
#DEFINE phase_feedback_resolution_steps 360
#DEFINE phase_feedback_resolution       1.0

'init
DIM DATA_20[100] AS LONG   ' integer parameters from python
DIM DATA_21[100] AS FLOAT  ' float parameters from python

'return data
''' commented out data is currently 
'data 22 is the cr result before the sequence
'data 23 is the first cr result after the sequence
'DIM DATA_24[max_purification_repetitions] AS LONG ' number of MBI attempts needed in the successful cycle
'DIM DATA_25[max_purification_repetitions] AS LONG ' number of cycles before success
'26 is used in cr for 'statistics'
'DIM DATA_27[max_purification_repetitions] AS LONG ' SSRO result after mbi / swap step
'30 ' CR integer parameters
'31 CR float parameters
'DIM DATA_37[max_purification_repetitions] AS LONG ' SSRO_after_electron_carbon_SWAP_result ' old

DIM DATA_29[max_SP_bins] AS LONG AT DM_LOCAL    ' SP counts
DIM DATA_100[max_purification_repetitions] AS LONG at DRAM_Extern' Phase_correction_repetitions needed to correct the phase of the carbon 
DIM DATA_101[max_purification_repetitions] AS LONG at DRAM_Extern' time spent for communication between adwins 
DIM DATA_102[max_purification_repetitions] AS LONG at DRAM_Extern' Information which how many AWG attempts lie between successful events
DIM DATA_103[max_purification_repetitions] AS LONG at DRAM_Extern' number of repetitions until the first succesful entanglement attempt 
DIM DATA_104[max_purification_repetitions] AS LONG at DRAM_Extern' number of repetitions after swapping until the second succesful entanglement attempt 
DIM DATA_105[max_purification_repetitions] AS LONG at DRAM_Extern ' SSRO counts electron readout after purification gate 
DIM DATA_106[max_purification_repetitions] AS LONG at DRAM_Extern' SSRO counts carbon spin readout after tomography 
DIM DATA_107[max_purification_repetitions] AS LONG at DRAM_Extern' SSRO counts last electron spin readout performed in the adwin seuqnece 
DIM DATA_108[max_purification_repetitions][max_nuclei] as FLOAT at DRAM_Extern' required phase feedback on the nuclear spin. mainly for debugging 
' DIM DATA_109[max_purification_repetitions] AS FLOAT at DRAM_Extern' minimum achievable phase deviation
' DIM DATA_110[100] AS FLOAT ' carbon offset phases for dynamic phase feedback via the adwin
' DIM DATA_111[360] AS LONG at DRAM_Extern' lookup table for number of repetitions
' DIM DATA_112[360] as FLOAT at DRAM_Extern' lookup table for min deviation 
' DIM DATA_113[600] AS LONG at DRAM_Extern' lookup table for phase to compensate

DIM DATA_109[max_purification_repetitions][max_nuclei] AS LONG AT DRAM_Extern ' feedback delay setting
DIM DATA_124[max_purification_repetitions] AS LONG AT DRAM_Extern ' nuclear phase offset sweep
DIM DATA_125[max_purification_repetitions] AS LONG AT DRAM_Extern ' sweep delay cycles

DIM DATA_114[max_purification_repetitions] AS LONG at DRAM_Extern' invalid data marker

' JS Debug stuff

#DEFINE overlong_cycles_per_mode_OUT  DATA_115
#DEFINE max_modes                 255

DIM overlong_cycles_per_mode[max_modes] AS LONG AT DM_LOCAL

DIM overlong_cycles_per_mode_OUT[max_modes] AS LONG AT DRAM_EXTERN

DIM current_mode AS LONG
DIM start_time AS LONG
DIM overlong_cycle_threshold AS LONG

#DEFINE mode_flowchart_OUT            DATA_110
#DEFINE mode_flowchart_cycles_OUT     DATA_111
#DEFINE max_flowchart_modes       200

DIM mode_flowchart[max_flowchart_modes] AS LONG AT DM_LOCAL
DIM mode_flowchart_cycles[max_flowchart_modes] AS LONG AT DM_LOCAL

DIM mode_flowchart_OUT[max_flowchart_modes] AS LONG AT DRAM_EXTERN
DIM mode_flowchart_cycles_OUT[max_flowchart_modes] AS LONG AT DRAM_EXTERN

#DEFINE flowchart_index             Par_50
' DIM flowchart_index AS LONG

' JS Nuclear stuff

#DEFINE nuclear_frequencies_IN         DATA_120
#DEFINE nuclear_phases_OUT             DATA_121
#DEFINE nuclear_phases_per_seqrep_IN   DATA_122
#DEFINE nuclear_phases_offset_IN       DATA_123

DIM nuclear_frequencies[max_nuclei] AS FLOAT AT DM_LOCAL ' carbon frequencies
DIM nuclear_phases[max_nuclei] AS FLOAT AT DM_LOCAL ' carbon phases
DIM nuclear_phases_per_seqrep[max_nuclei] AS FLOAT AT DM_LOCAL
DIM nuclear_phases_offset[max_nuclei] AS FLOAT AT DM_LOCAL

DIM nuclear_frequencies_IN[max_nuclei] AS FLOAT AT DRAM_EXTERN
DIM nuclear_phases_OUT[max_nuclei] AS FLOAT AT DRAM_EXTERN
DIM nuclear_phases_per_seqrep_IN[max_nuclei] AS FLOAT AT DRAM_EXTERN
DIM nuclear_phases_offset_IN[max_nuclei] AS FLOAT AT DRAM_EXTERN

DIM excess_phase_360s AS LONG AT DM_LOCAL

DIM phase_compensation_delay_cycles[2160] AS LONG AT DM_LOCAL ' max_nuclei*phase_resolution_steps = 2160
DIM phase_compensation_feedback_times[2160]  AS FLOAT AT DM_LOCAL

' these parameters are used for data initialization.
DIM Initializer[100] as LONG AT EM_LOCAL ' this array is used for initialization purposes and stored in the local memory of the adwin 
DIM InitializerFloat[100] AS FLOAT AT EM_LOCAL
DIM array_step as LONG

'general paramters
DIM cycle_duration AS LONG 'repetition rate of the event structure. Typically 1us
DIM repetition_counter, No_of_sequence_repetitions, success_event_counter AS LONG 'counts how many repetitions of the experiment have been done
DIM timer, wait_time, mode, i, j AS LONG 
DIM SP_duration AS LONG
DIM wait_after_pulse_duration AS LONG
DIM CR_result, first_CR AS LONG
DIM SSRO_result AS LONG
DIM Dynamical_stop_ssro_threshold, Dynamical_stop_ssro_duration, Success_of_SSRO_is_ms0 AS LONG
DIM digin_this_cycle AS long
DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM time_spent_in_state_preparation, time_spent_in_sequence, time_spent_in_communication as LONG
DIM duty_cycle as FLOAT

' Channels & triggers
dim AWG_done_was_low, AWG_repcount_was_low, PLU_event_di_was_high, master_slave_awg_trigger_delay as long
DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_repcount_DI_channel, AWG_event_jump_DO_channel, AWG_done_DI_pattern, AWG_repcount_DI_pattern AS LONG
DIM PLU_event_di_channel, PLU_event_di_pattern, PLU_which_di_channel, PLU_which_di_pattern AS LONG
dim sync_trigger_counter_channel, sync_trigger_counter_pattern as long
DIM invalid_data_marker_do_channel AS LONG

' MBI
dim mbi_timer, trying_mbi as long
DIM old_counts, counts AS LONG
DIM E_MBI_voltage AS FLOAT
DIM is_mbi_readout as long
DIM MBI_starts, MBI_failed AS LONG
dim current_MBI_attempt, MBI_attempts_before_CR as long
DIM C13_MBI_RO_duration, RO_duration as long 
DIM purify_RO_is_MBI_RO as long
DIM number_of_C_init_ROs, number_of_C_encoding_ROs AS LONG
DIM current_C_init_RO, current_C_encoding_RO AS LONG

' Phase compensation
DIM phase_to_compensate, total_phase_offset_after_sequence AS FLOAT
DIM phase_to_calculate, phase_compensation_repetitions, required_phase_compensation_repetitions,phase_correct_max_reps, phase_repetitions as long
DIM AWG_sequence_repetitions_first_attempt, AWG_sequence_repetitions_second_attempt as long

DIM number_of_dps_nuclei, current_feedback_nucleus AS LONG
DIM nuclear_feedback_angle, nuclear_feedback_time, nuclear_offset_sweep_value AS FLOAT
DIM delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_trigger_DO_channel AS LONG
DIM minimal_delay_cycles, do_phase_fb_delayline, do_sweep_delay_cycles, delay_feedback_N AS LONG
DIM delay_time_offset, delay_feedback_target_phase, delay_feedback_static_dec_duration AS FLOAT
DIM phase_feedback_index, nuclear_feedback_index, nuclear_feedback_cycles AS LONG
DIM do_phase_offset_sweep AS LONG
DIM delay_HH_trigger_DO_channel, do_HH_trigger AS LONG

DIM dedicate_next_cycle_to_calculations AS LONG
DIM requested_calculations AS LONG
#DEFINE REQ_CALC_NONE                                           0
#DEFINE REQ_CALC_UPDATE_ON_LDE_ATTEMPT                          1
#DEFINE REQ_CALC_UPDATE_ON_DELAY_TIME                           2
#DEFINE REQ_CALC_SET_DELAY_LINE_FOR_PHASE_CORRECTION            3
#DEFINE REQ_CALC_SET_DELAY_LINE_CYCLES_FROM_SWEEP               4
#DEFINE REQ_CALC_INIT_PHASES_OFFSET                             5

' Communication with other Adwin
DIM remote_adwin_di_success_channel, remote_adwin_di_success_pattern, remote_adwin_di_fail_channel, remote_adwin_di_fail_pattern as long
DIM remote_adwin_do_success_channel, remote_adwin_do_fail_channel, remote_awg_trigger_channel  as long
DIM local_success, remote_success, local_fail, remote_fail, combined_success as long
DIM success_mode_after_adwin_comm, fail_mode_after_adwin_comm as long
DIM success_mode_after_SSRO, fail_mode_after_SSRO as long
DIM adwin_comm_safety_cycles as long 'msmt param that tells how long the adwins should wait to guarantee bidirectional communication is successful
DIM adwin_comm_timeout_cycles, wait_for_awg_done_timeout_cycles as long ' if one side fails completely, the other can go on
DIM adwin_comm_done, adwin_timeout_requested as long
DIM n_of_comm_timeouts, is_two_setup_experiment as long
DIM PLU_during_LDE,LDE_1_is_init as long
DIM is_master,cumulative_awg_counts as long

' Sweeping carbon phases in the adwin via dynamic feedback
DIM current_ROseq, no_of_sweep_pts as LONG

' Sequence flow control
DIM do_carbon_init, do_C_init_SWAP_wo_SSRO AS LONG
DIM do_LDE_1 AS LONG
DIM do_swap_onto_carbon, do_SSRO_after_electron_carbon_SWAP as long
DIM do_LDE_2, do_phase_correction as long
DIM do_purifying_gate, do_carbon_readout as long

DIM mode_after_spinpumping, mode_after_init, mode_after_LDE, mode_after_LDE_2, mode_after_SWAP, mode_after_purification, mode_after_phase_correction as long

Dim time as long

SUB update_nuclear_phases_from_list(phase_list[])
  ' unfortunately variable indexed array access takes twice as long as constant access
  ' ugly solution: unroll the loop by hand
  
  ' note: max_nuclei is set at 6 now!
  
  nuclear_phases[1] = nuclear_phases[1] + phase_list[1]
  nuclear_phases[2] = nuclear_phases[2] + phase_list[2]
  nuclear_phases[3] = nuclear_phases[3] + phase_list[3]
  nuclear_phases[4] = nuclear_phases[4] + phase_list[4]
  nuclear_phases[5] = nuclear_phases[5] + phase_list[5]
  nuclear_phases[6] = nuclear_phases[6] + phase_list[6]
  
ENDSUB

SUB update_nuclear_phases_from_scalar(phase_scalar)
  ' unfortunately variable indexed array access takes twice as long as constant access
  ' ugly solution: unroll the loop by hand
  
  ' note: max_nuclei is set at 6 now!
  
  nuclear_phases[1] = nuclear_phases[1] + phase_scalar
  nuclear_phases[2] = nuclear_phases[2] + phase_scalar
  nuclear_phases[3] = nuclear_phases[3] + phase_scalar
  nuclear_phases[4] = nuclear_phases[4] + phase_scalar
  nuclear_phases[5] = nuclear_phases[5] + phase_scalar
  nuclear_phases[6] = nuclear_phases[6] + phase_scalar
  
ENDSUB

SUB update_nuclear_phases_from_time(evolution_time)
  ' I also unroll this loop to speed it up
  
  nuclear_phases[1] = nuclear_phases[1] + (evolution_time * nuclear_frequencies[1] * 360)
  nuclear_phases[2] = nuclear_phases[2] + (evolution_time * nuclear_frequencies[2] * 360)
  nuclear_phases[3] = nuclear_phases[3] + (evolution_time * nuclear_frequencies[3] * 360)
  nuclear_phases[4] = nuclear_phases[4] + (evolution_time * nuclear_frequencies[4] * 360)
  nuclear_phases[5] = nuclear_phases[5] + (evolution_time * nuclear_frequencies[5] * 360)
  nuclear_phases[6] = nuclear_phases[6] + (evolution_time * nuclear_frequencies[6] * 360)  
  
ENDSUB

SUB modulo_nuclear_phases() ' takes 122 cycles
  
  ' converting the floating point answer to a long truncates the decimal part, exactly what we want
  excess_phase_360s = nuclear_phases[1] / 360
  nuclear_phases[1] = nuclear_phases[1] - (excess_phase_360s * 360)
  
  excess_phase_360s = nuclear_phases[2] / 360
  nuclear_phases[2] = nuclear_phases[2] - (excess_phase_360s * 360)  
  
  excess_phase_360s = nuclear_phases[3] / 360
  nuclear_phases[3] = nuclear_phases[3] - (excess_phase_360s * 360)  
    
  excess_phase_360s = nuclear_phases[4] / 360
  nuclear_phases[4] = nuclear_phases[4] - (excess_phase_360s * 360)  
    
  excess_phase_360s = nuclear_phases[5] / 360
  nuclear_phases[5] = nuclear_phases[5] - (excess_phase_360s * 360)  
    
  excess_phase_360s = nuclear_phases[6] / 360
  nuclear_phases[6] = nuclear_phases[6] - (excess_phase_360s * 360)  
ENDSUB

'FUNCTION get_nuclear_feedback_index(phase_to_compensate, current_feedback_nucleus) AS LONG
'  
'  get_nuclear_feedback_index = Round(phase_to_compensate / phase_feedback_resolution) + 1
'  IF (get_nuclear_feedback_index > phase_feedback_resolution_steps) THEN
'    get_nuclear_feedback_index = get_nuclear_feedback_index - phase_feedback_resolution_steps
'  ENDIF
'  
'  get_nuclear_feedback_index = get_nuclear_feedback_index + (current_feedback_nucleus - 1) * phase_feedback_resolution_steps
'ENDFUNCTION

FUNCTION get_phase_feedback_index(phase_to_compensate) AS LONG
  get_phase_feedback_index = Round(phase_to_compensate / phase_feedback_resolution) + 1
  IF (get_phase_feedback_index > phase_feedback_resolution_steps) THEN
    get_phase_feedback_index = get_phase_feedback_index - phase_feedback_resolution_steps
  ENDIF
ENDFUNCTION

FUNCTION get_nuclear_feedback_index(phase_index, current_feedback_nucleus) AS LONG
  get_nuclear_feedback_index = phase_index + (current_feedback_nucleus - 1) * phase_feedback_resolution_steps
ENDFUNCTION




SUB reset_nuclear_phases()
  MemCpy(InitializerFloat[1], nuclear_phases[1], max_nuclei)
  '  FOR i = 1 TO max_nuclei
  '    nuclear_phases[i] = 0
  '  NEXT i
ENDSUB

SUB init_nuclear_phases_offset()
  reset_nuclear_phases()
  update_nuclear_phases_from_list(nuclear_phases_offset)
  
  IF (do_phase_offset_sweep > 0) THEN
    nuclear_offset_sweep_value = DATA_124[current_ROseq]
    IF (nuclear_offset_sweep_value < 0) THEN
      nuclear_offset_sweep_value = nuclear_offset_sweep_value + 360.0
    ENDIF
    INC(Par_65)
    FPar_38 = nuclear_offset_sweep_value
    update_nuclear_phases_from_scalar(nuclear_offset_sweep_value)
    modulo_nuclear_phases()
  ENDIF
ENDSUB


SUB sleep_for_trigger()
  ' 6 NOPs at 3.333 ns per operation corresponds to a waiting time of 20 ns
  ' let's make it 9 (30 ns) to be sure
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  ' CPU_SLEEP(9)
ENDSUB

SUB timer_tic()
  Par_39 = Read_Timer()
ENDSUB

SUB timer_toc()
  Par_40 = Read_Timer()
  Par_41 = Par_40 - Par_39 - 2 ' correct for the duration of the Read_Timer() call
ENDSUB

SUB strobe_tictoc()
  Par_42 = Par_43
  Par_43 = Read_Timer()
  Par_44 = Par_43 - Par_42
ENDSUB

SUB AWG_start_trigger()
  P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
  ' CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
  sleep_for_trigger()
  P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0) 
ENDSUB



LOWINIT:    'change to LOWinit which I heard prevents adwin memory crashes
  
  init_CR()
  
  n_of_comm_timeouts = 0 ' used for debugging, goes to a par   
  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 0 ' adwin arrays start at 1, but this counter starts at 0 -> we have to write to rep counter +1 all the time
  first_CR            = 0 ' this variable determines whether or not the CR after result is stored 
  wait_time           = 0
  current_MBI_attempt = 1
  digin_this_cycle    = 0
  is_mbi_readout      = 0
  RO_duration         = 0
  cumulative_awg_counts   = 0
  purify_RO_is_MBI_RO = 1
  
  time_spent_in_state_preparation =0
  time_spent_in_communication =0 
  time_spent_in_sequence =0
  duty_cycle = 0
  
  AWG_done_was_low = 1
  AWG_repcount_was_low =1
  AWG_sequence_repetitions_first_attempt =0
  AWG_sequence_repetitions_second_attempt =0
  phase_compensation_repetitions =0
  required_phase_compensation_repetitions =0
  phase_to_compensate =0
  total_phase_offset_after_sequence =0
  current_feedback_nucleus = 0
  
  local_success = 0
  remote_success = 0
  remote_fail = 0
  local_fail = 0
  combined_success = 0
  adwin_comm_done = 0
  adwin_timeout_requested = 0
  success_mode_after_adwin_comm = 1 'SpinPumping
  fail_mode_after_adwin_comm = 0 'CR check
  success_mode_after_SSRO = 0
  fail_mode_after_SSRO = 0
  current_C_init_RO = 0
  current_C_encoding_RO = 0
      
  success_event_counter = 0
  Success_of_SSRO_is_ms0 = 1 'usually, we condition on getting a click
  SSRO_result = 0
  
  mode = 0
  timer = 0
  mbi_timer = 0
  trying_mbi = 0
      
  current_ROseq = 1
''''''''''''''''''''''''''''''''''''''
  'read params from python script 
''''''''''''''''''''''''''''''''''''''
  cycle_duration               = DATA_20[1]
  SP_duration                  = DATA_20[2]
  wait_after_pulse_duration    = DATA_20[3] 'Time to wait after turning off a laser pulse to ensure it is really off
  MBI_attempts_before_CR       = DATA_20[4] 
  Dynamical_stop_ssro_threshold= DATA_20[5]
  Dynamical_stop_ssro_duration = DATA_20[6]
  is_master                    = DATA_20[7]
  is_two_setup_experiment      = Data_20[8]
  do_carbon_init               = DATA_20[9]
  do_C_init_SWAP_wo_SSRO       = DATA_20[10]
  do_swap_onto_carbon          = DATA_20[11]
  do_SSRO_after_electron_carbon_SWAP = DATA_20[12]
  do_LDE_2                     = DATA_20[13]
  do_phase_correction          = DATA_20[14]
  do_purifying_gate            = DATA_20[15]
  do_carbon_readout            = DATA_20[16]
  PLU_event_di_channel         = DATA_20[17]
  PLU_which_di_channel         = DATA_20[18]
  AWG_start_DO_channel         = DATA_20[19]
  AWG_done_DI_channel          = DATA_20[20]
  wait_for_awg_done_timeout_cycles = DATA_20[21]
  AWG_event_jump_DO_channel    = DATA_20[22]
  AWG_repcount_DI_channel      = DATA_20[23]
  remote_adwin_di_success_channel  = DATA_20[24]
  remote_adwin_di_fail_channel     = DATA_20[25]
  remote_adwin_do_success_channel  = DATA_20[26]
  remote_adwin_do_fail_channel     = DATA_20[27]
  adwin_comm_safety_cycles         = DATA_20[28]
  adwin_comm_timeout_cycles        = DATA_20[29]
  remote_awg_trigger_channel       = DATA_20[30]
  invalid_data_marker_do_channel   = DATA_20[31] 'marks timeharp data invalid
  No_of_sequence_repetitions       = DATA_20[32] 'how often do we run the sequence
  C13_MBI_RO_duration              = DATA_20[33] 'C13_MBI_RO_duration
  master_slave_awg_trigger_delay   = DATA_20[34]
  phase_correct_max_reps           = DATA_20[35]
  PLU_during_LDE                   = DATA_20[36]
  no_of_sweep_pts                  = DATA_20[37] ' number of adwin related sweep pts
  LDE_1_is_init                    = DATA_20[38] ' is the first LDE element for init? Then ignore the PLU
  delay_trigger_DI_channel         = DATA_20[39]
  delay_trigger_DO_channel         = DATA_20[40]
  number_of_dps_nuclei             = DATA_20[41]
  minimal_delay_cycles             = DATA_20[42]
  do_phase_fb_delayline            = DATA_20[43]
  do_sweep_delay_cycles            = DATA_20[44]
  delay_feedback_N                 = DATA_20[45]
  number_of_C_init_ROs             = DATA_20[46]
  number_of_C_encoding_ROs         = DATA_20[47]
  do_LDE_1                         = DATA_20[48]
  do_phase_offset_sweep            = DATA_20[49]
  delay_HH_trigger_DO_channel      = DATA_20[50]
  do_HH_trigger                    = DATA_20[51]
  
  ' float params from python
  E_SP_voltage                              = DATA_21[1] 'E spin pumping before MBI
  E_MBI_voltage                             = DATA_21[2]  
  A_SP_voltage                              = DATA_21[3]
  E_RO_voltage                              = DATA_21[4]
  A_RO_voltage                              = DATA_21[5]
  delay_time_offset                         = DATA_21[6]
  delay_feedback_target_phase               = DATA_21[7]
  delay_feedback_static_dec_duration       = DATA_21[8]
  
  ' phase_per_sequence_repetition     = DATA_21[6] ' how much phase do we acquire per repetition
  ' phase_per_compensation_repetition = DATA_21[7] '
  ' phase_feedback_resolution = DATA_21[8]
   
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  AWG_repcount_DI_pattern = 2 ^ AWG_repcount_DI_channel
  PLU_event_di_pattern = 2 ^ PLU_event_di_channel
  PLU_which_di_pattern = 2 ^ PLU_which_di_channel
  remote_adwin_di_success_pattern = 2^ remote_adwin_di_success_channel
  remote_adwin_di_fail_pattern = 2^ remote_adwin_di_fail_channel
  sync_trigger_counter_channel = 3
  sync_trigger_counter_pattern = 2 ^ (sync_trigger_counter_channel - 1)
  delay_trigger_DI_pattern = 2 ^ delay_trigger_DI_channel
  
  
''''''''''''''''''''''''''''''''''''''
  ' initialize the data arrays. set to -1 to discriminate between 0-readout and no-readout
''''''''''''''''''''''''''''''''''''''
 
  '  ' enter desired values into the initializer array
  FOR i = 1 TO 100
    Initializer[i] = -1
    InitializerFloat[i] = 0.0
  NEXT i
  '  
  '  
  '  ' note: the MemCpy function only works for T11 processors.
  '  ' this is a faster way of filling up global data arrays in the external memory. See Adbasic manual
  array_step = 1
  FOR i = 1 TO max_purification_repetitions/100' 520 is derived from max_purification_length/100
    MemCpy(Initializer[1],DATA_100[array_step],100)
    MemCpy(Initializer[1],DATA_101[array_step],100)
    MemCpy(Initializer[1],DATA_102[array_step],100)
    MemCpy(Initializer[1],DATA_103[array_step],100)
    MemCpy(Initializer[1],DATA_104[array_step],100)
    MemCpy(Initializer[1],DATA_105[array_step],100)
    MemCpy(Initializer[1],DATA_106[array_step],100)
    MemCpy(Initializer[1],DATA_107[array_step],100)
    MemCpy(Initializer[1],DATA_114[array_step],100)
    
    array_step = array_step + 100
  NEXT i
  
  array_step = 1
  FOR i = 1 TO max_purification_repetitions/10
    MemCpy(InitializerFloat[1],DATA_108[array_step][1],60)
    MemCpy(Initializer[1],DATA_109[array_step][1],60)
    
    array_step = array_step + 10
  NEXT i
  
  'initialize the max_SP_bins
  FOR i = 1 TO max_SP_bins
    DATA_29[i] = 0
  NEXT i
  
  FOR i = 1 TO max_modes
    overlong_cycles_per_mode[i] = -1
  NEXT i
  
  FOR i = 1 TO max_flowchart_modes
    mode_flowchart[i] = -1
    mode_flowchart_cycles[i] = -1
  NEXT i
  
  flowchart_index = 0
  
  
  FOR i = 1 to max_nuclei
    nuclear_frequencies[i] = nuclear_frequencies_IN[i]
    nuclear_phases_per_seqrep[i] = nuclear_phases_per_seqrep_IN[i]
    nuclear_phases_offset[i] = nuclear_phases_offset_IN[i]
  NEXT i
  
  init_nuclear_phases_offset()
  
  FOR i = 1 to number_of_dps_nuclei ' don't calculate the stuff for nuclei slots that are not in use; those have bullshit frequency values that upset the calculation
    FOR j = 1 to phase_feedback_resolution_steps
      ' overrotate by 5 rotations to ensure that the corresponding delay time is longer than the minimal delay time
      ' of course a more elegant (i.e. with less rotation on average) exists but meh for now
      ' note: minimal feedback time is actually twice the minimal delay time (because we delay twice per pulse)
      nuclear_feedback_index = (i-1) * phase_feedback_resolution_steps + j
      
      phase_to_compensate = (j - 1) * phase_feedback_resolution
      nuclear_feedback_angle = delay_feedback_target_phase - phase_to_compensate
      nuclear_feedback_time = nuclear_feedback_angle / (360 * nuclear_frequencies[i]) ' 30 cycles
      
      nuclear_feedback_cycles = tico_delay_line_calculate_cycles(nuclear_feedback_time / (2*delay_feedback_N)) ' two triggers per pulse
      IF (nuclear_feedback_cycles < minimal_delay_cycles) THEN
        Par_40 = delay_feedback_N
        FPar_38 = nuclear_feedback_time
        FPar_39 = delay_feedback_target_phase
        Par_65 = 0DEADBEEFh
        EXIT ' we've arrived at an impossible number of delay cycles, abandon ship!
      ENDIF
      
      phase_compensation_delay_cycles[nuclear_feedback_index] = nuclear_feedback_cycles
      phase_compensation_feedback_times[nuclear_feedback_index] = tico_delay_line_calculate_delay(nuclear_feedback_cycles) * delay_feedback_N * 2.0
    NEXT j
  NEXT i
  
  dedicate_next_cycle_to_calculations = 0
  requested_calculations = REQ_CALC_NONE
  
    
  
  AWG_sequence_repetitions_second_attempt = 0 ' reinit. otherwise error
  
''''''''''''''''''''''''''''
  ' init parameters
''''''''''''''''''''''''''''
  
  Par_60 = timer                  ' time
  Par_61 = mode                   ' current mode
  PAR_63 = 0                      ' stop flag
  PAR_73 = repetition_counter     ' repetition counter
  PAR_74 = 0                      ' MBI failed
  PAR_77 = success_event_counter  ' number of successful runs
  PAR_78 = 0                      ' MBI starts                    
  PAR_80 = 0                      ' n_of timeouts when waiting for AWG done
  PAR_62 = 0                      ' n_of_communication_timeouts for debugging
  PAR_65 = -1 ' for debugging
  par_10 = -1
  par_11 = -1
  par_12 = -1
  par_13 = -1
  par_14 = -1
  par_15 = -1
  PAR_55 = 0                      ' invalid data marker
  Par_62 = 0
  
  Par_40 = -1
  Par_41 = -1
  Par_42 = -1
  Par_43 = -1
  Par_44 = -1
'''''''''''''''''''''''''
  ' flow control: 
'''''''''''''''''''''''''
  if (do_carbon_readout = 1) then
    mode_after_purification = 9 ' Carbon tomography
  else
    if (do_purifying_gate = 1) THEN
      mode_after_purification = 10
      purify_RO_is_MBI_RO = 0
    else
      mode_after_purification = 11 ' wait for trigger then do SSRO
    endif
    
  endif
  
  IF (do_purifying_gate = 1) THEN
    mode_after_phase_correction = 8 ' purifying gate
  ELSE
    mode_after_phase_correction = mode_after_purification ' as defined above
  ENDIF
  
  if ((do_phase_correction=1)) THEN ' JS DLFB: we want to do phase correction anyway ' and (do_purifying_gate = 1)) then ' special case: in the adwin do phase only makes sense in conjunction with do_purify
    mode_after_LDE_2 = 7 'phase correction
  else
    mode_after_LDE_2 = mode_after_phase_correction ' as defined above
  endif
  
  IF (do_LDE_2 =1 ) THEN
    mode_after_swap = 6 ' LDE_2
  ELSE
    mode_after_swap = mode_after_LDE_2 ' as defined above
  ENDIF
  
  if (do_swap_onto_carbon = 1) then
    mode_after_LDE = 5 ' swap onto carbon
  else 
    mode_after_LDE = mode_after_swap ' as defined above
  endif
  
  IF (do_LDE_1=1) THEN
    mode_after_init = 4 ' LDE 1
  ELSE
    mode_after_init = mode_after_LDE
  ENDIF
    
  if (do_carbon_init = 1) then
    mode_after_spinpumping = 2 'MBI
  else
    mode_after_spinpumping = mode_after_init ' LDE 1
  endif


  
'''''''''''''''''''''''''''
  ' define channels etc
'''''''''''''''''''''''''''

  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter_channel, 000010000b) 'configure counter
  P2_CNT_MODE(CTR_MODULE, sync_trigger_counter_channel, 000010000b) 'configure counter

  P2_Digprog(DIO_MODULE,0011b) ' in  is now 16:23   'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel, 0)
  P2_DIGOUT(DIO_MODULE, remote_adwin_do_fail_channel, 0)
  P2_DIGOUT(DIO_MODULE, remote_adwin_do_success_channel, 0)
  
  IF ((do_phase_fb_delayline > 0) OR (do_sweep_delay_cycles > 0)) THEN
    tico_delay_line_init(DIO_MODULE, delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_trigger_DO_channel)
    tico_delay_line_set_enabled(1)
    tico_delay_line_set_cycles(0)
    IF (do_HH_trigger > 0) THEN
      tico_delay_line_init_HH_trigger(do_HH_trigger, delay_HH_trigger_DO_channel) 
    ENDIF
    
  ENDIF
  
   
  processdelay = cycle_duration   ' the event structure is repeated at this period. On T11 processor 300 corresponds to 1us. Can do at most 300 operations in one round.
  
  P2_CNT_CLEAR(CTR_MODULE, sync_trigger_counter_pattern)    'clear and turn on sync trigger counter
  P2_CNT_ENABLE(CTR_MODULE, sync_trigger_counter_pattern)
  
  Par_34 = 0
  Par_35 = 0
  
  current_mode = -1
  overlong_cycle_threshold = cycle_duration - 20  ' cycle_duration - 10 ' 9 cycles seems to be the length of the okay-length cycle branch in the overlong check, +1 to be sure
  

EVENT:
  
  'write information to pars for live monitoring
  PAR_61 = mode   
  Par_60 = timer
  
  IF (current_mode <> mode) THEN  
    inc(flowchart_index)  
    if (flowchart_index > max_flowchart_modes) THEN
      flowchart_index = 1
    endif
    mode_flowchart[flowchart_index] = mode
    mode_flowchart_cycles[flowchart_index] = 0
  endif
                    
  if (flowchart_index > 0) THEN
    inc(mode_flowchart_cycles[flowchart_index])
  endif

  
  current_mode = mode
  start_time = Read_Timer()
  
  IF (dedicate_next_cycle_to_calculations > 0) THEN    
    dedicate_next_cycle_to_calculations = 0
    
    SELECTCASE requested_calculations
        
      CASE REQ_CALC_UPDATE_ON_LDE_ATTEMPT
        update_nuclear_phases_from_list(nuclear_phases_per_seqrep)
        modulo_nuclear_phases()
        
      CASE REQ_CALC_UPDATE_ON_DELAY_TIME
        update_nuclear_phases_from_time(nuclear_feedback_time)
        modulo_nuclear_phases()
        
      CASE REQ_CALC_SET_DELAY_LINE_FOR_PHASE_CORRECTION
        phase_feedback_index = get_phase_feedback_index(nuclear_phases[current_feedback_nucleus])
        nuclear_feedback_index = get_nuclear_feedback_index(phase_feedback_index, current_feedback_nucleus)
        nuclear_feedback_cycles = phase_compensation_delay_cycles[nuclear_feedback_index]
        tico_delay_line_set_cycles(nuclear_feedback_cycles) ' takes +/- 36 cycles
        nuclear_feedback_time = phase_compensation_feedback_times[nuclear_feedback_index]
        DATA_108[repetition_counter + 1][current_feedback_nucleus] = nuclear_phases[current_feedback_nucleus]
        DATA_109[repetition_counter + 1][current_feedback_nucleus] = nuclear_feedback_cycles 
        
        dedicate_next_cycle_to_calculations = 1
        requested_calculations = REQ_CALC_UPDATE_ON_DELAY_TIME
      
      CASE REQ_CALC_SET_DELAY_LINE_CYCLES_FROM_SWEEP
        nuclear_feedback_cycles = DATA_125[current_ROseq]
        tico_delay_line_set_cycles(nuclear_feedback_cycles)
        
      CASE REQ_CALC_INIT_PHASES_OFFSET
        init_nuclear_phases_offset()
        
    ENDSELECT
   
    ' INC(timer)
  ELSE
      
    
    IF (wait_time > 0)  THEN
      wait_time = wait_time - 1
    ELSE
    
      SELECTCASE mode  
        
        CASE 200  ' dynamical stop RO.     
                     
          IF (timer = 0) THEN 
            P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE, counter_pattern OR sync_trigger_counter_pattern)    'turn on counter
            if (is_mbi_readout>0) then
              P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
              RO_duration = C13_MBI_RO_duration
            else
              P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
              RO_duration = dynamical_stop_SSRO_duration
            endif
          ELSE
            counts = P2_CNT_READ(CTR_MODULE, counter_channel) 'read counter
            IF (counts >= Dynamical_stop_ssro_threshold) THEN ' photon detected
              P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE, sync_trigger_counter_pattern)  ' disable photon counter, keep sync trigger counter on
              wait_time = RO_duration - timer ' make sure the SSRO element always has the same length (even in success case) to keep track of the carbon phase xxx to do: is this still accurate to the us?
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
              SSRO_result = 1
              DATA_107[repetition_counter+1] = SSRO_result 'save as last electron readout
              if (Success_of_SSRO_is_ms0>0) then ' Success_of_SSRO_is_ms0 is usually 1, but could be dynamically inverted here
                local_success = 1 
                local_fail = 0
                mode = success_mode_after_SSRO
              else 
                local_success = 0
                local_fail = 1
                mode = fail_mode_after_SSRO
              endif 
            ELSE 'no photon detected
              SSRO_result = 0
              DATA_107[repetition_counter+1] = SSRO_result 'save as last electron readout
              if (timer = RO_duration) then ' no count after ssro duration -> failed  xxx to do: is this still accurate to the us?
                P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
                P2_CNT_ENABLE(CTR_MODULE,sync_trigger_counter_pattern) 'disable photon counter, keep sync trigger counter on
                time_spent_in_sequence = time_spent_in_sequence + timer
                timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
                IF (Success_of_SSRO_is_ms0 = 0) THEN
                  local_success = 1 'remember for adwin communication in next mode. Success_of_SSRO_is_ms0 is usually 1, but could be inverted here
                  local_fail =0
                  mode = success_mode_after_SSRO
                ELSE 
                  local_success = 0
                  local_fail = 1
                  mode = fail_mode_after_SSRO
                ENDIF
              endif
            ENDIF

          ENDIF
   

        CASE 0 'CR check
      
          cr_result = CR_check(first_CR,repetition_counter) ' do CR check. if first_CR is high, the result will be saved as CR_after. 
          'first_CR = 0 ' forget for next repetition... is done in cr_mod.inc
        
          'check for break put after such that the last run records a CR_after result
          IF (((Par_63 > 0) or (repetition_counter >= max_repetitions)) or (repetition_counter >= No_of_sequence_repetitions)) THEN ' stop signal received: stop the process
            END
          ENDIF

          if ( cr_result > 0 ) then
            ' In case the result is not positive, the CR check will be repeated/continued
            time_spent_in_state_preparation = time_spent_in_state_preparation + timer
            timer = -1     
            mode = 1 'go to spin pumping directly
            wait_time = 10 ' do 10 cycles of nothing to give the adwin time to catch up on any overlong CR cycles
          endif  
        
        
        
        CASE 1    ' E spin pumping
        
          IF (timer = 0) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768) ' or turn on A laser
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)                        ' clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern OR sync_trigger_counter_pattern)                       ' turn on counter
            old_counts = 0
          
          ELSE ' this branch takes 186 - 190 cycles
            counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            DATA_29[timer] = DATA_29[timer] + counts - old_counts    ' for spinpumping arrival time histogram
            old_counts = counts
                    
            IF (timer = SP_duration) THEN
              P2_CNT_ENABLE(CTR_MODULE,sync_trigger_counter_pattern) ' disable photon counter, keep sync trigger cuounter on
              P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
              P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser      
              mode = mode_after_spinpumping
              wait_time = wait_after_pulse_duration 'wait a certain number of cycles to make sure the lasers are really off
              time_spent_in_state_preparation = time_spent_in_state_preparation + timer
              timer = -1
              
              IF (do_sweep_delay_cycles > 0) THEN
                dedicate_next_cycle_to_calculations = 1
                requested_calculations = REQ_CALC_SET_DELAY_LINE_CYCLES_FROM_SWEEP
              ENDIF
              
            ENDIF
          ENDIF
        
         
          
        CASE 2    ' Carbon init, either MBI or SWAP (with SSRO afterwards or not)
          ' We first need to send a trigger command to the AWGs on both sides that tells them to start the gate sequence
          ' in local mode, this is done by each ADWIN, in remote mode the Master Adwin also triggers the slave AWG
        
          IF (timer=0) THEN   ' MBI sequence starts
            INC(MBI_starts)
            PAR_78 = MBI_starts          
            ' Logic: If local or master, own awg is triggered. If nonlocal and slave, AWG is triggered by master's awg to minimize jitter
            AWG_start_trigger()
          
          
          ELSE ' AWG in MBI sequence is running
            ' Detect if the AWG is done and has sent a trigger; this construction prevents multiple adwin jumps when the awg sends a looooong pulse
            digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE)
            if ((digin_this_cycle and AWG_done_DI_pattern)>0) then ' AWG has done the MW pulses -> go to next step
              if (awg_done_was_low >0) then
                INC(current_C_init_RO)
                time_spent_in_state_preparation = time_spent_in_state_preparation + timer
                timer = -1
                IF (do_C_init_SWAP_wo_SSRO > 0) THEN 'no SSRO and no communication required
                  mode = 3 'go to MBI verification. Is required to send the jump trigger that signals Adwin is done with SSRO
                  local_success = 1
                  local_fail = 0
                  'SSRO_result = -2 ' for debugging
                ELSE
                  success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
                  mode = 200 ' go to dynamical stop RO
                  is_mbi_readout = 1 ' ... in MBI mode
                  success_mode_after_SSRO = 3 ' Check MBI success
                  fail_mode_after_SSRO = 3 ' Check MBI success
                ENDIF 
                awg_done_was_low = 0 
              endif
                
            else ' AWG not done yet
              awg_done_was_low = 1
              IF ( timer > wait_for_awg_done_timeout_cycles) THEN
                inc(PAR_80) ' signal the we have an awg timeout
                END ' terminate the process
              ENDIF  
            endif 
          ENDIF
        
        CASE 3 ' MBI SSRO done; check MBI success
          IF ( (local_success>0) OR (do_C_init_SWAP_wo_SSRO >0) ) THEN ' successful MBI readout
            'trying_mbi = 0
            mbi_timer = 0
            is_mbi_readout = 0
            current_MBI_attempt = 1 ' reset counter
            mode = 31 ' entanglement sequence
 
          ELSE ' MBI failed. Retry or communicate?
            INC(MBI_failed)
            PAR_74 = MBI_failed 'for debugging
            current_C_init_RO = 0 ' go back to initialising the first carbon

            IF (current_MBI_attempt = MBI_attempts_before_CR) then ' failed too often -> communicate failure (if in remote mode) and then go to CR
              current_MBI_attempt = 1 'reset counter
              mode = 0 ' directly back to CR
            ELSE 
              mode = 1 ' retry spinpumping and then MBI
              INC(current_MBI_attempt)
            ENDIF 
          ENDIF  
          time_spent_in_state_preparation = time_spent_in_state_preparation + timer
          timer = -1      
        
        CASE 31 'tell the AWG to jump in case of a succesful MBI attempts
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to the entanglement sequence
          ' CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          sleep_for_trigger()
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          
          IF (current_C_init_RO = number_of_C_init_ROs) THEN
            ' the last carbon has been initialised, move on
            mode = mode_after_init
            timer = -1
          ELSE
            ' we still have some carbons to initialize
            mode = 2
            timer = 0 ' skip the AWG triggering for timer=0
          ENDIF
          
        
        CASE 4    '  wait and count repetitions of the entanglement AWG sequence
          ' the awg gives repeated adwin sync pulses, which are counted. In the case of an entanglement event, we get a plu signal.
          ' In case there's no entanglement event, we get the awg done trigger, a pulse of which we detect the falling edge.
          ' In case this is a single-setup (e.g. phase calibration) measurement, we go on, 
          ' otherwise getting a done trigger means failure of the sequence and we go to CR cheking
          ' NOTE, if the AWG sequence is to short (close to a us, then it is possible that the time the signal is low is missed.
          IF (timer = 0) THEN ' first run: send triggers
            AWG_start_trigger()
          ENDIF
        
          ' monitor inputs
          digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE)
        
          if ((digin_this_cycle AND AWG_repcount_DI_pattern) >0) then 
            IF (AWG_repcount_was_low = 1) THEN ' awg has switched to high. this construction prevents double counts if the awg signal is long
              inc(AWG_sequence_repetitions_first_attempt) ' increase the number of attempts counter
            ENDIF
            AWG_repcount_was_low = 0
          else
            AWG_repcount_was_low = 1
          endif
          
        
          IF ((digin_this_cycle AND AWG_done_DI_pattern) > 0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (awg_done_was_low =1) then
              DATA_103[repetition_counter+1] = AWG_sequence_repetitions_first_attempt 'save the result
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              if ((PLU_during_LDE = 0) or (LDE_1_is_init = 1)) then ' this is a single-setup (e.g. phase calibration) measurement. Go on to next mode
                mode = mode_after_LDE
              else ' two setups involved: Done means failure of the sequence
                mode = 12 ' finalize and go to cr check
              endif
            endif 
            awg_done_was_low = 0 ' remember
          ELSE ' awg done is low.
            awg_done_was_low = 1
            if( timer > wait_for_awg_done_timeout_cycles) then
              inc(PAR_80) ' signal that we have an awg timeout
              PAR_30 = digin_this_cycle
              END ' terminate the process
            endif
          ENDIF       
       
        CASE 5  ' wait for the electron Carbon swap to be done and then read out the electron if this is specified in the msmt parameters
          IF (timer =0) THEN
            AWG_start_trigger()          
          endif 
        
        
          IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) >0 )THEN  'awg trigger tells us it is done with the swap sequence.
            time_spent_in_sequence = time_spent_in_sequence + timer
            timer = -1
            if (AWG_done_was_low >0) then ' prevents double jump in case the awg trigger is long
              INC(current_C_encoding_RO)
              IF (do_SSRO_after_electron_carbon_SWAP = 0) then
                mode = 51 ' see flow control
              ELSE
                mode = 200   ' dsSSRO
                is_mbi_readout = 1 ' ... in MBI mode
                Success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it before
                success_mode_after_SSRO = 51 ' see flow control
                fail_mode_after_SSRO = 12 ' finalize and start over
              ENDIF
              awg_done_was_low = 0
            endif
          ELSE ' AWG not done yet, trigger is low
            awg_done_was_low =1
            IF ( timer > wait_for_awg_done_timeout_cycles) THEN
              inc(PAR_80) ' signal the we have an awg timeout
              END ' terminate the process
            ENDIF  
          ENDIF
                
        CASE 51 ' success case of the swap operation. Is only triggered either if adwin comm was succesful or the local swap worked (single setup)
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) 
          ' CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          sleep_for_trigger()
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          
          IF (current_C_encoding_RO = number_of_C_encoding_ROs) THEN
            ' we're done encoding, moving on
            mode = mode_after_swap 'see flow control
            timer = -1
          ELSE
            ' we still have some encoding to do, jumping back to either LDE counting or swap directly
            mode = mode_after_init
            timer = 1
          ENDIF
          
        
        CASE 6    ' save ssro after swap result. Then wait and count repetitions of the entanglement AWG sequence as in case 4
          IF (timer =0) THEN
            'DATA_37[repetition_counter+1] = SSRO_result
            AWG_start_trigger()        
          ENDIF
                
                
          ' monitor inputs
          digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE) ' 71 cycles
                
          if ((digin_this_cycle AND AWG_repcount_DI_pattern) > 0) then 
            IF (AWG_repcount_was_low = 1) THEN ' awg has switched to high. this construction prevents double counts if the awg signal is long
              inc(AWG_sequence_repetitions_second_attempt) ' increase the number of attempts counter
                                      
              ' JS DLFB: pre-emptively adjust the number of delay cycles
              ' we don't have enough processing time left to do that in this round, 
              ' postpone it to the next round
              IF ((do_phase_fb_delayline > 0) AND (do_sweep_delay_cycles = 0)) THEN
                requested_calculations = REQ_CALC_UPDATE_ON_LDE_ATTEMPT
                dedicate_next_cycle_to_calculations = 1
              ENDIF
              
            
            ENDIF
            AWG_repcount_was_low = 0
          else
            AWG_repcount_was_low = 1
          endif
            
          IF ((digin_this_cycle AND AWG_done_di_pattern) >0) THEN  'awg trigger tells us it is done with the entanglement sequence. This means failure of the protocol
            if (awg_done_was_low > 0) then ' switched in this round
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1            
              DATA_104[repetition_counter+1] = AWG_sequence_repetitions_second_attempt 'save the result
              mode = mode_after_LDE_2
            ENDIF
          
            awg_done_was_low = 0  ' remember
          ELSE ' AWG not done yet
            awg_done_was_low = 1
            IF ( timer > wait_for_awg_done_timeout_cycles) THEN
              inc(PAR_80) ' signal the we have an awg timeout
              END ' terminate the process
            ENDIF  
          ENDIF
        
        CASE 7 ' phase correction phase
          ' we receive a trigger from the AWG to set up the delay line for the next carbon
          
                   
          IF (do_phase_fb_delayline > 0) THEN
            if ((timer=0) AND (do_sweep_delay_cycles=0)) THEN
              nuclear_feedback_time = delay_feedback_static_dec_duration
              dedicate_next_cycle_to_calculations = 1
              requested_calculations = REQ_CALC_UPDATE_ON_DELAY_TIME
            ELSE
              digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE) ' 71 cycles
                
              if ((digin_this_cycle AND AWG_repcount_DI_pattern) > 0) then 
                IF (AWG_repcount_was_low = 1) THEN ' awg has switched to high. this construction prevents double counts if the awg signal is long
                  ' if we are doing a fixed sweep of the number of delay cycles, we don't need to anything here anymore, the delay cycles are already set at the beginning of the repetition (case 1)
                  IF (do_sweep_delay_cycles = 0) THEN                    
                    ' we're moving to the next feedback carbon
                    INC(current_feedback_nucleus)
                
                    dedicate_next_cycle_to_calculations = 1
                    requested_calculations = REQ_CALC_SET_DELAY_LINE_FOR_PHASE_CORRECTION
                  
                    ' we want to do the trigger decoupling block update again as well for the next carbon
                    timer = -1
                  ENDIF            
                ENDIF
                AWG_repcount_was_low = 0
              else
                AWG_repcount_was_low = 1
              endif
            
              IF (current_feedback_nucleus = number_of_dps_nuclei) THEN
                ' we're done with setting up feedback cycles
                timer = -1
                mode = mode_after_phase_correction
              ENDIF
            ENDIF
          ELSE
            timer = -1
            mode = mode_after_phase_correction
          ENDIF      
          
        CASE 8 ' Wait until purification gate is done. 
                
          'check the done trigger
          IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)>0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (AWG_done_was_low > 0) then
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
              mode = 200 'go to SSRO
              is_mbi_readout = purify_RO_is_MBI_RO
              success_mode_after_SSRO = mode_after_purification
              fail_mode_after_SSRO = mode_after_purification   
            endif
            AWG_done_was_low = 0
          ELSE ' AWG not done yet
            AWG_done_was_low = 1
            IF ( timer > wait_for_awg_done_timeout_cycles) THEN
              inc(PAR_80) ' signal the we have an awg timeout
              END ' terminate the process
            ENDIF  
          ENDIF
        
        CASE 9 'store the result of the electron readout. Wait for TOMO gate to be done and do SSRO again
          IF (timer=0) THEN
            DATA_105[repetition_counter+1] = SSRO_result    
            if (SSRO_result = 1) then  ' send jump to awg in case the electron readout was ms=0. This is required for accurate gate phases
              P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1)
              ' CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              sleep_for_trigger()
              P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0)
            endif
          ENDIF    
          
          IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)>0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (awg_done_was_low>0) then
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
              mode = 200 'go to SSRO
              is_mbi_readout = 0
              success_mode_after_SSRO = 10
              fail_mode_after_SSRO = 10
            endif
            awg_done_was_low = 0
          ELSE ' AWG not done yet
            awg_done_was_low = 1
            IF ( timer > wait_for_awg_done_timeout_cycles) THEN
              inc(PAR_80) ' signal the we have an awg timeout
              END ' terminate the process
            ENDIF  
          ENDIF
 
        CASE 10 'store the result of the tomography and the sync number counter
          DATA_106[repetition_counter+1] = SSRO_result
          DATA_102[repetition_counter+1] = cumulative_awg_counts + AWG_sequence_repetitions_first_attempt + AWG_sequence_repetitions_second_attempt ' store sync number of successful run
          DATA_114[repetition_counter+1] = PAR_55 'what was the state of the invalid data marker?
          mode = 12 'go to reinit and CR check
          INC(repetition_counter) ' count this as a repetition. DO NOT PUT IN 12, because 12 can be used to init everything without previous success!!!!!
          first_CR=1 ' we want to store the CR after result in the next run
          inc(success_event_counter)
          PAR_77 = success_event_counter ' for the LabView live update
        
          inc(current_ROseq)
          IF (current_ROseq = no_of_sweep_pts+1) THEN
            current_ROseq = 1

          ENDIF
        
        CASE 11 ' in case one wants to jump to SSRO after the entanglement sequence
          ' to avoid confilicts in AWG timing, the ADWIN has to wait for another trigger before starting the readout.
          ' after that, we go to case 10 to increment the repetition counter and then we clean up in case 12
        
          IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)>0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (awg_done_was_low>0) then
              mode = 200
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              is_mbi_readout = 0
              success_mode_after_SSRO = 10 'used to be 12. Now we also go to case 10 in order to increment the rep counter and set first_CR to 0 before doing the cleanup
              fail_mode_after_SSRO = 10
              success_of_SSRO_is_ms0 = 1      
            endif
            awg_done_was_low = 0
          ELSE ' AWG not done yet
            awg_done_was_low = 1
            IF ( timer > wait_for_awg_done_timeout_cycles) THEN
              inc(PAR_80) ' signal the we have an awg timeout
              END ' terminate the process
            ENDIF  
          ENDIF
        
                              
        CASE 12 ' reinit all variables and go to cr check
        
          'IF (First_CR = 1) THEN ' last run has been successful
          '  IF (repetition_counter = 1) THEN ' start of the sequence
          '    cumulative_awg_counts = 0
          '  ELSE
          '    cumulative_awg_counts = DATA_102[repetition_counter-1]
          '  ENDIF
          '  
          '  DATA_102[repetition_counter] = DATA_102[repetition_counter]+AWG_sequence_repetitions_first_attempt+AWG_sequence_repetitions_second_attempt+cumulative_awg_counts+1
          '  
          'ELSE ' last run failed
          '  DATA_102[repetition_counter+1] = DATA_102[repetition_counter+1]+AWG_sequence_repetitions_first_attempt+AWG_sequence_repetitions_second_attempt
          'ENDIF

          Par_73 = repetition_counter ' write to PAR
          cumulative_awg_counts = cumulative_awg_counts + AWG_sequence_repetitions_first_attempt + AWG_sequence_repetitions_second_attempt 'remember sync counts, independent of success or failure
          'forget all parameters of previous runs
          AWG_repcount_was_low = 1
          AWG_done_was_low = 1  
          AWG_sequence_repetitions_first_attempt = 0
          AWG_sequence_repetitions_second_attempt = 0
          current_MBI_attempt = 1
          
          current_C_init_RO = 0
          current_C_encoding_RO = 0
          'trying_mbi = 0
          
          current_feedback_nucleus = 0        
          ' init_nuclear_phases_offset() ' this takes 55 cycles
          dedicate_next_cycle_to_calculations = 1
          requested_calculations = REQ_CALC_INIT_PHASES_OFFSET
          tico_delay_line_set_cycles(0)
        
          mbi_timer = 0 
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
        
          '        IF (Par_63 = 0) THEN ' if we are about to stop the process, don't reset the flowchart        
          '          flowchart_index = 0
          '        ENDIF
        
          mode = 0 ' go to cr
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1        
          duty_cycle = time_spent_in_sequence / (time_spent_in_state_preparation+time_spent_in_sequence+time_spent_in_communication)
          FPAR_58 = duty_cycle
          if ((time_spent_in_state_preparation+time_spent_in_sequence+time_spent_in_communication) > 200E6) then 'prevent overflows: duty cycle is reset after 2000 sec, data type long can hold a little more
            time_spent_in_state_preparation = 0
            time_spent_in_sequence = 0 
            time_spent_in_communication = 0
          endif
      endselect
    
      INC(timer)
    
    endif
  ENDIF
  
  
  Par_36 = (Read_Timer() - start_time)
  
  IF (Par_36 > overlong_cycle_threshold) THEN
    INC(overlong_cycles_per_mode[current_mode + 1])
    INC(Par_34)
    IF(current_mode = 7) THEN
      Par_35 = Par_36
      Par_37 = timer
      Par_38 = Par_41
    ENDIF
    
  ENDIF
    
FINISH:
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0) 
  
  IF ((do_phase_fb_delayline > 0) OR (do_sweep_delay_cycles > 0)) THEN
    tico_delay_line_finish()
  ENDIF
  
  FOR i = 1 to max_modes
    overlong_cycles_per_mode_OUT[i] = overlong_cycles_per_mode[i]
  NEXT i
  
  FOR i = 1 to max_flowchart_modes
    mode_flowchart_OUT[i] = mode_flowchart[i]
    mode_flowchart_cycles_OUT[i] = mode_flowchart_cycles[i]
  NEXT i
  
  FOR i = 1 to max_nuclei
    nuclear_phases_OUT[i] = nuclear_phases[i]
  NEXT i

