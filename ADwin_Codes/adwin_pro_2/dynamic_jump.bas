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
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
'<Header End>
#Include ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\djump_tico_helper.inc

DIM DATA_20[100] AS LONG

DIM AWG_start_DO_channel, AWG_done_DI_channel, AWG_done_DI_pattern AS LONG
DIM AWG_done AS LONG

DIM delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_strobe_DO_channel AS LONG

DIM cycle_duration AS LONG
Dim timer As Long
Dim current_sequence AS LONG

Init:
  cycle_duration            = DATA_20[1]
  AWG_start_DO_channel      = DATA_20[2]
  AWG_done_DI_channel       = DATA_20[3]
  delay_trigger_DI_channel  = DATA_20[4]
  delay_strobe_DO_channel   = DATA_20[5]
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  delay_trigger_DI_pattern = 2 ^ delay_trigger_DI_channel
  
  Processdelay = cycle_duration ' Clock cycle in units of 1 ns
  timer = 0
  current_sequence = 1
  AWG_done = 0
  
  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  
  tico_delay_line_init(DIO_MODULE, delay_trigger_DI_pattern, delay_strobe_DO_channel)
  tico_set_jump_and_delays(1)
  
  ' Trigger AWG
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
  CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
Event:
  Inc(timer)
  Par_20 = timer
  
  '  IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN
  '    IF (AWG_done = 0) THEN
  '      AWG_done = 1
  '      
  '      current_sequence = get_next_sequence(current_sequence)
  '      'tico_set_jump_and_delays(current_sequence)
  '      ' Do some measurements
  '    ELSE
  '      'tico_start_delay_line()
  '      AWG_done = 0
  '    ENDIF
  '  ENDIF
  
Finish:
  tico_delay_line_finish()
