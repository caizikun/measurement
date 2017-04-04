'<TiCoBasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = None
' Priority                       = High
' Version                        = 1
' TiCoBasic_Version              = 1.2.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUd277299
'<Header End>
' Variable trigger delay line that runs on the Tico-coprocessor
' Author: Jesse Slim, Feb 2017
'
' NOTE: This is a process without trigger (process type None), so we completely
' bypass the operating system and the event cycles it generates; we're gonna
' do that ourselves. Otherwise we would have to deal with a variable delay upon
' the start of each event cycle (up to 120 ns according to spec)

#INCLUDE C:\ADwin\TiCoBasic\inc\DIO32TiCo.inc
#INCLUDE .\configuration.inc

#DEFINE Enable                Par_10
#DEFINE Delay                 Par_11    ' number of delay cycles [* 20 ns]
#DEFINE Trigger_In            Par_12
#DEFINE Trigger_Out           Par_13 
#DEFINE Trigger_Count         Par_14 
#DEFINE Trigger_In_Pattern    Par_15
#DEFINE Errors                Par_16
#DEFINE Monitor               Par_17
#DEFINE StartRunning          Par_20
#DEFINE Stopped               Par_21

#DEFINE Output_Duration   10

Dim current_time, time_past, cycles_past AS LONG
Dim detected_bit_pattern, detected_time AS LONG

Enable = 0
Trigger_Count = 0
Errors = 0
Monitor = 0 

' Digprog(0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO

' main, infinite processing loop

Dig_Fifo_Mode(0)
Digin_Fifo_Clear()
Digin_Fifo_Enable(Trigger_In_Pattern)

DO
  
  ' Trigger_Out = 100000 ' loop for a total of 1e5 times * 6e-4 sec per loop = 60 s
  
  
  IF (Enable > 0) THEN
    ' Keep it enabled
    ' Enable = 0
    DO ' Wait for trigger input
      Inc(Monitor)
    UNTIL ((Digin_Fifo_Full() > 0) OR (StartRunning = 0))
    IF (StartRunning > 0) THEN
      current_time = Digin_Fifo_Read_Timer()
      Digin_Fifo_Read(detected_bit_pattern, detected_time)
      If (detected_bit_pattern > 0) THEN
        time_past = current_time - detected_time ' time past since detection in EDU clock cycles (10 ns)
        ' TODO: check if we need to handle overflows
        cycles_past = time_past / 2 ' convert EDU clock cycles to TiCo clock cycles
      
        NOPS(Delay - cycles_past)
      
        ' Generate trigger output
        Digout(Trigger_Out, 1)
        NOPS(Output_Duration)
        Digout(Trigger_Out, 0)
      
        Inc(Trigger_Count)
      ELSE
        Inc(Errors)
      ENDIF
    ENDIF
    Digin_Fifo_Clear()
  ELSE
    Digin_Fifo_Clear()
  ENDIF
  
UNTIL (StartRunning = 0)

