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
' This program is used for fast laser-scan over a large frequency range, with photodiode output aquisition.
' It sets the coarse laser wavelength usin g the "wavelength input" port of the NewFocus,
' and performs a fast voltage scan ("freq modulation" port), acquiring for each point 
' a voltage read-out from the ADC. For each, point the wavementer can be read-out
'
' Cristian Bonato - 2015
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM DAC_coarse_nr, DAC_fine_nr, ADC_nr, nr_fine_steps, nr_coarse_steps AS INTEGER
DIM start_coarse_volt, step_size_coarse, curr_voltage, start_fine_volt, stop_fine_volt, AS FLOAT 
DIM step_fine_volt, curr_coarse_volt, curr_fine_volt AS FLOAT
DIM DAC_binary_voltage, ADC_binary_voltage as integer
'settings values passed from python:
DIM DATA_200[8] as long
DIM DATA_199[8] as float 'voltages: start, stop, stepsize
'ourput data:
DIM DATA_11[100000] AS FLOAT 'photodiode read-out
DIM DATA_12[100000] AS FLOAT 'wavemeter read-out

dim timer, mode, i, wait_cycles as integer
DIM curr_coarse_step, curr_fine_step, sweep_index AS long

INIT:
    
  start_coarse_volt = DATA_199[1]
  step_size_coarse  = DATA_199[2]
  start_fine_volt   = DATA_199[3]
  stop_fine_volt    = DATA_199[4]
   
  DAC_coarse_nr   = DATA_200[1]
  DAC_fine_nr     = DATA_200[2]
  ADC_nr          = DATA_200[3]
  nr_fine_steps   = DATA_200[4]
  nr_coarse_steps = DATA_200[5]
  wait_cycles     = DATA_200[6]
     
  'Set initial DAC voltage
  DAC_binary_voltage = start_coarse_volt * 3276.8 + 32768        
  P2_DAC(DAC_Module, DAC_coarse_nr, DAC_binary_voltage)
  DAC_binary_voltage = start_fine_volt* 3276.8 + 32768        
  P2_DAC(DAC_Module, DAC_fine_nr, DAC_binary_voltage)
   
  'init data array
  FOR i = 1 TO nr_fine_steps*nr_coarse_steps
    DATA_11[i] = 0
    DATA_12[i] = 0
  NEXT i
  
  step_fine_volt = (stop_fine_volt - start_fine_volt)/nr_fine_steps
  FPar_3 = step_fine_volt
  timer = -1
  mode = 0
  sweep_index = 1
  curr_fine_step = 1
  curr_coarse_step = 1
  curr_coarse_volt = start_coarse_volt
  
EVENT:

  Inc(timer)

  SELECTCASE mode:
      
    CASE 0 'set new coarse wavelength
      DAC_binary_voltage = curr_coarse_volt * 3276.8 + 32768        
      P2_DAC(DAC_Module, DAC_coarse_nr, DAC_binary_voltage)
      DAC_binary_voltage = start_fine_volt * 3276.8 + 32768        
      P2_DAC(DAC_Module, DAC_fine_nr, DAC_binary_voltage)
      FPar_5 = curr_coarse_volt
      timer = -10000
      mode = 1
          
    CASE 1 'read-out photodiode voltage and wavemeter
      if (timer>=0) then
        adc_binary_voltage = P2_ADC (ADC_module, ADC_nr)
        DATA_11[sweep_index] = (adc_binary_voltage-32768)/3276.8
        DATA_12[sweep_index] = FPar_45
        Par_10 = sweep_index
        'FPar_5 = DATA_11[curr_step]
        Par_5 = curr_fine_step
        inc (sweep_index)
        inc (curr_fine_step)
        timer = -1
        mode = 2
      endif
      
    CASE 2 'set new laser-scan voltage
      if (timer>=0) then
        curr_fine_volt = curr_fine_volt + step_fine_volt
        DAC_binary_voltage = curr_fine_volt * 3276.8 + 32768        
        P2_DAC(DAC_Module, DAC_fine_nr, DAC_binary_voltage)
        timer = -10000
        FPar_4 = curr_fine_volt
        mode = 1
        
        if (curr_fine_step>nr_fine_steps) then
          mode = 0
          curr_fine_volt = start_fine_volt
          curr_fine_step = 1
          inc(curr_coarse_step)
          curr_coarse_volt = curr_coarse_volt + step_size_coarse
          Par_11 = curr_coarse_step
          if (curr_coarse_step>nr_coarse_steps) then
            END
          endif          
        endif
      endif    
      
  ENDSELECT

FINISH:  
  Par_49 = 0  'tell resonant counting process to stop summing its data into par 45-48  
