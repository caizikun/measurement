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

'init general settings
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

'init delay voltages per sweep
DIM DATA_40[max_sweep] AS FLOAT


DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM sweep_length AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG
DIM delay_voltage_DAC_channel, do_delay_voltage_control AS LONG

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
  delay_voltage_DAC_channel    = DATA_20[7]
  do_delay_voltage_control     = DATA_20[8] 
   
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel

  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0

  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

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
      
    IF (do_delay_voltage_control > 0) THEN
      P2_DAC_2(delay_voltage_DAC_channel, 3277*DATA_40[sweep_index]+32768)
    ENDIF
      
    inc(sweep_index)
    if (sweep_index > sweep_length) then
      sweep_index = 1
    endif
      
    INC(repetition_counter)
    Par_73 = repetition_counter
  endif
  
  
FINISH:
  P2_DAC_2(delay_voltage_DAC_channel, 3277*0+32768)
    
  

