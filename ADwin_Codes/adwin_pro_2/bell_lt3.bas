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
' mode  0: dio out to 0
' mode 1: CR check
' mode  2:  spin pumping with E or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with E or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  E pulse and photon counting for spin-readout with time dependence
'           -> mode 1
'

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr_mod.inc

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

DIM PLU_success_DI_channel, PLU_succes_DI_pattern AS LONG
DIM PLU_succes_is_high, PLU_succes_was_high, DIO_register AS LONG
DIM wait_for_AWG_done, sequence_wait_time, wait_before_RO AS LONG
DIM counts, old_counts AS LONG

DIM remote_CR_trigger_do_channel,AWG_done_di_channel,AWG_done_di_pattern, AWG_done_was_high,AWG_done_is_high,invalid_data_marker_do_channel  AS LONG
DIM succes_event_counter, remote_CR_wait_timer AS LONG
DIM CR_result,first_local AS LONG


INIT:
  init_CR()
  AWG_done_di_channel           = DATA_20[1]
  PLU_success_DI_channel        = DATA_20[2]
  SP_duration                   = DATA_20[3]
  local_wait_time_duration      = DATA_20[4]
  remote_CR_trigger_do_channel  = DATA_20[5]
  SSRO_duration                 = DATA_20[6]
  wait_for_AWG_done             = DATA_20[7]
  sequence_wait_time            = DATA_20[8]
  wait_before_RO                = DATA_20[9]
  invalid_data_marker_do_channel= DATA_20[10]
  

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
    
  PLU_succes_DI_pattern = 2 ^ PLU_success_DI_channel
  AWG_done_di_pattern = 2 ^ AWG_done_di_channel
  
  repetition_counter = 0
  first              = 0
  local_wait_time    = 0
  first_local        = 0
   
  succes_event_counter = 0
  remote_CR_wait_timer = 0
    
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
  P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off E laser

  P2_CNT_ENABLE(CTR_MODULE,0000b)'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter

  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO)
  P2_DIGOUT(DIO_MODULE,remote_CR_trigger_do_channel,0)

  mode = 0
  timer = 0
  
  'live updated pars
  Par_61 = mode
  Par_62 = 0                    'AWG signal timeout (no ent. events)
  Par_63 = 0                    ' Stop flag
  Par_73 = repetition_counter     ' SSRO repetitions
  par_77 = succes_event_counter 
  PAR_78 = 0 'invalid data marker
  PAR_80=0                     

EVENT:

    
  IF (local_wait_time > 0) THEN
    DEC(local_wait_time)
  ELSE
    Par_61 = mode
    SELECTCASE mode
       
      CASE 0 
        P2_DIGOUT(DIO_MODULE,remote_CR_trigger_do_channel, 0) ' stop triggering remote adwin
        P2_DIGOUT(DIO_MODULE,invalid_data_marker_do_channel, 0) ' turn off invalid data marker
        mode = 1
        timer = -1
        
      CASE 1 'CR check
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
          'P2_DAC(DAC_MODULE, repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on Ex laser XXXXXX
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          old_counts = 0
        ELSE 
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          DATA_24[timer] = DATA_24[timer] + counts - old_counts

          old_counts = counts
          IF (timer = SP_duration) THEN
            P2_CNT_ENABLE(CTR_MODULE,0)
            'P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*0+32768) ' turn off Ex laser XXXXXX
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser

            local_wait_time = local_wait_time_duration
            mode = 3            
            timer = -1
          ENDIF
        ENDIF
        
      case 3  ' signal local CR+SP done to remote adwin
        
        P2_DIGOUT(DIO_MODULE,remote_CR_trigger_do_channel, 1)
        IF (Par_55>0) THEN
          P2_DIGOUT(DIO_MODULE,invalid_data_marker_do_channel, 1)
        ENDIF
        INC(repetition_counter)
        INC(PAR_73)
        mode = 4            
        timer = -1
        remote_CR_wait_timer = 0
            
      case 4      'waiting for external trigger (AWG succes or timeout)
      
        AWG_done_was_high = AWG_done_is_high
        PLU_succes_was_high = PLU_succes_is_high
        DIO_register = P2_DIGIN_LONG(DIO_MODULE)
        AWG_done_is_high = (DIO_register AND AWG_done_di_pattern)
        PLU_succes_is_high = (DIO_register AND PLU_succes_DI_pattern)
        'PAR_80=Par_80+AWG_done_is_high
        IF ((PLU_succes_was_high = 0) AND (PLU_succes_is_high > 0)) THEN  'AWG triggers to start SSRO (ent. event)
          P2_DIGOUT(DIO_MODULE,remote_CR_trigger_do_channel, 0) ' stop triggering remote adwin
          INC(succes_event_counter)
          INC(Par_77)
          mode = 5
          timer = -1         
          DATA_27[succes_event_counter] = remote_CR_wait_timer   ' save CR timer just after LDE sequence 
          first = 1 
          first_local = 1
          local_wait_time = wait_before_RO
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
            
            local_wait_time = local_wait_time_duration 
            mode = 6
            timer = -1                    
          ENDIF
        ENDIF
        
      case 6  ' signal local SSRO done to remote adwin
        P2_DIGOUT(DIO_MODULE,remote_CR_trigger_do_channel, 1)
        local_wait_time = 10
        mode = 0            
        timer = -1
        
    ENDSELECT
    
    INC(timer)
    INC(remote_CR_wait_timer)
    
  ENDIF
  
FINISH:
  finish_CR()
  
  


