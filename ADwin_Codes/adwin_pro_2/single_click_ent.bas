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
' Bookmarks                      = 3,3,87,87,180,180,381,381,401,401,775,775,845,846
'<Header End>
' Single click ent. sequence, described in the planning folder. Based on the purification adwin script, with Jaco PID added in
' PH2016
'
' We use two setups. Each adwin is connected to its own awg jump trigger.
' Each setup gets a parameter 'is_master' that determines whether it is the Master (who controls communication) or the Slave (who waits for the other guy)
' The master AWG triggers the slave awg. Tpo this end, there's a hardware local <-> nonlocal switch
' Two channels are used for communication between adwins, one to signal success and one to signal failure.
' 
' 
' modes:
'   100 : Comms
'   200 : SSRO

'   0 : Phase check (master controlled only)
'   1 : Phase msmt (master only, not part of experimental seq.)
'   20: Start counting time since phase check
'   2 : CR check
'   3 : E spin pumping into ms=+/-1
'   4 : run entanglement sequence and count reps while waiting for PLU success signal
'   5 : decoupling and counting reps
'   6 : wait for AWG trigger to do SSRO
'   7 : Store ro result
'   8 : Parameter reinitialization

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr_mod_Bell.inc
#INCLUDE math.inc

' #DEFINE max_repetitions is defined as 500000 in cr check. Could be reduced to save memory
#DEFINE max_single_click_ent_repetitions    50000 ' high number needed to have good statistics in the phase msmt stuff
#DEFINE max_SP_bins       2000  
#DEFINE max_pid       1000000 ' Max number of measured points for pid stabilisation (5 ms / 200 mus ~ 25, 25*20000 ~ 500000, so can do 20000 repetitions)

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
'30 ' CR integer parameters
'31 CR float parameters

DIM DATA_29[max_SP_bins] AS LONG     ' SP counts
DIM DATA_100[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' Will eventually hold data on dynamical decoupling repetitions
DIM DATA_101[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' time spent for communication between adwins 
DIM DATA_102[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' number of repetitions until the first succesful entanglement attempt 
DIM DATA_103[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' SSRO counts electron spin readout performed in the adwin seuqnece 

' PH Fix this. NK: fix what ??? PH Cant remember :P
DIM DATA_104[max_pid] AS LONG at DRAM_Extern' Holds data on the measured counts during the PID stabilisation 'APD 1
DIM DATA_105[max_pid] AS LONG at DRAM_Extern' Holds data on the measured counts during the PID stabilisation 'APD 2
DIM DATA_106[max_pid] AS LONG at DRAM_Extern' Holds data on the measured counts during the sampling time  'APD 1
DIM DATA_107[max_pid] AS LONG at DRAM_Extern' Holds data on the measured counts during the sampling time  'APD 2
DIM DATA_108[max_single_click_ent_repetitions] AS LONG at DRAM_Extern 'save elapsed time since phase stab when succes ent.
DIM DATA_109[max_single_click_ent_repetitions] AS LONG at DRAM_Extern 'save last phase stab index when succes ent.
DIM DATA_110[max_pid] AS FLOAT at DRAM_Extern 'Hold the calculated phase during phase stabilisation
DIM DATA_114[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' Invalid data marker 

' these parameters are used for data initialization.
DIM Initializer[100] as LONG AT EM_LOCAL ' this array is used for initialization purposes and stored in the local memory of the adwin 
DIM Float_Initializer[100] as Float AT EM_LOCAL ' this array is used for initialization purposes and stored in the local memory of the adwin 
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
DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage, Phase_Msmt_voltage, Phase_Msmt_off_voltage AS FLOAT
DIM Phase_msmt_laser_DAC_channel, Phase_stab_DAC_channel as Long
DIM time_spent_in_state_preparation, time_spent_in_sequence, time_spent_in_communication as LONG
DIM duty_cycle as FLOAT
DIM AWG_sequence_repetitions_LDE AS long
DIM old_counts_1, old_counts_2, counts, counts_1, counts_2 AS Float

' Channels & triggers
dim AWG_done_was_low, AWG_repcount_was_low, PLU_event_di_was_high, master_slave_awg_trigger_delay as long
DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_repcount_DI_channel, AWG_event_jump_DO_channel, AWG_done_DI_pattern, AWG_repcount_DI_pattern AS LONG
DIM PLU_event_di_channel, PLU_event_di_pattern, PLU_which_di_channel, PLU_which_di_pattern AS LONG
DIM invalid_data_marker_do_channel AS LONG

' Communication with other Adwin
DIM remote_adwin_di_success_channel, remote_adwin_di_success_pattern, remote_adwin_di_fail_channel, remote_adwin_di_fail_pattern as long
DIM remote_adwin_do_success_channel, remote_adwin_do_fail_channel, remote_awg_trigger_channel  as long
DIM local_flag_1, remote_flag_1, local_flag_2, remote_flag_2, combined_success as long
DIM success_mode_after_adwin_comm, fail_mode_after_adwin_comm as long
DIM success_mode_after_SSRO, fail_mode_after_SSRO as long
DIM adwin_comm_safety_cycles as long 'msmt param that tells how long the adwins should wait to guarantee bidirectional communication is successful
DIM adwin_comm_timeout_cycles, wait_for_awg_done_timeout_cycles as long ' if one side fails completely, the other can go on
DIM adwin_comm_done, adwin_timeout_requested as long
DIM n_of_comm_timeouts, is_two_setup_experiment as long
DIM PLU_during_LDE, LDE_is_init as long
DIM is_master,cumulative_awg_counts, timeout_mode_after_adwin_comm, mode_flag as long

' Sequence flow control
DIM do_phase_stabilisation, only_meas_phase, do_dynamical_decoupling, do_post_ent_phase_msmt as long
DIM init_mode, mode_after_phase_stab, mode_after_LDE, mode_after_expm, mode_after_e_msmt as long

' Phase shifter PID params (note that only the master ADWIN controls the phase)
DIM Sig, setpoint, setpoint_angle, Prop, Dif,Int                    AS FLOAT        ' PID terms
DIM PID_GAIN,PID_Kp,PID_Kd,PID_Ki  AS FLOAT        ' PID parameters
DIM e, e_old                                        AS FLOAT        ' error term
DIM pid_time_factor, cosarg                                 AS FLOAT        ' account for changes in the adwin clock cycle
DIM store_index, store_index_stab, store_index_msmt,index,pid_points,pid_points_to_store,sample_points AS LONG ' Keep track of how long to sample for etc.
DIM count_int_cycles_stab, raw_count_int_time_stab, count_int_cycles_meas, raw_count_int_time_meas              AS LONG ' Time to count for per PID / phase msmt cycle
DIM zpl1_counter_channel,zpl2_counter_channel,zpl1_counter_pattern,zpl2_counter_pattern  AS LONG ' Channels for ZPL APDs
DIM elapsed_cycles_since_phase_stab, raw_phase_stab_max_time, phase_stab_max_cycles, modulate_stretcher_during_phase_msmt AS LONG
DIM stretcher_V_2pi,stretcher_V_correct, stretcher_V_max, Phase_Msmt_g_0, Phase_Msmt_Vis, total_cycles AS FLOAT

' On-demand decoupling stuff
DIM LDE_element_duration,max_sequence_duration,decoupling_element_duration AS FLOAT
DIM max_LDE_attempts,decoupling_repetitions,required_DD_repetitions AS LONG


DIM remaining_time_in_long_CR_check AS LONG


LOWINIT:    'change to LOWinit which I heard prevents adwin memory crashes
  
  init_CR()
  
  n_of_comm_timeouts = 0 ' used for debugging, goes to a par   
  repetition_counter  = 0 ' adwin arrays start at 1, but this counter starts at 0 -> we have to write to rep counter +1 all the time
  first_CR            = 0 ' this variable determines whether or not the CR after result is stored 
  wait_time           = 0
  digin_this_cycle    = 0
  cumulative_awg_counts   = 0
  
  remaining_time_in_long_CR_check  = 0
  
  time_spent_in_state_preparation =0
  time_spent_in_communication =0 
  time_spent_in_sequence =0
  duty_cycle = 0
  
  AWG_done_was_low = 1
  AWG_repcount_was_low =1
  AWG_sequence_repetitions_LDE = 0
  
  local_flag_1 = 0
  remote_flag_1 = 0
  remote_flag_2 = 0
  local_flag_2 = 0
  combined_success = 0
  adwin_comm_done = 0
  adwin_timeout_requested = 0
  success_mode_after_adwin_comm = 1 'SpinPumping
  fail_mode_after_adwin_comm = 0 'CR check
  timeout_mode_after_adwin_comm = 0
  mode_flag = 1
  
  success_event_counter = 0
  SSRO_result = 0
  
  mode = 0
  timer = 0
  
''''''''''''''''''''''''''''''''''''''
  'read params from python script 
''''''''''''''''''''''''''''''''''''''
  cycle_duration               = DATA_20[1]
  SP_duration                  = DATA_20[2]
  wait_after_pulse_duration    = DATA_20[3] 'Time to wait after turning off a laser pulse to ensure it is really off
  Dynamical_stop_ssro_threshold= DATA_20[4]
  Dynamical_stop_ssro_duration = DATA_20[5]
  is_master                    = DATA_20[6]
  is_two_setup_experiment      = Data_20[7]
  PLU_event_di_channel         = DATA_20[8]
  PLU_which_di_channel         = DATA_20[9]
  AWG_start_DO_channel         = DATA_20[10]
  AWG_done_DI_channel          = DATA_20[11]
  wait_for_awg_done_timeout_cycles = DATA_20[12]
  AWG_event_jump_DO_channel    = DATA_20[13]
  AWG_repcount_DI_channel      = DATA_20[14]
  remote_adwin_di_success_channel  = DATA_20[15]
  remote_adwin_di_fail_channel     = DATA_20[16]
  remote_adwin_do_success_channel  = DATA_20[17]
  remote_adwin_do_fail_channel     = DATA_20[18]
  adwin_comm_safety_cycles         = DATA_20[19]
  adwin_comm_timeout_cycles        = DATA_20[20]
  remote_awg_trigger_channel       = DATA_20[21]
  invalid_data_marker_do_channel   = DATA_20[22] 'marks timeharp data invalid
  No_of_sequence_repetitions       = DATA_20[23] 'how often do we run the sequence
  master_slave_awg_trigger_delay   = DATA_20[24]
  PLU_during_LDE              = DATA_20[25]
  LDE_is_init                 = DATA_20[26] ' is the first LDE element for init? Then ignore the PLU
  do_phase_stabilisation      = DATA_20[27]
  only_meas_phase             = DATA_20[28]
  do_dynamical_decoupling     = DATA_20[29]
  Phase_msmt_laser_DAC_channel= DATA_20[30] 
  Phase_stab_DAC_channel      = DATA_20[31]
  zpl1_counter_channel        = DATA_20[32]
  zpl2_counter_channel        = DATA_20[33]
  pid_points                  = DATA_20[34]
  pid_points_to_store         = DATA_20[35]
  sample_points               = DATA_20[36]
  raw_count_int_time_stab     = DATA_20[37]
  raw_count_int_time_meas     = DATA_20[38]
  raw_phase_stab_max_time     = DATA_20[39]
  modulate_stretcher_during_phase_msmt = DATA_20[40]
  max_LDE_attempts                = DATA_20[41]
  do_post_ent_phase_msmt      = DATA_20[42]
  
  ' float params from python
  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  Phase_Msmt_voltage           = DATA_21[5] 'PH Fix this
  Phase_Msmt_off_voltage       = DATA_21[6]
  PID_GAIN                     = DATA_21[7]
  PID_Kp                       = DATA_21[8]
  PID_Ki                       = DATA_21[9]
  PID_Kd                       = DATA_21[10]
  SETPOINT_angle               = DATA_21[11]
  stretcher_V_2pi              = DATA_21[12]
  stretcher_V_max              = DATA_21[13]
  Phase_Msmt_g_0               = DATA_21[14] ' Scaling factor to match APD channels
  Phase_Msmt_Vis               = DATA_21[15] ' Vis of interference
  LDE_element_duration         = DATA_21[16]
  decoupling_element_duration  = DATA_21[17]
  
  
  ' DD on demand stuff init
  max_sequence_duration = LDE_element_duration*max_LDE_attempts
  required_DD_repetitions = 0
  decoupling_repetitions = 0
  
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  AWG_repcount_DI_pattern = 2 ^ AWG_repcount_DI_channel
  PLU_event_di_pattern = 2 ^ PLU_event_di_channel
  PLU_which_di_pattern = 2 ^ PLU_which_di_channel
  remote_adwin_di_success_pattern = 2^ remote_adwin_di_success_channel
  remote_adwin_di_fail_pattern = 2^ remote_adwin_di_fail_channel
  zpl1_counter_pattern =  2 ^ (zpl1_counter_channel - 1)
  zpl2_counter_pattern =  2 ^ (zpl2_counter_channel - 1)
  
  count_int_cycles_stab = (300*raw_count_int_time_stab) / cycle_duration ' Want integration time for measured counts to be the same independent of the cycle duration
  count_int_cycles_meas = (300*raw_count_int_time_meas) / cycle_duration ' Want integration time for measured counts to be the same independent of the cycle duration
  phase_stab_max_cycles = (300*raw_phase_stab_max_time) / cycle_duration

  stretcher_V_correct = Round(1.2*stretcher_V_max/stretcher_V_2pi) * stretcher_V_2pi
  
  elapsed_cycles_since_phase_stab = 0
  Prop = 0
  Int = 0
  Dif = 0
  e = 0
  e_old = 0
  Sig = 0 
  store_index_stab = 0
  store_index_msmt = 0
  pid_time_factor = count_int_cycles_stab*cycle_duration/30000000
  
  
  
''''''''''''''''''''''''''''''''''''''
  ' initialize the data arrays. set to -1 to discriminate between 0-readout and no-readout
''''''''''''''''''''''''''''''''''''''
 
  '  ' enter desired values into the initializer array
  FOR i = 1 TO 100
    Initializer[i] = -1
  NEXT i

  '  ' enter desired values into the initializer array
  FOR i = 1 TO 100
    Float_Initializer[i] = -1.0
  NEXT i
  '  
  '  
  '  ' note: the MemCpy function only works for T11 processors.
  '  ' this is a faster way of filling up global data arrays in the external memory. See Adbasic manual
  array_step = 1
  FOR i = 1 TO max_single_click_ent_repetitions/100
    MemCpy(Initializer[1],DATA_100[array_step],100)
    MemCpy(Initializer[1],DATA_101[array_step],100)
    MemCpy(Initializer[1],DATA_102[array_step],100)
    MemCpy(Initializer[1],DATA_103[array_step],100)
    MemCpy(Initializer[1],DATA_108[array_step],100)
    MemCpy(Initializer[1],DATA_109[array_step],100)
    MemCpy(Initializer[1],DATA_114[array_step],100)
    array_step = array_step + 100
  NEXT i
  
  array_step = 1
  FOR i = 1 TO max_pid/100
    MemCpy(Initializer[1],DATA_104[array_step],100)
    MemCpy(Initializer[1],DATA_105[array_step],100)
    MemCpy(Initializer[1],DATA_106[array_step],100)
    MemCpy(Initializer[1],DATA_107[array_step],100)
    MemCpy(Float_Initializer[1],DATA_110[array_step],100)
    array_step = array_step + 100
  NEXT i
  
  'initialize the max_SP_bins
  FOR i = 1 TO max_SP_bins
    DATA_29[i] = 0
  NEXT i
   
''''''''''''''''''''''''''''
  ' init parameters
''''''''''''''''''''''''''''
  
  
  
  PAR_55 = 0                      ' Invalid data marker
  Par_60 = timer                  ' time
  Par_61 = 0                      ' current mode
  PAR_62 = 0                      ' n_of_communication_timeouts for debugging
  PAR_63 = 0                      ' stop flag
  PAR_65 = -1                     ' for debugging
  PAR_73 = repetition_counter     ' repetition counter
  PAR_77 = success_event_counter  ' number of successful runs
  PAR_80 = 0                      ' n_of timeouts when waiting for AWG done

'''''''''''''''''''''''''
  ' flow control: 
'''''''''''''''''''''''''

  if (do_dynamical_decoupling = 1) then
    mode_after_LDE = 5 ' dynamical decoupling
  else
    mode_after_LDE = 6 ' electron RO
  endif
  
  if (do_post_ent_phase_msmt = 1) then
    mode_after_e_msmt = 9
  else
    mode_after_e_msmt = 7
      
  endif
  
  if (only_meas_phase = 1) then
    mode_after_phase_stab = 1 'Phase msmt

    if (do_phase_stabilisation = 1) then
      mode_after_expm = 0 ' Go back to phase stabilisation
    else
      mode_after_expm = 1 ' Just continuously measure phase
    endif
    
  else
    mode_after_phase_stab = 2 ' Go to CR check
    mode_after_expm = 2 ' Go back to CR check until phase stabilisation needed
  endif

  if (do_phase_stabilisation = 1) then
    init_mode = 0 ' First mode is phase stabilisation / comm before phase stab
  else
    init_mode = mode_after_phase_stab
  endif
 
  mode = init_mode
  
'''''''''''''''''''''''''''
  ' define channels etc
'''''''''''''''''''''''''''
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE, counter_channel, 000010000b) 'configure counter
  
  P2_Digprog(DIO_MODULE,0011b) ' in  is now 16:23   'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel, 0)
  P2_DIGOUT(DIO_MODULE, remote_adwin_do_fail_channel, 0)
  P2_DIGOUT(DIO_MODULE, remote_adwin_do_success_channel, 0)
  
   
  processdelay = cycle_duration   ' the event structure is repeated at this period. On T11 processor 300 corresponds to 1us. Can do at most 300 operations in one round.

  ' Phase shifting defns
  P2_DAC_2(Phase_stab_DAC_channel, 0) ' Set phase shifter voltage to zero PH Think about this
  
  
  P2_CNT_MODE(CTR_MODULE, zpl1_counter_channel,000010000b) ' Configure the ZPL counter
  P2_CNT_CLEAR(CTR_MODULE, zpl1_counter_pattern)
    
EVENT:
  
  'write information to parse for live monitoring
  PAR_61 = mode   
  Par_60 = timer    
  IF (wait_time > 0)  THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
      
      CASE 100 ' communication between adwins
        ' communication logic: there is a fail and a success trigger. Both 0 means no signal has been sent, both high on slave side means signal has been received from master
        ' The master decides if both setups are successful, sends this to the slave, and waits for the slave to go on 11 to confirm communication, and sends a jump to both awg if succesful

        if (timer = 0) then ' forget values from previous runs
          adwin_timeout_requested = 0
          combined_success = 0
          adwin_comm_done = 0
          remote_flag_1 = 0
          remote_flag_2 = 0
        endif
        
        IF (adwin_comm_done > 0) THEN 'communication run was successful. Decide what to do next and clear memory. Second if statement (rather than ELSE) saves one clock cycle
          Selectcase combined_success
            Case 0 'fail: go to fail mode
              mode = fail_mode_after_adwin_comm
            Case 1 ' both successful: continue
              mode = success_mode_after_adwin_comm
            Case 2 ' local timeout
              mode = timeout_mode_after_adwin_comm
          endselect
          
          time_spent_in_communication = time_spent_in_communication + timer
          timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, 0) ' set the channels low
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 0) ' set the channels low
        ELSE
          'previous communication was not successful
          DATA_101[repetition_counter+1] = DATA_101[repetition_counter+1] + timer  ' store time spent in adwin communication for debugging
          digin_this_cycle = P2_DIGIN_LONG(DIO_MODULE)   ' read remote input channels
          if ( (digin_this_cycle AND remote_adwin_di_success_pattern) > 0) then
            remote_flag_1 = 1
          endif
          if ( (digin_this_cycle AND remote_adwin_di_fail_pattern) > 0) then
            remote_flag_2 = 1
          endif
                
          IF (is_master>0) THEN 

            if ((remote_flag_1 > 0 ) and (remote_flag_2 > 0)) then ' own signal successfully communicated to other side -> go on to next mode
              adwin_comm_done = 1 ' go to next mode in cleanup step below
              wait_time = adwin_comm_safety_cycles ' make sure the other adwin is ready for counting etc.
            else ' own signal not yet received on other side -> send it or wait for slave's signal to decide what to do
              IF ((remote_flag_1 >0) or (remote_flag_2 >0)) then ' remote signal received: decide whether both setups were successful
                if (((mode_flag = 1) and ((local_flag_1 > 0) and (remote_flag_1 >0))) or ((mode_flag = 2) and ((local_flag_2 > 0) and (remote_flag_2 >0)))) then
                  combined_success = 1 ' success
                else
                  combined_success = 0 ' failure (wrong mode!)
                endif
                'send combined success and then wait for confirmation
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, combined_success)
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 1-combined_success)
                
                ' the communcation timeout causes the adwin to crash. It is overburdened. I therefore have one adwin wait for the other indefinitely
              ELSE
                '              no signal received. Did the connection time out? (we only get here in case we have 00 on the inputs)
                if (timer > adwin_comm_timeout_cycles) then
                  inc(n_of_comm_timeouts) ' give to par for local debugging
                  par_62 = n_of_comm_timeouts
                  combined_success = 2 ' flag for timeout
                  adwin_comm_done = 1 ' below: reset everything and go on
                endif                
              ENDIF
              
            endif
            
                    
          ELSE ' I'm the slave, and the communication is not yet done.
            if (timer = 0) then ' first round: send my signal
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, local_flag_1)
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, local_flag_2) 
            else 'Did the master tell me what to do?
              if ((remote_flag_1 >0 ) or (remote_flag_2 >0)) then 'signal received
                P2_DIGOUT(DIO_MODULE, remote_adwin_do_success_channel, 1) 'send confirmation: both channels high
                P2_DIGOUT(DIO_MODULE, remote_adwin_do_fail_channel, 1) 'send confirmation
                combined_success = remote_flag_1
                wait_time = adwin_comm_safety_cycles ' wait in event loop for adwin communication safety time to make sure the other setup has received our signal
                adwin_comm_done = 1 ' below: reset everything and go on. I have taken this out!!! NK 20170331 (causes master to crash).
              else ' still no signal. Did the connection time out?
                IF (adwin_timeout_requested > 0) THEN ' previous run: timeout requested.
                  adwin_comm_done = 1 ' communication done (timeout). Still: reset parameters below
                  combined_success = 2
                  inc(n_of_comm_timeouts) ' give to par for local debugging
                  par_62 = n_of_comm_timeouts
                ELSE ' should I request a timeout in the next round now?
                  if (timer > adwin_comm_timeout_cycles) then
                    P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, 0) ' stop signalling
                    P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 0)
                    wait_time = adwin_comm_safety_cycles ' wait in event loop for adwin communication safety time
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
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
        ELSE
          counts_1 = P2_CNT_READ(CTR_MODULE, counter_channel) 'read counter
          IF (counts_1 >= Dynamical_stop_ssro_threshold) THEN ' photon detected
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            wait_time = dynamical_stop_SSRO_duration - timer ' make sure the SSRO element always has the same length (even in success case) to keep track of the carbon phase xxx to do: is this still accurate to the us?
            time_spent_in_sequence = time_spent_in_sequence + timer
            timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
            SSRO_result = 1
            DATA_103[repetition_counter+1] = SSRO_result 'save as last electron readout
            if (Success_of_SSRO_is_ms0>0) then ' Success_of_SSRO_is_ms0 is usually 1, but could be dynamically inverted here
              local_flag_1 = 1 
              local_flag_2 = 0
              mode = success_mode_after_SSRO
            else 
              local_flag_1 = 0
              local_flag_2 = 1
              mode = fail_mode_after_SSRO
            endif 
          ELSE 'no photon detected
            SSRO_result = 0
            DATA_103[repetition_counter+1] = SSRO_result 'save as last electron readout
            if (timer = dynamical_stop_SSRO_duration) then ' no count after ssro duration -> failed  xxx to do: is this still accurate to the us?
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
              IF (Success_of_SSRO_is_ms0 = 0) THEN
                local_flag_1 = 1 'remember for adwin communication in next mode. Success_of_SSRO_is_ms0 is usually 1, but could be inverted here
                local_flag_2 =0
                mode = success_mode_after_SSRO
              ELSE 
                local_flag_1 = 0
                local_flag_2 = 1
                mode = fail_mode_after_SSRO
              ENDIF
            endif
          ENDIF

        ENDIF
   

      CASE 0 ' Setup comm before phase stabilisation
      
        IF (is_two_setup_experiment = 0) THEN 'only one setup involved. Skip communication step
          mode = 10 'crack on with phase stab.
          timer = -1
        ELSE ' two setups involved
              
          local_flag_1 = 1 'flag 1 communicates that phase stabilising
          local_flag_2 = 0
          mode_flag = 1
          mode = 100 'go to communication step
          timeout_mode_after_adwin_comm = 0 ' Keeps waiting until gets confirmation that ready for phase stab.
          fail_mode_after_adwin_comm = 0 ' If wrong mode, still just go back to waiting for confirmation
          success_mode_after_adwin_comm = 10 ' After communication, go on to phase stab
          timer = -1
        endif
        
        
      CASE 10 'Phase stabilisation
        
        IF (timer = 0) THEN 
          
          'Check if stop signal received, or repetitions exceeded if only doing phase measurement (otherwise happens in CR check)
          IF ((Par_63 > 0) or ((only_meas_phase = 1) and ((repetition_counter >= max_repetitions) or (repetition_counter >= No_of_sequence_repetitions)))) THEN ' stop signal received: stop the process
            END
          ENDIF
          
          if (is_master > 0) then

            P2_CNT_ENABLE(CTR_MODULE, 0000b)
            P2_CNT_CLEAR(CTR_MODULE, zpl1_counter_pattern+zpl2_counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE, zpl1_counter_pattern+zpl2_counter_pattern)    'turn on counter
            P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_voltage+32768) ' turn on phase msmt laser
            old_counts_1 = 0
            old_counts_2 = 0
            
          endif
          store_index = 0
          index = 0
        ELSE
          if (is_master > 0) then
            if (index = count_int_cycles_stab) then ' Only reads apds every count int cycles
              index = 0
              counts_1 = P2_CNT_READ(CTR_MODULE, zpl1_counter_channel) - old_counts_1 'read counter
              counts_2 = P2_CNT_READ(CTR_MODULE, zpl2_counter_channel) - old_counts_2
              old_counts_1 = old_counts_1 + counts_1
              old_counts_2 = old_counts_2 + counts_2
              inc(store_index)
              if ((store_index > (pid_points-pid_points_to_store))) then            
                inc(store_index_stab)
                PAR_74 = store_index_stab
                DATA_104[store_index_stab] = counts_1
                DATA_105[store_index_stab] = counts_2
              endif

              cosarg = 2*((counts_1 / (counts_1 + counts_2*Phase_Msmt_g_0)) - 0.5) * Phase_Msmt_Vis
              if (cosarg >= 1) then
                cosarg = 0.999
              endif
              if (cosarg <= -1) then
                cosarg = -0.999
              endif
              
              counts = ARCCOS(cosarg)
              
              DATA_110[store_index_stab] = counts
              
              ' PID control
              e = SETPOINT_angle - counts
              Prop = PID_Kp * e                   ' Proportional term      
              Int = PID_Ki * ( Int + e )                    ' Integration term                                              ' 
              Dif = PID_Kd * ( e - e_old )             ' Differentiation term
              Sig = Sig + PID_GAIN * pid_time_factor* (Prop + Int + Dif) ' Calculate Output
              FPAR_74 = Sig
              ' Output inside reach of fibre stretcher?
              if (Sig > stretcher_V_max) then
                Sig = Sig - stretcher_V_correct
              endif
              if (Sig < -stretcher_V_max) then
                Sig = Sig + stretcher_V_correct
              endif
            
              ' Output
              P2_DAC_2(Phase_stab_DAC_channel, Sig*3276.8+32768 )
  
              ' Values needed for next cycle
              e_old = e
            endif
          
          else
            if (index = count_int_cycles_stab) then ' Just tick over waiting for the other adwin to phase stabilise.
              index = 0
              inc(store_index)
            endif
          endif
          
          inc(index)
          
          if (store_index>=pid_points) then
            if (is_master > 0) then
              P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser
            endif
            elapsed_cycles_since_phase_stab = 0 ' Set the elapsed time to zero
            mode = mode_after_phase_stab 'crack on
            timer = -1
            remaining_time_in_long_CR_check = 2000

          endif
        
          
        ENDIF
      
      
      CASE 1 ' Phase msmt
        IF (timer = 0) THEN 

          'Check if repetitions exceeded (here just in case not doing phase stabilisation)
          IF (((do_phase_stabilisation = 0) and (only_meas_phase = 1)) and (((Par_63 > 0) or (repetition_counter >= max_repetitions)) or (repetition_counter >= No_of_sequence_repetitions))) THEN ' stop signal received: stop the process
            END
          ENDIF
          
          P2_CNT_ENABLE(CTR_MODULE, 0000b)
          P2_CNT_CLEAR(CTR_MODULE, zpl1_counter_pattern+zpl2_counter_pattern)    'clear counter 'zpl1_counter_pattern
          P2_CNT_ENABLE(CTR_MODULE, zpl1_counter_pattern+zpl2_counter_pattern)    'turn on counter
          P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_voltage+32768) ' turn on phase msmt laser (Phase_msmt_laser_DAC_channel, Phase_Msmt_voltage)
          old_counts_1 = 0
          old_counts_2 = 0
          index = 0
          store_index = 0
          
          total_cycles = count_int_cycles_meas*sample_points
        ELSE
          if (modulate_stretcher_during_phase_msmt = 1) THEN
            ' Linearly ramp output
            P2_DAC_2(Phase_stab_DAC_channel, (2 * timer/total_cycles ) * stretcher_V_max*3276.8+32768 )
          endif
                       
          if (index = count_int_cycles_meas) then ' Only reads apds every count int cycles
            index = 0
            counts_1 = P2_CNT_READ(CTR_MODULE, zpl1_counter_channel) - old_counts_1 'read counter
            counts_2 = P2_CNT_READ(CTR_MODULE, zpl2_counter_channel) - old_counts_2
            old_counts_1 = old_counts_1 + counts_1
            old_counts_2 = old_counts_2 + counts_2
            inc(store_index_msmt)
            inc(store_index)
            DATA_106[store_index_msmt] = counts_1
            DATA_107[store_index_msmt] = counts_2
            
          endif
          
          inc(index)
          
          if (store_index >= sample_points) then
            
            if (modulate_stretcher_during_phase_msmt = 1) THEN
              ' Linearly ramp output
              P2_DAC_2(Phase_stab_DAC_channel, 0 )
            endif
            
            mode = 7
            timer = -1
            P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser ( Phase_msmt_laser_DAC_channel, Phase_Msmt_off_voltage)

          endif
          
        endif
        
      CASE 2 'CR check     
        
        cr_result = CR_check(first_CR,repetition_counter) ' do CR check.  if first_CR is high, the result will be saved as CR_after. 
        '        record_cr_counts()
        
        'check for break put after such that the last run records a CR_after result
        IF (((Par_63 > 0) or (repetition_counter >= max_repetitions)) or (repetition_counter >= No_of_sequence_repetitions)) THEN ' stop signal received: stop the process
          END
        ENDIF
        
        IF (remaining_time_in_long_CR_check > 0) THEN
          cr_result = -1
        ENDIF
        
        if ((cr_result = -1) or (cr_result = 1)) then
          ' Need to wait until a full CR check cycle has finished before jumping out, otherwise things get messy
          if ((elapsed_cycles_since_phase_stab > phase_stab_max_cycles) and (do_phase_stabilisation > 0)) then
            mode = init_mode 
            timer = -1
            reset_CR() ' For optimal robustness, reset the CR check variables.
          else
          
            if ( cr_result > 0 ) then
              ' In case the result is not positive, the CR check will be repeated/continued
              time_spent_in_state_preparation = time_spent_in_state_preparation + timer
              timer = -1     
              IF (is_two_setup_experiment = 0) THEN 'only one setup involved. Skip communication step
                mode = 3 'go to spin pumping directly
              ELSE ' two setups involved
            
                local_flag_1 = 0
                local_flag_2 = 1  'flag 2 communicates that CR checking
                mode_flag = 2
                mode = 100 'go to communication step
                timeout_mode_after_adwin_comm = 2 ' Keeps waiting until gets confirmation that CR check succeeded.
                fail_mode_after_adwin_comm = init_mode ' If wrong mode,  go back to phase stabilistation or CR check if not phase stabilising!
                success_mode_after_adwin_comm = 3 ' After communication, ' go to spin pumping 
          
              ENDIF
            endif
          endif
          
        endif
          
        
      CASE 3    ' E spin pumping
        
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768) ' or turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)                        ' clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)                       ' turn on counter
          old_counts_1 = 0
        ELSE
          counts_1 = P2_CNT_READ(CTR_MODULE,counter_channel)
          DATA_29[timer] = DATA_29[timer] + counts_1 - old_counts_1    ' for spinpumping arrival time histogram
          old_counts_1 = counts_1
                    
          IF (timer = SP_duration) THEN
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser      
            mode = 4 ' On to entanglement generation
            wait_time = wait_after_pulse_duration 'wait a certain number of cycles to make sure the lasers are really off
            time_spent_in_state_preparation = time_spent_in_state_preparation + timer
            timer = -1
          ENDIF
        ENDIF
        
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
            inc(AWG_sequence_repetitions_LDE) ' increase the number of attempts counter
          ENDIF
          AWG_repcount_was_low = 0
        else
          AWG_repcount_was_low = 1
        endif
        
        if ((digin_this_cycle AND PLU_event_di_pattern) >0) THEN ' PLU signal received
          DATA_108[repetition_counter+1] = elapsed_cycles_since_phase_stab
          DATA_109[repetition_counter+1] = store_index_stab
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
          mode = mode_after_LDE
        else ' no plu signal. check for timeout or done
          IF ((digin_this_cycle AND AWG_done_DI_pattern) > 0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (awg_done_was_low =1) then
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              if ((PLU_during_LDE = 0) or (LDE_is_init = 1)) then ' this is a single-setup measurement. Go on to next mode
                DATA_108[repetition_counter+1] = elapsed_cycles_since_phase_stab
                DATA_109[repetition_counter+1] = store_index_stab
                mode = mode_after_LDE
              else ' two setups involved: Done means failure of the sequence at the moment (PH For the ent on demand THIS SHOULD COMPENSATE BY CREATING A BEST E STATE)
                mode = 8 ' finalize and go to cr check
              endif
            endif 
            awg_done_was_low = 0 ' remember
          ELSE ' awg done is low.
            awg_done_was_low = 1
            if( timer > wait_for_awg_done_timeout_cycles) then
              inc(PAR_80) ' signal that we have an awg timeout
              END ' terminate the process
            endif
          ENDIF  
        endif
        

           

        
      CASE 5 ' Decoupling 
        
        ' AWG will go to dynamical decoupling, and output a sync pulse to the adwin once in a while
        ' Each adwin will count the number pulses and send a jump once the specified time has been reached.
        IF (timer =0) THEN 'first go: calculate required repetitions
          awg_repcount_was_low = 1
          awg_done_was_low = 1
          
          required_DD_repetitions = round((max_sequence_duration - AWG_sequence_repetitions_LDE*LDE_element_duration)/decoupling_element_duration) - 2
          IF (required_DD_repetitions < 2) THEN
            required_DD_repetitions = 2
          ENDIF
          FPAR_67  = decoupling_repetitions
        ENDIF 
        
        
        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_repcount_DI_pattern)>0) THEN 'awg has switched to high. this construction prevents double counts if the awg signal is long
          if (awg_repcount_was_low = 1) then
            inc(decoupling_repetitions)  
          endif
          awg_repcount_was_low = 0
        ELSE
          awg_repcount_was_low = 1
        ENDIF      
                          
        IF (decoupling_repetitions = required_DD_repetitions-1) THEN 'give jump trigger and go to next mode: tomography
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to tomo pulse sequence
          CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*3ns
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
          mode = 6
                                          
        ENDIF
        
        
      CASE 6 ' wait for RO trigger to come in
        ' monitor inputs 

        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN  'awg trigger tells us it is done with the entanglement sequence.
          if (awg_done_was_low =1) then
            timer = -1
            mode = 200 'SSRO
            success_mode_after_SSRO = mode_after_e_msmt
            fail_mode_after_SSRO = mode_after_e_msmt
          endif 
          awg_done_was_low = 0 ' remember
        ELSE ' awg done is low.
          awg_done_was_low = 1
          if( timer > wait_for_awg_done_timeout_cycles) then
            inc(PAR_80) ' signal that we have an awg timeout
            END ' terminate the process
          endif
        ENDIF
        
          
      
      CASE 9 ' Phase msmt after success
        IF (timer = 0) THEN 
          
          P2_CNT_ENABLE(CTR_MODULE, 0000b)
          P2_CNT_CLEAR(CTR_MODULE, zpl1_counter_pattern+zpl2_counter_pattern)    'clear counter 'zpl1_counter_pattern
          P2_CNT_ENABLE(CTR_MODULE, zpl1_counter_pattern+zpl2_counter_pattern)    'turn on counter
          P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_voltage+32768) ' turn on phase msmt laser (Phase_msmt_laser_DAC_channel, Phase_Msmt_voltage)
          index = 0  
        ELSE
                       
          if (index = count_int_cycles_meas) then ' Only reads apds every count int cycles
            counts_1 = P2_CNT_READ(CTR_MODULE, zpl1_counter_channel) 
            counts_2 = P2_CNT_READ(CTR_MODULE, zpl2_counter_channel)
            DATA_106[repetition_counter+1] = counts_1
            DATA_107[repetition_counter+1] = counts_2
             
            mode = 7 ' Finish the things
            timer = -1
            P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser ( Phase_msmt_laser_DAC_channel, Phase_Msmt_off_voltage)

          endif
          
            
          
        endif
        
        inc(index)
          
      CASE 7 'store the result of the e measurement and the sync number counter
        DATA_102[repetition_counter+1] = cumulative_awg_counts + AWG_sequence_repetitions_LDE ' store sync number of successful run
        DATA_114[repetition_counter+1] = PAR_55 'what was the state of the invalid data marker?
        DATA_100[repetition_counter+1] = decoupling_repetitions
        
        mode = 8 'go to reinit and CR check
        INC(repetition_counter) ' count this as a repetition. DO NOT PUT IN 7, because 12 can be used to init everything without previous success!!!!!
        first_CR=1 ' we want to store the CR after result in the next run
        inc(success_event_counter)
        PAR_77 = success_event_counter ' for the LabView live update
        
                              
      CASE 8 ' reinit all variables and go to cr check
        Par_73 = repetition_counter ' write to PAR
        cumulative_awg_counts = cumulative_awg_counts + AWG_sequence_repetitions_LDE 'remember sync counts, independent of success or failure
        'forget all parameters of previous runs
        AWG_repcount_was_low = 1
        AWG_done_was_low = 1  
        AWG_sequence_repetitions_LDE = 0
        decoupling_repetitions = 0
        remaining_time_in_long_CR_check = 0
        
        
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
        mode = mode_after_expm ' go to CR check or to relevant starting mode.
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
    INC(elapsed_cycles_since_phase_stab)
    DEC(remaining_time_in_long_CR_check)
  endif

    
FINISH:
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0) 
  if (is_master > 0) then
    P2_DAC_2(Phase_msmt_laser_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser
  endif
