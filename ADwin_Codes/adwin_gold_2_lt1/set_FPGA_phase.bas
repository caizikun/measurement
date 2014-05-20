'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277246  DASTUD\TUD277246
'<Header End>
#INCLUDE ADwinGoldII.inc
' #INCLUDE configuration.inc
DIM ch0, set0 AS LONG

INIT:
  CONF_DIO(10b)        
  set0 = 1
  ch0 = 22

  PAR_61 = ch0 

EVENT:
  Digout(12, 0)
  END
