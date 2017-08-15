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
' Please note:

' This script should solely be used as an initialization for other scripts using a TiCo controlled pulsar sequence
' See the other scripts, djump_tico_helper.inc and dynamic_jump_tico.bas (TiCo file) for a complete overview
'
' Still needs some changes though

#Include ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\djump_tico_helper.inc

DIM DATA_20[100] AS LONG

DIM AWG_start_DO_channel,AWG_jump_strobe_DO_channel AS LONG

DIM cycle_duration AS LONG
Dim timer As Long
Dim current_sequence AS LONG
Dim mode, do_init_only as long
Dim cur_rnd_idx AS LONG
Dim current_index AS LONG

LowInit:
  cycle_duration            = DATA_20[1]
  AWG_start_DO_channel      = DATA_20[2]
  AWG_jump_strobe_DO_channel= DATA_20[3]
  do_init_only              = Data_20[4]
  jump_bit_shift            = Data_20[5]
  
  Processdelay = cycle_duration ' Clock cycle in units of 1 ns
  
  'P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  'P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  
  current_sequence = 1
  tico_delay_line_init(AWG_start_DO_channel, AWG_jump_strobe_DO_channel)
  
  If (do_init_only = 1) Then 
    mode = 99
  else
    tico_set_jump_and_delays(current_sequence)
    mode = 1
  endif
  
Event:
  
  Selectcase mode
    case 1
      ' Enable the TICO!
      tico_start_sequence()   
      END
      
    case 2
      ' Check if TICO still running
      If (is_sequence_running() = 0) THEN ' Finished!!
        tico_delay_line_finish()
        END
      ENDIF
      
    case 99
      END
      
  endselect
  
Finish:
