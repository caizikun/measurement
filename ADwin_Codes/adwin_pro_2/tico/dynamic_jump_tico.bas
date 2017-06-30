'<TiCoBasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = External
' External_Address               = 80804880H
' External_Mask                  = FFFFH
' External_Value                 = 0
' External_Operation             = greater
' Priority                       = High
' Version                        = 1
' TiCoBasic_Version              = 1.2.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
'<Header End>
' Variable trigger delay line that runs on the Tico-coprocessor
' Author: Jesse Slim, Feb 2017
'
' This process is triggered on incoming edges saved in the FIFO
' WARNING: the external trigger settings may need to be changed if any hardware changes occur
'
' Trigger source: external, on Digin_Fifo_Full() > 0
' see DIO32TiCo.inc for the definition of Digin_Fifo_Full:
' Address: 80804880h
' Mask: 0FFFFH
' Test: > 0
'
' Parameters of the delay line need to be set from the ADwin
' Minimum absolute delay: 1120 ns + 0-20 ns jitter (56 clock cycles)
' Minimal delay setting: 15 cycles
' Effective delay on LT3 (rough measurement): (setting - 15) * 20ns + 1120ns
' Effective delay on LT4 (nice measurement with OR-box etc connected): (setting - 15) * 20ns + 1440ns + [0-20]ns of jitter
'
' TROUBLESHOOTING CHECKLIST:
'   - Is the DIO module address set correctly in the compiler settings? (funnily enough it doesn't complain if it is not talking to a DIO)
'   - Are the event trigger settings for the process correctly set corresponding to the hardware at hand?

#INCLUDE C:\ADwin\TiCoBasic\inc\DIO32TiCo.inc

#DEFINE Strobe_Out            Par_13 
#DEFINE Trigger_Count         Par_14 
#DEFINE Trigger_In_Pattern    Par_15
#DEFINE IrrelevantDetections  Par_16
#DEFINE ShortDelayErrors      Par_17
#DEFINE Started               Par_18
#DEFINE Awake                 Par_19
#DEFINE Jump_Bit_Shift        Par_20

#DEFINE Table_Size 256

#DEFINE current_time Par_30
#DEFINE current_index Par_31
#DEFINE current_element Par_32
#DEFINE cycles_past Par_33
#DEFINE detected_bit_pattern Par_34
#DEFINE old_time Par_35
#DEFINE corrected_delay Par_36
#DEFINE max_element Par_37
#DEFINE delay_bias Par_38
#DEFINE starting_bias Par_39

DIM Data_2[Table_Size] As Long ' jump table
DIM Data_3[Table_Size] As Long ' delay cycles

#DEFINE jump_table Data_2
#DEFINE delay_cycles Data_3

INIT:
  Dig_Fifo_Mode(0)
  Digin_Fifo_Enable(0)
  Digin_Fifo_Clear()
  Digin_Fifo_Enable(Trigger_In_Pattern)
  
  ' Enable = 0
  ' Trigger_Count = 0
  ' IrrelevantDetections = 0
  ' ShortDelayErrors = 0
  Started = Trigger_In_Pattern
  Awake = 1
  delay_bias = 30 ' In clock cyles (*20 ns)
  ' This is basically the diff between current_time and old_time within a loop
  starting_bias = 36 ' In processor cycles (*10 ns)
  max_element = Shift_Left(15, Jump_Bit_Shift)
EVENT:
  INC(Trigger_Count)
  Digin_Fifo_Read(detected_bit_pattern, old_time)
  old_time = old_time - starting_bias
  
  IF ((detected_bit_pattern AND Trigger_In_Pattern) > 0) THEN
    Digout(11, 1)
    NOPS(4)
    Digout(11, 0)
    
    current_index = 1
    Do
      current_element = jump_table[current_index]  
      Digout_Bits(current_element, max_element - current_element)
          
      ' Still need to check overflow
      current_time = Digin_Fifo_Read_Timer()
      cycles_past = Shift_Right(current_time - old_time, 1)
      corrected_delay = delay_cycles[current_index] - cycles_past - delay_bias
          
      If (corrected_delay > 5) Then
        NOPS(corrected_delay)
      Else
        '        old_time = old_time - Shift_Left(corrected_delay, 1)
        Inc(ShortDelayErrors)
      EndIf
          
      old_time = Digin_Fifo_Read_Timer()
          
      ' Output
      Digout(Strobe_Out, 1)
      NOPS(4)
      Digout(Strobe_Out, 0)
        
      Inc(current_index)
    Until (delay_cycles[current_index] = 0) ' is outputting jump index 0
  ELSE
    INC(IrrelevantDetections)
  ENDIF
  
FINISH:
  Digin_Fifo_Clear()
