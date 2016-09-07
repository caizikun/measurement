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
' This program is used for fast scans of the fine-tuning JPE piezos
' We try to track the cavity resonance by scanning around the maximum 
' of the signal in the previous scan.
' 
'C. Bonato
'
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' scan settings
DIM fpz1_DAC_ch, fpz2_DAC_ch, fpz3_DAC_ch, t0 as long
DIM pd_ADC_ch, pd_ref_ADC_ch, nr_steps AS long
DIM central_voltage, V_step_size, nr_avg_reps, nr_tracking_steps, start_voltage as float
DIM curr_volt, max, v AS FLOAT
DIM DAC_binary_voltage, ADC_binary_voltage, ADC_binary_voltage_ref, APD_int_time as integer
DIM counter_channel, counter_pattern AS LONG
DIM timer, mode, curr_step, i, wait_cycles, curr_track, sweep_index as integer

'settings values passed from python:
DIM DATA_200[10] as long
DIM DATA_199[8] as float 'voltages: start, stop, stepsize
'output data:
DIM DATA_11[100000] AS FLOAT  'photodiode voltage (signal)
DIM DATA_12[100000] AS FLOAT  'piezo voltage
DIM DATA_13[1000] AS LONG     'time stamps


INIT:
    
  central_voltage   = DATA_199[1]
  V_step_size       = DATA_199[2]
  
  fpz1_DAC_ch       = DATA_200[1] 'fine-tuning piezo jpe channel
  fpz2_DAC_ch       = DATA_200[2]
  fpz3_DAC_ch       = DATA_200[3]
  pd_ADC_ch         = DATA_200[4] 'photodiode ADC channel (signal)
  pd_ref_ADC_ch     = DATA_200[5] 'photodiode ADC channel (ref)
  nr_steps          = DATA_200[6]
  wait_cycles       = DATA_200[7]
  nr_avg_reps       = DATA_200[8]
  nr_tracking_steps = DATA_200[9] 
  
  start_voltage  = central_voltage - (nr_steps/2)*V_step_size
  'Set initial DAC voltages
  P2_DAC(DAC_Module, fpz1_DAC_ch, start_voltage * 3276.8 + 32768)
  P2_DAC(DAC_Module, fpz2_DAC_ch, start_voltage * 3276.8 + 32768)
  P2_DAC(DAC_Module, fpz3_DAC_ch, start_voltage * 3276.8 + 32768)
  
  curr_volt = start_voltage - V_step_size
     
  'init data array
  FOR i = 1 TO nr_steps*nr_tracking_steps
    DATA_11[i] = 0
    DATA_12[i] = 0
  NEXT i
  
  FOR i = 1 TO nr_tracking_steps
    DATA_13[i] = 0
  NEXT i

  P2_SE_Diff(ADC_module,0) 'sets ADCs to be used as single-ended (default is differential)
  counter_pattern     = 2 ^ (counter_channel-1)
  
  timer = -1
  mode = 0
  curr_step = 0
  curr_track = 0
  sweep_index = 0
  't0 = ReadTimer()

  
  
EVENT:

  Inc(timer)
  Par_3 = nr_steps
  Par_4 = nr_tracking_steps
  Par_6 = sweep_index
  DATA_11[sweep_index] = curr_step
  DATA_12[sweep_index] = curr_track

  SELECTCASE mode:
            
    CASE 0 'set laser voltage
      if (timer>=0) then
        inc(curr_step)  
        inc(sweep_index)      
        curr_volt = curr_volt + V_step_size
        'P2_DAC(DAC_Module, fpz1_DAC_ch, curr_volt * 3276.8 + 32768)
        'P2_DAC(DAC_Module, fpz2_DAC_ch, curr_volt * 3276.8 + 32768)
        'P2_DAC(DAC_Module, fpz3_DAC_ch, curr_volt * 3276.8 + 32768)
        timer = -10
        mode = 1
      endif    
      
    CASE 1 'read-out photodiode voltage
      if (timer>=0) then
        'adc_binary_voltage = P2_ADC (ADC_module, pd_ADC_ch)
        'v = (adc_binary_voltage-32768)/3276.8

        if (curr_step>=10) then
          curr_step = 0
          'curr_volt = central_voltage - (nr_steps/2)*V_step_size - V_step_size
          inc (curr_track)
          'DATA_13 [curr_track] = ReadTimer()-t0
          if (sweep_index>=15*nr_steps) then
            Par_5 = curr_track
            END
          endif
        endif
        mode = 0
        timer = -10
      endif
        
      
  ENDSELECT

FINISH:  
 
