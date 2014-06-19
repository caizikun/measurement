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
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
' Foldings                       = 518
'<Header End>
' MBI with the adwin, with dynamic CR-preparation, dynamic MBI-success/fail
' recognition, and SSRO at the end. 
'
' protocol:
' 
' modes: 
' MODES ARE OUTDATED, NEED TO BE UPDATED FOR THIS SCRIPT 
'   0 : CR check
'   2 : E spin pumping into ms=0
'   3 : MBI
'   4 : A-pumping
'   5 : wait for AWG
'   6 : spin-readout
'   7 : nuclear spin randomize

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins       500 ' not used anymore? Machiel 23-12-'13
#DEFINE max_sequences     100
#DEFINE max_time        10000
#DEFINE max_mbi_steps     100

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
DIM A_SP_voltage_after_C13_MBI, E_SP_voltage_after_C13_MBI, E_C13_MBI_voltage AS FLOAT
 




INIT:
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
  MBI_threshold                = DATA_20[11]
  nr_of_ROsequences            = DATA_20[12]
  wait_after_RO_pulse_duration = DATA_20[13]
  N_randomize_duration         = DATA_20[14]
  C13_MBI_threshold            = Data_20[15] 
  C13_MBI_RO_duration             = Data_20[16]
  SP_duration_after_C13        = Data_20[17] 
  
  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  E_MBI_voltage                = DATA_21[2]  
  E_N_randomize_voltage        = DATA_21[3]
  A_N_randomize_voltage        = DATA_21[4]
  repump_N_randomize_voltage   = DATA_21[5]
  E_SP_voltage_after_C13_MBI   = DATA_21[6]
  A_SP_voltage_after_C13_MBI   = DATA_21[7]
  E_C13_MBI_voltage            = DATA_21[8]
  ' initialize the data arrays
  FOR i = 1 TO max_repetitions
    DATA_24[i] = 0
    DATA_25[i] = 0
    DATA_28[i] = 0
    DATA_27[i] = 0
  NEXT i
        
  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 1
  first               = 0
  wait_time           = 0
  stop_MBI            = -2 ' wait_for_MBI_pulse + MBI_duration
  ROseq_cntr          = 1
  seq_cntr            = 1
  
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
  
  ' init parameters
  ' Y after the comment means I (wolfgang) checked whether they're actually used
  ' during the modifications of 2013/01/11
  PAR_73 = 0                      ' repetition counter
  PAR_74 = 0                      ' MBI failed Y
  PAR_77 = 0                      ' current mode (case) Y
  PAR_78 = 0                      ' MBI starts Y
  PAR_80 = 0                      ' ROseq_cntr Y 
  
EVENT:
 
  awg_in_was_hi = awg_in_is_hi
  awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
  
  'Detect if the AWG send a trigger
  if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
    awg_in_switched_to_hi = 1
  else
    awg_in_switched_to_hi = 0
  endif
    
  PAR_77 = mode        
  
  if(trying_mbi > 0) then
    inc(mbi_timer)
  endif   
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    
    SELECTCASE mode
           
      CASE 0 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 1 
          timer = -1 
          first = 0 
        ENDIF 
      
      CASE 1    ' E spin pumping for 14N MBI
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
            
            mode = 2
            wait_time = wait_after_pulse_duration
            timer = -1
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
                mode = 3
                wait_time = next_MBI_stop-timer
                timer = -1
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
      
                  IF (current_MBI_attempt = MBI_attempts_before_CR) then
                    current_cr_threshold = cr_preselect
                    mode = 0 '(check resonance and start over)
                    current_MBI_attempt = 1
                  ELSE
                    mode = 10
                    INC(current_MBI_attempt)
                  ENDIF                
                  timer = -1      
                ENDIF
              ENDIF          
            ENDIF
          ENDIF
        ENDIF
        
      CASE 3    ' A laser spin pumping after 14N MBI
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
            
            mode = 4
            timer = -1
          ENDIF
        ENDIF      
      
      CASE 4 'Start AWG sequence and wait for it to finish the init part  
        
        IF (timer=0) THEN 'Start the AWG sequence
          
          'INC(C13_MBI_starts)
               
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
          
          ' make sure we don't accidentally think we're done before getting the trigger
          'next_MBI_stop = -2
          'AWG_is_done = 0
          
        
        ELSE
          ' Wait for the AWG trigger that signals the init sequence is done, then spin pump or readout
          IF(awg_in_switched_to_hi > 0) THEN
            
            IF (C13_MBI_threshold = 0) THEN 'if no threshold, skip the RO part, proceed directly to SP

              mode = 6 ' go to spin pump after C13 init
              timer = -1
            
            ELSE ' if threshold > 0, proceed to RO 
              
              'next_C13_MBI_stop = timer + MBI_duration
              mode = 5 'Go the the MBI readout
              timer = -1           
            
            ENDIF
                      
          ENDIF
        ENDIF  
        
      CASE 5 'C13 init/MBI RO
        
        IF(timer=0) THEN 'Start the laser     
                
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_C13_MBI_voltage+32768) ' turn on Ex laser
          ' Needs Carbon Voltage 
          
        ELSE 'Check if we got a count or if we are the end of the RO
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          IF (counts >= C13_MBI_threshold) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
           
            mode = 6 'go to spin pumping on A after C13 init  
            wait_time = next_MBI_stop-timer
            timer = -1

          ELSE 
            IF (timer = C13_MBI_RO_duration ) THEN  'needs to be changed to C_MBI_duration 
              P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
              P2_CNT_ENABLE(CTR_MODULE,0)
        
              mode = 1 'back to the start (spin pumping before 14N MBI)
              timer = -1  
            ENDIF                
                  
          ENDIF
        ENDIF
        
      CASE 6    'A laser spin pumping after 13C MBI
        
        'is this not a very odd place to specify values? Shouldn't that be done before the loop? Adriaan 
        'A_SP_voltage_after_C13_MBI = DATA_35[ROseq_cntr]  ' currently these values are identical to the normal N-spin MBI 
        'E_SP_voltage_after_C13_MBI = DATA_39[ROseq_cntr]
        
        'A_SP_voltage_after_MBI = DATA_35[ROseq_cntr]
        'E_SP_voltage_after_MBI = DATA_39[ROseq_cntr]
        'SP_duration = DATA_33[ROseq_cntr]
        
       
        IF (timer = 0) THEN
          ' Typicallyl the laser power for one of the two is set to 0 in the msmt params that are loaded 
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_C13_MBI+32768) ' turn on A laser, for spin pumping after C13 MBI
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_C13_MBI+32768) ' turn on E laser, for spin pumping after C13 MBI
                              
        ELSE 
          ' when we're done, turn off the laser, send the event to the AWG and proceed to wait until RO
          IF (timer = SP_duration_after_C13) THEN
            
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            
            'Send event to the AWG to signal C13 MBI succes
            P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
                        
            wait_time = wait_after_pulse_duration
            
            mode = 7
            timer = -1
          ENDIF
        ENDIF           
              
      CASE 7    ' wait for AWG to finish and then readout

        ' we wait for the sequence to be finished. the AWG needs to tell us by a pulse,
        ' of which we detect the falling edge. Added by THT: "falling edge:, is that correct?
        ' we then move on to readout
        IF (awg_in_switched_to_hi > 0) THEN          
          mode = 8
          timer = -1
          wait_time = 0
        ENDIF
        
      CASE 8    ' readout on the E line
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
              INC(DATA_27[i])
            ENDIF
                    
            wait_time = wait_after_RO_pulse_duration
            P2_CNT_ENABLE(CTR_MODULE,0)
                        
            INC(ROseq_cntr)
            par_80 = ROseq_cntr
            
            INC(repetition_counter)
            Par_73 = repetition_counter
                      
            IF (ROseq_cntr = nr_of_ROsequences+1) THEN ' this means we're done with one full run
              INC(seq_cntr)
              mode = 0
              timer = -1                
              first = 1
              ROseq_cntr = 1
              
              ' we're done once we're at the last repetition and the last RO step
              IF (repetition_counter = RO_repetitions+1) THEN
                DEC(repetition_counter)
                Par_73 = repetition_counter
                END
              ENDIF
                 
              'ELSE ' means we're starting the next ROsequence THT: CAREFUL, THIS STILL NEEDS TO BE FIXED, I WILL ADD MULTIPLE RO's LATER
              ' mode = 4
              'timer = -1
            ENDIF
          ENDIF
        endif
        
      case 10 ' turn on the lasers to randomize the N-spin state before re-trying MBI
        
        if (timer = 0) then
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_N_randomize_voltage+32768)
        else
          if (timer = N_randomize_duration) then
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768)
            P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_off_voltage+32768)
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_off_voltage+32768)
            
            mode = 2
            timer = -1
            wait_time = wait_after_pulse_duration
          endif                    
        endif
                  
    endselect
    
    INC(timer)
    
  endif
  
    
FINISH:
  finish_CR()

