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
' Info_Last_Save                 = TUD277513  DASTUD\tud277513
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM channel, set AS LONG

INIT:
  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
 
  channel=PAR_61    'Number of DIO to set 
EVENT:

  PAR_62 = ((P2_DIGIN_Long(DIO_Module)) AND (2^channel))   'This sets the digital output with channelnr to the value given by set
  'PAR_62 = P2_DIGIN_Long(DIO_Module)
  END   
