'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
' Bookmarks                      = 3,3,16,16,22,22,87,87,89,89,204,204,351,351,352,352,367,367,593,593,664,664,855,856,857,864,865,866
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
#INCLUDE .\configuration.inc
#INCLUDE .\cr_mod.inc
'#INCLUDE .\cr.inc
'#INCLUDE .\cr_mod_Bell.inc
#INCLUDE math.inc

' #DEFINE max_repetitions is defined as 500000 in cr check. Could be reduced to save memory
#DEFINE max_purification_repetitions    52000 ' high number needed to have good statistics in the repump_speed calibration measurement
#DEFINE max_SP_bins       2000  

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

DIM DATA_29[max_SP_bins] AS LONG     ' SP counts
DIM DATA_100[max_purification_repetitions] AS LONG at DRAM_Extern' Phase_correction_repetitions needed to correct the phase of the carbon 
DIM DATA_101[max_purification_repetitions] AS LONG at DRAM_Extern' time spent for communication between adwins 
DIM DATA_102[max_purification_repetitions] AS LONG at DRAM_Extern' Information which how many AWG attempts lie between successful events
DIM DATA_103[max_purification_repetitions] AS LONG at DRAM_Extern' number of repetitions until the first succesful entanglement attempt 
DIM DATA_104[max_purification_repetitions] AS LONG at DRAM_Extern' number of repetitions after swapping until the second succesful entanglement attempt 
DIM DATA_105[max_purification_repetitions] AS LONG at DRAM_Extern ' SSRO counts electron readout after purification gate 
DIM DATA_106[max_purification_repetitions] AS LONG at DRAM_Extern' SSRO counts carbon spin readout after tomography 
DIM DATA_107[max_purification_repetitions] AS LONG at DRAM_Extern' SSRO counts last electron spin readout performed in the adwin seuqnece 
DIM DATA_108[max_purification_repetitions] as long at DRAM_Extern' sync number of the current event to compare to hydra harp data 

' these parameters are used for data initialization.
DIM Initializer[100] as LONG AT EM_LOCAL ' this array is used for initialization purposes and stored in the local memory of the adwin 
DIM array_step as LONG

'general paramters
DIM cycle_duration AS LONG 'repetition rate of the event structure. Typically 1us
DIM repetition_counter, No_of_sequence_repetitions, success_event_counter AS LONG 'counts how many repetitions of the experiment have been done
DIM timer, wait_time, mode, i AS LONG 
DIM SP_duration AS LONG
DIM wait_after_pulse_duration AS LONG
DIM CR_result, first_CR AS LONG
DIM SSRO_result AS LONG
DIM Dynamical_stop_ssro_threshold, Dynamical_stop_ssro_duration, Success_of_SSRO_is_ms0 AS LONG
DIM digin_this_cycle AS long
DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM time_spent_in_state_preparation, time_spent_in_sequence, duty_cycle, time_spent_in_communication as LONG

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


' Phase compensation
DIM phase_to_compensate, total_phase_offset_after_sequence, phase_per_sequence_repetition, phase_per_compensation_repetition,acquired_phase_during_compensation AS FLOAT
DIM phase_compensation_repetitions, required_phase_compensation_repetitions,phase_correct_max_reps as long
DIM AWG_sequence_repetitions_first_attempt, AWG_sequence_repetitions_second_attempt as long

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
DIM PLU_during_LDE as long
DIM is_master,cumulative_awg_counts as long

' Sequence flow control
DIM do_carbon_init, do_C_init_SWAP_wo_SSRO AS LONG
DIM do_swap_onto_carbon, do_SSRO_after_electron_carbon_SWAP as long
DIM do_LDE_2, do_phase_correction as long
DIM do_purifying_gate, do_carbon_readout as long

DIM mode_after_spinpumping, mode_after_LDE, mode_after_LDE_2, mode_after_SWAP, mode_after_purification, mode_after_phase_correction as long

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
      
  success_event_counter = 0
  Success_of_SSRO_is_ms0 = 1 'usually, we condition on getting a click
  SSRO_result = 0
  
  mode = 0
  timer = 0
  mbi_timer = 0
  trying_mbi = 0
      
  
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
  
  ' float params from python
  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  E_MBI_voltage                = DATA_21[2]  
  A_SP_voltage                 = DATA_21[3]
  E_RO_voltage                 = DATA_21[4]
  A_RO_voltage                 = DATA_21[5]
  phase_per_sequence_repetition     = DATA_21[6] ' how much phase do we acquire per repetition
  phase_per_compensation_repetition = DATA_21[7] '
  total_phase_offset_after_sequence = DATA_21[8] 'how much phase have we acquired during the pulses
              
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  AWG_repcount_DI_pattern = 2 ^ AWG_repcount_DI_channel
  PLU_event_di_pattern = 2 ^ PLU_event_di_channel
  PLU_which_di_pattern = 2 ^ PLU_which_di_channel
  remote_adwin_di_success_pattern = 2^ remote_adwin_di_success_channel
  remote_adwin_di_fail_pattern = 2^ remote_adwin_di_fail_channel
  sync_trigger_counter_channel = 3
  sync_trigger_counter_pattern = 2 ^ (sync_trigger_counter_channel - 1)
  
  
''''''''''''''''''''''''''''''''''''''
  ' initialize the data arrays. set to -1 to discriminate between 0-readout and no-readout
''''''''''''''''''''''''''''''''''''''
 
  '  ' enter desired values into the initializer array
  FOR i = 1 TO 100
    Initializer[i] = -1
  NEXT i
  '  
  '  
  '  ' note: the MemCpy function only works for T11 processors.
  '  ' this is a faster way of filling up global data arrays in the external memory. See Adbasic manual
  array_step = 1
  FOR i = 1 TO 520 ' 300 is derived from max_purification_length/100
    MemCpy(Initializer[1],DATA_100[array_step],100)
    MemCpy(Initializer[1],DATA_101[array_step],100)
    MemCpy(Initializer[1],DATA_102[array_step],100)
    MemCpy(Initializer[1],DATA_103[array_step],100)
    MemCpy(Initializer[1],DATA_104[array_step],100)
    MemCpy(Initializer[1],DATA_105[array_step],100)
    MemCpy(Initializer[1],DATA_106[array_step],100)
    MemCpy(Initializer[1],DATA_107[array_step],100)
    MemCpy(Initializer[1],DATA_108[array_step],100)
    array_step = array_step + 100
  NEXT i
  
  'initialize the max_SP_bins
  FOR i = 1 TO max_SP_bins
    DATA_29[i] = 0
  NEXT i
  
  
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
  
'''''''''''''''''''''''''
  ' flow control: 
'''''''''''''''''''''''''
  if (do_carbon_readout = 1) then
    mode_after_purification = 9 ' Carbon tomography
  else
    mode_after_purification = 11 ' wait for trigger then do SSRO
  endif
  
  IF (do_purifying_gate = 1) THEN
    mode_after_phase_correction = 8 ' purifying gate
  ELSE
    mode_after_phase_correction = mode_after_purification ' as defined above
  ENDIF
  
  if ((do_phase_correction=1) and (do_purifying_gate = 1)) then ' special case: in the adwin do phase only makes sense in conjunction with do_purify
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
  
  if (do_carbon_init = 1) then
    mode_after_spinpumping = 2 'MBI
  else
    mode_after_spinpumping = 4 ' LDE 1
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
   
  processdelay = cycle_duration   ' the event structure is repeated at this period. On T11 processor 300 corresponds to 1us. Can do at most 300 operations in one round.
  
  P2_CNT_CLEAR(CTR_MODULE, sync_trigger_counter_pattern)    'clear and turn on sync trigger counter
  P2_CNT_ENABLE(CTR_MODULE, sync_trigger_counter_pattern)
  
EVENT:
  
  'write information to pars for live monitoring
  PAR_61 = mode   
  Par_60 = timer    
  IF (wait_time > 0)  THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
      
      CASE 100 ' communication between adwins
        ' communication logic: there is a fail and a success trigger. Both 0 means no signal has been sent, both high on slave side means signal has been received from master
        ' The master decides if both setups are successful, sends this to the slave, and waits for the slave to go on 11 to confirm communication, and sends a jump to both awg if not succesful

        if (timer = 0) then ' forget values from previous runs
          adwin_timeout_requested = 0
          combined_success = 0
          adwin_comm_done = 0
          remote_success = 0
          remote_fail = 0
          par_15=0
        endif
        
        IF (adwin_comm_done > 0) THEN 'communication run was successful. Decide what to do next and clear memory. Second if statement (rather than ELSE) saves one clock cycle
          if (combined_success > 0) then ' both successful: continue
            mode = success_mode_after_adwin_comm
          else 'fail: go to fail mode
            mode = fail_mode_after_adwin_comm
          endif
          time_spent_in_communication = time_spent_in_communication + timer
          timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, 0) ' set the channels low
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 0) ' set the channels low
        ELSE
          'previous communication was not successful
          DATA_101[repetition_counter+1] = DATA_101[repetition_counter+1] + timer  ' store time spent in adwin communication for debugging
          digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE)   ' read remote input channels
          if ( (digin_this_cycle AND remote_adwin_di_success_pattern) > 0) then
            remote_success = 1
          endif
          if ( (digin_this_cycle AND remote_adwin_di_fail_pattern) > 0) then
            remote_fail = 1
          endif
                
          IF (is_master>0) THEN 
            if ((remote_success > 0 ) and (remote_fail > 0)) then ' own signal successfully communicated to other side -> go on to next mode
              adwin_comm_done = 1 ' go to next mode in cleanup step below
              wait_time = adwin_comm_safety_cycles ' make sure the other adwin is ready for counting etc.
            else ' own signal not yet received on other side -> send it or wait for slave's signal to decide what to do
              IF ((remote_success >0) or (remote_fail >0)) then ' remote signal received: decide whether both setups were successful
                if ((local_success > 0) and (remote_success >0)) then
                  combined_success = 1
                else
                  combined_success = 0
                endif
                'send combined success and then wait for confirmation
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, combined_success)
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 1-combined_success)
              ELSE
                ' no signal received. Did the connection time out? (we only get here in case we have 00 on the inputs)
                if (timer > adwin_comm_timeout_cycles) then
                  inc(n_of_comm_timeouts) ' give to par for local debugging
                  PAR_62 = n_of_comm_timeouts ' for debugging
                  combined_success = 0 ' just to be sure
                  adwin_comm_done = 1 ' below: reset everything and go on
                endif                
              ENDIF
              
            endif
            
                    
          ELSE ' I'm the slave, and the communication is not yet done.
            if (timer = 0) then ' first round: send my signal
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, local_success)
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 1-local_success) 
            else 'Did the master tell me what to do?
              if ((remote_success >0 ) or (remote_fail >0)) then 'signal received
                P2_DIGOUT(DIO_MODULE, remote_adwin_do_success_channel, 1) 'send confirmation: both channels high
                P2_DIGOUT(DIO_MODULE, remote_adwin_do_fail_channel, 1) 'send confirmation
                combined_success = remote_success
                wait_time = adwin_comm_safety_cycles ' wait in event loop for adwin communication safety time to make sure the other setup has received our signal
                adwin_comm_done = 1 ' below: reset everything and go on
              else ' still no signal. Did the connection time out?
                IF (adwin_timeout_requested > 0) THEN ' previous run: timeout requested.
                  adwin_comm_done = 1 ' communication done (timeout). Still: reset parameters below
                  combined_success = 0
                  inc(n_of_comm_timeouts) ' give to par for local debugging
                  PAR_62 = n_of_comm_timeouts ' for debugging
                ELSE ' should I request a timeout in the next round now?
                  if (timer > adwin_comm_timeout_cycles) then
                    P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, 0) ' stop signalling
                    P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 0)
                    wait_time = 2* adwin_comm_safety_cycles ' wait in event loop for adwin communication safety time
                    adwin_timeout_requested = 1
                  endif  
                ENDIF
              endif
            endif
          ENDIF
        ENDIF
                

       
        
        
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
          IF (is_two_setup_experiment = 0) THEN 'only one setup involved. Skip communication step
            mode = 1 'go to spin pumping directly
          ELSE ' two setups involved
            local_success = 1 ' remember for communication step
            local_fail = 0
            mode = 100 'go to communication step
            fail_mode_after_adwin_comm = 0 ' back to cr check. Fail can be timeout. This allows to keep the NV on resonance in case the other setup has jumped
            success_mode_after_adwin_comm = 1 ' go to spin pumping 
          ENDIF
        endif  
        
        
        
      CASE 1    ' E spin pumping
        
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768) ' or turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)                        ' clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern OR sync_trigger_counter_pattern)                       ' turn on counter
          old_counts = 0
        ELSE
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
          ENDIF
        ENDIF
        
         
          
      CASE 2    ' Carbon init, either MBI or SWAP (with SSRO afterwards or not)
        ' We first need to send a trigger command to the AWGs on both sides that tells them to start the gate sequence
        ' in local mode, this is done by each ADWIN, in remote mode the Master Adwin also triggers the slave AWG
        
        IF (timer=0) THEN   ' MBI sequence starts
          INC(MBI_starts)
          PAR_78 = MBI_starts          
          ' Logic: If local or master, own awg is triggered. If nonlocal and slave, AWG is triggered by master's awg to minimize jitter
          if (is_two_setup_experiment = 0) then
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
          else 
            IF (is_master>0) THEN ' trigger own and remote AWG
              'P2_Digout_Bits(DIO_MODULE, (2^AWG_start_DO_channel AND 2^remote_awg_trigger_channel),0) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,1)
              CPU_SLEEP(master_slave_awg_trigger_delay) ' shift the awg trigger such that it occurs at the same time.
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
              CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              'P2_Digout_Bits(DIO_MODULE, 0, (2^AWG_start_DO_channel AND 2^remote_awg_trigger_channel)) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,0)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
            ENDIF
          endif 
          
        ELSE ' AWG in MBI sequence is running
          ' Detect if the AWG is done and has sent a trigger; this construction prevents multiple adwin jumps when the awg sends a looooong pulse
          digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE)
          if ((digin_this_cycle and AWG_done_DI_pattern)>0) then ' AWG has done the MW pulses -> go to next step
            if (awg_done_was_low >0) then
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
          if (is_two_setup_experiment = 0) then 'only one setup involved. Skip communication step
            mode = 31 ' entanglement sequence
          else
            mode = 100 ' adwin communication
            fail_mode_after_adwin_comm = 0 ' CR check 
            success_mode_after_adwin_comm = 31 ' entanglement sequence
          endif 
        ELSE ' MBI failed. Retry or communicate?
          INC(MBI_failed)
          PAR_74 = MBI_failed 'for debugging

          IF (current_MBI_attempt = MBI_attempts_before_CR) then ' failed too often -> communicate failure (if in remote mode) and then go to CR
            current_MBI_attempt = 1 'reset counter
            if (is_two_setup_experiment > 0) then 'two setups involved
              fail_mode_after_adwin_comm = 0 ' CR check. Don't have to specify success_mode because I didn't succeed
              mode = 100
            else
              mode = 0 ' directly back to CR
            endif
          ELSE 
            mode = 1 ' retry spinpumping and then MBI
            INC(current_MBI_attempt)
          ENDIF 
        ENDIF  
        time_spent_in_state_preparation = time_spent_in_state_preparation + timer
        timer = -1      
        
      CASE 31 'tell the AWG to jump in case of a succesful MBI attempts
        P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to the entanglement sequence
        CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
        mode = 4
        timer = -1
        
      CASE 4    '  wait and count repetitions of the entanglement AWG sequence
        ' the awg gives repeated adwin sync pulses, which are counted. In the case of an entanglement event, we get a plu signal.
        ' In case there's no entanglement event, we get the awg done trigger, a pulse of which we detect the falling edge.
        ' In case this is a single-setup (e.g. phase calibration) measurement, we go on, 
        ' otherwise getting a done trigger means failure of the sequence and we go to CR cheking
        ' NOTE, if the AWG sequence is to short (close to a us, then it is possible that the time the signal is low is missed.
        IF (timer = 0) THEN ' first run: send triggers
          if (is_two_setup_experiment = 0) then  ' give AWG trigger
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
          else 
            IF (is_master > 0) THEN ' trigger own and remote AWG
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,1)
              CPU_SLEEP(master_slave_awg_trigger_delay) ' shift the awg trigger such that it occurs at the same time.
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
              CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,0)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
            ENDIF
          endif 
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
          
        if ((digin_this_cycle AND PLU_event_di_pattern) >0) THEN ' PLU signal received
          '          IF (is_master >0) THEN ' plu which only connected on lt4
          '            if ((digin_this_cycle AND PLU_which_di_pattern) >0) then
          '              DATA_102[repetition_counter+1]=1 ' store which detector has clicked in first round. Second round will be stored on next decimal (add 10 or 20)
          '            else
          '              DATA_102[repetition_counter+1]=2
          '            endif        
          '          ENDIF
          DATA_103[repetition_counter+1] = AWG_sequence_repetitions_first_attempt ' save the result
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
          mode = mode_after_LDE   
        else ' no plu signal. check for timeout or done
          IF ((digin_this_cycle AND AWG_done_DI_pattern) > 0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (awg_done_was_low =1) then
              DATA_103[repetition_counter+1] = AWG_sequence_repetitions_first_attempt 'save the result
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              if (PLU_during_LDE = 0) then ' this is a single-setup (e.g. phase calibration) measurement. Go on to next mode
                mode = mode_after_LDE
              else ' two setups involved: Done means failure of the sequence
                mode = 12 ' finalize and go to cr check
                'P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to beginning of MBI and wait for trigger
                'CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
                'P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
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
        endif

        
       
      CASE 5  ' wait for the electron Carbon swap to be done and then read out the electron if this is specified in the msmt parameters
        IF (timer =0) THEN
          if (is_two_setup_experiment = 0) then  ' give AWG trigger
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
          else 
            IF (is_master>0) THEN ' trigger own and remote AWG
              'P2_Digout_Bits(DIO_MODULE, (2^AWG_start_DO_channel OR 2^remote_awg_trigger_channel),0) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,1)
              CPU_SLEEP(master_slave_awg_trigger_delay) 
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
              CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              'P2_Digout_Bits(DIO_MODULE, 0, (2^AWG_start_DO_channel OR 2^remote_awg_trigger_channel)) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,0)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
            ENDIF
          endif 
        ENDIF
        
        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) >0 )THEN  'awg trigger tells us it is done with the swap sequence.
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
          if (AWG_done_was_low >0) then ' prevents double jump in case the awg trigger is long
            IF (do_SSRO_after_electron_carbon_SWAP = 0) then
              mode = mode_after_swap ' see flow control
            ELSE
              mode = 200   ' dsSSRO
              is_mbi_readout = 1 ' ... in MBI mode
              Success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it before
              if (is_two_setup_experiment > 0) THEN
                success_mode_after_SSRO = 100 'adwin comm
                fail_mode_after_SSRO = 100
                success_mode_after_adwin_comm = 51  ' see flow control
                fail_mode_after_adwin_comm = 12 ' finalize and go to cr. could also be 6 in case one wants to implement a deterministic protocol
              else
                success_mode_after_SSRO = 51 ' see flow control
                fail_mode_after_SSRO = 12 ' finalize and start over
              endif
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
        CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
        mode = mode_after_swap 'see flow control
        timer = -1
        
      CASE 6    ' save ssro after swap result. Then wait and count repetitions of the entanglement AWG sequence as in case 4
        IF (timer =0) THEN
          'DATA_37[repetition_counter+1] = SSRO_result
          if (is_two_setup_experiment = 0) then  ' give AWG trigger
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
          else 
            IF (is_master > 0) THEN ' trigger own and remote AWG
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,1)
              CPU_SLEEP(master_slave_awg_trigger_delay) ' shift the awg trigger such that it occurs at the same time.
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
              CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,0)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
            ENDIF
          endif 
        ENDIF
                
                
        ' monitor inputs
        digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE)
                
        if ((digin_this_cycle AND AWG_repcount_DI_pattern) > 0) then 
          IF (AWG_repcount_was_low = 1) THEN ' awg has switched to high. this construction prevents double counts if the awg signal is long
            inc(AWG_sequence_repetitions_second_attempt) ' increase the number of attempts counter
          ENDIF
          AWG_repcount_was_low = 0
        else
          AWG_repcount_was_low = 1
        endif
        
        'check the PLU
        IF ((digin_this_cycle AND PLU_event_di_pattern) > 0) THEN 'PLU signal received
          DATA_103[repetition_counter+1] = AWG_sequence_repetitions_second_attempt 'save the result
          'if ((digin_this_cycle AND PLU_which_di_pattern)>0) then
          '  DATA_102[repetition_counter+1]= DATA_102[repetition_counter+1]+10 ' store which detector has clicked in second round. +10 or +20 to discriminate from first round
          'else
          '  DATA_102[repetition_counter+1]= DATA_102[repetition_counter+1]+20
          'endif
          mode = mode_after_LDE_2 'go on to next case
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
        ELSE ' no plu signal:  check the done trigger     
          IF ((digin_this_cycle AND AWG_Done_di_pattern) >0) THEN  'awg trigger tells us it is done with the entanglement sequence. This means failure of the protocol
            if (awg_done_was_low > 0) then ' switched in this round
              DATA_104[repetition_counter+1] = AWG_sequence_repetitions_second_attempt 'save the result
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              IF ((is_two_setup_experiment = 0) OR (PLU_during_LDE = 0)) then ' this is a single-setup (e.g. phase calibration) measurement. Go on to next mode
                mode = mode_after_LDE_2
              ELSE ' two setups involved: Done means failure of the sequence
                mode = 12 ' finalize and go to cr check
                'P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to beginning of MBI and wait for trigger
                'CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
                'P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
              ENDIF
            endif
            awg_done_was_low = 0  ' remember
          ELSE ' AWG not done yet
            awg_done_was_low = 1
            IF ( timer > wait_for_awg_done_timeout_cycles) THEN
              inc(PAR_80) ' signal the we have an awg timeout
              END ' terminate the process
            ENDIF  
          ENDIF
        ENDIF


        
        
      CASE 7 ' Phase synchronisation
        ' AWG will go to dynamical decoupling, and output a sync pulse to the adwin once in a while
        ' Each adwin will count the number pulses and send a jump once a given phase has been reached.
        IF (timer =0) THEN 'first go: calculate required repetitions
          required_phase_compensation_repetitions = 1
          awg_repcount_was_low = 0
          phase_compensation_repetitions =0
          phase_to_compensate = total_phase_offset_after_sequence + AWG_sequence_repetitions_second_attempt * phase_per_sequence_repetition
          if (phase_to_compensate > 360) then           ' The built in Mod function works only for integers and takes 0.44 us.
            Do                              
              phase_to_compensate = phase_to_compensate - 360
            Until (phase_to_compensate  <= 360)
          endif
        
        ENDIF
                
        IF (timer = 1) THEN
          ' minimum is two repetitions
          ' required count is repetitions - 1
          ' we want to be within two degrees from the desired state
          acquired_phase_during_compensation = phase_per_compensation_repetition
          Do                              
            inc(required_phase_compensation_repetitions)
            acquired_phase_during_compensation = acquired_phase_during_compensation + phase_per_compensation_repetition
            IF (acquired_phase_during_compensation > 360) THEN
              acquired_phase_during_compensation =   acquired_phase_during_compensation-360
            ENDIF
          Until (( Abs(phase_to_compensate-acquired_phase_during_compensation)  <= 4.5) OR (required_phase_compensation_repetitions>phase_correct_max_reps-1))
                  
          Dec(required_phase_compensation_repetitions)  ' we do one unaccounted repetition in the AWG.
          DATA_100[repetition_counter+1] = required_phase_compensation_repetitions
        ENDIF 
                
        
        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_repcount_DI_pattern)>0) THEN 'awg has switched to high. this construction prevents double counts if the awg signal is long
          if (awg_repcount_was_low = 1) then
            inc(phase_compensation_repetitions)  
          endif
          awg_repcount_was_low = 0
        ELSE
          awg_repcount_was_low = 1
        ENDIF
        
        IF (phase_compensation_repetitions = required_phase_compensation_repetitions) THEN 'give jump trigger and go to next mode: tomography
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to tomo pulse sequence
          CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
          mode = mode_after_phase_correction
        ENDIF
        
      CASE 8 ' Wait until purification gate is done. 
                
        IF (timer =0) THEN
          if (is_two_setup_experiment = 0) then  ' give AWG trigger
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
          else 
            IF (is_master>0) THEN ' trigger own and remote AWG
              'P2_Digout_Bits(DIO_MODULE, (2^AWG_start_DO_channel AND 2^remote_awg_trigger_channel),0) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,1)
              CPU_SLEEP(master_slave_awg_trigger_delay) 
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
              CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              'P2_Digout_Bits(DIO_MODULE, 0, (2^AWG_start_DO_channel AND 2^remote_awg_trigger_channel)) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,0)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
            ENDIF
          endif 
        ENDIF
                
        'check the done trigger
        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)>0) THEN  'awg trigger tells us it is done with the entanglement sequence.
          if (AWG_done_was_low > 0) then
            time_spent_in_sequence = time_spent_in_sequence + timer
            timer = -1
            success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
            mode = 200 'go to SSRO
            is_mbi_readout = 1
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
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
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
        inc(success_event_counter)
        PAR_77 = success_event_counter ' for the LabView live update
        DATA_106[repetition_counter+1] = SSRO_result
        DATA_102[repetition_counter+1] = cumulative_awg_counts + AWG_sequence_repetitions_first_attempt + AWG_sequence_repetitions_second_attempt ' store sync number of successful run
        DATA_108[repetition_counter+1] = P2_CNT_READ(CTR_MODULE, sync_trigger_counter_channel)         ' store value of the sync number counter. Redundant to the above, but this is really important
        mode = 12 'go to reinit and CR check
        INC(repetition_counter) ' count this as a repetition. DO NOT PUT IN 12, because 12 can be used to init everything without previous success!!!!!
        first_CR=1 ' we want to store the CR after result in the next run
        inc(success_event_counter)
        PAR_77 = success_event_counter ' for the LabView live update
        
        
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
        '  DATA_108[repetition_counter] = P2_CNT_READ(CTR_MODULE, sync_trigger_counter_channel) ' repetition_counter has been incremented, therefore no +1
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
        'trying_mbi = 0
        mbi_timer = 0 
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
        mode = 0 ' go to cr
        time_spent_in_sequence = time_spent_in_sequence + timer
        timer = -1        
        duty_cycle = time_spent_in_sequence / (time_spent_in_state_preparation+time_spent_in_sequence+time_spent_in_communication)
        PAR_80 = duty_cycle
        if ((time_spent_in_state_preparation+time_spent_in_sequence+time_spent_in_communication) > 2000E6) then 'prevent overflows: duty cycle is reset after 2000 sec, data type long can hold a little more
          time_spent_in_state_preparation = 0
          time_spent_in_sequence =0 
          time_spent_in_communication=0
        endif
    endselect
    
    INC(timer)
    
  endif

    
FINISH:
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0) 

