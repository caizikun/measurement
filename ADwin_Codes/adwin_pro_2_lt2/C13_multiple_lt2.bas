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
' recognition, dynamic initialization and MBEand SSRO at the end.
'
' protocol:
'   Case selector 
'   Cases :

' TODO_MAR: Create data structures to store Succes and photon arrival time

' Name of new variables to be introduced and corresponding counters
'
' N_init_C  Long
' N_MBE     Long
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

#DEFINE max_nr_of_Carbon_init_steps 20 
#DEFINE max_nr_of_Carbon_MBE_steps 20

' ####################
' Declaration of variables
' ####################
'init
DIM DATA_20[100] AS LONG                          ' long parameters
DIM DATA_21[100] AS FLOAT                         ' float parameters

DIM DATA_33[max_sequences] AS LONG                ' A SP after MBI durations
DIM DATA_34[max_sequences] AS LONG                ' E RO durations
DIM DATA_35[max_sequences] AS FLOAT               ' A SP after MBI voltages
DIM DATA_36[max_sequences] AS FLOAT               ' E RO voltages
DIM DATA_38[max_sequences] AS LONG                ' sequence wait times
DIM DATA_39[max_sequences] AS FLOAT               ' E SP after MBI voltages
DIM DATA_37[max_sequences] AS LONG                ' Not used?
DIM DATA_40[max_sequences] AS LONG                ' C13 MBI threshold list


DIM DATA_27[max_repetitions] AS LONG ' Final SSRO result 

DIM DATA_24[max_repetitions] AS LONG ' number of MBI attempts needed in the successful cycle 
DIM DATA_25[1] AS LONG ' Data array to store the number of N initialization START events 
DIM DATA_28[1] AS LONG ' Data array to store the number of N initialization SUCCES events 

'C13 measurement data
DIM DATA_29[max_nr_of_Carbon_init_steps] AS LONG 'Data array to store the number of carbon initialization START events 
DIM DATA_32[max_nr_of_Carbon_init_steps] AS LONG 'Data array to store the number of carbon initialization SUCCES events 

'C13 MBE data
DIM DATA_41[max_nr_of_Carbon_MBE_steps] AS LONG 'Data array to store the number of carbon MBE START events 
DIM DATA_42[max_nr_of_Carbon_MBE_steps] AS LONG 'Data array to store the number of carbon MBE SUCCES events 

'C13 Parity data
DIM DATA_43[max_repetitions] AS LONG 'Parity measurement outcomes (NOTE: multiple parity measurements are stored in a single array of length Nr_parity * repetitions

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
dim N_randomize_duration as long

dim awg_in_is_hi, awg_in_was_hi, awg_in_switched_to_hi as long
dim t1, t2 as long

'added for C13 initialization
DIM C13_MBI_threshold, C13_MBI_RO_state, C13_MBI_RO_duration,SP_duration_after_C13 AS LONG
DIM Nr_C13_init, Nr_MBE, Nr_parity_msmts, Parity_threshold AS LONG
DIM Carbon_init_cntr, MBE_cntr, parity_msmt_cntr AS LONG
DIM A_SP_voltage_after_C13_MBI, E_SP_voltage_after_C13_MBI, E_C13_MBI_RO_voltage AS FLOAT
DIM A_SP_voltage_after_MBE, E_SP_voltage_after_MBE, E_MBE_RO_voltage, E_Parity_RO_voltage as Float 
DIM SP_duration_after_MBE, Parity_RO_duration as Long


'Added for multiple C13 script
DIM case_success AS LONG
DIM Current_C_init as LONG
DIM MBE_counter as LONG
DIM Parity_msmnt_counter as LONG
DIM Nr_C13_init as LONG 

DIM MBE_threshold AS LONG 
DIM MBE_RO_duration AS LONG 
DIM run_case_selector AS LONG 

INIT:
  ' ####################
  ' Initializing variables from Data
  ' ####################
  
  ' integers
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  SP_E_duration                = DATA_20[3] 'E spin pumping duration before MBI
  wait_after_pulse_duration    = DATA_20[4]
  RO_repetitions               = DATA_20[5] ' The total number of measurements (= data points * repetitions)
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
  MBE_threshold                = DATA_20[18] 
  Parity_threshold             = DATA_20[19] 
 
  C13_MBI_RO_duration          = DATA_20[20]
  SP_duration_after_C13        = DATA_20[21]

  MBE_RO_duration              = DATA_20[22]
  SP_duration_after_MBE        = DATA_20[23]

  Parity_RO_duration           = DATA_20[24] 
  C13_MBI_RO_state             = DATA_20[25]


  ' floats
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
  DATA_25[1] = 0
  DATA_28[1] = 0

  FOR i = 1 TO max_repetitions
    DATA_24[i] = 0
    DATA_27[i] = 0
    DATA_43[i] = 0
  NEXT i
  
  FOR i = 1 TO max_nr_of_Carbon_init_steps
    DATA_29[i] = 0
    DATA_32[i] = 0
  NEXT i  

  FOR i = 1 TO max_nr_of_Carbon_init_steps
    DATA_41[i] = 0
    DATA_42[i] = 0
  NEXT i  


  ' ####################
  ' Initializing variables to set values
  ' ####################

  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 1  ' Counts the number of completed runs of the measurement sequence (from CR-check to Final RO)
  first               = 0
  wait_time           = 0
  stop_MBI            = -2 ' wait_for_MBI_pulse + MBI_duration
  ROseq_cntr          = 1
  case_success        = 0

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
  processdelay = cycle_duration

  awg_in_is_hi = 0
  awg_in_was_hi = 0
  awg_in_switched_to_hi = 0

  'Parameters added for C13 init
  Current_C_init = 1
  MBE_counter = 0
  Parity_msmnt_counter = 0
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

  ' #############
  ' Case selector
  ' #############
  IF (run_case_selector = 1) THEN 'Start case selector 
    SelectCase mode 
      
      CASE 0    'CR check // go to SP-E 
        mode = 1    
      
      CASE 1    'SP-E // go to MBI
        mode = 2 
      
      CASE 2 'Start Nitrogen MBI seq and wait for trigger // go to MBI RO  
        mode  = 3
       
      CASE 3 'MBI RO // go to SP-A (succes) OR Nitrogen reset OR CR check       
        IF (case_success =1) THEN
          mode = 4
        ELSE 
          IF (current_MBI_attempt = MBI_attempts_before_CR) THEN  
            mode = 0
            current_MBI_attempt = 1
            current_cr_threshold = cr_preselect
          ELSE  
            mode = 22 
            INC(current_MBI_attempt)
          ENDIF
        ENDIF
        
      CASE 4 'Spin pumpin A // go to start C13 init sequence 
        mode = 5
        
      CASE 5 'Start C13 MBI seq and wait for trigger // go to C13 MBI readout OR SP-A  
        IF (C13_MBI_threshold = 0) THEN  
          mode = 7
        ELSE  
          mode = 6
        ENDIF
                                   
      CASE 6 'C13 MBI readout // go to SP-A OR CR-Check 
        IF (case_success = 1) THEN
          mode = 7
                  
        ELSE 
          mode = 0 
        ENDIF
                                 
      CASE 7 'Spin pump A // go to next C13 MBI OR MBE/Parity OR final RO  
        
        INC(DATA_32[Current_C_init]) 'Count the number of C13 MBI succes for this MBI step
        
        IF (Current_C_init = Nr_C13_init) THEN 'If all carbon initialized 
          IF (Nr_MBE > 0) THEN  
            mode = 8 'to MBE
          ELSE  
            IF (Nr_parity_msmts >0) THEN  'Editing
              mode = 11 'to Parity msmt 
            ELSE
              mode = 13 'to final RO 
            ENDIF
          ENDIF   
        ELSE  
          mode = 5 ' to next Carbon MBI 
          INC(Current_C_init) ' go to next C13 init
          C13_MBI_threshold = DATA_40[Current_C_init] 'go to next C13 init threshold
        ENDIF               
      
      CASE 8 'Start C13 MBE seq and wait for trigger // go to MBE RO 
        mode = 9 
        
      CASE 9 'MBE RO // go to SP-A OR back to CR check 
        IF (case_success = 1) Then '1 for ms = 0, 0 for ms =-1
          mode = 10  'to SP-A
          inc(MBE_counter) 
        ELSE
          mode = 0  
        ENDIF
      
      CASE 10 'SP-A // go to more MBE steps OR final RO  
        IF (MBE_counter = Nr_MBE) THEN
          IF (Nr_parity_msmts >0) THEN  
            mode = 11 'to Parity msmt 
          ELSE
            mode = 13 'to final RO 
          ENDIF 
        ELSE
          mode = 8 'to more MBE  
        ENDIF
        
      CASE 11 'Start parity msmnt seq and wait for trigger // go to Parity msmt RO 
        mode = 12
       
      CASE 12 'Parity RO // go to more Parity msmnt or final RO
        inc(Parity_msmnt_counter)
        IF (Parity_msmnt_counter = Nr_parity_msmts) THEN
          mode = 13 'to final RO
        ELSE 
          mode = 11 'to more  Parity msmt
        ENDIF
                                     
      CASE 13 'start Final RO
        mode = 14
      
      CASE 14 ' Final RO
        mode = 0
      
      CASE 22' If reset N retry MBI (goto spin pump E) 
        mode = 1 
        
    EndSelect 
    ' After case is selected, reset parameters 
    timer = 0 
    run_case_selector = 0
    case_success = 0 
    PAR_77 = mode
 
  ENDIF
  ' ####################
  ' END of Case selector
  ' ####################
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
        
      CASE 0 'CR check // go to SP-E 

        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          run_case_selector = 1
          case_success = 1
          first = 0 
          Current_C_init = 1                          'Reset the Current C index if there was a failure 
          C13_MBI_threshold = DATA_40[Current_C_init] 'Also go back to first init threshold
          MBE_counter = 0
          Parity_msmnt_counter =0  
        ENDIF

      CASE 1 'SP-E // go to MBI
        
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          
        ELSE
          IF (timer = SP_E_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE,0)                                       ' THT: is this nescessary?
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            
            wait_time = wait_after_pulse_duration
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 2  'Start Nitrogen MBI seq and wait for trigger // go to MBI RO  
        IF(timer=0) THEN
          
          INC(MBI_starts)
          PAR_78 = MBI_starts

          INC(data_25[1]) ' Total number of N MBI attempts 

          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)                                  ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

        ELSE
          awg_in_was_hi = awg_in_is_hi
          awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
          
          if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
            awg_in_switched_to_hi = 1
          else
            awg_in_switched_to_hi = 0
          endif
 
          IF(awg_in_switched_to_hi > 0) THEN
                        
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)     'clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
            run_case_selector = 1
            
          ENDIF 
        ENDIF
        
      CASE 3 'MBI RO // go to SP-A (succes) OR Nitrogen reset OR CR check
        counts = P2_CNT_READ(CTR_MODULE, counter_channel)
        IF (counts >= MBI_threshold) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
          P2_CNT_ENABLE(CTR_MODULE,0)

          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)   ' AWG trigger (event jump)
          CPU_SLEEP(9)                                        ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)

          DATA_24[repetition_counter] = current_MBI_attempt ' number of attempts needed since last CR check
          INC(DATA_28[1]) 

          case_success = 1
          run_case_selector = 1
                    
          wait_time = MBI_duration-timer
          current_MBI_attempt = 1
                 
        ELSE
          IF (timer = MBI_duration-1) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
            INC(MBI_failed)
            PAR_74 = MBI_failed
            case_success = 0
            run_case_selector = 1
          ENDIF
        ENDIF
      
      CASE 4    'Spin pumpin A // go to start C13 init sequence 
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
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 5 'Start C13 MBI seq and wait for trigger // go to C13 MBI readout OR SP-A  
        IF (timer=0) THEN 
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)                                  ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
          
          INC(DATA_29[Current_C_init]) 'Count the total number of C13 starts for this initialization steps        
          
        ELSE
          
          awg_in_was_hi = awg_in_is_hi
          awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
          if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
            awg_in_switched_to_hi = 1
          else
            awg_in_switched_to_hi = 0
          endif
                    
          IF(awg_in_switched_to_hi > 0) THEN
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 6 'C13 MBI readout // go to SP-A OR CR-Check 

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

            IF (C13_MBI_RO_state = 1) THEN
              case_success = 0
            ENDIF
            IF (C13_MBI_RO_state = 0) THEN
              case_success = 1
            ENDIF
            
            wait_time = next_MBI_stop-timer
            run_case_selector = 1
            
          ELSE
            IF (timer = C13_MBI_RO_duration ) THEN
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0)
                            
              IF (C13_MBI_RO_state = 1) THEN
                case_success = 1
              ENDIF
              
              IF (C13_MBI_RO_state = 0) THEN
                case_success = 0
              ENDIF
                            
              run_case_selector = 1
            ENDIF
          ENDIF
        ENDIF
        
      CASE 7 'Spin pump A // go to next C13 MBI OR MBE OR final RO  
        IF (timer = 0) THEN 'Turn on lasers
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_C13_MBI+32768) ' turn on A laser
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_C13_MBI+32768) ' turn on E laser

          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)

        ELSE
          IF (timer >= SP_duration_after_C13) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration
            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 8 'Start C13 MBE seq and wait for trigger // go to MBE RO
        IF (timer=0) THEN 'Start the AWG sequence
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
          
          INC(DATA_41[MBE_counter+1]) ' count the number of MBE starts
          
        ELSE
          
          awg_in_was_hi = awg_in_is_hi
          awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
          if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
            awg_in_switched_to_hi = 1
          else
            awg_in_switched_to_hi = 0
          endif
                    
          IF(awg_in_switched_to_hi > 0) THEN
            'case_success =1
            run_case_selector = 1

          ENDIF
        ENDIF


      CASE 9 'MBE RO // go to SP-A OR back to CR check 
        ' TODO_MAR: store RO results
        IF (timer = 0) THEN 'Start the laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)     'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_MBE_RO_voltage+32768) ' turn on Ex laser

        ELSE 'Check if we got a count or if we are the end of the RO
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) 
          IF (counts >= MBE_threshold) THEN 
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
            wait_time = next_MBI_stop-timer
            case_success      = 1
            run_case_selector = 1
            
            INC(DATA_42[MBE_counter+1]) ' count the number of MBE successes

          ELSE ' If at the end of RO duration without enough counts
            IF (timer = MBE_RO_duration ) THEN 
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0)
              case_success      = 0
              run_case_selector = 1
            ENDIF
          ENDIF
        ENDIF

      CASE 10 'SP-A // go to more MBE steps OR final RO  
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_MBE+32768) ' turn on A laser
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_MBE+32768) ' turn on E laser
        
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)

        ELSE
          IF (timer = SP_duration_after_MBE) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration

            case_success = 1
            run_case_selector = 1
          ENDIF
        ENDIF
       
      CASE 11 'start parity msmst sequence and wait for trigger // go to parity RO
        IF (timer=0) THEN 'Start the AWG sequence
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)                                  ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
        ELSE
          awg_in_was_hi = awg_in_is_hi
          awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
          IF ((awg_in_was_hi = 0) AND (awg_in_is_hi > 0)) THEN
            awg_in_switched_to_hi = 1
          ELSE
            awg_in_switched_to_hi = 0
          ENDIF
          
          IF(awg_in_switched_to_hi > 0) THEN
            run_case_selector = 1
          ENDIF
        ENDIF

      CASE 12 'parity RO // go to more parity msmnts OR final RO 
        ' TODO_MAR: store RO results
        IF(timer=0) THEN 'Start the laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_Parity_RO_voltage+32768) ' turn on Ex laser 
                  
        ELSE
          counts = P2_CNT_READ(CTR_MODULE, counter_channel) ' Read counters
           
          IF ((counts >0) OR (timer = parity_RO_duration )) THEN  
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0) 'Turn off counter
                  
            IF (counts = 0) THEN 'Jump AWG to alternative branch if RO result 0 counts (ms=1)
              P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
              CPU_SLEEP(9)                                       ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
            ELSE
              INC(DATA_43[(repetition_counter-1) * Nr_parity_msmts + Parity_msmnt_counter +1])        
            ENDIF 
            
            run_case_selector = 1
        
          ENDIF
        ENDIF
         
      CASE 13 'start Final RO     
        
        awg_in_was_hi = awg_in_is_hi
        awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
          
        IF ((awg_in_was_hi = 0) AND (awg_in_is_hi > 0)) THEN
          awg_in_switched_to_hi = 1
        ELSE
          awg_in_switched_to_hi = 0
        ENDIF
                
        IF (awg_in_switched_to_hi > 0) THEN
          run_case_selector = 1
          wait_time = 0
          
          'start laser for RO
          RO_duration = DATA_34[ROseq_cntr]
          E_RO_Voltage = DATA_36[ROseq_cntr]
          
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277 * E_RO_voltage + 32768) ' turn on Ex laser
                              
        ENDIF
        
      CASE 14    'Final RO // go to CR check
        
        counts = P2_CNT_READ(CTR_MODULE, counter_channel)
        IF ((timer = RO_duration-1) OR (counts > 0)) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser

          IF (counts > 0) THEN
            i = repetition_counter
            INC(DATA_27[i]) 
          ENDIF

          wait_time = wait_after_RO_pulse_duration
          P2_CNT_ENABLE(CTR_MODULE,0)

          INC(repetition_counter)
          Par_73 = repetition_counter
          
          run_case_selector = 1
          first = 1
          
          ' The complete measurement is done once the repetition counter reaches the total repetitions (=data points*repetitions)
          IF (repetition_counter = RO_repetitions+1) THEN
            DEC(repetition_counter)
            Par_73 = repetition_counter
            END
          
          ENDIF
        ENDIF
      
      CASE 22 'If reset N retry MBI (goto spin pump E) 
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_N_randomize_voltage+32768)
        ELSE
          IF (timer = N_randomize_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768)
            P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_off_voltage+32768)
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_off_voltage+32768)

            case_success =0
            run_case_selector = 1
            wait_time = wait_after_pulse_duration
          ENDIF
        ENDIF

    ENDSELECT
    INC(timer)
  ENDIF
  



FINISH:
  finish_CR()

