'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
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
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

DIM int_time AS LONG        ' in ms
DIM timer AS LONG       ' multiples of int_time
DIM on_resonance_counter, adc_binary_voltage AS LONG   ' 1--4
DIM single_run, pd_ADC_ch, ADC_voltage_bin AS LONG   ' if 1, measure only once, then stop
DIM ADC_average_voltage,on_resonance_threshold, ADC_voltage AS FLOAT
DIM i AS LONG               ' tmp index
DIM DATA_40[500] AS LONG

DIM voltage_histogram[500] AS LONG

INIT:
  int_time = PAR_23                  ' [ms]
  single_run = PAR_25
  on_resonance_counter = 0
  pd_ADC_ch = 16
  timer = -1
  ADC_average_voltage = 0.
  P2_SE_Diff(ADC_module,0)        'sets ADCs to be used as single-ended (default is differential)
  
  for i = 1 to 500
    voltage_histogram[i]=0
  Next i
  
EVENT:
  
  Inc(timer)
  if (timer = int_time) then
    timer = -1
    FPAR_40 = ADC_average_voltage/int_time
    FPAR_41 = on_resonance_counter/int_time*100
    ADC_average_voltage = 0.
    on_resonance_counter = 0
    for i = 1 to 500
      DATA_40[i]=voltage_histogram[i]
      voltage_histogram[i]=0
    Next i
    if (single_run > 0) then
      end
    endif
    
  else 
    adc_binary_voltage = P2_ADC (ADC_module, pd_ADC_ch)
    ADC_voltage = (adc_binary_voltage-32768)/3276.8 
    ADC_voltage_bin = Round(ADC_voltage*100)
    IF ((ADC_voltage_bin>0) and (ADC_voltage_bin<400)) then
      inc(voltage_histogram[ADC_voltage_bin])
    endif
    ADC_average_voltage = ADC_average_voltage+ ADC_voltage
  endif
