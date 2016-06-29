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
' Info_Last_Save                 = TUD277459  DASTUD\TUD277459
'<Header End>
' this program implements single-shot readout fully controlled by ADwin Gold II
'
' protocol:
' mode  0:  CR check
' mode  2:  spin pumping with Ex or A pulse, photon counting for time dependence of SP
' mode  3:  optional: spin pumping with Ex or A pulse, photon counting for postselection on 0 counts
'           counts > 0 -> mode 1
' mode  4:  optional: trigger for AWG sequence, or static wait time
' mode  5:  Ex pulse and photon counting for spin-readout with time dependence
'           -> mode 1

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc

#DEFINE max_SP_bins        500
#DEFINE max_stat            10

'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_28[100] AS LONG

'return
DIM DATA_24[max_SP_bins] AS LONG AT EM_LOCAL      ' SP counts ' not used anymore? Machiel 23-12-'13
DIM DATA_25[max_repetitions] AS LONG  ' SSRO counts spin readout



DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel AS LONG
DIM send_AWG_start, wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM SP_duration, SP_filter_duration AS LONG
DIM SSRO_repetitions, SSRO_duration, SSRO_stop_after_first_photon, sweep_length AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG
DIM Use_shutter, Shutter_channel, Shutter_opening_time, Shutter_safety_time AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT

DIM timer, aux_timer, mode, i, sweep_index AS LONG
DIM AWG_done AS LONG
DIM first AS LONG

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts AS LONG

INIT:  
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  send_AWG_start               = DATA_20[3]
  wait_for_AWG_done            = DATA_20[4]
  SP_duration                  = DATA_20[5]
  SP_filter_duration           = DATA_20[6]
  sequence_wait_time           = DATA_20[7]
  wait_after_pulse_duration    = DATA_20[8]
  SSRO_repetitions             = DATA_20[9]
  SSRO_duration                = DATA_20[10]
  SSRO_stop_after_first_photon = DATA_20[11]
  cycle_duration               = DATA_20[12] '(in processor clock cycles, 3.333ns)
  sweep_length                 = DATA_20[13]
  Use_shutter                  = DATA_20[14]
  Shutter_channel              = DATA_20[15]
  Shutter_opening_time         = DATA_20[16]
  Shutter_safety_time          = DATA_20[17]
  
  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  par_80 = SSRO_stop_after_first_photon
  
  FOR i = 1 TO max_SP_bins
    DATA_24[i] = 0
  NEXT i
  
  FOR i = 1 TO sweep_length
    DATA_25[i] = 0
  NEXT i
   
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel

  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
      
  P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off repump
  P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
  P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off Ex laser

  P2_CNT_ENABLE(CTR_MODULE,0000b) 'turn off all counters
  P2_CNT_MODE(CTR_MODULE,counter_channel, 00001000b) 'configure counter

  P2_Digprog(DIO_MODULE,11)
  P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)

  sweep_index = 1
  mode = 0
  timer = 0
  PAR_60=0
  PAR_62=0
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter


EVENT:
    
  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE

    SELECTCASE mode
      
      CASE 0 'safety wait-time for shutter heating (specified >35 msec)
        
        IF (timer > 0) THEN
          mode = 1
          timer = -1
        ENDIF
                  
      CASE 1 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 2
          timer = -1
          first = 0
        ENDIF

      CASE 2    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
        else
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          DATA_24[timer] = DATA_24[timer] + counts
        Endif

        IF (timer = SP_duration) THEN
          P2_CNT_ENABLE(CTR_MODULE,0)
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                
          
          IF (DATA_28[sweep_index]> 0) THEN
            IF (use_shutter > 0) THEN
              P2_DIGOUT(DIO_Module,Shutter_channel, 1)
              INC(PAR_60)
            ENDIF
            mode = 3
            
            wait_after_pulse = wait_after_pulse_duration
          ELSE
            mode = 4
          ENDIF
          timer = -1
        ENDIF
      
      CASE 3    '  wait for fixed duration
        
        IF ((use_shutter > 0) AND (timer >= (data_28[sweep_index]-Shutter_opening_time))) THEN
          P2_DIGOUT(DIO_Module,Shutter_channel, 0)
          INC(PAR_60)
          wait_after_pulse = Shutter_opening_time
          mode = 4
          timer = -1
        ENDIF
        IF (timer >= (data_28[sweep_index])) THEN
          wait_after_pulse = 0
          mode = 4
          timer = -1
        ENDIF
  
     
      CASE 4    ' spin readout
               
        IF (timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE, counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
        endif
         
        IF (timer = SSRO_duration) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          P2_CNT_ENABLE(CTR_MODULE,0)

          if (counts > 0) then
            inc(data_25[sweep_index])
          endif
          
          inc(sweep_index)
          if (sweep_index > sweep_length) then
            sweep_index = 1
          endif
          
          mode = 0
          IF (use_shutter > 0) THEN
            INC(PAR_60)
            timer = -Shutter_safety_time
          ELSE
            timer = -1
          ENDIF
          wait_after_pulse = wait_after_pulse_duration
          inc(repetition_counter)
          Par_73 = repetition_counter
          IF (repetition_counter = SSRO_repetitions) THEN
            END
          ENDIF
          first = 1

        ENDIF
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


