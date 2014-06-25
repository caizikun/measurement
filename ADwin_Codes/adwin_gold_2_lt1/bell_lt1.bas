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

#INCLUDE ADwinGoldII.inc
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
DIM DATA_27[max_events_dim] AS LONG  'time spent waiting after local CR ok, for entanglement event
DIM DATA_28[max_CR_counts] AS LONG  'CR hist after sequence

DIM SP_duration, SP_filter_duration AS LONG
DIM SSRO_duration AS LONG
DIM local_wait_time, local_wait_time_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT

DIM timer, aux_timer, mode, i AS LONG
DIM first AS LONG

DIM repetition_counter AS LONG

DIM AWG_success_DI_channel, AWG_succes_DI_pattern AS LONG
DIM AWG_succes_is_high, AWG_succes_was_high, DIO_register AS LONG
DIM wait_for_AWG_done, sequence_wait_time AS LONG
DIM counts, old_counts AS LONG

DIM remote_CR_trigger_do_channel,AWG_done_di_channel,AWG_done_di_pattern, AWG_done_was_high,AWG_done_is_high  AS LONG
DIM succes_event_counter, remote_CR_wait_timer AS LONG
DIM CR_result,first_local AS LONG


INIT:
  init_CR()
  AWG_done_di_channel           = DATA_20[1]
  AWG_success_DI_channel        = DATA_20[2]
  SP_duration                   = DATA_20[3]
  local_wait_time_duration      = DATA_20[4]
  remote_CR_trigger_do_channel  = DATA_20[5]
  SSRO_duration                 = DATA_20[6]
  wait_for_AWG_done             = DATA_20[7]
  sequence_wait_time            = DATA_20[8]
  

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
    
  AWG_succes_DI_pattern = 2 ^ AWG_success_DI_channel
  AWG_done_di_pattern = 2 ^ AWG_done_di_channel
  
  repetition_counter = 0
  first              = 0
  local_wait_time    = 0
  first_local        = 0
   
  succes_event_counter = 0
  remote_CR_wait_timer = 0
    
  DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
  DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off E laser

  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter

  CONF_DIO(0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO)
  DIGOUT(remote_CR_trigger_do_channel,0)

  mode = 0
  timer = 0
  
  'live updated pars
  Par_61 = mode
  Par_62 = 0                    'AWG signal timeout (no ent. events)
  Par_63 = 0                    ' Stop flag
  Par_73 = repetition_counter     ' SSRO repetitions
  par_77 = succes_event_counter 
  PAR_80=0                     

EVENT:

    
  IF (local_wait_time > 0) THEN
    DEC(local_wait_time)
  ELSE
    Par_61 = mode
    SELECTCASE mode
       
      CASE 0 'CR check
        DIGOUT(remote_CR_trigger_do_channel, 0) ' stop triggering remote adwin
        CR_result = CR_check(first,succes_event_counter+1)
        IF ( CR_result > 0 ) THEN
          'IF (Par_63 > 0) THEN
          '  END
          'ENDIF
          mode = 2
          timer = -1
        ENDIF
        IF (( CR_result <> 0 ) AND (first_local > 0)) THEN
          i = MIN_LONG(cr_counts+1,max_CR_counts)
          INC(DATA_28[i])
          first_local = 0
        ENDIF
        
      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          'DAC( repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on Ex laser XXXXXX
          DAC(E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          CNT_CLEAR( counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          old_counts = 0
        ELSE 
          counts = CNT_READ(counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts

          old_counts = counts
          IF (timer = SP_duration) THEN
            CNT_ENABLE(0)
            DAC(repump_laser_DAC_channel, 3277*0+32768) ' turn off Ex laser XXXXXX
            DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser

            local_wait_time = local_wait_time_duration
            mode = 3            
            timer = -1
          ENDIF
        ENDIF
        
      case 3  ' signal local CR+SP done to remote adwin
        
        DIGOUT(remote_CR_trigger_do_channel, 1)
        INC(repetition_counter)
        INC(PAR_73)
        mode = 4            
        timer = -1
        remote_CR_wait_timer = 0
            
      case 4      'waiting for external trigger (AWG succes or timeout)
      
        AWG_done_was_high = AWG_done_is_high
        AWG_succes_was_high = AWG_succes_is_high
        DIO_register = DIGIN_LONG()
        AWG_done_is_high = (DIO_register AND AWG_done_di_pattern)
        AWG_succes_is_high = (DIO_register AND AWG_succes_DI_pattern)
        'PAR_80=Par_80+AWG_done_is_high
        IF ((AWG_succes_was_high = 0) AND (AWG_succes_is_high > 0)) THEN  'AWG triggers to start SSRO (ent. event)
          DIGOUT(remote_CR_trigger_do_channel, 0) ' stop triggering remote adwin
          INC(succes_event_counter)
          INC(Par_77)
          mode = 5
          timer = -1         
          DATA_27[succes_event_counter] = remote_CR_wait_timer   ' save CR timer just after LDE sequence 
          first = 1 
          first_local = 1
        ELSE                  
          IF (wait_for_AWG_done > 0) THEN
            
            IF ((AWG_done_was_high = 0) AND (AWG_done_is_high > 0)) THEN
              INC(PAR_62)            
              mode = 0
              timer = -1
              local_wait_time = 10
              first = 1
              first_local = 1
            ENDIF
          ELSE
            IF (timer = sequence_wait_time) THEN
              INC(PAR_62)            
              mode = 0
              timer = -1
              local_wait_time = 10
              first = 1
              first_local = 1
            ENDIF
          ENDIF    
        ENDIF     
    
      CASE 5    ' spin readout
        
        IF (timer = 0) THEN
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          DAC(E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on E laser
          DAC(A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
          old_counts = 0
        
        ELSE 
          
          IF (timer = SSRO_duration) THEN
            DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            counts = CNT_READ(counter_channel) - old_counts
            old_counts = counts
            DATA_25[succes_event_counter] = counts
            CNT_ENABLE(0)
            
            local_wait_time = local_wait_time_duration 
            mode = 6
            timer = -1                    
          ENDIF
        ENDIF
        
      case 6  ' signal local SSRO done to remote adwin
        DIGOUT(remote_CR_trigger_do_channel, 1)
        local_wait_time = 10
        mode = 0            
        timer = -1
        
    ENDSELECT
    
    INC(timer)
    INC(remote_CR_wait_timer)
    
  ENDIF
  
FINISH:
  finish_CR()
  
  


