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
<<<<<<< HEAD
' Info_Last_Save                 = TUD277246  DASTUD\TUD277246
' Bookmarks                      = 3,16,64,144,286,480,516,518,564,566,624,626,649,670
=======
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
' Bookmarks                      = 3,16,62,142,283,487,523,525,569,571,629,631,654,675
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
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
'   3 : Carbon init successful?
'   4 : run entanglement sequence and count reps while waiting for PLU success signal
'   5 : wait for the electron Carbon swap to be done and then read out the electron if this is specified in the msmt parameters
'   6 : save SSRO after SWAP result, run entanglement sequence and count reps while waiting for PLU success signal
'   7 : Phase synchronisation
'   8 : Purification gate
'   9 : Tomo gte
'  10 : Save result


#INCLUDE ADwinPro_All.inc
<<<<<<< HEAD
#INCLUDE ADwinGoldII.inc
=======
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
#INCLUDE .\configuration.inc
#INCLUDE .\cr_mod.inc
#INCLUDE math.inc

' #DEFINE max_repetitions 100000  this is defined as 500000 in cr check
#DEFINE max_sequences      100
#DEFINE max_time         10000
#DEFINE max_mbi_steps      100
#DEFINE max_SP_bins       2000
#DEFINE max_CR_counts      200     

'init
<<<<<<< HEAD
DIM DATA_20[100] AS LONG                           ' integer parameters from python
DIM DATA_21[100] AS FLOAT                          ' float parameters from python
=======
DIM DATA_20[100] AS LONG   ' integer parameters from python
DIM DATA_21[100] AS FLOAT  ' float parameters from python
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200

'return data
'data 22 is the cr result before the sequence
'data 23 is the first cr result after the sequence
DIM DATA_24[max_repetitions] AS LONG ' number of MBI attempts needed in the successful cycle
DIM DATA_25[max_repetitions] AS LONG ' number of cycles before success
'26 is used in cr for 'statistics'
DIM DATA_27[max_repetitions] AS LONG ' SSRO result after mbi / swap step
DIM DATA_28[max_repetitions] AS LONG ' time needed until mbi success (in process cycles)
DIM DATA_29[max_SP_bins] AS LONG     ' SP counts
'30 ' CR integer parameters
'31 CR float parameters
<<<<<<< HEAD

=======
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
DIM DATA_33[max_repetitions] AS LONG  'time spent for communication between adwins
DIM DATA_34[max_repetitions] AS LONG ' Information whether same or opposite detector has clicked (provided by the PLU)
DIM DATA_35[max_repetitions] AS LONG ' number of repetitions until the first succesful entanglement attempt
DIM DATA_36[max_repetitions] AS LONG ' number of repetitions after swapping until the second succesful entanglement attempt
DIM DATA_37[max_repetitions] AS LONG ' SSRO_after_electron_carbon_SWAP_result
<<<<<<< HEAD
DIM DATA_38[max_repetitions] AS LONG ' SSRO counts final spin readout
=======
DIM DATA_38[max_repetitions] AS LONG ' SSRO counts after purifying gate
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
DIM DATA_39[max_repetitions] AS LONG ' SSRO counts final spin readout

DIM i as long ' for FOR loops
DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_repcount_DI_channel, AWG_event_jump_DO_channel, AWG_done_DI_pattern, AWG_repcount_DI_pattern AS LONG
DIM AWG_repcount_is_hi, AWG_repcount_was_hi, AWG_repcount_switched_to_hi as long
DIM AWG_sequence_repetitions_first_attempt, AWG_sequence_repetitions_second_attempt as long
'Phase compensation
DIM phase_to_compensate, total_phase_offset_after_sequence, phase_per_sequence_repetition, phase_per_compensation_repetition AS FLOAT
DIM phase_compensation_repetitions, required_phase_compensation_repetitions as long

DIM SP_duration AS LONG
DIM wait_after_pulse_duration AS LONG
DIM cycle_duration AS LONG 'repetition rate of the event structure. Typically 1us
DIM Dynamical_stop_ssro_threshold, Dynamical_stop_ssro_duration, Success_of_SSRO_is_ms0 AS LONG
DIM CR_result AS LONG
DIM SSRO_result AS LONG
DIM C_init_SWAP_wo_SSRO AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM E_MBI_voltage AS FLOAT

DIM timer, wait_time, mode AS LONG

DIM MBI_failed AS LONG
DIM old_counts, counts AS LONG
DIM first_CR AS LONG
DIM MBI_starts AS LONG
DIM repetition_counter AS LONG 'counts how many repetitions of the experiment have been done

' MBI stuff
dim current_MBI_attempt as long
dim MBI_attempts_before_CR as long
dim mbi_timer as long
dim trying_mbi as long
dim AWG_done_is_hi, AWG_done_was_hi, AWG_done_switched_to_hi as long

'Added for communication with other Adwin and PLU
DIM remote_adwin_di_success_channel, remote_adwin_di_success_pattern, remote_adwin_di_fail_channel, remote_adwin_di_fail_pattern as long
<<<<<<< HEAD
DIM remote_adwin_do_success_channel, remote_adwin_do_fail_channel  as long
=======
DIM remote_adwin_do_success_channel, remote_adwin_do_fail_channel, remote_awg_trigger_channel  as long
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
DIM local_success, remote_success, local_fail, remote_fail, combined_success as long
DIM success_mode_after_adwin_comm, fail_mode_after_adwin_comm as long
DIM success_mode_after_SSRO, fail_mode_after_SSRO as long
DIM adwin_comm_safety_cycles as long 'msmt param that tells how long the adwins should wait to guarantee bidirectional communication is successful
DIM adwin_comm_timeout_cycles as long ' if one side fails completely, the other can go on
DIM adwin_comm_done, adwin_timeout_requested as long
<<<<<<< HEAD
DIM n_of_comm_timeouts, is_single_setup_experiment as long
DIM is_master, is_barrett_kok as long
=======
DIM n_of_comm_timeouts, is_two_setup_experiment as long
DIM is_master, is_barrett_kok, has_phase_compensation as long
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200

DIM PLU_event_di_channel, PLU_event_di_pattern, PLU_which_di_channel, PLU_which_di_pattern AS LONG
DIM PLU_event_di_was_high, PLU_event_di_is_high AS LONG
DIM detector_of_last_entanglement, same_detector as LONG

DIM do_SSRO_after_electron_carbon_SWAP, SSRO_after_electron_carbon_SWAP_result as long
DIM communicate_SSRO_after_electron_carbon_SWAP as long

DIM invalid_data_marker_do_channel AS LONG
DIM succes_event_counter AS LONG



LOWINIT:    'change to LOWinit which I heard prevents adwin memory crashes
  'read int params from python script
  
  init_CR()
  
  cycle_duration               = DATA_20[1]
  SP_duration                  = DATA_20[2]
  wait_after_pulse_duration    = DATA_20[3] 'Time to wait after turning off a laser pulse to ensure it is really off

<<<<<<< HEAD
  MBI_attempts_before_CR       = DATA_20[5] 
  C_init_SWAP_wo_SSRO          = DATA_20[7]
  Dynamical_stop_ssro_threshold= DATA_20[6]
  Dynamical_stop_ssro_duration = DATA_20[4]
  
  is_single_setup_experiment   = Data_20[8]
  is_master                    = DATA_20[9]
  is_barrett_kok               = DATA_20[9]
  
  PLU_event_di_channel         = DATA_20[10]
  PLU_which_di_channel         = DATA_20[11]
  
  AWG_start_DO_channel         = DATA_20[12]
  AWG_done_DI_channel          = DATA_20[13]
  AWG_event_jump_DO_channel    = DATA_20[14]
  AWG_repcount_DI_channel      = DATA_20[15]
=======
  MBI_attempts_before_CR       = DATA_20[4] 
  C_init_SWAP_wo_SSRO          = DATA_20[5]
  Dynamical_stop_ssro_threshold= DATA_20[6]
  Dynamical_stop_ssro_duration = DATA_20[7]
  
  is_two_setup_experiment   = Data_20[8]
  is_master                    = DATA_20[9]
  is_barrett_kok               = DATA_20[10]
  
  PLU_event_di_channel         = DATA_20[11]
  PLU_which_di_channel         = DATA_20[12]
  
  AWG_start_DO_channel         = DATA_20[13]
  AWG_done_DI_channel          = DATA_20[14]
  AWG_event_jump_DO_channel    = DATA_20[15]
  AWG_repcount_DI_channel      = DATA_20[16]
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
  
  remote_adwin_di_success_channel  = DATA_20[17]
  remote_adwin_di_fail_channel     = DATA_20[18]
  remote_adwin_do_success_channel  = DATA_20[19]
  remote_adwin_do_fail_channel     = DATA_20[20]
  adwin_comm_safety_cycles         = DATA_20[21]
  adwin_comm_timeout_cycles        = DATA_20[22]
  
  do_SSRO_after_electron_carbon_SWAP = DATA_20[23]          ' if no, one will continue with the sequence, if yes, the success of the swap will be stored
  communicate_SSRO_after_electron_carbon_SWAP = DATA_20[24] ' if no, one will continue with the sequence, if yes, the sequence will continue only if both setups were succesful
<<<<<<< HEAD

  invalid_data_marker_do_channel   = DATA_20[24] 'marks timeharp data invalid
=======
  remote_awg_trigger_channel = DATA_20[25]
  invalid_data_marker_do_channel   = DATA_20[26] 'marks timeharp data invalid
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
  
  ' read float params from python
  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  E_MBI_voltage                = DATA_21[2]  
  A_SP_voltage                 = DATA_21[3]
  E_RO_voltage                 = DATA_21[4]
  A_RO_voltage                 = DATA_21[5]
  phase_per_sequence_repetition = DATA_21[6] ' how much phase do we acquire per repetition
  phase_per_compensation_repetition =DATA_21[7] '
  total_phase_offset_after_sequence = DATA_21[8] 'how much phase have we acquired during the pulses
  
  ' initialize the data arrays
  FOR i = 1 TO max_repetitions
    DATA_24[i] = 0
    DATA_25[i] = 0
    DATA_27[i] = 0
    DATA_28[i] = 0
<<<<<<< HEAD
    DATA_29[i] = 0
=======
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
    DATA_33[i] = 0
    DATA_34[i] = 0
    DATA_35[i] = 0
    DATA_36[i] = 0
    DATA_37[i] = 0
    DATA_38[i] = 0
    DATA_39[i] = 0
  NEXT i
  
  FOR i = 1 TO max_SP_bins
    DATA_29[i] = 0
  NEXT i

  n_of_comm_timeouts = 0 ' used for debugging, goes to a par   
  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 1
  first_CR            = 1
  wait_time           = 0
  current_MBI_attempt = 1
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  AWG_repcount_DI_pattern = 2 ^ AWG_repcount_DI_channel
  PLU_event_di_pattern = 2 ^ PLU_event_di_channel
  PLU_which_di_pattern = 2 ^ PLU_which_di_channel
  remote_adwin_di_success_pattern = 2^ remote_adwin_di_success_channel
  remote_adwin_di_fail_pattern = 2^ remote_adwin_di_fail_channel
  
  AWG_repcount_is_hi =0
  AWG_repcount_was_hi =0
  AWG_repcount_switched_to_hi=0
  AWG_sequence_repetitions_first_attempt =0
  AWG_sequence_repetitions_second_attempt =0
  phase_compensation_repetitions =0
  required_phase_compensation_repetitions =0
  PLU_event_di_was_high=0
  PLU_event_di_is_high=0
  detector_of_last_entanglement = 0
  same_detector =0 
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
      
  succes_event_counter = 0
  Success_of_SSRO_is_ms0 = 1 'usually, we condition on getting a click
  SSRO_result = 0
      
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter

  P2_Digprog(DIO_MODULE,11) ' in  is now 16:23   'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel, 0)
  P2_DIGOUT(DIO_MODULE,11,0) ' set repumper modulation high.
  
  mode = 0
  timer = 0
  mbi_timer = 0
  trying_mbi = 0
  processdelay = cycle_duration   ' the event structure is repeated at this period. On T11 processor 300 corresponds to 1us. Can do at most 300 operations in one round.
  
  AWG_done_is_hi = 0      
  AWG_done_was_hi = 0
  AWG_done_switched_to_hi = 0
  
  ' init parameters
  Par_61 = mode                   ' current mode
  PAR_63 = 0                      ' stop flag
  PAR_73 = repetition_counter     ' repetition counter
  PAR_74 = 0                      ' MBI failed
  PAR_77 = succes_event_counter   ' number of entanglement events
  PAR_78 = 0                      ' MBI starts Y
  PAR_76 = 0                      ' n_of_communication_timeouts for debugging
  


  
EVENT:
  
  'write information to pars for live monitoring
  PAR_61 = mode        
  PAR_76 = n_of_comm_timeouts ' for debugging
  
    
  if(trying_mbi > 0) then ' Increase number of mbi trials by one
    inc(mbi_timer)
  endif
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
      
      CASE 100 ' communication between adwins
        ' communication logic: there is a fail and a success trigger. Both 0 means no signal has been sent, both high on slave side means signal has been received from master
        ' The master decides if both setups are successful, sends this to the slave, and waits for the slave to go on 11 to confirm communication, and sends a jump to both awg if not succesful
        IF (adwin_comm_done = 0) THEN 'previous communication was not successful
          DATA_33[repetition_counter] = DATA_33[repetition_counter] + timer
          combined_success = 0
          remote_success = (P2_DIGIN_LONG(DIO_MODULE) AND remote_adwin_di_success_channel) 'read remote channels
          remote_fail = (P2_DIGIN_LONG(DIO_MODULE) AND remote_adwin_di_fail_channel)
        
          IF (is_master>0) THEN 
            if ((remote_success > 0) and (remote_fail > 0)) then ' own signal successfully communicated to other side -> go on to next mode
              adwin_comm_done = 1
            else ' own signal not yet received on other side -> send it or wait for slave's signal to decide what to do
              IF ((remote_success > 0) or (remote_fail > 0)) then ' remote signal received: decide whether both setups were successful
                if ((local_success > 0) and (remote_success > 0)) then
                  combined_success = 1
                else
                  combined_success = 0
                endif
                'send combined success, wait for a round trip to make sure that our signal has arrived
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, combined_success)
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 1-combined_success)
                wait_time = 2 * adwin_comm_safety_cycles ' wait in event loop for adwin communication safety time
              ELSE ' no signal received. Did the connection time out?
                if (timer > adwin_comm_timeout_cycles) then
                  inc(n_of_comm_timeouts) ' give to par for local debugging
                  combined_success = 0 ' just to be sure
                  adwin_comm_done = 1 ' below: reset everything and go on
                endif                
              ENDIF 
            endif
            
          ELSE ' I'm the slave. 
            if (timer = 0) then 'first round: send my signal
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, local_success)
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 1-local_success) 
            else 'Did the master tell me what to do?
              if ((remote_success > 0) or (remote_fail > 0)) then 'signal received
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, 1) 'send confirmation: both channels high
                P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 1) 'send confirmation
                wait_time = adwin_comm_safety_cycles ' wait in event loop for adwin communication safety time
                combined_success = remote_success
                adwin_comm_done = 1 ' below: reset everything and go on
              else ' still no signal. Did the connection time out?
                IF (adwin_timeout_requested > 0) THEN ' previous run: timeout requested.
                  adwin_comm_done = 1 ' communication done (timeout). Still: reset parameters below
                  combined_success = 0
                  inc(n_of_comm_timeouts) ' give to par for local debugging
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

        IF (adwin_comm_done > 0) THEN 'communication run was successful. Decide what to do next and clear memory
          if (combined_success > 0) then ' both successful: continue
            mode = success_mode_after_adwin_comm
          else 'fail: go to fail mode
            mode = fail_mode_after_adwin_comm
          endif
          adwin_timeout_requested = 0
          adwin_comm_done = 0 'forget for next round of the experiment
          timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel, 0) ' set the channels low
          P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel, 0)
        ENDIF
       
        
        
      CASE 200  ' dynamical stop RO.     
                     
        IF (timer = 0) THEN 
          P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
        ELSE
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) 'read counter
          IF (counts >= Dynamical_stop_ssro_threshold) THEN ' photon detected
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE, 0)  ' disable counter
            wait_time = dynamical_stop_SSRO_duration - timer ' make sure the SSRO element always has the same length (even in success case) to keep track of the carbon phase xxx to do: is this still accurate to the us?
            timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
            SSRO_result = 1
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
            if (timer = dynamical_stop_SSRO_duration) then ' no count after ssro duration -> failed  xxx to do: is this still accurate to the us?
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0) 'disable counter
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
        
        IF ((Par_63 > 0) or (repetition_counter > max_repetitions)) THEN ' stop signal received: stop the process
          END
        ENDIF

        'forget all parameters of previous runs
        AWG_sequence_repetitions_first_attempt =0
        AWG_sequence_repetitions_second_attempt =0
        current_MBI_attempt = 1
        trying_mbi = 0
        mbi_timer = 0 
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
        P2_DIGOUT(DIO_MODULE,remote_adwin_do_fail_channel,0) 
        
        if ( CR_check(first_CR,succes_event_counter+1) > 0 ) then ' do CR check. if First_CR is high, the result will be saved. 
          ' In case the result is zero, the CR check will be repeated
          timer = -1          
<<<<<<< HEAD
          IF (is_single_setup_experiment = 1) THEN 'only one setup involved. Skip communication step
=======
          IF (is_two_setup_experiment = 0) THEN 'only one setup involved. Skip communication step
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
            mode = 1 'go to spin pumping directly
          ELSE ' two setups involved
            local_success = 1 ' remember for communication step
            local_fail = 0
            mode = 100 'go to communication step
            fail_mode_after_adwin_comm = 0 ' back to cr check. Fail can be timeout. This allows to keep the NV on resonance in case the other setup has jumped
            success_mode_after_adwin_comm = 1 ' go to spin pumping 
          ENDIF
        endif  
        first_CR = 0        
        
        
      CASE 1    ' E spin pumping
        
        IF (timer = 0) THEN
          P2_DIGOUT(DIO_MODULE,11,1) ' set repumper modulation high.
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768) ' or turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)                        ' clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)                       ' turn on counter
          old_counts = 0
        ELSE
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          DATA_29[timer] = DATA_29[timer] + counts - old_counts    ' for spinpumping arrival time histogram
          old_counts = counts
                    
          IF (timer = SP_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE,0) ' diable counter
            P2_DIGOUT(DIO_MODULE,11,0)  ' set repumper modulation low.
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser      
            mode = 2   'go to mbi
            wait_time = wait_after_pulse_duration 'wait a certain number of cycles to make sure the lasers are really off
            timer = -1
          ENDIF
        ENDIF
        
          
          
      CASE 2    ' Carbon init, either MBI or SWAP (with SSRO afterwards or not)
        ' We first need to send a trigger command to the AWGs on both sides that tells them to start the gate sequence
<<<<<<< HEAD
        ' in local mode, this is done by each ADWIN, in remote mode the Master AWG (later) triggers the slave AWG
=======
        ' in local mode, this is done by each ADWIN, in remote mode the Master Adwin also triggers the slave AWG
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
        
        IF (timer=0) THEN   ' MBI sequence starts
          INC(MBI_starts)
          PAR_78 = MBI_starts          
          if(data_25[repetition_counter] = 0) then  ' first mbi run (data25: number of mbi cycles before success in respective run)
            trying_mbi = 1
          endif
          INC(data_25[repetition_counter])
          ' Logic: If local or master, own awg is triggered. If nonlocal and slave, AWG is triggered by master's awg to minimize jitter
<<<<<<< HEAD
          if ((is_single_setup_experiment > 0) or (is_master>0)) then   
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0) 
          endif 
         
=======
          if (is_two_setup_experiment = 0) then   
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
          else 
            IF (is_master>0) THEN ' trigger own and remote AWG
              'P2_Digout_Bits(DIO_MODULE, (2^AWG_start_DO_channel AND 2^remote_awg_trigger_channel),0) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,1)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,1)
              CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              'P2_Digout_Bits(DIO_MODULE, 0, (2^AWG_start_DO_channel AND 2^remote_awg_trigger_channel)) ' xxx: Try if this works. Would eliminate delay between triggering
              P2_DIGOUT(DIO_MODULE, remote_awg_trigger_channel,0)
              P2_DIGOUT(DIO_MODULE, AWG_start_DO_channel,0)
            ENDIF
          endif 
          
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
        ELSE ' AWG in MBI sequence is running
          ' Detect if the AWG is done and has sent a trigger; this construction prevents multiple adwin jumps when the awg sends a looooong pulse
          AWG_done_was_hi = AWG_done_is_hi
          AWG_done_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)  
          if ((AWG_done_was_hi = 0) and (AWG_done_is_hi > 0)) then ' AWG has done the MW pulses -> go to next step
            timer = -1
            IF (C_init_SWAP_wo_SSRO > 0) THEN 'no SSRO and no communication required
              mode = 4 'go straight to the entanglement sequence
            ELSE
              success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
              mode = 200 ' go to dynamical stop RO
              success_mode_after_SSRO = 3 ' Check MBI success
              fail_mode_after_SSRO = 3 ' Check MBI success
            ENDIF        
          endif 
        ENDIF
        
          
      CASE 3 ' MBI SSRO done; check MBI success
        IF (local_success>0) THEN ' successful MBI readout
          trying_mbi = 0
          mbi_timer = 0
          DATA_24[repetition_counter] = DATA_24[repetition_counter] + current_MBI_attempt ' number of attempts needed in the successful cycle for histogram
          DATA_28[repetition_counter] = DATA_28[repetition_counter] + mbi_timer ' save the time MBI has taken
          DATA_27[repetition_counter] = SSRO_result
          current_MBI_attempt = 1 ' reset counter
<<<<<<< HEAD
          if (is_single_setup_experiment = 1) then 'only one setup involved. Skip communication step
=======
          if (is_two_setup_experiment = 0) then 'only one setup involved. Skip communication step
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
            mode = 4 ' entanglement sequence
          else
            mode = 100 ' adwin communication
            fail_mode_after_adwin_comm = 0 ' CR check 
            success_mode_after_adwin_comm = 4 ' entanglement sequence
          endif 
        ELSE ' MBI failed. Retry or communicate?
          INC(MBI_failed)
          PAR_74 = MBI_failed 'for debugging
           
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to beginning of MBI and wait for trigger
          CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          
          IF (current_MBI_attempt = MBI_attempts_before_CR) then ' failed too often -> communicate failure (if in remote mode) and then go to CR
            current_MBI_attempt = 1 'reset counter
<<<<<<< HEAD
            if (is_single_setup_experiment = 0) then 'two setups involved
=======
            if (is_two_setup_experiment > 0) then 'two setups involved
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
              fail_mode_after_adwin_comm = 0 ' CR check. Don't have to specify fail_mode because I didn't succeed
              mode = 100
            else
              mode = 0 ' directly back to CR
            endif
          ELSE 
            mode = 1 ' retry spinpumping and then MBI
            INC(current_MBI_attempt)
          ENDIF 
        ENDIF               
        timer = -1      
        
      
        
      CASE 4    '  wait and count repetitions of the entanglement AWG sequence
   
        ' the awg gives repeated adwin sync pulses, which are counted. In the case of an entanglement event, we get a plu signal.
        ' In case there's no entanglement event, we get the awg done trigger, a pulse of which we detect the falling edge.
        ' In case this is a single-setup (e.g. phase calibration) measurement, we go on, 
        ' otherwise getting a done trigger means failure of the sequence and we go to CR cheking
        ' NOTE, if the AWG sequence is to short (close to a us, then it is possible that the time the signal is low is missed.
        
        INC(repetition_counter) 'whenever we start the entanglement sequence, we count this as a repetition. AWG will stop and send a done trigger once the max amount of reps is reached
        
        AWG_repcount_was_hi = AWG_repcount_is_hi
        AWG_repcount_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_repcount_DI_pattern)
        IF ((AWG_repcount_was_hi = 0) and (AWG_repcount_is_hi > 0)) THEN 'awg has switched to high. this construction prevents double counts if the awg signal is long
          inc(AWG_sequence_repetitions_first_attempt) ' increase the number of attempts counter
        ENDIF
<<<<<<< HEAD
        
        'check the done trigger
        'IF (Digin_Edge(1) AND AWG_done_DI_pattern) THEN ' XXX try this construction. might enable shorter sequences
=======
        'check the done trigger
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
        AWG_done_was_hi = AWG_done_is_hi ' check the status of the done channel
        AWG_done_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
        IF ((AWG_done_was_hi = 0) and (AWG_done_is_hi > 0)) THEN  'awg trigger tells us it is done with the entanglement sequence.
          DATA_35[repetition_counter] = AWG_sequence_repetitions_first_attempt 'save the result
          timer = -1
<<<<<<< HEAD
          if (is_single_setup_experiment > 0 ) then ' this is a single-setup phase calibration measurement. Go on to next mode:
=======
          if (is_two_setup_experiment = 0 ) then ' this is a single-setup phase calibration measurement. Go on to next mode:
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
            mode = 7 'is single setup experiment: correct for acquired phase, do purification gate and carbon readout.
          else ' two setups involved: Done means failure of the sequence
            mode = 0 'go to cr check
            P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to beginning of MBI and wait for trigger
            CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          endif
        ENDIF
        
        'check the PLU
        PLU_event_di_was_high = PLU_event_di_is_high
        PLU_event_di_is_high = (P2_DIGIN_LONG(DIO_MODULE) AND PLU_event_di_pattern)
        detector_of_last_entanglement = (P2_DIGIN_LONG(DIO_MODULE) AND PLU_which_di_pattern)
        IF ((PLU_event_di_was_high = 0) and (PLU_event_di_is_high > 0)) THEN ' PLU signal received
          DATA_35[repetition_counter] = AWG_sequence_repetitions_first_attempt ' save the result
          timer = -1
          if (is_barrett_kok > 0) then
            mode = 200 ' jump to SSRO
            success_mode_after_ssro = 10 'mode 10: store the ssro result and go to cr check
            fail_mode_after_ssro = 10
          else
            mode = 5 'go on to SWAP operation
          endif
          
        ENDIF

              
      CASE 5  'wait for the electron Carbon swap to be done and then read out the electron if this is specified in the msmt parameters
        AWG_done_was_hi = AWG_done_is_hi ' check the status of the done channel
        AWG_done_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
        IF ((AWG_done_was_hi = 0) and (AWG_done_is_hi > 0)) THEN  'awg trigger tells us it is done with the swap sequence.
          timer = -1
          if ( do_SSRO_after_electron_carbon_SWAP =0  0 ) then
            mode = 6
          else
            mode = 200   ' dsSSRO
            Success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it before
            IF (communicate_SSRO_after_electron_carbon_SWAP >0) THEN
              success_mode_after_SSRO = 100 'adwin comm
              fail_mode_after_SSRO = 100
            ENDIF
            success_mode_after_SSRO = 6
            fail_mode_after_SSRO = 6 ' we have to go on here, independent of the local result, to keep the setups in sync
          endif
        ENDIF
        
      CASE 6    ' save ssro after swap result. Then wait and count repetitions of the entanglement AWG sequence as in case 4 
        
        DATA_37[repetition_counter] = SSRO_result
        
        AWG_repcount_was_hi = AWG_repcount_is_hi
        AWG_repcount_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_repcount_DI_pattern)
        IF ((AWG_repcount_was_hi = 0) and (AWG_repcount_is_hi > 0)) THEN 'awg has switched to high. this construction prevents double counts if the awg signal is long
          inc(AWG_sequence_repetitions_second_attempt) ' increase the number of attempts counter
        ENDIF
        
        'check the done trigger
        AWG_done_was_hi = AWG_done_is_hi ' check the status of the done channel
        AWG_done_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
        IF ((AWG_done_was_hi = 0) and (AWG_done_is_hi > 0)) THEN  'awg trigger tells us it is done with the entanglement sequence. This means failure of the protocol
          DATA_36[repetition_counter] = AWG_sequence_repetitions_second_attempt 'save the result
          timer = -1
          mode = 0 'go to cr check  XXX we could also do tomography (mode =7) here to measure the (decohered) carbon state after swapping the first round
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to beginning of MBI and wait for trigger
          CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
        ENDIF
        
        'check the PLU
        PLU_event_di_was_high = PLU_event_di_is_high
        PLU_event_di_is_high = (P2_DIGIN_LONG(DIO_MODULE) AND PLU_event_di_pattern) 
        IF ((PLU_event_di_was_high = 0) and (PLU_event_di_is_high > 0)) THEN 'PLU signal received
          DATA_35[repetition_counter] = AWG_sequence_repetitions_second_attempt 'save the result
          'check whether clicks happened on the same detector
          same_detector = detector_of_last_entanglement ' remember result of first round
          detector_of_last_entanglement = (P2_DIGIN_LONG(DIO_MODULE) AND PLU_which_di_pattern) 'second round result
          IF (same_detector = detector_of_last_entanglement) THEN ' identical in both rounds
            same_detector = 1
          ELSE 'not identical
            same_detector = 0
          ENDIF
          DATA_34[repetition_counter] = same_detector 'save to data file
          mode = 7 'go on to next case
          timer = -1
        ENDIF
        
      CASE 7 ' Phase synchronisation
        ' AWG will go to dynamical decoupling, and output a sync pulse to the adwin once in a while
        ' Each adwin will count the number pulses and send a jump once a given phase has been reached.
        
        IF (timer =0) THEN 'first go: calculate required repetitions
          phase_to_compensate = total_phase_offset_after_sequence + (AWG_sequence_repetitions_first_attempt + AWG_sequence_repetitions_second_attempt) * phase_per_sequence_repetition
          if (same_detector = 0) then
            phase_to_compensate = phase_to_compensate + 3.1415
          endif
          if (phase_to_compensate > 6.283) then           ' The built in Mod function works only for integers and takes 0.44 us.
            Do                              
              phase_to_compensate = phase_to_compensate - 6.283
            Until (phase_to_compensate  <= 6.283)
          endif
          required_phase_compensation_repetitions = Round(phase_to_compensate / phase_per_compensation_repetition)
        ENDIF
        
        AWG_repcount_was_hi = AWG_repcount_is_hi
        AWG_repcount_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_repcount_DI_pattern)
        IF ((AWG_repcount_was_hi = 0) and (AWG_repcount_is_hi > 0)) THEN 'awg has switched to high. this construction prevents double counts if the awg signal is long
          inc(phase_compensation_repetitions )
        ENDIF

        IF (phase_compensation_repetitions >= required_phase_compensation_repetitions) THEN 'give jump trigger and go to next mode: tomography
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,1) ' tell the AWG to jump to tomo pulse sequence
          CPU_SLEEP(9) ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE, AWG_event_jump_DO_channel,0) 
          timer = -1
          mode = 8
        ENDIF
        
      CASE 8 ' Wait until purification gate is done. 
        'check the done trigger
        AWG_done_was_hi = AWG_done_is_hi ' check the status of the done channel
        AWG_done_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
        IF ((AWG_done_was_hi = 0) and (AWG_done_is_hi > 0)) THEN  'awg trigger tells us it is done with the entanglement sequence.
          timer = -1
          success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
          mode = 200 'go to SSRO
          success_mode_after_SSRO = 9
          fail_mode_after_SSRO = 9   
        ENDIF
        
      CASE 9 'store the result of the purification step. wait for TOMO gate to be done and do SSRO again
        DATA_38[repetition_counter] = SSRO_result
        AWG_done_was_hi = AWG_done_is_hi ' check the status of the done channel
        AWG_done_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
        IF ((AWG_done_was_hi = 0) and (AWG_done_is_hi > 0)) THEN  'awg trigger tells us it is done with the entanglement sequence.
          timer = -1
          success_of_SSRO_is_ms0 = 1 'in case one wants to change this here or has changed it elsewhere
          mode = 200 'go to SSRO
          success_mode_after_SSRO = 10
          fail_mode_after_SSRO = 10
        ENDIF
        
      CASE 10 'store the result of the tomography
        timer = -1
<<<<<<< HEAD
        DATA_38[repetition_counter] = SSRO_result
=======
        DATA_39[repetition_counter] = SSRO_result
>>>>>>> 52d59ddb0186d8e5e6873e3af90d5fe1adc7c200
        mode =0 'go to CR check
        Par_73 = repetition_counter
        
    endselect
    
    INC(timer)
    
  endif

    
FINISH:
  finish_CR()

