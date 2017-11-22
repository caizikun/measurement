'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
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
' ADwin process to delay a trigger
' Author: Jesse Slim, Feb 2017

'Include
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

'Define var's
#DEFINE Enabled     Par_10
#DEFINE Delay       Par_11                    'trigger delay [* 10 ns]


DIM AWG_start_DO_channel, AWG_done_DI_channel AS LONG                 
DIM AWG_done_DI_pattern AS LONG

INIT:
  'Reset Index
  processdelay = 100                              'Delay between each event 
  
  AWG_start_DO_channel         = 18 ' DATA_20[1]
  AWG_done_DI_channel          = 9 'DATA_20[2]
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
EVENT:
  IF (Enabled > 0) THEN
    IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN ' trigger received
      CPU_SLEEP(Delay)
      P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' send out trigger
    ENDIF
  ENDIF
  
      
    
  
