'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' holds the settings for communication between ADwin CPU and TiCo processor
' is filled automatically by the TiCo initialization command
DIM tdrv_datatable[150] AS LONG   

#DEFINE TiCo_Enable               10
#DEFINE TiCo_Delay                11
#DEFINE TiCo_Trigger_In           12
#DEFINE TiCo_Trigger_Out          13 
#DEFINE TiCo_Trigger_Count        14
#DEFINE TiCo_Trigger_In_Pattern   15

INIT:
  
  Processdelay = 1000

  P2_TDrv_Init(DIO_MODULE, 1, tdrv_datatable)
  P2_TiCo_Stop(2 ^ DIO_MODULE)
  
  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  
  P2_Set_Par(DIO_MODULE, 1, TiCo_Enable, 0)
  
  P2_Set_Par(DIO_MODULE, 1, TiCo_Delay, 0) ' waiting time of 200 ns
  P2_Set_Par(DIO_MODULE, 1, TiCo_Trigger_In, 21)
  P2_Set_Par(DIO_MODULE, 1, TiCo_Trigger_In_Pattern, 2 ^ 21)
  P2_Set_Par(DIO_MODULE, 1, TiCo_Trigger_Out, 12)
  
  P2_TiCo_Start(2 ^ DIO_MODULE)
  P2_TiCo_Start_Process(tdrv_datatable, 1)
  
EVENT:
  
  Par_1 = P2_Get_Par(DIO_MODULE, 1, TiCo_Enable)
  Par_2 = P2_Get_Par(DIO_MODULE, 1, TiCo_Trigger_Count)
  
  If (Par_1 < 1) Then
    P2_Set_Par(DIO_MODULE, 1, TiCo_Enable, 1)
  EndIf
  
