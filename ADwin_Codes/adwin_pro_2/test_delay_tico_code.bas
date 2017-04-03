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

#DEFINE Output_Duration   10

Enable = 0
Trigger_Count = 0

' Digprog(0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO

' main, infinite processing loop
DO
  
  ' Trigger_Out = 100000 ' loop for a total of 1e5 times * 6e-4 sec per loop = 60 s
  
  
  IF (Enable > 0) THEN
    ' Keep it enabled
    ' Enable = 0
    DO ' Wait for trigger input
      Inc(Par_17)
    UNTIL ((in(100H) AND Trigger_In_Pattern) > 0)
    Par_17 = 0
    Inc(Trigger_Count)
    NOPS(Delay)
    
    ' Generate trigger output
    Digout(Trigger_Out, 1)
    NOPS(Output_Duration)
    Digout(Trigger_Out, 0)
  ENDIF
  
UNTIL (0 = 1)
