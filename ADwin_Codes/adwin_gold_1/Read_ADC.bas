'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 7
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10239  DASTUD\TUD10239
'<Header End>
DIM val AS INTEGER
DIM val_float AS FLOAT
EVENT:
  val=ADC(PAR_21)
  val_float = (val - 32768)/3276.8
  FPAR_21=val_float
  END
