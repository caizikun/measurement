'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.1.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = TUD278094  DASTUD\TUD278094
' Bookmarks                      = 3,3,19,19,81,81,83,83,163,163,304,304,305,305,327,327,598,598,668,669,670
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
' 100 : ADWIN communication
' 200 : dynamical stop SSRO

'   0 : Phase check (master only)
'   1 : Phase msmt (master only, not part of experimental seq.)
'   2 : CR check
'   3 : E spin pumping into ms=+/-1
'   4 : Send AWG trigger in case of success on both sides.
'   5 : run entanglement sequence and count reps while waiting for PLU success signal
'   6 : decoupling and counting reps
'   7 : electron RO
'   8 : Parameter reinitialization


#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr_mod_Bell.inc
#INCLUDE math.inc

' #DEFINE max_repetitions is defined as 500000 in cr check. Could be reduced to save memory
#DEFINE max_single_click_ent_repetitions    20000 ' high number needed to have good statistics in the phase msmt stuff
#DEFINE max_SP_bins       2000  
#DEFINE max_pid       500000 ' Max number of measured counts for pid stabilisation (5 ms / 200 mus ~ 25, 25*20000 ~ 500000, so can do 20000 repetitions)
#DEFINE max_sample    500000 ' Max number of measured count for sampling - Note that can do fewer repetitions if want to sample for longer.

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
DIM DATA_100[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' Phase_correction_repetitions needed to correct the phase of the carbon 
DIM DATA_101[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' time spent for communication between adwins 
DIM DATA_102[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' number of repetitions until the first succesful entanglement attempt 
DIM DATA_103[max_single_click_ent_repetitions] AS LONG at DRAM_Extern' SSRO counts electron spin readout performed in the adwin seuqnece 
' PH Fix this
DIM DATA_104[max_pid] AS LONG at DRAM_Extern' Holds data on the measured counts during the PID stabilisation
DIM DATA_105[max_sample] AS LONG at DRAM_Extern' Holds data on the measured counts during the sampling time

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
DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage, Phase_Msmt_voltage, Phase_Msmt_off_voltage AS FLOAT
DIM Phase_msmt_DAC_channel as Long
DIM time_spent_in_state_preparation, time_spent_in_sequence, time_spent_in_communication as LONG
DIM duty_cycle as FLOAT
DIM AWG_sequence_repetitions_LDE AS long
DIM old_counts, counts AS LONG

' Channels & triggers
dim AWG_done_was_low, AWG_repcount_was_low, PLU_event_di_was_high, master_slave_awg_trigger_delay as long
DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_repcount_DI_channel, AWG_event_jump_DO_channel, AWG_done_DI_pattern, AWG_repcount_DI_pattern AS LONG
DIM PLU_event_di_channel, PLU_event_di_pattern, PLU_which_di_channel, PLU_which_di_pattern AS LONG
dim sync_trigger_counter_channel, sync_trigger_counter_pattern as long
DIM invalid_data_marker_do_channel AS LONG

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
DIM PLU_during_LDE, LDE_is_init as long
DIM is_master,cumulative_awg_counts as long

' Sequence flow control
DIM do_phase_stabilisation, only_meas_phase, do_dynamical_decoupling as long
DIM init_mode, mode_after_phase_stab, mode_after_LDE as long

' Phase shifter PID params (note that only the master ADWIN controls the phase)
DIM Sig, setpoint, Prop, Dif,Int                   AS FLOAT        ' PID terms
DIM PID_GAIN,PID_Kp,PID_Kd,PID_Ki                         AS FLOAT        ' PID parameters
DIM e, e_old                              AS FLOAT        ' error term
DIM pid_time_factor                       AS FLOAT        ' account for changes in the adwin clock cycle
DIM offset_index,store_index,index,pid_cycles,sample_cycles AS LONG ' Keep track of how long to sample for etc.
DIM count_int_cycles              AS LONG ' Number of cycles to count for per PID / phase msmt cycle
DIM zpl1_counter_channel,zpl2_counter_channel,zpl1_counter_pattern,zpl2_counter_pattern  AS LONG ' Channels for ZPL APDs

Dim time as long
LOWINIT:    'change to LOWinit which I heard prevents adwin memory crashes
  
  init_CR()
  
  n_of_comm_timeouts = 0 ' used for debugging, goes to a par   
  repetition_counter  = 0 ' adwin arrays start at 1, but this counter starts at 0 -> we have to write to rep counter +1 all the time
  first_CR            = 0 ' this variable determines whether or not the CR after result is stored 
  wait_time           = 0
  digin_this_cycle    = 0
  cumulative_awg_counts   = 0
  
  time_spent_in_state_preparation =0
  time_spent_in_communication =0 
  time_spent_in_sequence =0
  duty_cycle = 0
  
  AWG_done_was_low = 1
  AWG_repcount_was_low =1
  AWG_sequence_repetitions_LDE = 0
  
  local_success = 0
  remote_success = 0
  remote_fail = 0
  local_fail = 0
  combined_success = 0
  adwin_comm_done = 0
  adwin_timeout_requested = 0
  success_mode_after_adwin_comm = 1 'SpinPumping
  fail_mode_after_adwin_comm = 0 'CR check
      
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
  PLU_during_LDE                   = DATA_20[25]
  LDE_is_init                    = DATA_20[26] ' is the first LDE element for init? Then ignore the PLU
  ' PH NEED TO FIX THIS
  Phase_msmt_DAC_channel      = DATA_20[27]
  pid_cycles                  = DATA_20[28]
  sample_cycles               = DATA_20[29]
  
   
  ' float params from python
  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  A_SP_voltage                 = DATA_21[3]
  E_RO_voltage                 = DATA_21[4]
  A_RO_voltage                 = DATA_21[5]
  Phase_Msmt_voltage           = DATA_21[6] 'PH Fix this
  Phase_Msmt_off_voltage       = DATA_21[7]
  PID_GAIN                     = DATA_21[8]
  PID_Kp                       = DATA_21[9]
  PID_Ki                       = DATA_21[10]
  PID_Kd                       = DATA_21[11]
  
   
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  AWG_repcount_DI_pattern = 2 ^ AWG_repcount_DI_channel
  PLU_event_di_pattern = 2 ^ PLU_event_di_channel
  PLU_which_di_pattern = 2 ^ PLU_which_di_channel
  remote_adwin_di_success_pattern = 2^ remote_adwin_di_success_channel
  remote_adwin_di_fail_pattern = 2^ remote_adwin_di_fail_channel
  sync_trigger_counter_channel = 3
  sync_trigger_counter_pattern = 2 ^ (sync_trigger_counter_channel - 1)
  zpl1_counter_channel = 2
  zpl1_counter_pattern =  2 ^ (zpl1_counter_channel - 1)
  
  e = 0
  e_old = 0
  Sig = 0 
  pid_time_factor = count_int_cycles*cycle_duration/30000000
  
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
  FOR i = 1 TO 520 ' 520 is derived from max_purification_length/100
    MemCpy(Initializer[1],DATA_100[array_step],100)
    MemCpy(Initializer[1],DATA_101[array_step],100)
    MemCpy(Initializer[1],DATA_102[array_step],100)
    MemCpy(Initializer[1],DATA_103[array_step],100)
    array_step = array_step + 100
  NEXT i
    
  FOR i = 1 TO 520 ' 520 is derived from max_purification_length/100
    MemCpy(Initializer[1],DATA_104[array_step],100)
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
  PAR_77 = success_event_counter  ' number of successful runs
  PAR_80 = 0                      ' n_of timeouts when waiting for AWG done
  PAR_62 = 0                      ' n_of_communication_timeouts for debugging
  PAR_65 = -1 ' for debugging
  par_10 = -1
  par_11 = -1
  par_12 = -1
  par_13 = -1
  par_14 = -1
  par_15 = -1
  
  Par_62 = 0
'''''''''''''''''''''''''
  ' flow control: 
'''''''''''''''''''''''''

  if (do_dynamical_decoupling = 1) then
    mode_after_LDE = 5 ' dynamical decoupling
  else 
    mode_after_LDE = 6 ' electron RO
  endif
  
  if (only_meas_phase = 1) then
    mode_after_phase_stab = 1 'Phase stab msmt
  else
    mode_after_phase_stab = 2 ' CR check
  endif

  if (do_phase_stabilisation = 1) then
    init_mode = 0 'Phase stabilisation
  else
    init_mode = 2 ' CR check
  endif
  
  
'''''''''''''''''''''''''''
  ' define channels etc
'''''''''''''''''''''''''''
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,Phase_msmt_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser

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
  
  ' Phase shifting defns
  P2_DAC_2(14, 0) ' Set phase shifter voltage to zero
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
                  par_62 = n_of_comm_timeouts
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
                  par_62 = n_of_comm_timeouts
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
          P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
        ELSE
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) 'read counter
          IF (counts >= Dynamical_stop_ssro_threshold) THEN ' photon detected
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE, sync_trigger_counter_pattern)  ' disable photon counter, keep sync trigger counter on
            wait_time = dynamical_stop_SSRO_duration - timer ' make sure the SSRO element always has the same length (even in success case) to keep track of the carbon phase xxx to do: is this still accurate to the us?
            time_spent_in_sequence = time_spent_in_sequence + timer
            timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
            SSRO_result = 1
            DATA_103[repetition_counter+1] = SSRO_result 'save as last electron readout
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
            DATA_103[repetition_counter+1] = SSRO_result 'save as last electron readout
            if (timer = dynamical_stop_SSRO_duration) then ' no count after ssro duration -> failed  xxx to do: is this still accurate to the us?
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
   

         
      CASE 0 ' Phase check
        IF (timer = 0) THEN 
          P2_CNT_CLEAR(CTR_MODULE, zpl1_counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, zpl1_counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,Phase_msmt_DAC_channel, 3277*Phase_Msmt_voltage+32768) ' turn off phase msmt laser
          old_counts = 0
          offset_index = repetition_counter * pid_cycles ' PH CHECK
          index = 0
          store_index = 0
        ELSE
          if (index = count_int_cycles) then ' Only reads apds every count int cycles
            index = 0
            counts = P2_CNT_READ(CTR_MODULE, zpl1_counter_channel) - old_counts 'read counter
            old_counts = old_counts + counts
            inc(store_index)
            DATA_26[offset_index + store_index] = counts 
 
            ' PID control
            e = SETPOINT - counts
            Prop = PID_Kp * e'                   ' Proportional term      
            Int = PID_Ki * ( Int + e )                    ' Integration term                                              ' 
            Dif = PID_Kd * ( e - e_old )             ' Differentiation term
            Sig = Sig + PID_GAIN * pid_time_factor* (Prop + Int + Dif) ' Calculate Output
  
            ' Output inside reach of fibre stretcher?
            if (Sig > 9.5) then
              Sig = Sig - 11.0775 ' PH Shouldnt be hard coded
            endif
            if (Sig < -9.5) then
              Sig = Sig + 11.0775
            endif
        
            ' Output
            P2_DAC_2(14, Sig*3276.8+32768 )
  
            ' Values needed for next cycle
            e_old = e
          endif
          
          inc(index)
          
          if (timer>pid_cycles) then
            mode = mode_after_phase_stab
            timer = -1
            P2_DAC(DAC_MODULE,Phase_msmt_DAC_channel, 3277*Phase_Msmt_off_voltage+32768) ' turn off phase msmt laser

          endif
        
          
        ENDIF
        
      CASE 1 ' Phase msmt
        IF (timer = 0) THEN 
          P2_CNT_CLEAR(CTR_MODULE, zpl1_counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, zpl1_counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,Phase_msmt_DAC_channel, 3277*Phase_Msmt_voltage+32768) ' turn off phase msmt laser
          old_counts = 0
          offset_index = repetition_counter * sample_cycles ' PH CHECK
          index = 0
          store_index = 0
        ELSE
          if (index = count_int_cycles) then ' Only reads apds every count int cycles
            index = 0
            counts = P2_CNT_READ(CTR_MODULE, zpl1_counter_channel) - old_counts 'read counter
            old_counts = old_counts + counts
            inc(store_index)
            DATA_26[offset_index + store_index] = counts 
            
          endif
          
          inc(index)
          
          if (timer>sample_cycles) then
            mode = 7
            timer = -1
            P2_DAC(DAC_MODULE,Phase_msmt_DAC_channel, 3277*Phase_Msmt_voltage+32768) ' turn off phase msmt laser

          endif
          
        endif
        
          
      CASE 2 'CR check
      
        cr_result = CR_check(first_CR,repetition_counter) ' do CR check.  if first_CR is high, the result will be saved as CR_after. 
        
        'check for break put after such that the last run records a CR_after result
        IF (((Par_63 > 0) or (repetition_counter >= max_repetitions)) or (repetition_counter >= No_of_sequence_repetitions)) THEN ' stop signal received: stop the process
          END
        ENDIF

        if ( cr_result > 0 ) then
          ' In case the result is not positive, the CR check will be repeated/continued
          time_spent_in_state_preparation = time_spent_in_state_preparation + timer
          timer = -1     
          IF (is_two_setup_experiment = 0) THEN 'only one setup involved. Skip communication step
            mode = 3 'go to spin pumping directly
          ELSE ' two setups involved
            local_success = 1 ' remember for communication step
            local_fail = 0
            mode = 100 'go to communication step
            fail_mode_after_adwin_comm = 0 ' back to cr check. Fail can be timeout. This allows to keep the NV on resonance in case the other setup has jumped
            success_mode_after_adwin_comm = 3 ' go to spin pumping 
          ENDIF
        endif  
        
      CASE 3    ' E spin pumping
        
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
            mode = 4
            wait_time = wait_after_pulse_duration 'wait a certain number of cycles to make sure the lasers are really off
            time_spent_in_state_preparation = time_spent_in_state_preparation + timer
            timer = -1
          ENDIF
        ENDIF
        
      CASE 4    '  wait and count repetitions of the entanglement AWG sequence
        ' the awg gives repeated adwin sync pulses, which are counted. In the case of an entanglement event, we get a plu signal.
        ' In case there's no entanglement event, we get the awg done trigger, a pulse of which we detect the falling edge.
        ' PH REWRITE! In case this is a single-setup (e.g. phase calibration) measurement, we go on, 
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
          DATA_102[repetition_counter+1] = AWG_sequence_repetitions_LDE ' save the result
          time_spent_in_sequence = time_spent_in_sequence + timer
          timer = -1
          mode = mode_after_LDE   
        else ' no plu signal. check for timeout or done
          IF ((digin_this_cycle AND AWG_done_DI_pattern) > 0) THEN  'awg trigger tells us it is done with the entanglement sequence.
            if (awg_done_was_low =1) then
              DATA_102[repetition_counter+1] = AWG_sequence_repetitions_LDE 'save the result
              time_spent_in_sequence = time_spent_in_sequence + timer
              timer = -1
              if ((PLU_during_LDE = 0) or (LDE_is_init = 1)) then ' this is a single-setup measurement. Go on to next mode
                mode = mode_after_LDE
              else ' two setups involved: Done means failure of the sequence PH AT SOME POINT THIS SHOULD COMPENSATE BY CREATING A BEST E STATE
                mode = 7 ' finalize and go to cr check
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
            
        '   0 : Phase check (master only)
        '   1 : Phase msmt (master only, not part of experimental seq.)
        '   2 : CR check
        '   3 : E spin pumping into ms=+/-1
        '   4 : run entanglement sequence and count reps while waiting for PLU success signal
        '   5 : decoupling and counting reps
        '   200 : SSRO
        '   7 : Parameter reinitialization
        
      CASE 5 ' Decoupling '' PH REWRITE!!
        ' AWG will go to dynamical decoupling, and output a sync pulse to the adwin once in a while
        ' Each adwin will count the number pulses and send a jump once the specified time has been reached.
        '        IF (timer =0) THEN 'first go: calculate required repetitions
        '
        '          awg_repcount_was_low = 1
        '          
        '          
        '          ' DATA_100[repetition_counter+1] = required_phase_compensation_repetitions
        '          
        '          
        '        ENDIF 
        '                
        '        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_repcount_DI_pattern)>0) THEN 'awg has switched to high. this construction prevents double counts if the awg signal is long
        '          if (awg_repcount_was_low = 1) then
        '            inc(phase_compensation_repetitions)  
        '            'Par_65 = phase_compensation_repetitions
        '          endif
        '          awg_repcount_was_low = 0
        '        ELSE
        '          awg_repcount_was_low = 1
        '        ENDIF
        '        
        '        IF (phase_compensation_repetitions = required_phase_compensation_repetitions) THEN 'give jump trigger and go to next mode: tomography
        '          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to tomo pulse sequence
        '          CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        '          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
        '          time_spent_in_sequence = time_spent_in_sequence + timer
        '          timer = -1
        '          mode = 200 'SSRO
        '          success_mode_after_SSRO = 6
        '          fail_mode_after_SSRO = 6 
        '          
        '        ENDIF
        
      CASE 6 'store the result of the e measurement and the sync number counter
        DATA_102[repetition_counter+1] = cumulative_awg_counts + AWG_sequence_repetitions_LDE ' store sync number of successful run
       
        mode = 7 'go to reinit and CR check
        INC(repetition_counter) ' count this as a repetition. DO NOT PUT IN 12, because 12 can be used to init everything without previous success!!!!!
        first_CR=1 ' we want to store the CR after result in the next run
        inc(success_event_counter)
        PAR_77 = success_event_counter ' for the LabView live update
        
                              
      CASE 7 ' reinit all variables and go to cr check
        Par_73 = repetition_counter ' write to PAR
        cumulative_awg_counts = cumulative_awg_counts + AWG_sequence_repetitions_LDE 'remember sync counts, independent of success or failure
        'forget all parameters of previous runs
        AWG_repcount_was_low = 1
        AWG_done_was_low = 1  
        AWG_sequence_repetitions_LDE = 0
        
        
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
        mode = init_mode ' go to init mode
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

    
FINISH:
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
  P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0) 

