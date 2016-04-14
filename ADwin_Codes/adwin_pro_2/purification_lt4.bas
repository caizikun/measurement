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
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
'<Header End>
' Purification sequence, as sketched in the purification/planning folder
' AR2016
'
' We use two setups. Each adwin is connected to its own awg start trigger. One adwin (lt4) is connected to the AWG jump trigger
' Two channels are used for communication between adwins, one to signal success and one to signal failure
' 
' modes:
'   0 : CR check
'   1 : wait for other adwin
'   2 : E spin pumping into ms=+/-1
'   3 : MBI of one carbon spin: Trigger AWG and wait for done
'   4 : MBI SSRO
'   5 : communicate MBI success to other adwin
'   6 : count repetitions of the entanglement sequence while waiting for PLU success signal
'   7 : wait for AWG (SWAP gate)
'   8 : spin-readout
'   9 : communicate success to other adwin
'  10 : count repetitions of the entanglement sequence while waiting for PLU success signal
'  11 : calculate phase compensation and signal to AWGs
'  12 : wait for AWG (purification gate)
'  13 : SSRO
'  14 : give AWG start and wait for done (Tomo Gate)
'  15 : SSRO

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr_mod.inc

#DEFINE max_sequences     100
#DEFINE max_time        10000
#DEFINE max_mbi_steps     100
#DEFINE max_events_dim  50000
#DEFINE max_SP_bins      2000
#DEFINE max_CR_counts     200
#DEFINE remote_communication_timeout 2000   'no signal from remote adwin for 2000 cycles=2ms: communication timeout           

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

'return from mbi (unchanged)
DIM DATA_24[max_repetitions] AS LONG ' number of MBI attempts needed in the successful cycle
DIM DATA_25[max_repetitions] AS LONG ' number of cycles before success
DIM DATA_27[max_repetitions] AS LONG ' SSRO counts mbi
DIM DATA_28[max_repetitions] AS LONG ' time needed until mbi success (in process cycles)
DIM DATA_29[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
'return from Bell (data_nr changed)
DIM DATA_40[max_events_dim] AS LONG  ' SSRO counts spin readout
DIM DATA_41[max_events_dim] AS LONG  'time spent waiting for remote adwin
DIM DATA_42[max_CR_counts] AS LONG  'CR hist after sequence
DIM DATA_43[max_repetitions] AS LONG ' Information whether same or opposite detector has clicked (provided by the PLU)

DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_event_jump_DO_channel, AWG_done_DI_pattern AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM SP_duration, SP_E_duration, SP_filter_duration, MBI_duration AS LONG
DIM sequence_wait_time, wait_after_pulse_duration AS LONG
DIM RO_repetitions, RO_duration AS LONG
DIM cycle_duration AS LONG
DIM wait_for_MBI_pulse AS LONG
DIM MBI_threshold AS LONG
DIM nr_of_ROsequences AS LONG
DIM adwin_communication_safety_microseconds as long

DIM E_SP_voltage, A_SP_voltage, A_SP_voltage_after_MBI, E_SP_voltage_after_MBI, E_RO_voltage, A_RO_voltage AS FLOAT
DIM E_MBI_voltage AS FLOAT
dim E_N_randomize_voltage, A_N_randomize_voltage, repump_N_randomize_voltage AS FLOAT

DIM timer, mode, i, tmp AS LONG
DIM wait_time AS LONG
DIM repetition_counter AS LONG
dim seq_cntr as long
DIM MBI_failed AS LONG
DIM old_counts, counts AS LONG
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

'Added for communication with other Adwin and PLU
DIM remote_adwin_di_success_channel, remote_adwin_di_success_pattern, remote_adwin_di_fail_channel, remote_adwin_di_fail_pattern as long
DIM remote_adwin_do_success_channel, remote_adwin_do_fail_channel as long
DIM local_success, remote_success, local_fail, remote_fail as long '0 means no result obtained, 1 means successful, 2 means failure
DIM n_of_communication_timeouts, is_single_setup_experiment as long

DIM PLU_count_di_channel, PLU_count_di_pattern, PLU_which_di_channel, PLU_which_di_pattern AS LONG
DIM PLU_count_is_high, PLU_count_was_high, PLU_which_is_high, PLU_which_was_high AS LONG

DIM invalid_data_marker_do_channel AS LONG
DIM wait_for_AWG_done, sequence_wait_time AS LONG
DIM succes_event_counter AS LONG
DIM CR_result, first_local AS LONG

LOWINIT:    'change to LOWinit which I heard prevents adwin memory crashes
  'read int params from python script
  
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  AWG_event_jump_DO_channel    = DATA_20[3]
  SP_E_duration                = DATA_20[4] 'E spin pumping duration before MBI
  wait_after_pulse_duration    = DATA_20[5] 'Time to wait after turning off a laser pulse to ensure it is really off
  RO_repetitions               = DATA_20[6]
  cycle_duration               = DATA_20[7]
  MBI_duration                 = DATA_20[8]
  MBI_attempts_before_CR       = DATA_20[9]
  MBI_threshold                = DATA_20[10]
  nr_of_ROsequences            = DATA_20[11]
  N_randomize_duration         = DATA_20[12]
  
  remote_adwin_di_success_channel = DATA_20[13]
  remote_adwin_di_fail_channel= DATA_20[14]
  remote_adwin_do_success_channel= DATA_20[15]
  remote_adwin_do_fail_channel= DATA_20[16]
  adwin_communication_safety_microseconds = DATA_20[17]
  
  is_single_setup_experiment = Data_20[18]


  SSRO_duration                = DATA_20[22]
  wait_for_AWG_done            = DATA_20[23]
  sequence_wait_time           = DATA_20[24]
  PLU_count_di_channel           = DATA_20[25]
  PLU_which_di_channel           = DATA_20[26]
  invalid_data_marker_do_channel= DATA_20[29]
  
  ' read float params from python
  E_SP_voltage                 = DATA_21[1] 'E spin pumping before MBI
  E_MBI_voltage                = DATA_21[2]  
  E_N_randomize_voltage        = DATA_21[3]
  A_N_randomize_voltage        = DATA_21[4]
  repump_N_randomize_voltage   = DATA_21[5]
  A_SP_voltage                 = DATA_21[6]
  E_RO_voltage                 = DATA_21[7]
  A_RO_voltage                 = DATA_21[8]
  
  ' initialize the data arrays
  FOR i = 1 TO max_repetitions
    DATA_24[i] = 0
    DATA_25[i] = 0
    DATA_27[i] = 0
    DATA_28[i] = 0
    DATA_43[i] = 0
  NEXT i
  
  FOR i = 1 TO max_SP_bins
    DATA_29[i] = 0
  NEXT i
  
  FOR i = 1 TO max_events_dim
    DATA_40[i] = 0
    DATA_41[i] = 0
  NEXT i
  
  FOR i = 1 TO max_CR_counts
    DATA_42[i] = 0
  NEXT i
  
  n_of_communication_timeouts = 0 ' used for debugging, goes to a par   
  MBI_failed          = 0
  MBI_starts          = 0
  repetition_counter  = 1
  first               = 0
  first_local        = 0
  wait_time           = 0
  local_wait_time    = 0
  remote_CR_wait_timer = 0
  stop_MBI            = -2 ' wait_for_MBI_pulse + MBI_duration
  ROseq_cntr          = 1
  seq_cntr            = 1
  
  next_MBI_stop = -2
  AWG_is_done = 0
  current_MBI_attempt = 1
  next_MBI_laser_stop = -2
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  PLU_count_di_pattern = 2 ^ PLU_count_di_channel
  PLU_which_di_pattern = 2 ^ PLU_which_di_channel
  remote_adwin_di_success_pattern = 2^ remote_adwin_di_success_channel
  remote_adwin_di_fail_pattern = 2^ remote_adwin_di_fail_channel
  
  local_sucess = 0
  remote_success = 0
  remote_fail = 0
  local_fail = 0
  check_remote = 1
      
  succes_event_counter = 0
      
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter

  P2_Digprog(DIO_MODULE,11) ' in  is now 16:23   'configure DIO 08:15 as input, all other ports as output
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  P2_DIGOUT(DIO_MODULE,11,0) ' set repumper modulation high.
  
  tmp = P2_Digin_Edge(DIO_MODULE,0)
  mode = 0
  timer = 0
  mbi_timer = 0
  trying_mbi = 0
  processdelay = cycle_duration   ' the event structure is repeated at this period. On T11 processor 300 corresponds to 1us. Can do at most 300 operations in one round.
  
  awg_in_is_hi = 0      
  awg_in_was_hi = 0
  awg_in_switched_to_hi = 0
  
  ' init parameters
  ' Y after the comment means I (wolfgang) checked whether they're actually used
  ' during the modifications of 2013/01/11
  Par_60 = -1                      'remote mode
  Par_61 = -1                      'local mode
  Par_62 = 0                       'AWG signal timeouts (no ent. events)
  PAR_63 = 0                       'stop flag
  PAR_73 = 0                      ' repetition counter
  PAR_74 = 0                      ' MBI failed Y
  PAR_77 = succes_event_counter   ' number of entanglement events
  PAR_78 = 0                      ' MBI starts Y
  PAR_80 = 0                      ' ROseq_cntr Y 
  PAR_76 = 0                      ' n_of_communication_timeouts for debugging
  


  
  
EVENT:
  
  'write information to pars for live monitoring
  PAR_61 = mode        
  PAR_76 = n_of_communication_timeouts ' for debugging
    
  if(trying_mbi > 0) then ' Increase number of mbi trials by one
    inc(mbi_timer)
  endif
  
  IF (wait_time > 0) THEN
    wait_time = wait_time - 1
  ELSE
    ' modes:
    '   0 : CR check
    '   1 : wait for other adwin
    '   2 : E spin pumping into ms=+/-1
    '   3 : MBI of one carbon spin: Trigger AWG and wait for done
    '   4 : MBI SSRO
    '   5 : communicate MBI success to other adwin
    '   6 : count repetitions of the entanglement sequence while waiting for PLU success signal
    '   7 : wait for AWG (SWAP gate)
    '   8 : spin-readout
    '   9 : communicate success to other adwin
    '  10 : count repetitions of the entanglement sequence while waiting for PLU success signal
    '  11 : calculate phase compensation and signal to AWGs
    '  12 : wait for AWG (purification gate)
    '  13 : SSRO
    '  14 : give AWG start and wait for done (Tomo Gate)
    '  15 : SSRO
    
    SELECTCASE mode
       
      CASE 0 'CR check // go to wait for other adwin
        
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          first = 0
          
        ENDIF
        CR_result = CR_check(first,succes_event_counter+1)
        IF ( CR_result > 0 ) THEN 
          IF (Par_63 > 0) THEN 'stop signal received: stop the process
            END
          ENDIF
          MBE_counter = 0
          mode = 1 ' go to wait for second setup to be ready
          timer = -1 ' timer is incremented at the end of the select_case mode structure. Will be zero in the next run
        ENDIF
        
        IF ( (CR_result <> 0) AND (cr_counts < max_CR_counts) ) THEN
          INC(DATA_42[cr_counts+1]) 'CR hist after sequence
        ENDIF

        
        
        
      CASE 1 'communication between adwins
        
        IF (is_single_setup_experiment > 0) THEN ' don't have to wait, jump to next element
          mode = 2
          timer = -1
          
        ELSE 'communicate with other setup
          if (timer = 0) then  ' we only get here if CR check was successful. Send this to other side
            P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,1) 
            P2_DIGOUT(DIO_MODULE,remote_adwin_do_failure_channel,0) 'just to be sure that there are no misunderstandings
          endif 
        
          ' let's see what the other side is doing:
          remote_success = (P2_DIGIN_LONG(DIO_MODULE) AND remote_adwin_di_success_channel) ' other side was successful as well
          IF (remote_success > 0)  THEN
            remote_success = 0 'forget it for the future
            mode = 2 ' go to spin pumping
            timer = -1
            CPU_SLEEP(500) ' this means 500*10ns = 5us delay to ensure the signal we are currently sending also reaches the other adwin. Then switch off again
            P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
            P2_DIGOUT(DIO_MODULE,remote_adwin_do_failure_channel,0) ' just to be sure
          ELSE ' no success signal. Check for fail signal
            remote_fail = (P2_DIGIN_LONG(DIO_MODULE) AND remote_adwin_di_fail_channel) ' other side failed
            IF (remote_fail > 0) then
              mode = 0 ' go back to cr check
              remote_fail = 0 ' forget for the future
              timer = -1
              CPU_SLEEP(500) ' this means 500*10ns = 5us delay to ensure the signal we are currently sending also reaches the other adwin. Then switch off again
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_success_channel,0)
              P2_DIGOUT(DIO_MODULE,remote_adwin_do_failure_channel,0)
            ENDIF 
            
            'no fail and no success: check whether communication timed out
            IF (timer > remote_communication_timeout) THEN
              INC(n_of_communication_timeouts)
              mode = 0 'go back to cr check
              timer = -1
            endif  
          endif
        endif
        
      
        
        
        
      CASE 2    ' E spin pumping
        
        IF (timer = 0) THEN
          P2_DIGOUT(DIO_MODULE,11,1) ' set repumper modulation high.
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768) ' or turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)                        ' clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)                       ' turn on counter
          old_counts = 0
        ELSE
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts    ' for arrival time histogram
          old_counts = counts
                    
          IF (timer >= SP_E_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE,0) ' diable counter
            P2_DIGOUT(DIO_MODULE,11,0)  ' set repumper modulation low.
            P2_DAC(DAC_MODULE, E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE, A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            
            mode = 3   'go to mbi
            wait_time = wait_after_pulse_duration ' make sure the lasers are really off
            timer = 0
          ENDIF
        ENDIF
          
      
      
          
      CASE 3    ' MBI
        ' We first need to trigger the AWG to do the selective pi-pulse
        ' then wait until this is done
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
          CPU_SLEEP(9)                                  ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
       
         
        ELSE
          awg_in_was_hi = awg_in_is_hi
          awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
  
          'Detect if the AWG send a trigger
          if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
            awg_in_switched_to_hi = 1
          else
            awg_in_switched_to_hi = 0
          endif
         
          ' we expect a trigger from the AWG once it has done the MW pulse
          ' as soon as we assume the AWG has done the MW pulse, we turn on the E-laser,
          ' and start counting
          IF(awg_in_switched_to_hi > 0) THEN
            
            mode = 3
            timer = 0     'set to 0 to make the duratio of the next mode, MBI RO, accurate to the us 
                       
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
          ENDIF
        ENDIF
      
      CASE 3  'MBI RO  
        counts = P2_CNT_READ(CTR_MODULE, counter_channel)
        IF (counts >= MBI_threshold) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
          P2_CNT_ENABLE(CTR_MODULE,0)
          

          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
                
          DATA_24[seq_cntr] = current_MBI_attempt ' number of attempts needed in the successful cycle
          mode = 4
          wait_time = MBI_duration-timer
          timer = -1
          current_MBI_attempt = 1
          trying_mbi = 0
          
          'save the time MBI takes
          DATA_28[seq_cntr] = mbi_timer
          mbi_timer = 0

                         
          ' MBI succeeds if the counts surpass the threshold;
          ' we then trigger an AWG jump (sequence has to be long enough!) and move on to SP on A
          ' if MBI fails, we
          ' - try again (until max. number of attempts, after some scrambling)
          ' - go back to CR checking if max number of attempts is surpassed
            
        ELSE 
          IF (timer = MBI_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            P2_CNT_ENABLE(CTR_MODULE,0)
            INC(MBI_failed)
            PAR_74 = MBI_failed
      
            IF (current_MBI_attempt = MBI_attempts_before_CR) then
              current_cr_threshold = cr_preselect
              mode = 0 '(check resonance and start over)
              current_MBI_attempt = 1
            ELSE
              mode = 7
              INC(current_MBI_attempt)
            ENDIF                
            timer = -1      
          ENDIF
        ENDIF          
        
      CASE 4    ' A laser spin pumping

        A_SP_voltage_after_MBI = DATA_35[ROseq_cntr]
        E_SP_voltage_after_MBI = DATA_39[ROseq_cntr]
        SP_duration = DATA_33[ROseq_cntr]
       
        ' turn on A laser; we don't need to count here for the moment
        IF (timer = 0) THEN
          P2_DIGOUT(DIO_MODULE,11,1) ' set repumper modulation high.
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage_after_MBI+32768) ' turn on A laser, for spin pumping after MBI
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage_after_MBI+32768) ' turn on E laser, for spin pumping after MBI
        ELSE 
          
          ' when we're done, turn off the laser and proceed to the sequence
          IF (timer = SP_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            P2_DIGOUT(DIO_MODULE,11,0) ' set repumper modulation low.
            IF (use_shutter > 0) THEN
              P2_DIGOUT(DIO_Module,Shutter_channel, 1)
              'INC(PAR_60)
            ENDIF            
            
            wait_time = wait_after_pulse_duration
            
            mode = 5
            timer = -1
          ENDIF
        ENDIF      
      
      CASE 5    '  wait for AWG sequence or for fixed duration
        
        send_AWG_start = DATA_37[ROseq_cntr]
        sequence_wait_time = DATA_38[ROseq_cntr]
        
        'IF (timer = 0) THEN
        '
        'endif       
       
        ' two options: either run an AWG sequence...
        IF (send_AWG_start > 0) THEN
          
          IF (timer = 0) THEN
            P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel, 1)  ' AWG trigger
            CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
            P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel, 0)          
          
          ELSE
            
            ' we wait for the sequence to be finished. the AWG needs to tell us by a pulse,
            ' of which we detect the falling edge.
            ' we then move on to readout
            
            'NOTE, if the AWG sequenc is to short (close to a us, then it is possible that the time the signal is low is missed?
            awg_in_was_hi = awg_in_is_hi
            awg_in_is_hi = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
  
            'Detect if the AWG send a trigger
            if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
              awg_in_switched_to_hi = 1
            else
              awg_in_switched_to_hi = 0
            endif
            
            IF(awg_in_switched_to_hi > 0) THEN  
              IF (use_shutter > 0) THEN
                mode = 11
              ELSE
                mode = 6
              ENDIF          
              timer = -1
              wait_time = 0
              
              RO_duration = DATA_34[ROseq_cntr]
              E_RO_Voltage = DATA_36[ROseq_cntr]
            ENDIF
          ENDIF
        
        ELSE
          ' if we do not run an awg sequence, we just wait the specified time, and go then to readout
          IF (use_shutter > 0) THEN
            mode = 11
          ELSE
            mode = 6
          ENDIF  
            
            
          timer = -1
          wait_time = sequence_wait_time
      
          RO_duration = DATA_34[ROseq_cntr]
          E_RO_Voltage = DATA_36[ROseq_cntr]
        ENDIF
      
      CASE 11 'Closing Shutter
        P2_DIGOUT(DIO_Module,Shutter_channel, 0)
        'INC(PAR_60)
        timer = -1
        wait_time = Shutter_opening_time
        mode = 6
    
      CASE 6    ' readout on the E line
       
        ' IMPORTANT: to make sure that the RO duration is set precisely there should be as little tasks as possible
        '            during the RO. Otherwise we observe that the RO is artifically extended (missing clock cycles?).
         
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
            
            IF (use_shutter > 0) THEN
              wait_time = Shutter_safety_time
              'INC(PAR_60)
            ELSE
              wait_time = wait_after_pulse_duration
            ENDIF
            
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
                 
            ELSE
              ' means we're starting the next ROsequence
              mode = 4
              timer = -1
            ENDIF
          ENDIF
        endif
        
      case 7 ' turn on the lasers to (hopefully) randomize the N-spin state before re-trying MBI
        
        if (timer = 0) then
          P2_DIGOUT(DIO_MODULE,11,1) ' set repumper modulation high.
          P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_N_randomize_voltage+32768)
          P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_N_randomize_voltage+32768)
        else
          if (timer = N_randomize_duration) then
            P2_DIGOUT(DIO_MODULE,11,0) ' set repumper modulation low.
            P2_DAC(DAC_MODULE,E_laser_DAC_channel,3277*E_off_voltage+32768)
            P2_DAC(DAC_MODULE,A_laser_DAC_channel,3277*A_off_voltage+32768)
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel,3277*repump_off_voltage+32768)
            
            mode = 1
            timer = -1
            wait_time = wait_after_pulse_duration
          endif                    
        endif
                  
    endselect
    
    INC(timer)
    
  endif

    
FINISH:
  finish_CR()

