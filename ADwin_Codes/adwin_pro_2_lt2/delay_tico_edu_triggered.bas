'<TiCoBasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 30
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
#INCLUDE .\configuration.inc

#DEFINE Enable                Par_10
#DEFINE Delay                 Par_11    ' number of delay cycles [* 20 ns]
#DEFINE Trigger_In            Par_12
#DEFINE Trigger_Out           Par_13 
#DEFINE Trigger_Count         Par_14 
#DEFINE Trigger_In_Pattern    Par_15
#DEFINE IrrelevantDetections  Par_16
#DEFINE ShortDelayErrors      Par_17
#DEFINE Started               Par_18
#DEFINE Awake                 Par_19

#DEFINE Output_Duration   10

' Dim current_time, time_past, cycles_past AS LONG
' Dim detected_bit_pattern, detected_time AS LONG
' Dim corrected_delay AS LONG

#DEFINE current_time Par_30
#DEFINE time_past Par_31
#DEFINE cycles_past Par_32
#DEFINE detected_bit_pattern Par_33
#DEFINE detected_time Par_34
#DEFINE corrected_delay Par_35

INIT:
  Dig_Fifo_Mode(0)
  Digin_Fifo_Enable(0)
  Digin_Fifo_Clear()
  Digin_Fifo_Enable(Trigger_In_Pattern)
  
  ProcessDelay = 30
  
  Enable = 0
  Trigger_Count = 0
  IrrelevantDetections = 0
  ShortDelayErrors = 0
  Started = Trigger_In_Pattern
  Awake = 1


EVENT:  
  ' we caught a trigger
  IF (Enable > 0) THEN
    current_time = Digin_Fifo_Read_Timer()
    Digin_Fifo_Read(detected_bit_pattern, detected_time)
    IF ((detected_bit_pattern AND Trigger_In_Pattern) > 0) THEN       
      ' TODO: check if we need to handle overflows
      ' cycles_past = (current_time - detected_time) / 2 ' this line takes 34 cycles (680 ns) to execute => better to do the division with a bit shift
      cycles_past = Shift_Right(current_time - detected_time, 1) ' this line takes 6 cycles (120 ns) to execute
      corrected_delay = Delay - cycles_past ' this line takes 4 cycles (80 ns) to execute
        
      IF (corrected_delay > 5) THEN
        NOPS(corrected_delay)
        
        ' Generate trigger output
        Digout(Trigger_Out, 1)
        NOPS(Output_Duration)
        Digout(Trigger_Out, 0)
        
        INC(Trigger_Count)
        
      ELSE
        INC(ShortDelayErrors)
        ' this probably means that we are receiving pulses more quickly than we can handle
        ' and the fifo buffer is overflowing, let's clear it
        Digin_Fifo_Clear()
      ENDIF
    ELSE
      INC(IrrelevantDetections)
    ENDIF
  ELSE
    Digin_Fifo_Clear()
  ENDIF
  
FINISH:
  Digin_Fifo_Enable(0)
  Digin_Fifo_Clear()
  

