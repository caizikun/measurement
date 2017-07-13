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
#DEFINE NoDelaySetErrors      Par_20

#DEFINE Delay_ParBuffer_WritePtr         Par_38
#DEFINE Delay_ParBuffer_ReadPtr          Par_39
#DEFINE Delay_ParBuffer_Size             40


#DEFINE Output_Duration   2 ' 40 ns

' Dim current_time, time_past, cycles_past AS LONG
' Dim detected_bit_pattern, detected_time AS LONG
' Dim corrected_delay AS LONG

#DEFINE current_time Par_30
#DEFINE time_past Par_31
#DEFINE cycles_past Par_32
#DEFINE detected_bit_pattern Par_33
#DEFINE detected_time Par_34
#DEFINE corrected_delay Par_35

SUB get_delay_from_parbuffer()
  ' beautifully ugly
  SelectCase Delay_ParBuffer_ReadPtr
    Case 1:
      Delay = Par_1
    Case 2:
      Delay = Par_2
    Case 3:
      Delay = Par_3
    Case 4:
      Delay = Par_4
    Case 5:
      Delay = Par_5
    Case 6:
      Delay = Par_6
    Case 7:
      Delay = Par_7
    Case 8:
      Delay = Par_8
    Case 9:
      Delay = Par_9
    Case 10:
      Delay = Par_10
    Case 11:
      Delay = Par_11
    Case 12:
      Delay = Par_12
    Case 13:
      Delay = Par_13
    Case 14:
      Delay = Par_14
    Case 15:
      Delay = Par_15
    Case 16:
      Delay = Par_16
    Case 17:
      Delay = Par_17
    Case 18:
      Delay = Par_18
    Case 19:
      Delay = Par_19
    Case 20:
      Delay = Par_20
    Case 21:
      Delay = Par_21
    Case 22:
      Delay = Par_22
    Case 23:
      Delay = Par_23
    Case 24:
      Delay = Par_24
    Case 25:
      Delay = Par_25
    Case 26:
      Delay = Par_26
    Case 27:
      Delay = Par_27
    Case 28:
      Delay = Par_28
    Case 29:
      Delay = Par_29
    Case 30:
      Delay = Par_30
    Case 31:
      Delay = Par_31
    Case 32:
      Delay = Par_32
    Case 33:
      Delay = Par_33
    Case 34:
      Delay = Par_34
    Case 35:
      Delay = Par_35
    Case 36:
      Delay = Par_36
    Case 37:
      Delay = Par_37
    Case 38:
      Delay = Par_38
    Case 39:
      Delay = Par_39
    Case 40:
      Delay = Par_40
    Case 41:
      Delay = Par_41
    Case 42:
      Delay = Par_42
    Case 43:
      Delay = Par_43
    Case 44:
      Delay = Par_44
    Case 45:
      Delay = Par_45
    Case 46:
      Delay = Par_46
    Case 47:
      Delay = Par_47
    Case 48:
      Delay = Par_48
    Case 49:
      Delay = Par_49
    Case 50:
      Delay = Par_50
    Case 51:
      Delay = Par_51
    Case 52:
      Delay = Par_52
    Case 53:
      Delay = Par_53
    Case 54:
      Delay = Par_54
    Case 55:
      Delay = Par_55
    Case 56:
      Delay = Par_56
    Case 57:
      Delay = Par_57
    Case 58:
      Delay = Par_58
    Case 59:
      Delay = Par_59
    Case 60:
      Delay = Par_60
    Case 61:
      Delay = Par_61
    Case 62:
      Delay = Par_62
    Case 63:
      Delay = Par_63
    Case 64:
      Delay = Par_64
    Case 65:
      Delay = Par_65
    Case 66:
      Delay = Par_66
    Case 67:
      Delay = Par_67
    Case 68:
      Delay = Par_68
    Case 69:
      Delay = Par_69
    Case 70:
      Delay = Par_70
    Case 71:
      Delay = Par_71
    Case 72:
      Delay = Par_72
    Case 73:
      Delay = Par_73
    Case 74:
      Delay = Par_74
    Case 75:
      Delay = Par_75
    Case 76:
      Delay = Par_76
    Case 77:
      Delay = Par_77
    Case 78:
      Delay = Par_78
    Case 79:
      Delay = Par_79
    Case 80:
      Delay = Par_80
  EndSelect
ENDSUB


INIT:  
  Dig_Fifo_Mode(0)
  Digin_Fifo_Enable(0)
  Digin_Fifo_Clear()
  Digin_Fifo_Enable(Trigger_In_Pattern)
  
  ProcessDelay = 30
  
  ' Enable = 0
  Trigger_Count = 0
  IrrelevantDetections = 0
  ShortDelayErrors = 0
  Started = Trigger_In_Pattern
  Awake = 1
  
  Delay_ParBuffer_WritePtr = 1
  Delay_ParBuffer_ReadPtr = 1


EVENT:  
  ' we caught a trigger
  IF (Enable > 0) THEN
    Digin_Fifo_Read(detected_bit_pattern, detected_time)
    IF ((detected_bit_pattern AND Trigger_In_Pattern) > 0) THEN       
      If (Delay_ParBuffer_WritePtr = Delay_ParBuffer_ReadPtr) THEN
        Inc(NoDelaySetErrors)
      ELSE
        ' Read out the linear buffer
        get_delay_from_parbuffer()
        current_time = Digin_Fifo_Read_Timer()
      
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
        INC(Delay_ParBuffer_ReadPtr)
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
  

