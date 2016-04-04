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
' Info_Last_Save                 = TUD277246  DASTUD\tud277246
'<Header End>
#INCLUDE ADwinGoldII.inc
' #INCLUDE configuration.inc
DIM ch0, set0 AS LONG
DIM i AS LONG


INIT:
  CONF_DIO(0011b)
  'CONF_DIO(13)      'configure DIO 08:15 as input, all other ports as output
  set0 = 1
  ch0 = 22
  PAR_74=-1
  PAR_75=-1
  PAR_76=-1
  PAR_61 = ch0 
  i=-2
EVENT:
  
  PAR_75=i
  set0=DIGIN(23)
  DIGOUT(3,1)
  CPU_SLEEP(9)
  DIGOUT(3,1)
  PAR_74 = set0
  if (set0>0) then
    PAR_76=42
    END
  ELSE
    i=PAR_75+1
    PAR_75=i
    i=PAR_75
    
  endif
FINISH:
  
