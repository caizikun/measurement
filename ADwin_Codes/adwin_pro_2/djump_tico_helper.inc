'<ADbasic Header, Headerversion 001.001>
'<Header End>
' Control functions for the TiCo/EDU delay line

' TiCo parameter addresses used for communication
#DEFINE TiCoDL_Enable               10
#DEFINE TiCoDL_Jump_Bit_Shift       11
#DEFINE TiCoDL_AWG_start_DO_channel        12
#DEFINE TiCoDL_jump_strobe_DO_channel      13
#DEFINE TiCoDL_Awake                 19

#DEFINE TiCo_Jump_Table     1
#DEFINE TiCo_Delay_Cycles   2

#Define TDIM 256 ' # jump table dimensions
#Define JUMP_BIT_SHIFT 4

#DEFINE max_element Shift_Left(15, Jump_Bit_Shift)

#Define jump_table Data_100
#Define delay_cycles Data_101
#Define next_table Data_102

' holds the settings for communication between ADwin CPU and TiCo processor
' is filled automatically by the TiCo initialization command
DIM tdrv_datatable[150] AS LONG 
DIM TiCo_DIO_MODULE AS LONG
DIM TiCo_Strobe_Channel AS LONG

DIM DATA_100[65536] AS LONG
DIM DATA_101[65536] AS LONG
DIM DATA_102[512] AS LONG

SUB tico_delay_line_init(DIO_MODULE, AWG_start_DO_channel, AWG_jump_strobe_DO_channel)
  TiCo_DIO_MODULE = DIO_MODULE
  P2_TiCo_Restart(2 ^ TiCo_DIO_MODULE)
  P2_TDrv_Init(TiCo_DIO_MODULE, 1, tdrv_datatable)
  P2_TiCo_Stop_Process(tdrv_datatable, 1)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_jump_strobe_DO_channel, AWG_jump_strobe_DO_channel)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_AWG_start_DO_channel, AWG_start_DO_channel)
  P2_Set_Par(TiCo_DIO_MODULE, 1, TiCoDL_Jump_Bit_Shift, JUMP_BIT_SHIFT)
  P2_TiCo_Start_Process(tdrv_datatable, 1)
  
  ' Wait until the TiCo is done initializing
  DO
    CPU_SLEEP(100)
  UNTIL (P2_Get_Par(TiCo_DIO_MODULE, 1, TiCoDL_Awake) > 0)
ENDSUB

SUB tico_delay_line_finish()
  P2_TiCo_Stop_Process(tdrv_datatable, 1)
ENDSUB

Function get_next_sequence(seq_index) As Long
  Dim return_index As Long 
  return_index = 2 * seq_index - 1
  get_next_sequence = next_table[return_index]
EndFunction

SUB tico_set_jump_and_delays(seq_index)
  Dim start_index As Long
  start_index = TDIM * (seq_index - 1) + 1
  P2_SetData_Long(tdrv_datatable, TiCo_Jump_Table, 1, TDIM, jump_table, start_index, 3)
  P2_SetData_Long(tdrv_datatable, TiCo_Delay_Cycles, 1, TDIM, delay_cycles, start_index, 3)
ENDSUB

