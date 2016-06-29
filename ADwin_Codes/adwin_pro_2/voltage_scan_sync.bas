'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277562  DASTUD\TUD277562
'<Header End>
' This program is used for fast voltage scans (fine-tuning JPE piezos, laser frequency).
' It includes the option to wait for a trigger from the Montana Sync signal, to 
' synchronize measurements on the cryostat cooling cycle
' 
'C. Bonato (cbonato80@gmail.com)
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE Math.inc

' scan settings
DIM DAC_ch_1, DAC_ch_2, DAC_ch_3 as long
DIM pd_ADC_ch, pd_ref_ADC_ch, nr_steps, ADC_averaging_cycles AS long
DIM start_volt1, start_volt2, start_volt3, end_volt1, end_volt2, end_volt3 as float
DIM step_size, curr_volt_1, curr_volt_2, curr_volt_3 AS FLOAT
DIM DAC_binary_voltage, ADC_binary_voltage, ADC_binary_voltage_ref as integer
DIM ADC_average_voltage AS FLOAT
DIM use_sync, sync_ch, sync_pattern,scan_reverse AS LONG
DIM sweep_idx, curr_scan, curr_scan_mod2,nr_scans, delay, trigger, t0, t1, idle_timer, t1_wait, t0_wait AS LONG
'settings values passed from python:
DIM DATA_20[100] as long
DIM DATA_21[100] as float 'voltages: start, stop, stepsize
'output data:
DIM DATA_11[300000] AS FLOAT 'photodiode voltage (signal)
DIM DATA_12[10000] AS LONG 'time-stamps scans
DIM DATA_13[300000] AS FLOAT ' wavemeter signal [GHz]

dim timer, mode, curr_step, i, wait_cycles as integer

INIT:
    

  
  DAC_ch_1     = DATA_20[1] '0 = inactive
  DAC_ch_2     = DATA_20[2] '0 = inactive
  DAC_ch_3     = DATA_20[3] '0 = inactive
  pd_ADC_ch    = DATA_20[4] 'photodiode ADC channel (signal)
  use_sync     = DATA_20[5] 'use sync signal from Montana (0 = False, 1 = True)
  sync_ch      = DATA_20[6] 'digital input channel (Montana sync trigger)
  nr_steps     = DATA_20[7]
  nr_scans     = DATA_20[8]
  wait_cycles  = DATA_20[9]
  delay        = DATA_20[10] 'delay after trigger (microseconds)
  ADC_averaging_cycles = DATA_20[11]
  scan_reverse = DATA_20[12] 
 
  start_volt1 = DATA_21[1]
  start_volt2 = DATA_21[2]
  start_volt3 = DATA_21[3]
  step_size   = DATA_21[4]
  
  'Set initial DAC voltages
  if (DAC_ch_1 > 0) then
    P2_DAC(DAC_Module, DAC_ch_1, start_volt1 * 3276.8 + 32768)
  endif
  if (DAC_ch_2 > 0) then
    P2_DAC(DAC_Module, DAC_ch_2, start_volt2 * 3276.8 + 32768)
  endif
  if (DAC_ch_3 > 0) then
    P2_DAC(DAC_Module, DAC_ch_3, start_volt3 * 3276.8 + 32768)
  endif
  
  curr_volt_1 = start_volt1
  curr_volt_2 = start_volt2
  curr_volt_3 = start_volt3
  end_volt1 = start_volt1+step_size*nr_steps 'calculate the end voltages
  end_volt2 = start_volt2+step_size*nr_steps
  end_volt3 = start_volt3+step_size*nr_steps
  
     
  'init data array
  FOR i = 1 TO nr_steps*nr_scans
    DATA_11[i] = 0
    DATA_13[i] = 0
  NEXT i
  
  FOR i = 1 TO nr_scans+1
    DATA_12[i] = 0
  NEXT i

  P2_SE_Diff(ADC_module,0)        'sets ADCs to be used as single-ended (default is differential)
  P2_Digprog(DIO_MODULE,0011b)    '31:24 DI, 23:16 DI, 15:08 DO 07:00 DO
  sync_pattern = 2^sync_ch
  
  timer = -1
  trigger = 0
  curr_step = 1
  curr_scan = 0
  'step_size = -step_size 'reverse the step size. for every new scan the step_size will be reversed to scan up->down and back
  if (use_sync > 0) then
    mode = 0
  else
    mode = 3
  endif
  sweep_idx = 0
  idle_timer = 0
  t0 = ReadTimer()
  
EVENT:

  Par_50 = nr_scans
  Par_51 = nr_steps
  Par_52 = mode
  Par_53 = curr_scan
  Par_54 = curr_step
  Par_55 = sweep_idx
  FPar_52 = step_size
  FPar_53 =  curr_volt_1
  Par_56 = DAC_ch_1 
  
  Inc(timer)

  SELECTCASE mode:
      
    CASE 0 'check if sync signal is low, else wait
      trigger = ((P2_DIGIN_Long(DIO_Module)) AND sync_pattern)
      inc (idle_timer)

      if (trigger=0) then
        mode = 1
      else
        mode = 0
      endif
      
      'If no low signal for 3,3 sec, abort
      if (idle_timer>3300000) then
        DATA_12[1] = 0 
        end
      endif
      
         
    CASE 1 'wait for trigger
      trigger = ((P2_DIGIN_Long(DIO_Module)) AND sync_pattern)
      inc (idle_timer)

      if (trigger>0) then
        mode = 2
        t0 = ReadTimer() 'init cycle counter
      else
        mode = 1
      endif
      
      'If no trigger for 3,3 sec, abort
      if (idle_timer>3300000) then
        DATA_12[1] = 0
        end
      endif

       
    CASE 2 'wait requested delay
      t1 = ReadTimer()-t0
      if (t1>=delay) then
        PAR_49 = delay
        mode = 3
      endif
      
    CASE 3 'new scan  
      curr_step = 1
      inc(curr_scan)
      
      'check here if the current scan is odd or even. odd: scan from start to end. even: scan from end to start.
      'curr_scan_mod2=1
      if (scan_reverse >0) then
        curr_scan_mod2 = Mod(curr_scan,2)
        step_size = -step_size 'change the sign of step size, so that the direction of sweeping is reversed
        if (curr_scan_mod2 = 1) then
          curr_volt_1 = start_volt1 
          curr_volt_2 = start_volt2 
          curr_volt_3 = start_volt3 
        else
          curr_volt_1 = end_volt1
          curr_volt_2 = end_volt2
          curr_volt_2 = end_volt3
        endif
      ELSE
        curr_volt_1 = start_volt1 
        curr_volt_2 = start_volt2 
        curr_volt_3 = start_volt3 
      ENDIF    
      
      if (DAC_ch_1 > 0) then
        P2_DAC(DAC_Module, DAC_ch_1, curr_volt_1 * 3276.8 + 32768)
      endif
      if (DAC_ch_2 > 0) then
        P2_DAC(DAC_Module, DAC_ch_2, curr_volt_2 * 3276.8 + 32768)
      endif
      if (DAC_ch_3 > 0) then
        P2_DAC(DAC_Module, DAC_ch_3, curr_volt_3 * 3276.8 + 32768)
      endif
      t1 = ReadTimer()
      DATA_12[curr_scan+1] = t1-t0
      if (curr_scan>nr_scans) then
        DATA_12[1] = 1
        
        end
      else
        mode = 10
        timer = -30  'wait 30 microseconds before scan starts
        't0_wait = ReadTimer() 'remove the reading timer, but use the statement using timer above instead SvD 3-2-2016
      endif     
      
    CASE 10 'wait for piezo to restore to init position 
      't1_wait = ReadTimer() 'remove the reading timer, but use an incrementint timer instead
      'if (t1_wait-t0_wait > 5000) then
      if (timer>=0) then 'use this instead of statement above
        mode = 4
        timer = -1
      endif
      
      
    CASE 4 'read-out photodiode voltage
      
      
      if (timer>=0) then
        if (timer >=ADC_averaging_cycles) then
          inc(sweep_idx)
          DATA_11[sweep_idx] = ADC_average_voltage/ADC_averaging_cycles
          DATA_13[sweep_idx] = FPar_42
          'DATA_12[sweep_idx] = curr_step'(adc_binary_voltage_ref-32768)/3276.8
          'FPar_51 = DATA_11[sweep_idx]
          mode = 5
          timer = -1
        else
          'if timer
          adc_binary_voltage = P2_ADC (ADC_module, pd_ADC_ch)
          ADC_average_voltage = ADC_average_voltage+ (adc_binary_voltage-32768)/3276.8
        endif
      ENDIF
      
      
    CASE 5 'set next voltage
      if (timer>=0) then
        if (DAC_ch_1 > 0) then
          P2_DAC(DAC_Module, DAC_ch_1, curr_volt_1 * 3276.8 + 32768)
        endif
        if (DAC_ch_2 > 0) then
          P2_DAC(DAC_Module, DAC_ch_2, curr_volt_2 * 3276.8 + 32768)
        endif
        if (DAC_ch_3 > 0) then
          P2_DAC(DAC_Module, DAC_ch_3, curr_volt_3 * 3276.8 + 32768)
        endif

        timer = -wait_cycles
        mode = 4
        ADC_average_voltage = 0.
         
        
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
