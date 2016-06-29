'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277562  DASTUD\TUD277562
'<Header End>
' this program implements single-shot readout fully controlled by ADwin Gold II
'
' protocol:
' mode  0: CR check
' mode  2:  spin pumping with E or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with E or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  E pulse and photon counting for spin-readout with time dependence
'           -> mode 1
'

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

#DEFINE max_modulation_bins 10000

'init     
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

'return

DIM DATA_24[max_modulation_bins] AS FLOAT      ' SP counts
DIM DATA_25[max_modulation_bins] AS FLOAT  ' SSRO counts spin readout

DIM output_dac_channel, input_adc_channel, modulation_bins, error_averaging AS LONG
DIM adc_read AS LONG 
DIM modulation_amplitude, modulation_frequency, cur_mod_voltage, cur_mod, mod_bin_factor  AS FLOAT
DIM timer, aux_timer, mode, i AS LONG

LOWINIT:
  output_dac_channel           = DATA_20[1]
  input_adc_channel            = DATA_20[2]
  modulation_bins              = DATA_20[3]
  error_averaging              = DATA_20[4]
  

  modulation_amplitude         = DATA_21[1]
  modulation_frequency         = DATA_21[2]
  
  
  mod_bin_factor = 1-(1/modulation_bins/error_averaging)
  
  FOR i = 1 TO modulation_bins
    DATA_24[i] = Sin(-3.14+2*3.14*i/modulation_bins)
    DATA_25[i] = 0
  NEXT i
    
  P2_SE_Diff(ADC_module,0)  
  PROCESSDELAY = Round(300*1000000/(modulation_frequency*modulation_bins)/2.)

  mode = 0
  timer = 0
  FPar_73 = 0
  'FPar_74 = mod_bin_factor
  
  'live updated pars

EVENT:


  SELECTCASE mode
      
    CASE 0 'modulate
      cur_mod = DATA_24[timer+1]
      cur_mod_voltage = FPar_71 + modulation_amplitude*cur_mod
      P2_DAC(DAC_MODULE,output_dac_channel, 3277*cur_mod_voltage+32768) ' turn off green
      mode = 1    
      
    CASE 1
      adc_read = P2_ADC(ADC_module, input_adc_channel)
      FPar_72 = (adc_read-32768)/3276.8  
      FPar_73=FPar_73*mod_bin_factor+cur_mod*(FPar_72)'*(1-mod_bin_factor)
      'DATA_25[timer+1] = 0.99*DATA_25[timer+1] + FPar_72*0.01
      Inc(timer)
      IF (timer = modulation_bins) THEN
        timer=0
      ENDIF
      mode=0
      Par_71 = timer
      
    CaseElse
      PAR_80=1
      END
       
  ENDSELECT
    


