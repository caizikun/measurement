'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 1000
' Eventsource                    = External
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
#INCLUDE .\control_tico_delay_line.inc
Import Math.lic

#Define DIO_MODULE 2
#Define DAC_MODULE_JUMP 3

#Define TICO_IN 1
#Define TICO_OUT 2

#Define HIGH 49152 ' 5 V
#Define LOW 32768 ' 0 V
#Define DIFF (HIGH - LOW)

#Define N 4 ' # of event bits
#Define TDIM 256 ' # jump table dimensions

DIM DATA_20[100] AS LONG

DIM DATA_40[65536] AS LONG ' jump table
DIM DATA_41[65536] AS FLOAT ' delay cycles
DIM DATA_42[512] AS LONG ' next seq table [goto, event jump]

' reformatted versions of above
DIM DATA_10[TDIM][TDIM] AS LONG
DIM DATA_11[TDIM][TDIM] AS FLOAT
DIM DATA_12[TDIM][2] AS LONG

DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_done_DI_pattern AS LONG

Dim jump_pattern[N] As Long ' Event bits
Dim jump_out[N] As Long ' Event output voltage
Dim jump_zero[N] As Long

DIM cycle_duration AS LONG

DIM do_tico_delay_control AS LONG
DIM delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_trigger_DO_channel AS LONG

Dim strobe As Long
Dim event_bit_index, seq_index, element_index As Long ' Dummy indices for looping
Dim current_element As Long
Dim current_delay As Float

Dim timer As Long
Init:
  IF (Par_10 = 0) THEN
    EXIT
  ENDIF
  
  cycle_duration            = DATA_20[1]
  AWG_start_DO_channel      = DATA_20[2]
  AWG_done_DI_channel       = DATA_20[3]
  delay_trigger_DI_channel  = DATA_20[4]
  delay_trigger_DO_channel  = DATA_20[5]
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  delay_trigger_DI_pattern = 2 ^ delay_trigger_DI_channel
    
  For event_bit_index = 1 To N
    jump_zero[event_bit_index] = LOW
  Next event_bit_index
  event_bit_index = 1
  
  ' Init jump tables
  current_element = 0
  For element_index = 1 To TDIM
    Inc(current_element)
    DATA_10[seq_index][element_index] = DATA_40[current_element]
    DATA_11[seq_index][element_index] = DATA_41[current_element]
      
    If (DATA_40[current_element] < 0) Then
      DATA_12[seq_index][1] = DATA_42[seq_index * 2 - 1]
      DATA_12[seq_index][2] = DATA_42[seq_index * 2]
      
      Inc(seq_index)
      element_index = 0
    EndIf
  Next element_index
  
  Processdelay = cycle_duration ' Clock cycle in units of 1 ns
  timer = 0
  seq_index = 1
  
  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  
  CPU_Dig_IO_Config(110010b) ' DIO-1 for output, DIO-0 for input w/ rising edge
  
  ' Trigger AWG if idle
  CPU_Digout(1,1)
  CPU_SLEEP(9)
  CPU_Digout(1,0)
  
  tico_delay_line_init(DIO_MODULE, delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_trigger_DO_channel)
Event:
  Inc(timer)
  Par_20 = timer
  
  seq_index = 1
  For element_index = 1 To 3
    current_element = DATA_10[seq_index][element_index]
    current_delay = DATA_11[seq_index][element_index]
    
    Par_26 = current_element
    FPar_26 = current_delay
    
    Par_27 = DATA_12[seq_index][1]
            
    Do
      Inc(Par_21)
      current_delay = current_delay - 0.05 ' Super incorrect
    Until (Par_21 > 100)
    Par_21 = 0
                  
    If (current_element < 0) Then
      ' GOTO next seq
      element_index = 0
      seq_index = DATA_12[seq_index][1]
                    
      ' Stop looping
      If (seq_index = 1) Then
        End
      EndIf
       
    Else
      
      jump_pattern[1] = Mod(current_element, 2)
      jump_pattern[2] = Mod(Shift_right(current_element, 1), 2)
      jump_pattern[3] = Mod(Shift_right(current_element, 2), 2)
      jump_pattern[4] = Mod(Shift_right(current_element, 3), 2)
                  
      Par_25 = current_element
                
      For event_bit_index = 1 To N
        jump_out[event_bit_index] = LOW + jump_pattern[event_bit_index] * DIFF
      Next event_bit_index
                  
      P2_DAC(DAC_MODULE_JUMP, 5, HIGH)
      P2_Sleep(150)
      P2_DAC(DAC_MODULE_JUMP, 5, LOW)
      P2_DAC4(DAC_MODULE_JUMP, jump_out, 1)
      P2_Sleep(150)
      P2_DAC4(DAC_MODULE_JUMP, jump_zero, 1)
    EndIf
        
  Next element_index
  
Finish:
  tico_delay_line_finish()
