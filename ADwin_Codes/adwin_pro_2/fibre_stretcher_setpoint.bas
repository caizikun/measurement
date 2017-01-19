'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
' primary purpose of this program: 
' get count rates of internal ADwin counters 3
' Looking for setpoint for PID controller
 
' Input:
' - Signal
' - (process)Delay 
' 
' Output:
' - Setpoint (setpoint) (



' Including packages
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' Defining FPAR
#DEFINE setpoint        FPAR_14              ' Setpoint of PID process

' Defining PAR
#DEFINE DELAY           PAR_10               ' Processdelay

' Defining var
DIM counts, counts_min, counts_max           AS FLOAT        ' Setpoint 

INIT:
  PROCESSDELAY = 3000000*DELAY               ' Processdelay
  
  setpoint = 0
  P2_DAC_2(14, 0)
  
  ' Init counts min and max
  P2_CNT_LATCH(CTR_MODULE, 1111b)       ' Measure
  counts_min = abs(P2_CNT_READ_LATCH(CTR_MODULE, 2) /2)
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,1111b)
  P2_CNT_ENABLE(CTR_MODULE,1111b) 
  counts_max = 0
  
Event:
      
  P2_CNT_LATCH(CTR_MODULE, 1111b)       ' Measure
  counts = P2_CNT_READ_LATCH(CTR_MODULE, 2) 
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,1111b)
  P2_CNT_ENABLE(CTR_MODULE,1111b) 
  
  if (counts > counts_max) then
    counts_max = counts
  endif
  
  if (counts < counts_min) then
    counts_min = counts
  endif
  
  setpoint = (counts_max - counts_min)/2 + counts_min
