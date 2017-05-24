'<ADbasic Header, Headerversion 001.001>
'<Header End>
' Control functions for the TiCo/EDU delay line

' TiCo parameter addresses used for communication
#DEFINE TiCoDL_Enable               10
#DEFINE TiCoDL_Delay                11
#DEFINE TiCoDL_Trigger_In           12
#DEFINE TiCoDL_Trigger_Out          13 
#DEFINE TiCoDL_Trigger_Count        14
#DEFINE TiCoDL_Trigger_In_Pattern   15
#DEFINE TiCoDL_IrrelevantDetections 16
#DEFINE TiCoDL_ShortDelayErrors     17
#DEFINE TiCoDL_Started              18

#DEFINE dl_cycle_duration           20.0e-9

' holds the settings for communication between ADwin CPU and TiCo processor
' is filled automatically by the TiCo initialization command
DIM tdrv_datatable[150] AS LONG 
DIM TiCo_DIO_MODULE AS LONG

SUB tico_delay_line_init(DIO_MODULE, delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_trigger_DO_channel)
  TiCo_DIO_MODULE = DIO_MODULE
  P2_TiCo_Restart(2 ^ TiCo_DIO_MODULE)
  P2_TDrv_Init(TiCo_DIO_MODULE, 1, tdrv_datatable)
  P2_TiCo_Stop_Process(tdrv_datatable, 1)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Enable, 0)  
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Delay, 0)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Trigger_In, delay_trigger_DI_channel)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Trigger_In_Pattern, delay_trigger_DI_pattern)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Trigger_Out, delay_trigger_DO_channel)
  P2_TiCo_Start_Process(tdrv_datatable, 1)
ENDSUB

SUB tico_delay_line_finish()
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Enable, 0)
  P2_TiCo_Stop_Process(tdrv_datatable, 1)
ENDSUB

SUB tico_delay_line_set_cycles(input_cycles)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Delay, input_cycles)
ENDSUB

SUB tico_delay_line_set_delay(input_delay) ' input_delay in seconds
  tico_delay_line_set_cycles(tico_delay_line_calculate_cycles(input_delay))
ENDSUB


SUB tico_delay_line_set_enabled(input_enabled)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Enable, input_enabled)
ENDSUB

FUNCTION tico_delay_line_calculate_cycles(input_delay) AS LONG
  DIM excess_delay AS FLOAT
  DIM corrected_cycles AS LONG
  excess_delay = input_delay - minimal_delay_time
  tico_delay_line_calculate_cycles = Round(excess_delay / dl_cycle_duration) + minimal_delay_cycles
ENDFUNCTION

FUNCTION tico_delay_line_calculate_delay(input_cycles) AS LONG
  tico_delay_line_calculate_delay = (input_cycles - minimal_delay_cycles) * dl_cycle_duration + minimal_delay_time
ENDFUNCTION




