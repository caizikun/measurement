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
#DEFINE g_0             FPAR_77              ' Scalefactor ZPL APD 0

' Defining PAR
#DEFINE DELAY           PAR_10               ' Processdelay

' Defining var
DIM n_0, n_max_0           AS FLOAT        ' ZPL APD 0 
DIM n_1, n_max_1           AS FLOAT        ' ZPL APD 1

INIT:
  PROCESSDELAY = 30000*DELAY               ' Processdelay
  
  P2_DAC_2(14, 0)
  n_max_0 = 0
  n_max_1 = 0
  
  ' init counter
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 2,000010000b)
  P2_CNT_MODE(CTR_MODULE, 3,000010000b)
  'CNT_SE_DIFF(0000b)
  P2_CNT_CLEAR(CTR_MODULE, 0110b)
  P2_CNT_ENABLE(CTR_MODULE, 0110b)
 
  
Event:
  'measure    
  P2_CNT_LATCH(CTR_MODULE, 0110b)       
  n_0 = P2_CNT_READ_LATCH(CTR_MODULE, 2)
  n_1 = P2_CNT_READ_LATCH(CTR_MODULE, 3) 
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,0110b)
  P2_CNT_ENABLE(CTR_MODULE,0110b) 
  
  'find coefficients
  if (n_0 > n_max_0) then
    n_max_0 = n_0
  endif
  
  if (n_1 > n_max_1) then
    n_max_1 = n_1
  endif
  g_0 = n_max_1/n_max_0
