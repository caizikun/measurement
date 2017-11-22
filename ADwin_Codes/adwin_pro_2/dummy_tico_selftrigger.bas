'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
' this program implements single-shot readout fully controlled by ADwin Gold II
'
' protocol:
' mode  0:  CR check
' mode  2:  spin pumping with Ex or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with Ex or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  Ex pulse and photon counting for spin-readout with time dependence
'           -> mode 1

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

#DEFINE max_SP_bins        500
#DEFINE max_stat            10
#DEFINE max_sweep           500000

' TiCo parameter addresses used for communication
#DEFINE TiCo_Enable               10
#DEFINE TiCo_Delay                11
#DEFINE TiCo_Trigger_In           12
#DEFINE TiCo_Trigger_Out          13 
#DEFINE TiCo_Trigger_Count        14
#DEFINE TiCo_Trigger_In_Pattern   15
#DEFINE TiCo_IrrelevantDetections 16
#DEFINE TiCo_ShortDelayErrors     17

'init general settings
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

'init delay voltages per sweep
DIM DATA_41[max_sweep] AS LONG


DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM sweep_length AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG
DIM do_tico_delay_control, delay_trigger_DI_channel, delay_trigger_DI_pattern, delay_trigger_DO_channel AS LONG
' holds the settings for communication between ADwin CPU and TiCo processor
' is filled automatically by the TiCo initialization command
DIM tdrv_datatable[150] AS LONG 

DIM timer, aux_timer, mode, i, sweep_index AS LONG
DIM AWG_done AS LONG
DIM first AS LONG

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts AS LONG

INIT:  
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  send_AWG_start               = DATA_20[3]
  wait_for_AWG_done            = DATA_20[4]
  cycle_duration               = DATA_20[5] '(in processor clock cycles, 3.333ns)
  sweep_length                 = DATA_20[6]
  do_tico_delay_control        = DATA_20[7]
  delay_trigger_DI_channel     = DATA_20[8]
  delay_trigger_DO_channel     = DATA_20[9]
   
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel
  delay_trigger_DI_pattern = 2 ^ delay_trigger_DI_channel

  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0

  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
  
  ' set up tico delay control
  IF (do_tico_delay_control > 0) THEN
    P2_TiCo_Restart(2 ^ DIO_MODULE)
    P2_TDrv_Init(DIO_MODULE, 1, tdrv_datatable)
    P2_TiCo_Stop_Process(tdrv_datatable, 1)
    P2_Set_Par(DIO_MODULE, 1, TiCo_Enable, 0)  
    P2_Set_Par(DIO_MODULE, 1, TiCo_Delay, 0)
    P2_Set_Par(DIO_MODULE, 1, TiCo_Trigger_In, delay_trigger_DI_channel)
    P2_Set_Par(DIO_MODULE, 1, TiCo_Trigger_In_Pattern, delay_trigger_DI_pattern)
    P2_Set_Par(DIO_MODULE, 1, TiCo_Trigger_Out, delay_trigger_DO_channel)
    P2_TiCo_Start_Process(tdrv_datatable, 1)
  ENDIF

  sweep_index = 1
  mode = 0
  timer = 0
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter

EVENT:
  PAR_80 = timer
  INC(timer)
    
  IF (timer = 1000000) THEN
    timer = 0
      
    IF (do_tico_delay_control > 0) THEN
      Par_11 = DATA_41[sweep_index]
      P2_Set_Par(DIO_MODULE, 1, TiCo_Delay, DATA_41[sweep_index])
      P2_Set_Par(DIO_MODULE, 1, TiCo_Enable, 1)
    ENDIF
      
    inc(sweep_index)
    if (sweep_index > sweep_length) then
      sweep_index = 1
    endif
      
    INC(repetition_counter)
    Par_73 = repetition_counter
  endif
  
  
FINISH:
  IF (do_tico_delay_control > 0) THEN
    P2_Set_Par(DIO_MODULE, 1, TiCo_Enable, 0)
    P2_TiCo_Stop_Process(tdrv_datatable, 1)
  ENDIF
  

