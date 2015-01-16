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
' This program is used for fast laser-scan with photodiode output aquisition.
' It performs a one-dimensional voltage scan (laser scan), acquiring for each point
' a voltage read-out from the ADC.
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM DAC_nr, ADC_nr, nr_steps AS INTEGER
DIM start_voltage, step_size, curr_voltage AS FLOAT
DIM DAC_binary_voltage, ADC_binary_voltage as integer
'settings values passed from python:
DIM DATA_200[8] as long
DIM DATA_199[8] as float 'voltages: start, stop, stepsize
'ourput data:
DIM DATA_11[100000] AS LONG

dim timer, mode, curr_step, i, wait_cycles as integer

INIT:
    
  start_voltage   = DATA_199[1]
  step_size       = DATA_199[2]
 
  DAC_nr          = DATA_200[1]
  ADC_nr          = DATA_200[2]
  nr_steps        = DATA_200[3]
  wait_cycles     = DATA_200[4]
     
  'Set initial DAC voltage
  DAC_binary_voltage = start_voltage * 3276.8 + 32768        
  P2_DAC(DAC_Module, DAC_nr, DAC_binary_voltage)
   
  'init data array
  FOR i = 1 TO nr_steps
    DATA_11[i] = i*3
  NEXT i
  
  timer = -1
  mode = 0
  curr_step = 1
  
EVENT:

  Inc(timer)

  SELECTCASE mode:
      
    CASE 0 'read-out photodiode voltage
      if (timer>=0) then
        adc_binary_voltage = P2_ADC (ADC_module, ADC_nr)
        'DATA_11[curr_step] = (adc_binary_voltage-32768)/3276.8
        'FPar_5 = DATA_11[curr_step]
        Par_5 = curr_step
        timer = -wait_cycles
        mode = 1
      endif
      
    CASE 1 'set laser-scan voltage
      if (timer>=0) then
        DAC_binary_voltage = curr_voltage * 3276.8 + 32768        
        P2_DAC(DAC_Module, DAC_nr, DAC_binary_voltage)
        timer = -wait_cycles
        mode = 0
        inc(curr_step)
        curr_voltage = curr_voltage + step_size
        if (curr_step>nr_steps) then
          END
        endif
      endif    
  ENDSELECT

FINISH:  
  Par_49 = 0  'tell resonant counting process to stop summing its data into par 45-48  
