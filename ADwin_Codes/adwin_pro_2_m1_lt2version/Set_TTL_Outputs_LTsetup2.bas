'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = TUD277931  DASTUD\TUD277931
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM channel, set AS LONG

INIT:
  P2_Digprog(DIO_MODULE,11)  'configure DIO 08:15 as input, all other ports as output
  channel=PAR_61    'Number of DIO to set 
  set=PAR_62        'can be 1 or 0
EVENT:

  P2_DIGOUT(DIO_Module,channel, set)   'This sets the digital output with channelnr to the value given by set
   
  END   
