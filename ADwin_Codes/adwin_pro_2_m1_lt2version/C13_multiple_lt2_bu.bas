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
' Info_Last_Save                 = TUD277459  DASTUD\TUD277459
'<Header End>
' MBI with the adwin, with dynamic CR-preparation, dynamic MBI-success/fail
' recognition, and SSRO at the end.
'
' protocol:
'   Case selector 
'   Cases :
' Nr_C13_init= 2
' Nr_MBE =1
' Nr_parity_msmts =0

' TODO_MAR: Create data structures to store Succes and photon arrival time

' Name of new variables to be introduced and corresponding counters
'
' N_init_C  Long
' N_MBE  Long
' N_parity_msmts Long (loaded from adwins )
' Carbon Init counter (long)
' MBE counter (long)
' parity msmt counter (long)

' ###########################################
'  Start of program end of documentation
' ###########################################


#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins       500 ' not used anymore? Machiel 23-12-'13
#DEFINE max_sequences     100
#DEFINE max_time        10000
#DEFINE max_mbi_steps     100

' ####################
' Declaration of variables
' ####################
'init
DIM DATA_20[100] AS LONG                           ' integer parameters
DIM DATA_21[100] AS FLOAT                          ' float parameters
DIM DATA_33[max_sequences] AS LONG                ' A SP after MBI durations
DIM DATA_34[max_sequences] AS LONG                ' E RO durations
DIM DATA_35[max_sequences] AS FLOAT               ' A SP after MBI voltages
DIM DATA_36[max_sequences] AS FLOAT               ' E RO voltages
DIM DATA_37[max_sequences] AS LONG                ' send AWG start
DIM DATA_38[max_sequences] AS LONG                ' sequence wait times
DIM DATA_39[max_sequences] AS FLOAT               ' E SP after MBI voltages

'return
DIM DATA_24[max_repetitions] AS LONG ' number of MBI attempts needed in the successful cycle
DIM DATA_25[max_repetitions] AS LONG ' number of cycles before success
DIM DATA_27[max_repetitions] AS LONG ' SSRO counts
DIM DATA_28[max_repetitions] AS LONG ' time needed until mbi success (in process cycles)

DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_event_jump_DO_channel, AWG_done_DI_pattern AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM SP_duration, SP_E_duration, SP_filter_duration, MBI_duration AS LONG
DIM sequence_wait_time, wait_after_pulse_duration AS LONG
DIM RO_repetitions, RO_duration AS LONG
DIM cycle_duration AS LONG
DIM sweep_length AS LONG
DIM wait_for_MBI_pulse AS LONG
DIM MBI_threshold AS LONG
DIM nr_of_ROsequences AS LONG
DIM wait_after_RO_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage_after_MBI, E_SP_voltage_after_MBI, E_RO_voltage, A_RO_voltage AS FLOAT
DIM E_MBI_voltage AS FLOAT
dim E_N_randomize_voltage, A_N_randomize_voltage, repump_N_randomize_voltage AS FLOAT

DIM timer, mode, i, tmp AS LONG
DIM wait_time AS LONG
DIM repetition_counter AS LONG
dim seq_cntr as long
DIM MBI_failed AS LONG
DIM counts AS LONG
DIM first AS LONG
DIM stop_MBI AS LONG
DIM MBI_starts AS LONG
DIM ROseq_cntr AS LONG

' MBI stuff
dim next_MBI_stop, next_MBI_laser_stop, AWG_is_done as long
dim current_MBI_attempt as long
dim MBI_attempts_before_CR as long
dim mbi_timer as long
dim trying_mbi as long
dim N_randomize_duration as long

dim awg_in_is_hi, awg_in_was_hi, awg_in_switched_to_hi as long
dim t1, t2 as long

'added for C13 initialization
DIM C13_MBI_threshold, C13_MBI_RO_duration,SP_duration_after_C13 AS LONG
DIM Nr_C13_init, Nr_MBE, Nr_parity_msmts, Parity_threshold AS LONG
DIM Carbon_init_cntr, MBE_cntr, parity_msmt_cntr AS LONG
DIM A_SP_voltage_after_C13_MBI, E_SP_voltage_after_C13_MBI, E_C13_MBI_RO_voltage AS FLOAT
DIM A_SP_voltage_after_MBE, E_SP_voltage_after_MBE, E_MBE_RO_voltage, E_Parity_RO_voltage as Float 
DIM SP_duration_after_MBE, Parity_RO_duration as Long


'Added for multiple C13 script
DIM case_success AS LONG
DIM Current_C_init as LONG
DIM MBE_counter as LONG
DIM Nr_C13_init as LONG 

DIM MBE_threshold AS LONG 
DIM MBE_RO_duration AS LONG 
DIM run_case_selector AS LONG 

INIT:
  ' ####################
  ' Initializing variables from Data
  ' ####################
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  SP_E_duration                = DATA_20[3] 'E spin pumping duration before MBI
  wait_after_pulse_duration    = DATA_20[4]
  RO_repetitions               = DATA_20[5]
  sweep_length                 = DATA_20[6] ' not used? -machiel 23-12-'13
  cycle_duration               = DATA_20[7]
  AWG_event_jump_DO_channel    = DATA_20[8]
  MBI_duration                 = DATA_20[9]
  MBI_attempts_before_CR       = DATA_20[10]
  nr_of_ROsequences            = DATA_20[11]
  wait_after_RO_pulse_duration = DATA_20[12]
  N_randomize_duration         = DATA_20[13]
  
  Nr_C13_init                  = DATA_20[14]
  Nr_MBE                       = DATA_20[15]
  Nr_parity_msmts              = DATA_20[16]

  MBI_threshold                = DATA_20[17]
  C13_MBI_threshold            = DATA_20[18] 
  MBE_threshold                = DATA_20[19] 
  Parity_threshold             = DATA_20[20] 
 
  C13_MBI_RO_duration          = DATA_20[21]
  SP_duration_after_C13        = DATA_20[22]

  MBE_RO_duration              = DATA_20[23]
  SP_duration_after_MBE        = DATA_20[24]

  Parity_RO_duration           = DATA_20[25] 



  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  E_MBI_voltage                = DATA_21[2]
  E_N_randomize_voltage        = DATA_21[3]
  A_N_randomize_voltage        = DATA_21[4]
  repump_N_randomize_voltage   = DATA_21[5]
  E_C13_MBI_RO_voltage         = DATA_21[6]  
  E_SP_voltage_after_C13_MBI   = DATA_21[7]
  A_SP_voltage_after_C13_MBI   = DATA_21[8]

  E_MBE_RO_voltage             = DATA_21[9]
  A_SP_voltage_after_MBE       = DATA_21[10]
  E_SP_voltage_after_MBE       = DATA_21[11]

  E_Parity_RO_voltage          = DATA_21[12]


  ' initialize the data arrays
  FOR i = 1 TO max_repetitions
    DATA_24[i] = 0
    DATA_25[i] = 0
    DATA_28[i] = 0
    DATA_27[i] = 0
  NEXT i

  ' ####################
  ' Initializing variables to set values
  ' ####################

  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 1
  first               = 0
  wait_time           = 0
  stop_MBI            = -2 ' wait_for_MBI_pulse + MBI_duration
  ROseq_cntr          = 1
  seq_cntr            = 1

  case_success = 0

  ' Multiple C counters
  Carbon_init_cntr = 0
  MBE_cntr  =0
  parity_msmt_cntr = 0

  next_MBI_stop = -2
  AWG_is_done = 0
  current_MBI_attempt = 1
  next_MBI_laser_stop = -2

  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel

  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,00001000b) 'configure counter

  P2_Digprog(DIO_MODULE,11) ' in  is now 16:23   'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

  tmp = P2_Digin_Edge(DIO_MODULE,0)
  mode = 0
  timer = 0
  mbi_timer = 0
  trying_mbi = 0
  processdelay = cycle_duration

  awg_in_is_hi = 0
  awg_in_was_hi = 0
  awg_in_switched_to_hi = 0

  'Parameters added for C13 init
  Current_C_init = 1
  MBE_counter = 0
  case_success = 0
  run_case_selector = 0

  ' init parameters
  ' Y after the comment means I (wolfgang) checked whether they're actually used
  ' during the modifications of 2013/01/11
  PAR_73 = 0                      ' repetition counter
  PAR_74 = 0                      ' MBI failed Y
  PAR_77 = 0                      ' current mode (case) Y
  PAR_78 = 0                      ' MBI starts Y
  PAR_80 = 0                      ' ROseq_cntr
  
  PAR_60 = 0 ' DEBUGGING 'print' 
EVENT:
  ' ####################
  ' Event running
  ' ####################
  awg_in_was_hi = awg_in_is_hi
  awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)

  'Detect if the AWG send a trigger
  if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
    awg_in_switched_to_hi = 1
    'TODO_MAR: Only execute this if waiting for AWG trigger change after the rest is working 
  else
    awg_in_switched_to_hi = 0
  endif
  if(trying_mbi > 0) then
    inc(mbi_timer)
  endif

  ' Does this prevent continueing to the next mode?
  ' ##################
  ' Case selector
  ' ##################
  IF (run_case_selector = 1) THEN 'Start case selector 
    SelectCase mode 
      Case 0 'If CR done go to SP-E
        mode = 1  
      Case 1 'If SP-E done go to MBI
        mode = 2 
      Case 2 'IF MBI succesfull spin pump A  
        IF (case_success =1) THEN
          mode = 3
        ELSE 
          IF (current_MBI_attempt = MBI_attempts_before_CR) THEN 'If not succesfull CR check 
            mode = 0
            current_MBI_attempt = 1
            current_cr_threshold = cr_preselect ' TODO_MAR: Check what this line means
          ELSE 'If not succesfull first few times reset N 
            mode = 22 
            INC(current_MBI_attempt)
          ENDIF
        ENDIF
      Case 3' After spin pump A start C13 init 
        mode = 4
      Case 4 ' If start C13 done goto --
        IF (C13_MBI_threshold = 0) THEN ' Spin pump if threshold = 0 
          mode = 6
        ELSE ' RO if threshold != 0 
          mode = 5
        ENDIF
                                   
      Case 5 ' If C13 RO succes go to spin pump else back to CR check 
        IF (case_success = 1) THEN
          mode = 6
        ELSE 
          mode = 0 
        ENDIF                           
      Case 6 ' C13 Init Spin Pump A 
        IF (Current_C_init = Nr_C13_init) THEN 'If all carbon initialized 
          IF (Nr_MBE > 0) THEN ' and MBE type measurement go to MBE 
            mode = 7
          ELSE ' Else go to final RO 
            mode = 12 
          ENDIF   
        ELSE 'If not all Carbons initialised, initialize next one 
          mode = 4 
          INC(Current_C_init)
        ENDIF               
      
      Case 7 ' If MBE started goto MBE RO 
        mode = 8 
        
      Case 8 'MBE RO  
        IF (case_success = 1) Then
          mode = 9 'If MBE RO succesfull go to SP
          inc(MBE_counter) 
        ELSE
          mode = 0  
        ENDIF
      
      Case 9 'Spin pumping  
        
        IF (MBE_counter = Nr_MBE) Then
          mode = 12 'After spin pumping go to Final RO
        ELSE
          mode = 7 'more MBE steps to do 
        ENDIF
                
                   
      Case 12 'start Final RO
        mode = 13
      
      Case 13 ' Final RO
        mode = 0
      
      Case 22' If reset N retry MBI (goto spin pump E) 
        mode = 1 
        
    EndSelect 
    ' After case is selected, reset parameters 
    timer = 0 
    run_case_selector = 0
    case_success = 0 
    PAR_77 = mode
 
  ENDIF
  ' ##################
  ' END of Case selector
  ' ##################
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    SELECTCASE mode
        
      CASE 0 'CR check

        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          run_case_selector = 1
          case_success = 1
          first = 0 
          Current_C_init = 1 ' Reset the Current C index if there was a failure 
          MBE_counter = 0
        ENDIF

      CASE 1    ' Spin pump E before 14N MBI
        ' turn on E laser and start counting

        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter

        ELSE
          ' turn off the lasers, and read the counter
          IF (timer = SP_E_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE,0)                                       ' why enable the counters when just spin pumping ?
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            ' P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser Why is it turned off if it was never turned on?
            wait_time = wait_after_pulse_duration
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 2    ' MBI Nitrogen
        ' MBI starts now; we first need to trigger the AWG to do the selective pi-pulse
        ' then wait until we receive a trigger indicating that this is done
        IF(timer=0) THEN
          INC(MBI_starts)
          PAR_78 = MBI_starts

          if (current_MBI_attempt = 1) then
            if(data_25[seq_cntr] = 0) then
              trying_mbi = 1
            endif
            INC(data_25[seq_cntr]) ' number of cycles to success
          endif

          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)


          ' make sure we don't accidentally think we're done before getting the trigger
          next_MBI_stop = -2
          AWG_is_done = 0


        ELSE

          ' we expect a trigger from the AWG once it has done the MW pulse
          ' as soon as we assume the AWG has done the MW pulse, we turn on the E-laser,
          ' and start counting
          IF(awg_in_switched_to_hi > 0) THEN
            next_MBI_stop = timer + MBI_duration
            AWG_is_done = 1
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
          ELSE
            IF (AWG_is_done = 1) THEN
              counts = P2_CNT_READ(CTR_MODULE, counter_channel)
              IF (counts >= MBI_threshold) THEN
                P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
                P2_CNT_ENABLE(CTR_MODULE,0)

                P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger (event jump)
                CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
                P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)

                DATA_24[seq_cntr] = current_MBI_attempt ' number of attempts needed in the successful cycle

                case_success = 1
                wait_time = next_MBI_stop-timer
                run_case_selector = 1
                current_MBI_attempt = 1
                trying_mbi = 0
                ' we want to save the time MBI takes
                DATA_28[seq_cntr] = mbi_timer
                mbi_timer = 0
                ' MBI succeeds if the counts surpass the threshold;
                ' we then trigger an AWG jump (sequence has to be long enough!) and move on to SP on A
                ' if MBI fails, we
                ' - try again (until max. number of attempts, after some scrambling)
                ' - go back to CR checking if max number of attempts is surpassed
              ELSE
                IF (timer = next_MBI_stop ) THEN
                  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
                  P2_CNT_ENABLE(CTR_MODULE,0)
                  INC(MBI_failed)
                  PAR_74 = MBI_failed
                  case_success = 0
                  run_case_selector = 1
                ENDIF
              ENDIF
            ENDIF
          ENDIF 
        ENDIF

      CASE 3    ' Spin pump A  after 14N MBI
        A_SP_voltage_after_MBI = DATA_35[ROseq_cntr]
        E_SP_voltage_after_MBI = DATA_39[ROseq_cntr]
        SP_duration = DATA_33[ROseq_cntr]

        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_MBI+32768) ' turn on A laser, for spin pumping after MBI
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_MBI+32768) ' turn on E laser, for spin pumping after MBI
        ELSE
          IF (timer = SP_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 4 ' Start C13-init AWG and wait for trigger
        IF (timer=0) THEN 'Start the AWG sequence
          'INC(C13_MBI_starts)
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
        ELSE
        
          ' Wait for the AWG trigger that signals the init sequence is done, then spin pump or readout
          IF(awg_in_switched_to_hi > 0) THEN
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 5 ' C13 init/MBI RO

        IF(timer=0) THEN 'Start the laser

          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_C13_MBI_RO_voltage+32768) ' turn on Ex laser
          ' Needs Carbon Voltage

        ELSE 'Check if we got a count or if we are the end of the RO
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          IF (counts >= C13_MBI_threshold) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
            ' TODO_MAR: Save count and timer

            case_success =1
            wait_time = next_MBI_stop-timer
            run_case_selector = 1

          ELSE
            IF (timer = C13_MBI_RO_duration ) THEN
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0)
              case_success =0
              run_case_selector = 1
            ENDIF
          ENDIF
        ENDIF
        
      CASE 6 ' Spin pump A after C13 init
        IF (timer = 0) THEN 'Turn on lasers
          ' Typically the laser power for one of the two is set to 0 in the msmt params that are loaded
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_C13_MBI+32768) ' turn on A laser
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_C13_MBI+32768) ' turn on E laser
          'this signal is never send for sure
          'Send event to the AWG to signal C13 MBI succes
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
          'SP_duration_after_C13 =3

        ELSE
          ' when we're done, turn off the laser, send the event to the AWG and proceed to wait until RO
          IF (timer >= SP_duration_after_C13) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 7 ' Start C13 MBE and wait for trigger
        IF (timer=0) THEN 'Start the AWG sequence
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
        ELSE
          ' Wait for the AWG trigger that signals the init sequence is done, then spin pump or readout
          IF(awg_in_switched_to_hi > 0) THEN
            case_success =1
            run_case_selector = 1

          ENDIF
        ENDIF


      CASE 8 ' C13 MBE RO
        ' TODO_MAR: store RO results
        IF (timer = 0) THEN 'Start the laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)     'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_MBE_RO_voltage+32768) ' turn on Ex laser

        ELSE 'Check if we got a count or if we are the end of the RO
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) ' Read counter
          ' If enough counts
          IF (counts >= MBE_threshold) THEN 
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
            wait_time = next_MBI_stop-timer
            case_success      = 1
            run_case_selector = 1

          ELSE ' If at the end of RO duration without enough counts
            IF (timer = MBE_RO_duration ) THEN 
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0)
              case_success      = 0
              run_case_selector = 1
            ENDIF
          ENDIF
        ENDIF

      CASE 9 ' Spin pump A after C13 MBE
        ' TODO_MAR: Replace spin pump amplitudes by custom SP amplitudes from msmt params
        '     now identical to SP amplitudes from case 6
        IF (timer = 0) THEN
          ' Typically the laser power for one of the two is set to 0 in the msmt params that are loaded
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_C13_MBI+32768) ' turn on A laser
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_C13_MBI+32768) ' turn on E laser

          'Send event to the AWG to signal C13 MBI succes

          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)

        ELSE
          ' when we're done, turn off the laser, proceed to wait until RO
          IF (timer = SP_duration_after_C13) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration

            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 10 ' start C13 Parity and wait for trigger
        IF (timer=0) THEN 'Start the AWG sequence
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
        ELSE
          ' Wait for the AWG trigger that signals the init sequence is done, then spin pump or readout
          IF(awg_in_switched_to_hi > 0) THEN
            case_success =1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 11 ' C13 Parity RO
        ' TODO_MAR: store RO results
        IF(timer=0) THEN 'Start the laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_C13_MBI_RO_voltage+32768) ' turn on Ex laser
        ELSE 'Check if we got a count or if we are the end of the RO
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) ' Read counter
          ' If enough counts
          IF (counts >= C13_MBI_threshold) THEN 'TODO_MAR: replace C13_MBI threshold with Parity threshold
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
            wait_time = next_MBI_stop-timer
            case_success =1
            run_case_selector = 1

          ELSE ' If at the end of RO duration without enough counts
            IF (timer = C13_MBI_RO_duration ) THEN  'needs to be changed to C_MBI_duration
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0)
              case_success = 0
              run_case_selector = 1
            ENDIF
          ENDIF
        ENDIF
   
      CASE 12    ' wait for AWG trigger before final RO

        ' we wait for the sequence to be finished. the AWG needs to tell us by a pulse,
        ' of which we detect the falling edge.
        ' we then move on to readout
        IF (awg_in_switched_to_hi > 0) THEN
          run_case_selector = 1
          wait_time = 0
        ENDIF
        
      CASE 13    'Final RO
        RO_duration = DATA_34[ROseq_cntr]
        E_RO_Voltage = DATA_36[ROseq_cntr]

        IF (timer = 0) THEN

          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277 * E_RO_voltage + 32768) ' turn on Ex laser

        ELSE
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          IF ((timer = RO_duration) OR (counts > 0)) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser

            IF (counts > 0) THEN
              i = repetition_counter
              INC(DATA_27[i]) 'NOTE_MAR: This is the data that is saved. I should look here for clues on using the rest
            ENDIF

            wait_time = wait_after_RO_pulse_duration
            P2_CNT_ENABLE(CTR_MODULE,0)

            INC(ROseq_cntr)
            par_80 = ROseq_cntr

            INC(repetition_counter)
            Par_73 = repetition_counter

            IF (ROseq_cntr = nr_of_ROsequences+1) THEN ' this means we're done with one full run
              INC(seq_cntr)
              run_case_selector = 1
              first = 1
              ROseq_cntr = 1

              ' we're done once we're at the last repetition and the last RO step
              IF (repetition_counter = RO_repetitions+1) THEN
                DEC(repetition_counter)
                Par_73 = repetition_counter
                END
              ENDIF

              'ELSE ' means we're starting the next ROsequence
            ENDIF
          ENDIF
        ENDIF



      CASE 22 ' Reset N-spin state before re-trying MBI
        if (timer = 0) then
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_N_randomize_voltage+32768)
        else
          if (timer = N_randomize_duration) then
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768)
            P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_off_voltage+32768)
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_off_voltage+32768)

            case_success =0
            run_case_selector = 1
            wait_time = wait_after_pulse_duration
          endif
        endif

    endselect
    INC(timer)
  ENDIF
  



FINISH:
  finish_CR()

