'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.2.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = TUD278276  DASTUD\TUD278276
'<Header End>
#Include ADwinPro_All.inc

' #Define DIO_module 2

#Define DAC_MODULE_JUMP 3
#Define DAC_MODULE_STROBE 4

#Define HIGH 49152 ' 5 V
#Define LOW 32768 ' 0 V
#Define DIFF (HIGH - LOW)

#Define N 4 ' # of event bits

Dim jump_pattern[N] As Long ' Event bits
Dim jump_out[N] As Long ' Event output voltage
Dim flag as long

Dim strobe As Long
Dim index as Long

Init:

  ' P2_DigProg(DIO_module, 0011b)
  Par_11 = 0
  Par_12 = 0
  flag =0 
  Processdelay = Par_10 ' Clock cycle in units of 1 ns
  CPU_Dig_IO_Config(100010b)
Event:
  
  jump_pattern[1] = Par_1
  jump_pattern[2] = Par_2
  jump_pattern[3] = Par_3
  jump_pattern[4] = Par_4
  
  For index = 1 To N
    jump_out[index] = LOW + jump_pattern[index] * DIFF
  Next index
  index = 1
  
  If (CPU_Digin(0) = 1) Then
    Inc(Par_12)
    If (flag = 1) then
      P2_DAC(DAC_MODULE_STROBE, 1, HIGH)
      P2_DAC(DAC_MODULE_JUMP, 1, HIGH)
      flag =0
    Else 
      flag = 1
    EndIF
    
    ' P2_DAC4(DAC_MODULE_JUMP, jump_out, 1)
  Else
    P2_DAC(DAC_MODULE_STROBE, 1, LOW)
    P2_DAC(DAC_MODULE_JUMP, 1, LOW)
    ' P2_DAC4(DAC_MODULE_JUMP, jump_out, 1)
  EndIf
  
  Inc(Par_11)
  
Finish:
  ' P2_DAC(DAC_module, DAC_no, 32768)
  ' P2_Digout(DIO_Module, 0, 0)
