'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
'<Header End>
'DIM ret_val AS INTEGER
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM value, time AS LONG

EVENT:
  value=FPar_20*3276.8+32768  'Convert voltage to bit value
  IF (Par_20<9) THEN
    P2_DAC(DAC_Module,Par_20, value)           'PAR_20 = DAC number
  ELSE
    P2_DAC(DAC_Module_2,Par_20-8, value) 
  ENDIF
  
  END
