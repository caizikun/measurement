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
' This program records a timeseries of photodiode read-out with specified delay (wait_cycles)
' We also save the time stamp of each read-out
' C. Bonato --- cbonato80@gmail.com
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM pd_ADC_ch, pd_ref_ADC_ch, nr_steps, use_counter, t0 AS long
DIM DAC_binary_voltage, ADC_binary_voltage, ADC_binary_voltage_ref, APD_int_time as integer
DIM counter_channel, counter_pattern AS LONG
'settings values passed from python:
DIM DATA_200[5] as long
'output data:
DIM DATA_11[100000] AS FLOAT 'photodiode voltage (signal)
DIM DATA_12[100000] AS FLOAT 'photodiode voltage (reference)
DIM DATA_13[100000] AS FLOAT 'time stamps
dim timer, mode, curr_step, i, wait_cycles as integer

INIT:
      
  pd_ADC_ch       = DATA_200[1] 'photodiode ADC channel (signal)
  pd_ref_ADC_ch   = DATA_200[2] 'photodiode ADC channel (ref)
  nr_steps        = DATA_200[3]
  wait_cycles     = DATA_200[4]
     
  'init data array
  FOR i = 1 TO nr_steps
    DATA_11[i] = 0
    DATA_12[i] = 0
  NEXT i
  
  P2_SE_Diff(ADC_module,0) 'sets ADCs to be used as single-ended (default is differential)
  counter_pattern     = 2 ^ (counter_channel-1)
  
  timer = -1
  mode = 0
  curr_step = 1
  t0 = Read_Timer()
  
EVENT:

  Inc(timer)

  SELECTCASE mode:
      
    CASE 0 'read-out photodiode voltage
      if (timer>=0) then
        adc_binary_voltage = P2_ADC (ADC_module, pd_ADC_ch)
        adc_binary_voltage_ref = P2_ADC (ADC_module, pd_ref_ADC_ch)
        DATA_11[curr_step] = (adc_binary_voltage-32768)/3276.8
        DATA_12[curr_step] = (adc_binary_voltage_ref-32768)/3276.8
        DATA_13[curr_step] = Read_Timer() - t0
        FPar_5 = DATA_11[curr_step]
        mode = 1
        timer = -wait_cycles
        curr_step = curr_step + 1
        if (curr_step>=nr_steps) then
          END
        endif
      endif
      
    CASE 1 'wait mode
      if (timer>=0) then
        mode = 0
        timer = -1
      endif    
  ENDSELECT

FINISH:  

