'<TiCoBasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 50
' Eventsource                    = Timer
' Priority                       = High
' Version                        = 1
' TiCoBasic_Version              = 1.2.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
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

#DEFINE Enable                 Par_10
#DEFINE Jump_Bit_Shift         Par_11
#DEFINE AWG_start_DO_channel   Par_12
#DEFINE AWG_jump_strobe_DO_channel Par_13

#DEFINE awake                 Par_19
' #DEFINE current_index         Par_20
#DEFINE current_element       Par_21
#DEFINE corrected_delay       Par_22
#DEFINE max_element           Par_23
#DEFINE delay_bias            Par_24
#DEFINE ShortDelayErrors      Par_25
#DEFINE max_index             Par_26

DIM Data_1[1000] As Long ' jump table
DIM Data_2[1000] As Long ' delay cycles

DIM current_index As Long

#DEFINE jump_table Data_1
#DEFINE delay_cycles Data_2

INIT:
  
  Enable = 0
  delay_bias = 41 ' In clock cyles (*20 ns)
  
  max_element = Shift_Left(15, Jump_Bit_Shift)
  
  awake = 1
  
  Par_37 = 0
  Processdelay = 50 ' In clock cyles (*20 ns)
EVENT:
  Inc(Par_37)
  
  If (Enable = 1) Then

    ' Trigger AWG
    DIGOUT(AWG_start_DO_channel,1)
    DIGOUT(AWG_start_DO_channel,0)
    
    For current_index = 1 To max_index
      ' get current jump index and output it early so strobe can catch it properly
      current_element = jump_table[current_index]  
      Digout_Bits(current_element, max_element - current_element) ' Set the jump table
         
      ' Still need to check overflow
      corrected_delay = delay_cycles[current_index] - delay_bias
          
      If (corrected_delay > 5) Then
        NOPS(corrected_delay)
      Else
        Inc(ShortDelayErrors)
      EndIf
          
      ' Output strobe and jump immediately
      Digout(AWG_jump_strobe_DO_channel, 1)
      ' NOPS(4) ' Is this really necessary?
      Digout(AWG_jump_strobe_DO_channel, 0)
    Next current_index
    
    Digout_Bits(0, max_element) ' Output 0 = go back to AWG idle mode
    NOPS(10)
    Digout(AWG_jump_strobe_DO_channel, 1)
    Digout(AWG_jump_strobe_DO_channel, 0)
      
    Enable = 0

  EndIf
  
    
FINISH:
