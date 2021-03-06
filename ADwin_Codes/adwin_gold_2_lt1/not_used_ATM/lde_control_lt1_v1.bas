'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 300
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.6
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
#INCLUDE ADwinGoldII.inc

' Modes:
' 0 : waiting
' 1 : CR check
' 2 : repumping
' 3 : SSRO

' Resources used:
'
' PARs
' ====
' Inputs:
' 68  cr_check_count_threshold_probe
' 75  cr_check_count_threshold_prepare

' Outputs:
' 65  number of raw edges detected from SSRO in from lt2
' 67  number of ROs performed
' 70  cumulative counts from probe intervals
' 71  below CR threshold events
' 72  number of CR checks performed (lt1)
' 76  cumulative counts during repumping
' 77  number of ok pulses sent to lt2
' 79  number of start pulses received from lt2
' 80  cumulative counts in PSB when not CR chekging or repummping 

' FPARs
' =====
' Inputs:
'
' Outputs:
'
' DATA
' ==== 
' Inputs:
' DATA_20 (integer)
'   1 : counter
'   2 : green aom channel
'   3 : E aom channel
'   4 : A aom channel
'   5 : CR check steps (no of process cycles)
'   6 : CR threshold (after preparation with green)
'   7 : CR threshold (already prepared)
'   8 : repump steps
'   9 : trigger remote cr in bit
'  10 : trigger finished remote cr out
'  11 : trigger remote ssro in bit
'  12 : ssro steps
'
' DATA_21 (float)
'   1 : green repump voltage
'   2 : green offset voltage (0V != no laser output)
'   3 : E CR voltage
'   4 : A CR voltage
'   5 : E RO voltage
'   6 : A RO voltage
'
' Outputs:
' Outputs:
' DATA_7[-max_hist_cts] (int) : CR count histogram after unsuccessful entanglement attempts
' DATA_8[-max_hist_cts] (int) : CR count histogram after all attempts
' DATA_22 (int) : SSRO results
' DATA_23 (int) : CR counts after SSRO

' general, parameters
DIM i as long
dim mode as integer
dim timer as long
dim DATA_20[12] as long
dim DATA_21[6] as float

' statistics
#DEFINE max_hist_cts 100                ' dimension of photon counts histogram for CR
DIM DATA_7[max_hist_cts] as long       ' histogram of counts during 1st CR after interference sequence
DIM DATA_8[max_hist_cts] as long       ' histogram of counts during CR (all attempts)

' CR and repump settings
DIM counter AS LONG                 ' select internal ADwin counter 1 - 4 for conditional readout
DIM green_aom_channel AS LONG       ' DAC channel for green laser AOM
DIM green_voltage AS Float          ' voltage of repump pulse
dim green_off_voltage as float
dim ex_aom_channel as long
dim ex_cr_voltage as Float
dim a_aom_channel as long
dim a_cr_voltage as Float
dim current_cr_check_counts as long
dim cr_check_steps as long                      ' how long to check, in units of process cycles (lt1)
dim cr_check_count_threshold_prepare as long    ' initial C&R threshold after repump (lt1)
dim cr_check_count_threshold_probe as long      ' C&R threshold for probe after sequence (lt1)
dim repump_steps as long
dim current_cr_threshold as long
dim first_cr_probe_after_lde as integer

' control from lt2
dim trigger_cr_dio_in_bit, trigger_cr_dio_out as integer
dim cr_was_triggered, cr_is_triggered as integer
dim trigger_ssro_dio_in_bit as integer
dim ssro_was_triggered, ssro_is_triggered as integer
dim DIO_register as long
dim trigger_ssro_dio_in as long
dim trigger_cr_dio_channel as long

' ssro
#define max_readouts 1000000
dim DATA_22[max_readouts] as long
dim DATA_23[max_readouts] as long
dim RO_event_idx as long
dim RO_counts as long
dim ex_ro_voltage as float
dim a_ro_voltage as float
dim RO_steps as long
dim cr_after_ssro as integer

init:
  mode = 0
  timer = 0
  cr_after_ssro = 0
  
  for i=1 to max_hist_cts
    DATA_7[i] = 0
    DATA_8[i] = 0
  next i

  ' init CR check variables
  counter = data_20[1]
  green_aom_channel = data_20[2]
  ex_aom_channel = data_20[3]
  a_aom_channel = data_20[4]
  cr_check_steps = data_20[5]
  cr_check_count_threshold_prepare = data_20[6]
  cr_check_count_threshold_probe = data_20[7]
  repump_steps = data_20[8]
   
  green_voltage = data_21[1]
  green_off_voltage = data_21[2] 
  ex_cr_voltage = data_21[3]
  a_cr_voltage = data_21[4]
  
  current_cr_check_counts = 0
  current_cr_threshold = cr_check_count_threshold_prepare
  first_cr_probe_after_lde = 0
  
  ' remote control
  trigger_cr_dio_channel = data_20[9]
  trigger_cr_dio_in_bit =  2^trigger_cr_dio_channel
  trigger_cr_dio_out = data_20[10] 
  trigger_ssro_dio_in = data_20[11]
  cr_is_triggered = 1
  cr_was_triggered = 1
  ssro_is_triggered = 1
  ssro_was_triggered = 1
  
  ' ssro
  ex_ro_voltage = data_21[5]
  a_ro_voltage = data_21[6]
  RO_event_idx = 0
  RO_steps = data_20[12]  
  for i=1 to max_readouts
    DATA_22[i] = -1
    DATA_23[i] = -1
  next i
  
  ' prepare hardware
  DAC(green_aom_channel, 3277*green_off_voltage+32768)
  DAC(ex_aom_channel, 32768)
  DAC(a_aom_channel, 32768)
  
  par_58 = 0
  par_59 = 0
  
  par_60 = 0
  par_61 = 0
  par_62 = 0
  par_63 = 0
  par_64 = 0
  par_65 = 0                      ' number of SSRO triggers received from LT2
  par_67 = 0                      ' number of SSROs performed
  par_68 = cr_check_count_threshold_probe
  par_75 = cr_check_count_threshold_prepare
  
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' below CR threshold events
  PAR_72 = 0                      ' number of CR checks performed (lt1)
  par_76 = 0                      ' cumulative counts during repumping
  par_77 = 0                      ' number of ok pulses sent to lt2
  Par_79 = 0                      ' number of CR triggers received from lt2
  
  CNT_ENABLE(0000b)
  CNT_MODE(1,00001000b)
  CNT_MODE(2,00001000b)
  CNT_MODE(3,00001000b)
  CNT_MODE(4,00001000b)
  CNT_SE_DIFF(0000b)
  CNT_CLEAR(1111b)
  CNT_ENABLE(1111b)
  
  CONF_DIO(13)
  DIGOUT(trigger_cr_dio_out, 0)
  
event:
  cr_check_count_threshold_probe = par_68
  cr_check_count_threshold_prepare = par_75
  
  'DIO_register = digin_edge(1)
  
  'cr_is_triggered = ((DIO_register) and (trigger_cr_dio_in_bit))
  'ssro_is_triggered = ((DIO_register) and (trigger_ssro_dio_in_bit))
  
  cr_was_triggered = cr_is_triggered   
  cr_is_triggered = DIGIN(trigger_cr_dio_channel)

  ssro_was_triggered = ssro_is_triggered 
  ssro_is_triggered = DIGIN(trigger_ssro_dio_in)
  
  if ((cr_was_triggered = 0) and (cr_is_triggered > 0)) then
    inc(par_62)
  endif
  
  
  if ((ssro_was_triggered = 0) and (ssro_is_triggered > 0)) then
    inc(RO_event_idx)
    inc(par_65)
  endif
  
  selectcase mode:
      
    case 0 'received a trigger from LT2
  
      if ((cr_was_triggered = 0) and (cr_is_triggered > 0)) then       
        inc(Par_79)
        mode = 1
        timer = -1
        first_cr_probe_after_lde = 1
      else 
        if ((ssro_was_triggered = 0) and (ssro_is_triggered > 0)) then
          mode = 3
          timer = -1
        endif
      endif
      
    case 1 'CR check
        
      if (timer = 0) then
        inc(Par_60)
        DIGOUT(trigger_cr_dio_out, 0)
        
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b)
        CNT_ENABLE(1111b)
        
        DAC(ex_aom_channel, 3277*ex_cr_voltage+32768) ' turn on the red lasers
        DAC(a_aom_channel, 3277*a_cr_voltage+32768)      
      endif
      
      if (timer = cr_check_steps) then
        CNT_LATCH(1111b)
        current_cr_check_counts = CNT_READ_LATCH(counter)
        par_70 = par_70 + current_cr_check_counts
          
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b) ' clear counter
        
        if (cr_after_ssro > 0) then ' this is for the cr after ssro. than it has to go back to mode 0
          DATA_23[RO_event_idx] = current_cr_check_counts 'save cr counts after ssro
          mode = 0
          timer = -1
          DAC(ex_aom_channel, 32768) ' turn off the red lasers
          DAC(a_aom_channel, 32768)
          cr_after_ssro = 0
          Inc(par_61)
        else
          Inc(par_72)     
          if (current_cr_check_counts < current_cr_threshold) then
            mode = 2
            timer = -1
            Inc(par_71)
          else
            DAC(ex_aom_channel, 32768) ' turn off the red lasers
            DAC(a_aom_channel, 32768)
        
            DIGOUT(trigger_cr_dio_out, 1)
            Inc(par_77)
            current_cr_threshold = cr_check_count_threshold_probe
            mode = 0
            timer = -1

          endif
        endif
        
        
        if (current_cr_check_counts < max_hist_cts) then
          if (first_cr_probe_after_lde > 0) then ' first CR after the sequence 
            DATA_7[current_cr_check_counts+1] = DATA_7[current_cr_check_counts+1] + 1
          endif
          DATA_8[current_cr_check_counts+1] = DATA_8[current_cr_check_counts+1] + 1
        endif
        
        first_cr_probe_after_lde = 0
        
      endif
      
    case 2 'Repump
      if (timer = 0) then
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b)
        CNT_ENABLE(1111b)        
        DAC(green_aom_channel, 3277*(green_off_voltage+green_voltage)+32768)  
      endif
      
      if (timer = repump_steps) then
        DAC(green_aom_channel, 3277*green_off_voltage+32768)
        current_cr_threshold = cr_check_count_threshold_prepare
        CNT_LATCH(1111b)
        par_76 = par_76 + CNT_READ_LATCH(counter)       
        mode = 1
        timer = -1      
      endif
      
    case 3 'SSRO
      if (timer = 0) then      
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b)
        CNT_ENABLE(1111b)  
        DAC(ex_aom_channel, 3277*ex_ro_voltage+32768) ' turn on the red lasers
        DAC(a_aom_channel, 3277*a_ro_voltage+32768)
      endif
      
      if (timer = RO_steps) then
        DAC(ex_aom_channel, 32768) ' turn off the red lasers
        DAC(a_aom_channel, 32768)
        CNT_LATCH(1111b)        
        data_22[RO_event_idx] = CNT_READ_LATCH(counter)
        CNT_ENABLE(0000b)
        CNT_CLEAR(1111b) ' clear counter   
        
        inc(par_67)
        cr_after_ssro = 1
        mode = 1
        timer = -1

      endif
               
  endselect
  
  timer = timer + 1
