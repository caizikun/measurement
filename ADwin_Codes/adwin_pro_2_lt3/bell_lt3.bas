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
' this program implements single-shot readout fully controlled by ADwin Gold II
'
' protocol:
' mode  0: CR check
' mode  2:  spin pumping with E or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with E or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  E pulse and photon counting for spin-readout with time dependence
'           -> mode 1
'

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins       2000
#DEFINE max_events_dim      50000
#DEFINE max_CR_counts 200

'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

'return
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[max_events_dim] AS LONG  ' SSRO counts spin readout
DIM DATA_27[max_events_dim] AS LONG  'time spent waiting for remote adwin
DIM DATA_28[max_CR_counts] AS LONG  'CR hist after sequence

DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_done_DI_pattern AS LONG

DIM SP_duration, SP_filter_duration AS LONG
DIM SSRO_duration AS LONG
DIM local_wait_time, local_wait_time_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT

DIM timer, aux_timer, mode, i AS LONG
DIM AWG_done AS LONG
DIM first AS LONG

DIM repetition_counter AS LONG


DIM counts, old_counts AS LONG

DIM remote_mode, remote_delay_time, do_sequences, remote_CR_wait_timer AS LONG
DIM remote_CR_trigger_di_channel,remote_CR_trigger_di_pattern, remote_CR_was_high,remote_CR_is_high ,wait_for_remote_CR  AS LONG
DIM PLU_di_channel, PLU_di_pattern AS LONG
DIM AWG_in_is_high, AWG_in_was_high, PLU_is_high, PLU_was_high, DIO_register AS LONG
DIM wait_for_AWG_done, sequence_wait_time AS LONG
DIM succes_event_counter AS LONG
DIM CR_result,first_local AS LONG


INIT:
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  SP_duration                  = DATA_20[3]
  local_wait_time_duration     = DATA_20[4]
  remote_CR_trigger_di_channel = DATA_20[5]
  SSRO_duration                = DATA_20[6]
  wait_for_AWG_done            = DATA_20[7]
  sequence_wait_time           = DATA_20[8]
  PLU_di_channel               = DATA_20[9]
  do_sequences                 = DATA_20[10]
  wait_for_remote_CR           = DATA_20[11]

  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  
  
  FOR i = 1 TO max_SP_bins
    DATA_24[i] = 0
  NEXT i
  
  FOR i = 1 TO max_events_dim
    DATA_25[i] = 0
    DATA_27[i] = 0
  NEXT i
  
  FOR i = 1 TO max_CR_counts
    DATA_28[i] = 0
  NEXT i
      
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  PLU_di_pattern = 2 ^ PLU_di_channel
  remote_CR_trigger_di_pattern = 2 ^ remote_CR_trigger_di_channel
  remote_CR_is_high = 1
  
  repetition_counter  = 0
  first               = 0
  first_local        = 0
  local_wait_time    = 0
  remote_CR_wait_timer = 0
  
  remote_mode  = 0
  remote_delay_time = 0
  
  succes_event_counter = 0
    
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off E laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter

  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
 
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

  mode = 0
  timer = 0
  
  'live updated pars
  Par_60 = -1                      'remote mode
  Par_61 = -1                      'local mode
  Par_62 = 0                       'AWG signal timeouts (no ent. events)
  PAR_63 = 0                       'stop flag
  Par_64 = 0                       'ADWIN LT1 READY TRIGGER
  
  Par_73 = repetition_counter     ' SSRO repetitions
  par_77 = succes_event_counter
  
  PAR_80 = 20*wait_for_remote_CR
  

EVENT:

  if (remote_delay_time > 0) then  
    dec(remote_delay_time)
  ELSE
    Par_60 = remote_mode
    selectcase remote_mode
    
      case 0 'start remote CR check (automatically)
        IF (wait_for_remote_CR > 0) THEN
          remote_mode = 1
          remote_CR_wait_timer = 0
          remote_delay_time = 5
        ELSE
          remote_mode = 2
        ENDIF
                                              
      case 1 'remote CR check running
      
        ' check state of other adwin and whether it has changed to ready
        remote_CR_was_high = remote_CR_is_high
        remote_CR_is_high = ((P2_DIGIN_LONG(DIO_MODULE)) AND (remote_CR_trigger_di_pattern))
             
        IF ((remote_CR_was_high = 0) AND (remote_CR_is_high > 0)) THEN ' ADwin switched to high during last round. 
          'P2_DIGOUT(DIO_MODULE,remote_CR_trigger_do_channel, 0)
          'remote_CR_is_high = 0
          remote_mode = 2
          INC(Par_64)
        ENDIF             
      
      case 2 'remote CR OK, remote adwin waiting
      
      case 3 'remote SSRO running
        ' check state of other adwin and whether it has changed to ready
        remote_CR_was_high = remote_CR_is_high
        remote_CR_is_high = ((P2_DIGIN_LONG(DIO_MODULE)) AND (remote_CR_trigger_di_pattern))
                     
        IF ((remote_CR_was_high = 0) AND (remote_CR_is_high > 0)) THEN ' ADwin switched to high during last round.
          'remote_CR_is_high = 0 
          remote_mode = 4
        ENDIF
                
      case 4 'remote SSRO OK, remote adwin waiting
      
    endselect
  endif
  
  IF (local_wait_time > 0) THEN
    DEC(local_wait_time)
  ELSE
    Par_61 = mode
    SELECTCASE mode
      
      CASE 0 'CR check
        CR_result = CR_check(first,succes_event_counter+1)
        IF ( CR_result > 0 ) THEN
          IF (Par_63 > 0) THEN
            END
          ENDIF
          mode = 2
          timer = -1
        ENDIF
        IF (((first_local > 0) AND (CR_result <> 0)) AND (cr_counts<max_CR_counts)) THEN
          INC(DATA_28[cr_counts+1])
          first_local = 0
        ENDIF
        
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          'P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on Ex laser XXXXXX
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,  counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE, counter_pattern)    'turn on counter
          old_counts = 0
        ELSE 
          counts = P2_CNT_READ(CTR_MODULE, counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts

          old_counts = counts
          IF (timer = SP_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE, 0)
            'P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*0+32768) ' turn off Ex laser XXXXXX
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser

            local_wait_time = local_wait_time_duration
            mode = 3            
            timer = -1
          ENDIF
        ENDIF
            
      case 3 'local init OK, wait for remote
      
        ' todo: we could save the waiting times, or at least averages of them.
        IF (remote_mode = 2) THEN
          if (do_sequences = 0) then
            mode = 0 
            remote_mode = 0
          else      
            mode = 4
            local_wait_time = 5 ' we need to make sure that the AWG is receptive for triggering now!
            DATA_27[succes_event_counter + 1] = remote_CR_wait_timer   ' save CR timer just before LDE sequence
          endif        
          timer = -1
        ENDIF      
    
      case 4 ' trigger LDE, then wait for timeout (AWG) OR success (PLU)
      
        IF (timer = 0) THEN
          
          INC(repetition_counter)
          INC(par_73)
          
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel, 1) ' trigger the AWG to start LDE
          CPU_SLEEP(9)
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel, 0)
          
          'P2_DIGOUT(DIO_MODULE,PLU_arm_do_channel, 1) ' arm the PLU once at the beginning of the LDE sequence
          'CPU_SLEEP(9)
          'P2_DIGOUT(DIO_MODULE,PLU_arm_do_channel, 0)
          
          ' par_60 = (DIGIN_EDGE(1) AND (PLU_di_channel_in_bit))
        
        ELSE
          
          ' logic: if we get a PLU event, we go to the Spin reaoout
          '        if we get an AWG event before a PLU event, we go back to init/CR
          
          PLU_was_high = PLU_is_high
          AWG_in_was_high = AWG_in_is_high
          DIO_register = P2_DIGIN_LONG(DIO_MODULE)
          PLU_is_high = (DIO_register AND PLU_di_pattern)
          AWG_in_is_high = (DIO_register AND AWG_done_DI_pattern)          
          
          IF ((PLU_was_high = 0) AND (PLU_is_high > 0)) THEN              
            INC(par_77)
            INC(succes_event_counter)
            mode = 5
            timer = -1
            remote_mode = 3
            first = 1
            first_local = 1
          ELSE  
            IF (wait_for_AWG_done > 0) THEN
              IF ((AWG_in_was_high = 0) AND (AWG_in_is_high > 0)) THEN
                INC(PAR_62)            
                mode = 0
                timer = -1
                remote_mode = 0
                local_wait_time = 10
                first = 1
                first_local = 1
              ENDIF
            ELSE
              IF (timer = sequence_wait_time) THEN
                INC(PAR_62)            
                mode = 0
                timer = -1
                remote_mode = 0
                local_wait_time = 10
                first = 1
                first_local = 1
              ENDIF
            ENDIF
          ENDIF        
        ENDIF        
      
    
      CASE 5    ' spin readout
        
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on E laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        
        ELSE 
          
          IF (timer = SSRO_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            counts = P2_CNT_READ(CTR_MODULE,counter_channel) - old_counts
            old_counts = counts
            DATA_25[succes_event_counter] = counts
            P2_CNT_ENABLE(CTR_MODULE,0)
            
            mode = 6
            timer = -1
            
            local_wait_time = local_wait_time_duration
                     
          ENDIF
        ENDIF
      CASE 6 'local SSRO OK, wait for remote SSRO done
        IF ((remote_mode = 4) OR (wait_for_remote_CR =0)) THEN
          mode = 0 
          remote_mode = 0
          timer = -1
        ENDIF      
    ENDSELECT
    
    INC(timer)
    INC(remote_CR_wait_timer)
    
  ENDIF
  
FINISH:
  finish_CR()
  
  


