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
' 
'C. Bonato
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM fpz1_DAC_ch, fpz2_DAC_ch, fpz3_DAC_ch as long
DIM pd_ADC_ch, pd_ref_ADC_ch, nr_steps, use_counter, counts AS long
DIM start_voltage_1, start_voltage_2, start_voltage_3 as float
DIM step_size, curr_volt_1, curr_volt_2, curr_volt_3 AS FLOAT
DIM DAC_binary_voltage, ADC_binary_voltage, ADC_binary_voltage_ref, APD_int_time as integer
DIM counter_channel, counter_pattern AS LONG
'settings values passed from python:
DIM DATA_200[10] as long
DIM DATA_199[8] as float 'voltages: start, stop, stepsize
'output data:
DIM DATA_11[100000] AS FLOAT 'photodiode voltage (signal)
DIM DATA_12[100000] AS FLOAT 'photodiode voltage (reference)
DIM DATA_13[100000] AS LONG  'APD counts


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
  pd_ref_ADC_ch   = DATA_200[5] 'photodiode ADC channel (ref)
  nr_steps        = DATA_200[6]
  wait_cycles     = DATA_200[7]
  use_counter     = DATA_200[8] '0 = photodiode, >0 = APD counter
  APD_int_time    = DATA_200[9] 'integration time for APD
  counter_channel = DATA_200[10] 
  
  'Set initial DAC voltages
  P2_DAC(DAC_Module, fpz1_DAC_ch, start_voltage_1 * 3276.8 + 32768)
  P2_DAC(DAC_Module, fpz2_DAC_ch, start_voltage_2 * 3276.8 + 32768)
  P2_DAC(DAC_Module, fpz3_DAC_ch, start_voltage_3 * 3276.8 + 32768)
  
  curr_volt_1 = start_voltage_1
  curr_volt_2 = start_voltage_2
  curr_volt_3 = start_voltage_3
     
  'init data array
  FOR i = 1 TO nr_steps
    DATA_11[i] = 0
    DATA_12[i] = 0
    DATA_13[i] = 0
  NEXT i
  
  P2_SE_Diff(ADC_module,0) 'sets ADCs to be used as single-ended (default is differential)
  counter_pattern     = 2 ^ (counter_channel-1)
  P2_CNT_ENABLE(CTR_MODULE,0000b) 'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel,000010000b) 'configure counter
  
  timer = -1
  mode = 0
  curr_step = 1
  
EVENT:

  Inc(timer)

  SELECTCASE mode:
      
    CASE 0 'read-out photodiode voltage
      if (use_counter==0) then
        if (timer>=0) then
          adc_binary_voltage = P2_ADC (ADC_module, pd_ADC_ch)
          adc_binary_voltage_ref = P2_ADC (ADC_module, pd_ref_ADC_ch)
          DATA_11[curr_step] = (adc_binary_voltage-32768)/3276.8
          DATA_12[curr_step] = (adc_binary_voltage_ref-32768)/3276.8
          FPar_5 = DATA_11[curr_step]
          Par_5 = curr_step
          Par_6 = pd_ADC_ch
          mode = 1
          timer = -wait
        endif
      else
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
        Endif

        IF (timer = APD_int_time) THEN
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          Par_7 = counts
          DATA_13[curr_step] = counts
          P2_CNT_ENABLE(CTR_MODULE,0)
          mode = 1          
          timer = -wait_cycles
        ENDIF                          
      endif
      
    CASE 1 'set laser-scan voltage
      if (timer>=0) then
        P2_DAC(DAC_Module, fpz1_DAC_ch, curr_volt_1 * 3276.8 + 32768)
        P2_DAC(DAC_Module, fpz2_DAC_ch, curr_volt_2 * 3276.8 + 32768)
        P2_DAC(DAC_Module, fpz3_DAC_ch, curr_volt_3 * 3276.8 + 32768)
        timer = -wait_cycles
        mode = 0
        inc(curr_step)
        curr_volt_1 = curr_volt_1 + step_size
        curr_volt_2 = curr_volt_2 + step_size
        curr_volt_3 = curr_volt_3 + step_size
        if (curr_step>nr_steps) then
          END
        endif
      endif    
  ENDSELECT

FINISH:  
  Par_49 = 0  'tell resonant counting process to stop summing its data into par 45-48  
