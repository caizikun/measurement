'<ADbasic Header, Headerversion 001.001>
'<Header End>
' Control functions for the TiCo/EDU delay line

#INCLUDE ..\adwin_pro_2\configuration.inc
#INCLUDE Math.inc

' TiCo parameter addresses used for communication
#DEFINE TiCoDL_Enable               10
#DEFINE TiCoDL_Jump_Bit_Shift       11
#DEFINE TiCoDL_AWG_start_DO_channel        12
#DEFINE TiCoDL_jump_strobe_DO_channel      13
#DEFINE TiCoDL_Awake                 19
#DEFINE TiCoDL_max_index             26

' TiCo global data indices
#DEFINE TiCo_Jump_Table     1
#DEFINE TiCo_Delay_Cycles   2

#Define Rands_Size 10000000

#Define jump_table Data_100
#Define delay_cycles Data_101
#Define next_table Data_102
#Define seq_indices Data_103

#Define random_jumps Data_110

' holds the settings for communication between ADwin CPU and TiCo processor
' is filled automatically by the TiCo initialization command
DIM tdrv_datatable[150] AS LONG

' Constants for correct output
DIM jump_bit_shift AS LONG

DIM do_random_gates AS LONG ' Fill the jump table with random jumps instead
DIM rand_jump_factor AS LONG
DIM rand_jump_index AS LONG

DIM dummy_index AS LONG

DIM DATA_100[1000000] AS LONG
DIM DATA_101[1000000] AS LONG
DIM DATA_102[10000] AS LONG
DIM DATA_103[10000] AS LONG

DIM Data_110[Rands_Size] As Long At DRAM_Extern ' random jumps

SUB tico_delay_line_init(AWG_start_DO_channel, AWG_jump_strobe_DO_channel)  
  P2_TiCo_Restart(2 ^ DIO_MODULE)
  P2_TDrv_Init(DIO_MODULE, 1, tdrv_datatable)
  P2_TiCo_Stop_Process(tdrv_datatable, 1)
  P2_Set_Par(DIO_MODULE, 1, TiCoDL_jump_strobe_DO_channel, AWG_jump_strobe_DO_channel)
  P2_Set_Par(DIO_MODULE, 1, TiCoDL_AWG_start_DO_channel, AWG_start_DO_channel)
  P2_Set_Par(DIO_MODULE, 1, TiCoDL_Jump_Bit_Shift, jump_bit_shift)
  P2_TiCo_Start_Process(tdrv_datatable, 1)
  
  ' Wait until the TiCo is done initializing
  DO
    CPU_SLEEP(100)
  UNTIL (P2_Get_Par(DIO_MODULE, 1, TiCoDL_Awake) > 0)
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
  Dim start_index, end_index, length As Long
  start_index = seq_indices[seq_index] ' inclusive
  end_index = seq_indices[seq_index + 1] ' exclusive
  length = end_index - start_index
  
  P2_Set_Par(DIO_MODULE, 1, TiCoDL_max_index, length)
  P2_SetData_Long(tdrv_datatable, TiCo_Jump_Table, 1, length, jump_table, start_index, 3)
  P2_SetData_Long(tdrv_datatable, TiCo_Delay_Cycles, 1, length, delay_cycles, start_index, 3)
ENDSUB

SUB randomize_jumps(seq_index)
  Dim start_index, end_index As Long
  start_index = seq_indices[seq_index] ' inclusive
  end_index = seq_indices[seq_index + 1] - 1 ' inclusive
  
  For dummy_index = start_index To end_index
    jump_table[dummy_index] = random_jumps[rand_jump_index]
    
    rand_jump_index = rand_jump_index + rand_jump_factor
    
    If (rand_jump_index > Rands_Size) Then
      rand_jump_index = Max_Long(Mod(rand_jump_index, Rands_Size), 1) ' reset
      Inc(rand_jump_factor)
    EndIf
    
  Next dummy_index
ENDSUB

SUB tico_start_sequence()
  P2_Set_Par(DIO_MODULE, 1, TiCoDL_Enable, 1)
ENDSUB

Function is_sequence_running() As Long
  is_sequence_running = P2_Get_Par(DIO_MODULE, 1, TiCoDL_Enable)
EndFunction
