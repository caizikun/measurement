'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = No
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\..\adwin_pro_2\configuration.inc
#INCLUDE .\..\adwin_pro_2_lt2\cr_mod_dummy.inc
#INCLUDE .\..\adwin_pro_2_lt2\control_tico_delay_line.inc
'#INCLUDE .\cr.inc
'#INCLUDE .\cr_mod_Bell.inc
#INCLUDE math.inc

#define dx_data_array    DATA_1
#define dm_data_array    DATA_2
#define em_data_array    DATA_3
#define dx_data_array_2    DATA_11
#define dm_data_array_2    DATA_12
#define em_data_array_2    DATA_13
#define arr_length    100

DIM dx_data_array[100] AS LONG AT DRAM_EXTERN
DIM dm_data_array[100] AS LONG AT DM_LOCAL
DIM em_data_array[100] AS LONG AT EM_LOCAL

DIM dx_data_array_2[100] AS LONG AT DRAM_EXTERN
DIM dm_data_array_2[100] AS LONG AT DM_LOCAL
DIM em_data_array_2[100] AS LONG AT EM_LOCAL

DIM dm_local_array[arr_length] AS LONG AT DM_LOCAL
DIM em_local_array[arr_length] AS LONG AT EM_LOCAL
DIM dx_local_array[200] AS LONG AT DRAM_EXTERN

DIM dx_long_var AS LONG AT DRAM_EXTERN
DIM dm_long_var AS LONG AT DM_LOCAL
DIM em_long_var AS LONG AT EM_LOCAL

DIM dx_long_var_2 AS LONG AT DRAM_EXTERN
DIM dm_long_var_2 AS LONG AT DM_LOCAL
DIM em_long_var_2 AS LONG AT EM_LOCAL

DIM i as long at DM_LOCAL


DIM l1, l2, l3 AS LONG AT DM_LOCAL
DIM f1, f2, f3 AS FLOAT AT DM_LOCAL

DIM fl_arr[10] AS FLOAT AT DM_LOCAL

SUB timer_tic()
  Par_38 = Read_Timer()
  Par_39 = Read_Timer()
ENDSUB

SUB timer_toc()
  Par_40 = Read_Timer()
  Par_41 = Par_40 - Par_39 - (Par_39 - Par_38) ' correct for the duration of the Read_Timer() call
ENDSUB

INIT:
  processdelay = 300
  l1 = 1
  l2 = 1
  l3 = 1
  f1 = 1
  f2 = 1
  f3 = 1
  
EVENT:
  fl_arr[1] = fl_arr[2] + fl_arr[3]
  
  Par_1 = 11
  Par_2 = 3
  
  timer_tic()
  f1 = f2 / f3
  timer_toc()
  
FINISH:
  Par_2 = 1
