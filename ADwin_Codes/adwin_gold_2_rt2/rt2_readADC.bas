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
' Info_Last_Save                 = TUD276198  DASTUD\TUD276198
'<Header End>
'DIM ret_val AS INTEGER

#INCLUDE ADwinGoldII.inc
'#INCLUDE .\configuration.inc
DIM value, adc_binary_voltage AS LONG

EVENT:
  'P2_SE_Diff(ADC_module,0)
  adc_binary_voltage = ADC(Par_21)
  FPar_21 = (adc_binary_voltage-32768)/3276.8
  END
