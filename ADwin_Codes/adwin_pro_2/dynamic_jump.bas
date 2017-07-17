'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
'<Header End>
#Include ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\djump_tico_helper.inc

DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT  ' float parameters from python

DIM AWG_start_DO_channel,AWG_jump_strobe_DO_channel AS LONG

DIM cycle_duration AS LONG
Dim timer As Long
Dim current_sequence AS LONG
Dim mode, do_init_only, tico_running as long

LowInit:
  cycle_duration            = DATA_20[1]
  AWG_start_DO_channel      = DATA_20[2]
  AWG_jump_strobe_DO_channel = DATA_20[3]
  do_init_only              = Data_20[4]
  
  Processdelay = cycle_duration ' Clock cycle in units of 1 ns
  ' The above line crashes when pressing F8
  timer = 0
  current_sequence = 1
  
  'P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  'P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  
  tico_delay_line_init(DIO_MODULE, AWG_start_DO_channel, AWG_jump_strobe_DO_channel)
  
  If (do_init_only = 1) Then 
    mode  = 99
  else
    mode = 1
  endif
  
Event:
  
  Selectcase mode
    case 1
      ' Enable the TICO!
      P2_Set_Par(DIO_MODULE, 1, TiCoDL_Enable, 1)            
      mode = 2
      
    case 2
      ' Check if TICO still running
      Tico_Running = P2_Get_Par(DIO_MODULE, 1, TiCoDL_Enable)
      If (Tico_Running = 0) THEN ' Finished!!
      ENDIF
      
    case 99
      tico_delay_line_finish()
      END
      
  endselect
  
  Inc(timer)
  
  
Finish:
  
