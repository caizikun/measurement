'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc


#DEFINE max_sample    500000

DIM DATA_20[100] AS LONG
DIM DATA_24[max_sample] AS LONG
DIM DATA_25[max_sample] AS LONG

'Define variables
DIM index, sample_cycles   AS LONG
DIM repetition_counter, max_repetitions   AS LONG

Init:
  index = 0
  sample_cycles               = DATA_20[1]
  max_repetitions             = DATA_20[2]
  repetition_counter  = 0

  FOR repetition_counter = 1 TO max_sample
    DATA_24[repetition_counter] = 0
    DATA_25[repetition_counter] = 0
  NEXT repetition_counter

  repetition_counter = 1

  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,0110b)
  P2_CNT_ENABLE(CTR_MODULE,0110b)
  
Event:

      
  inc(index)
  
  Par_51 = sample_cycles
  Par_52 = index
  Par_53 = repetition_counter
  
  if (index>sample_cycles) then
    ' Measure counts
    P2_CNT_LATCH(CTR_MODULE, 0110b)
    DATA_24[repetition_counter] = P2_CNT_READ_LATCH(CTR_MODULE, 2)
    DATA_25[repetition_counter] = P2_CNT_READ_LATCH(CTR_MODULE, 3)
    P2_CNT_ENABLE(CTR_MODULE,0000b)
    P2_CNT_CLEAR(CTR_MODULE,0110b)
    P2_CNT_ENABLE(CTR_MODULE,0110b)
  
    inc(repetition_counter)  
    index = 0
    
    IF (repetition_counter = max_repetitions) THEN
      END
    ENDIF

        
  endif

