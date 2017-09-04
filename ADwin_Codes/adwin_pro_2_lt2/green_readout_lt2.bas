'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277459  DASTUD\TUD277459
'<Header End>
' primary purpose of this program: 
' Control a measurement with Green readout.
' Adwin is used to 
' - count number of syncs (on counter channel, send by AWG) 
' and 
'- stop measurement when total number of syncs is reached(total_sync = # datapoints * # repetitions / datapoint)
 
' input:
' counter number 
' total number of reps
' DO channel connected to AWG (start     )
' DO channel connected to AWG (event jump)
' output:
' - PAR_73 : Number of syncs

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM AWG_event_jump_DO_channel,AWG_start_DO_channel, sync_counter_idx, total_sync_nr,cnt AS LONG
DIM AWG_done_DI_channel,AWG_done_DI_pattern as LONG
DIM mode,wait_after_click AS LONG


DIM DATA_20[100] AS LONG

INIT:
  AWG_start_DO_channel         = DATA_20[1]
  AWG_event_jump_DO_channel    = DATA_20[2]
  total_sync_nr                = DATA_20[3]
  sync_counter_idx             = DATA_20[4]
  AWG_done_DI_channel          = DATA_20[5]
    
  mode=0
  wait_after_click=0
  PAR_73=0
  
  PROCESSDELAY = 300 
    
  P2_CNT_ENABLE(CTR_MODULE,0000b) 'turn off all counters
  'P2_CNT_MODE(CTR_MODULE,counter_channel, 00001000b) 'configure counter

  P2_Digprog(DIO_MODULE,11)
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  AWG_done_DI_pattern=  2^AWG_done_DI_channel
  ' init counter
  'P2_CNT_ENABLE(CTR_MODULE,0000b)
  'P2_CNT_MODE(CTR_MODULE,sync_counter_idx,00001000b)
  'CNT_SE_DIFF(0000b)
  'P2_CNT_CLEAR(CTR_MODULE,1111b)
  'P2_CNT_ENABLE(CTR_MODULE,1111b)
  
EVENT:
  IF (wait_after_click > 0) THEN
    DEC(wait_after_click)
  ELSE

  
    SELECTCASE mode
  
  
      CASE 0
        P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
        CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
      
        mode=1
  
      CASE 1
        'cnt=0

        'get counts
        'CNT_LATCH(1111b) XXXX GO ON HERE
        'cnt = CNT_READ_LATCH(sync_counter_idx)
      
        'P2_CNT_ENABLE(CTR_MODULE,0000b)
        'P2_CNT_CLEAR(CTR_MODULE,1111b)
        'P2_CNT_ENABLE(CTR_MODULE,1111b)
        'PAR_73 = PAR_73 + cnt
        IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN  
          PAR_73=PAR_73+1
          if (PAR_73=total_sync_nr) THEN
            mode = 2
          else
            wait_after_click=2
          endif
          
        ENDIF
      
      
        
      
        
      CASE 2 
        P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,1)  ' AWG trigger
        CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
        P2_DIGOUT(DIO_MODULE,AWG_event_jump_DO_channel,0)
        END
    ENDSELECT
  endif
  
