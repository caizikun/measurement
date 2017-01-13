'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277562  DASTUD\TUD277562
'<Header End>
' This program is used for fast scans of the fine-tuning JPE piezos.
' Read-out can be performed either with counter or photodiode (NOT YET IMPLEMENTED!!!)
' This version waits for a trigger from the Montana Sync signal, to 
' synchronize measurements on the cryostat cooling cycle
' 
'C. Bonato (cbonato80@gmail.com)
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM fpz1_DAC_ch, fpz2_DAC_ch, fpz3_DAC_ch as long
DIM pd_ADC_ch, pd_ref_ADC_ch, nr_steps, use_counter, counts AS long
DIM start_voltage_1, start_voltage_2, start_voltage_3 as float
DIM step_size, curr_volt_1, curr_volt_2, curr_volt_3 AS FLOAT
DIM DAC_binary_voltage, ADC_binary_voltage, ADC_binary_voltage_ref, APD_int_time as integer
DIM counter_channel, counter_pattern, montana_sync_ch, sync_pattern AS LONG
DIM sweep_idx, curr_scan, nr_scans, delay, trigger, t0, t1, idle_timer, t1_wait, t0_wait AS LONG
'settings values passed from python:
DIM DATA_200[10] as long
DIM DATA_199[8] as float 'voltages: start, stop, stepsize
'output data:
DIM DATA_11[300000] AS FLOAT 'photodiode voltage (signal)
DIM DATA_12[10000] AS LONG 'time-stamps scans

dim timer, mode, curr_step, i, wait_cycles as integer

INIT:
    
  start_voltage_1 = DATA_199[1]
  start_voltage_2 = DATA_199[2]
  start_voltage_3 = DATA_199[3]
  step_size       = DATA_199[4]
  
  fpz1_DAC_ch     = DATA_200[1] 'fine-tuning piezo jpe channel
  fpz2_DAC_ch     = DATA_200[2]
  fpz3_DAC_ch     = DATA_200[3]
  pd_ADC_ch       = DATA_200[4] 'photodiode ADC channel (signal)
  montana_sync_ch = DATA_200[5] 'digital input channel (Montana sync trigger)
  nr_steps        = DATA_200[6]
  nr_scans        = DATA_200[7]
  wait_cycles     = DATA_200[8]
  delay           = DATA_200[9] 'dealy after trigger (microseconds)
  
  
  'Set initial DAC voltages
  P2_DAC(DAC_Module, fpz1_DAC_ch, start_voltage_1 * 3276.8 + 32768)
  P2_DAC(DAC_Module, fpz2_DAC_ch, start_voltage_2 * 3276.8 + 32768)
  P2_DAC(DAC_Module, fpz3_DAC_ch, start_voltage_3 * 3276.8 + 32768)
  
  curr_volt_1 = start_voltage_1
  curr_volt_2 = start_voltage_2
  curr_volt_3 = start_voltage_3
     
  'init data array
  FOR i = 1 TO nr_steps*nr_scans
    DATA_11[i] = 0
  NEXT i
  
  FOR i = 1 TO nr_scans
    DATA_12[i] = 0
  NEXT i

  P2_SE_Diff(ADC_module,0) 'sets ADCs to be used as single-ended (default is differential)
  counter_pattern     = 2 ^ (counter_channel-1)
  P2_CNT_ENABLE(CTR_MODULE,0000b) 'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter
  P2_Digprog(DIO_MODULE,0011b)      '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  sync_pattern = 2^montana_sync_ch
  
  timer = -1
  mode = 0
  curr_step = 1
  curr_scan = 0
  trigger = 0
  sweep_idx = 0
  idle_timer = 0
  
  
EVENT:
  Par_57 = mode
  Par_58 = curr_scan
  Par_59 = curr_step
  Par_60 = sweep_idx
  Par_50 = nr_scans
  Par_51= nr_steps
  Inc(timer)

  SELECTCASE mode:
      
    CASE 0 'check if trigger low, else wait
      trigger = ((P2_DIGIN_Long(DIO_Module)) AND sync_pattern)
      inc (idle_timer)
      if (idle_timer>1000000) then
        DATA_12[1] = 0
        end
      endif
      if (trigger=0) then
        mode = 1
      else
        mode = 0
      endif
         
    CASE 1 'wait for trigger
      trigger = ((P2_DIGIN_Long(DIO_Module)) AND sync_pattern)
      inc (idle_timer)
      if (idle_timer>1000000) then
        DATA_12[1] = 0
        end
      endif

      if (trigger>0) then
        mode = 2
        t0 = ReadTimer()
      else
        mode = 1
      endif
       
    CASE 2 'wait requested delay
      t1 = ReadTimer()-t0
      if (t1>=delay) then
        PAR_49 = delay
        mode = 3
      endif
      
    CASE 3 'new piezo scan  
    
      curr_step = 1
      inc(curr_scan)
      curr_volt_1 = start_voltage_1 
      curr_volt_2 = start_voltage_2 
      curr_volt_3 = start_voltage_3 
      P2_DAC(DAC_Module, fpz1_DAC_ch, curr_volt_1 * 3276.8 + 32768)
      P2_DAC(DAC_Module, fpz2_DAC_ch, curr_volt_2 * 3276.8 + 32768)
      P2_DAC(DAC_Module, fpz3_DAC_ch, curr_volt_3 * 3276.8 + 32768)
      t1 = ReadTimer()
      DATA_12[curr_scan+1] = t1-t0
      if (curr_scan>nr_scans) then
        DATA_12[1] = 1
        end
      else
        mode = 10
        t0_wait = ReadTimer()
      endif     
      
    CASE 10 'wait for piezo to restore to init position 
      t1_wait = ReadTimer()
      if (t1_wait-t0_wait > 333000) then
        mode = 4
      endif
      
      
    CASE 4 'read-out photodiode voltage
      if (timer>=0) then
        adc_binary_voltage = P2_ADC (ADC_module, pd_ADC_ch)
        inc(sweep_idx)
        DATA_11[sweep_idx] = (adc_binary_voltage-32768)/3276.8
        DATA_12[sweep_idx] = (adc_binary_voltage_ref-32768)/3276.8
        FPar_51 = DATA_11[sweep_idx]
        Par_5 = curr_step
        Par_6 = pd_ADC_ch
        mode = 5
        timer = -1
      endif
      
    CASE 5 'set laser-scan voltage
      if (timer>=0) then
        P2_DAC(DAC_Module, fpz1_DAC_ch, curr_volt_1 * 3276.8 + 32768)
        P2_DAC(DAC_Module, fpz2_DAC_ch, curr_volt_2 * 3276.8 + 32768)
        P2_DAC(DAC_Module, fpz3_DAC_ch, curr_volt_3 * 3276.8 + 32768)
        FPar_50 = curr_volt_1
        timer = -wait_cycles
        mode = 4
        inc(curr_step)
        curr_volt_1 = curr_volt_1 + step_size
        curr_volt_2 = curr_volt_2 + step_size
        curr_volt_3 = curr_volt_3 + step_size
        if (curr_step>nr_steps) then
          mode = 3
        endif
      endif    
  ENDSELECT

FINISH:  
  Par_49 = 0  'tell resonant counting process to stop summing its data into par 45-48  
