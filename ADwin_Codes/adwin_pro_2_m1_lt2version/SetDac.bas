'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = TUD277931  DASTUD\tud277931
'<Header End>
'DIM ret_val AS INTEGER
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
DIM value, time AS LONG

EVENT:
  value=FPar_20*3276.8+32768  'Convert voltage to bit value
  P2_DAC_2(Par_20, value)           'PAR_20 = DAC number
  END
