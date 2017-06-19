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
#DEFINE TiCoDL_Awake                19
#DEFINE TiCoDL_NoDelaySetErrors     20

#DEFINE TiCoDL_ParBuffer_WritePtr_Idx       38
#DEFINE TiCoDL_ParBuffer_ReadPtr_Idx        39
#DEFINE TiCoDL_ParBuffer_Start_Idx          41

#DEFINE dl_cycle_duration           20.0e-9

' holds the settings for communication between ADwin CPU and TiCo processor
' is filled automatically by the TiCo initialization command
DIM tdrv_datatable[150] AS LONG 
DIM TiCo_DIO_MODULE AS LONG
DIM TiCo_ParBuffer_WritePtr AS LONG

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
  
  tico_delay_reset_buffer()
  
  P2_TiCo_Start_Process(tdrv_datatable, 1)
ENDSUB

SUB tico_delay_reset_buffer()
  TiCo_ParBuffer_WritePtr = TiCoDL_ParBuffer_Start_Idx
  P2_Set_Par(TiCo_DIO_Module, 1, TiCoDL_ParBuffer_WritePtr_Idx, TiCoDL_ParBuffer_Start_Idx)
  P2_Set_Par(TiCo_DIO_Module, 1, TiCoDL_ParBuffer_ReadPtr_Idx, TiCoDL_ParBuffer_Start_Idx)
ENDSUB


SUB tico_delay_line_finish()
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Enable, 0)
  P2_TiCo_Stop_Process(tdrv_datatable, 1)
ENDSUB

SUB tico_delay_line_set_cycles(input_cycles, num_delays)
  DIM loopidx AS LONG
  DIM delay_cycles_array[20] AS LONG AT DM_LOCAL
  
  ' beautifully ugly loop unwindification; should be much faster though (3 cycles per element instead of ~17-ish in a for loop)
  SelectCase num_delays
    CCase 20
      delay_cycles_array[20] = input_cycles
    CCase 19
      delay_cycles_array[19] = input_cycles
    CCase 18
      delay_cycles_array[18] = input_cycles
    CCase 17
      delay_cycles_array[17] = input_cycles
    CCase 16
      delay_cycles_array[16] = input_cycles
    CCase 15
      delay_cycles_array[15] = input_cycles
    CCase 14
      delay_cycles_array[14] = input_cycles
    CCase 13
      delay_cycles_array[13] = input_cycles
    CCase 12
      delay_cycles_array[12] = input_cycles
    CCase 11
      delay_cycles_array[11] = input_cycles
    CCase 10
      delay_cycles_array[10] = input_cycles
    CCase 9
      delay_cycles_array[9] = input_cycles
    CCase 8
      delay_cycles_array[8] = input_cycles
    CCase 7
      delay_cycles_array[7] = input_cycles
    CCase 6
      delay_cycles_array[6] = input_cycles
    CCase 5
      delay_cycles_array[5] = input_cycles
    CCase 4
      delay_cycles_array[4] = input_cycles
    CCase 3
      delay_cycles_array[3] = input_cycles
    CCase 2
      delay_cycles_array[2] = input_cycles
    CCase 1
      delay_cycles_array[1] = input_cycles
  EndSelect
  
  timer_tic()
  tico_delay_line_set_cycles_array(delay_cycles_array, num_delays)
  timer_toc()
ENDSUB

SUB tico_delay_line_set_cycles_array(input_cycles_array[], num_delays)
  ' P2_SetData_Long(tdrv_datatable, TiCoDL_LinearBuffer_Idx, TiCo_LinearBuffer_WritePtr, num_delays, input_cycles_array, 1, 3) ' takes 410-450 cycles (!!)
  timer_tic()
  P2_Set_Par_Block(TiCo_DIO_Module, 1, input_cycles_array, 1, TiCo_ParBuffer_WritePtr, num_delays)
  timer_toc()
  TiCo_ParBuffer_WritePtr = TiCo_ParBuffer_WritePtr + num_delays
  P2_Set_Par(TiCo_DIO_Module, 1, TiCoDL_ParBuffer_WritePtr_Idx, TiCo_ParBuffer_WritePtr)
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

FUNCTION tico_delay_line_calculate_delay(input_cycles) AS FLOAT
  tico_delay_line_calculate_delay = (input_cycles - minimal_delay_cycles) * dl_cycle_duration + minimal_delay_time
ENDFUNCTION




