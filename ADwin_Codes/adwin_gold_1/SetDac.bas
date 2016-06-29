'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.2
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10226  TUD10226\localadmin
'<Header End>
'DIM ret_val AS INTEGER
DIM value AS LONG
EVENT:
  value=FPar_20*3276.8+32768  'Convert voltage to bit value
  DAC(Par_20,value)           'PAR_20 = DAC number
  END
