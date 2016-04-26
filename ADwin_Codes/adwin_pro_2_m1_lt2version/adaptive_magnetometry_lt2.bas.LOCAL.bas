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
' Info_Last_Save                 = TUD276198  DASTUD\TUD276198
'<Header End>
' this program implements adaptive magnetometry protocols (Cappellaro, real-time calculation of optimal phase)
'
' protocol:
' mode  0:  CR check
' mode  1:  spin pumping with A pulse
' mode  2:  AWG (N-init, Ramsey)
' mode  3:  Ex pulse and photon counting for spin-readout with time dependence (repetitive e-spin ssro)
' mode  4:  calculate optimal phase
' -> mode 0

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc
#INCLUDE Math.inc

#DEFINE max_stat            10
#DEFINE max_prob_array    40000
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM p_real[max_prob_array] AS FLOAT
DIM p_imag[max_prob_array] AS FLOAT
DIM p_real_old[max_prob_array] AS FLOAT
DIM p_imag_old[max_prob_array] AS FLOAT
DIM ch[8] AS LONG

'return
DIM DATA_25[max_repetitions] AS LONG  ' SSRO counts spin readout

DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel AS LONG
DIM wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM SP_duration AS LONG
DIM repetitions, SSRO_duration, SSRO_stop_after_first_photon, sweep_length AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM c_n, t_n, pi AS FLOAT

DIM timer, aux_timer, mode, i, k, sweep_index, a, k_opt AS LONG
DIM AWG_done AS LONG
DIM first, do_adaptive, do_phase_calibr AS LONG
DIM min_phase, max_phase, delta_phi AS FLOAT

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts AS LONG
DIM adptv_steps, curr_adptv_phase, dig_phase, curr_adptv_step, rep_index, curr_msmnt_result AS LONG

INIT:  
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  wait_for_AWG_done            = DATA_20[3]
  SP_duration                  = DATA_20[4]
  sequence_wait_time           = DATA_20[5]
  wait_after_pulse_duration    = DATA_20[6]
  repetitions                  = DATA_20[7]  'now this is the nr of times we repeat the series of adaptive msmnt steps
  SSRO_duration                = DATA_20[8]
  SSRO_stop_after_first_photon = DATA_20[9]
  cycle_duration               = DATA_20[10] '(in processor clock cycles, 3.333ns)
  sweep_length                 = DATA_20[11]
  do_adaptive                  = DATA_20[12] 'do_adaptive=1 activates adptv protocol, =0 sets phase always to zero
  adptv_steps                  = DATA_20[13] 'nr of msmnt steps in adaptive protocol
  ch[1]                        = DATA_20[14] 'adwin channels for 8-bit phase to FPGA
  ch[2]                        = DATA_20[15]
  ch[3]                        = DATA_20[16]
  ch[4]                        = DATA_20[17]
  ch[5]                        = DATA_20[18]
  ch[6]                        = DATA_20[19]
  ch[7]                        = DATA_20[20]
  ch[8]                        = DATA_20[21]
  do_phase_calibr              = DATA_20[22] 'phase calibration modality (sine wave)
  min_phase                    = DATA_20[23] 'min phase for calibration
  max_phase                    = DATA_20[24] 'max phase for calibration
  
  pi = 3.14
  
  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  par_80 = SSRO_stop_after_first_photon
   
  FOR i = 1 TO repetitions*adptv_steps
    DATA_25[i] = 0
  NEXT i
  
  FOR i = 1 TO 2^(adptv_steps+2)+1
    p_real[i] = 0
    p_imag[i] = 0
    p_real_old[i] = 0
    p_imag_old[i] = 0
  NEXT i    
  
  p_real[2^(adptv_steps+1)] = 1
  p_imag[2^(adptv_steps+1)] = 0
  
  delta_phi = (max_phase-min_phase)/adptv_steps
  
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
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter
  curr_adptv_phase = 0
  rep_index = 1
  curr_msmnt_result = 0
  a = 0

EVENT:
    
  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE

    SELECTCASE mode
        
      CASE 0 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 1
          timer = -1
          first = 0
        ENDIF

      CASE 1    ' Ex or A laser spin pumping
        IF (timer = 0) THEN
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
        else
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
        Endif

        IF (timer = SP_duration) THEN
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                
          
          mode = 2
            
          ' SET PHASE TO FPGA (8-bit)
          a = 2*255*curr_adptv_phase/180
          FOR i = 0 TO 7
            a = a/2
            dig_phase = mod (a, 2)
            'set hardware phase channel (8-i) to dig_phase
          NEXT i
      
                            
          wait_after_pulse = wait_after_pulse_duration
          timer = -1
        ENDIF
      
      CASE 2    '  wait for AWG sequence or for fixed duration
        IF (timer = 0) THEN
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          P2_DIGOUT(DIO_MODULE,AWG_start_DO_channel,0)
          aux_timer = 0
          AWG_done = 0
        endif
         
        IF (wait_for_AWG_done > 0) THEN 
          IF (AWG_done = 0) THEN
            par_60 = (P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
            IF ((P2_DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN
              AWG_done = 1
              IF (sequence_wait_time > 0) THEN
                aux_timer = timer
              ELSE
                mode = 3
                timer = -1
                wait_after_pulse = 0
              ENDIF
            ENDIF
          ELSE
            IF (timer - aux_timer >= sequence_wait_time) THEN
              mode = 3
              timer = -1
              wait_after_pulse = 0
            ENDIF
          ENDIF
        ELSE
          IF (timer >= sequence_wait_time) THEN
            mode = 3
            timer = -1
            wait_after_pulse = 0
            'ELSE
            'CPU_SLEEP(9)
          ENDIF
        ENDIF
     
      CASE 3    ' spin readout
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
            inc(curr_msmnt_result)
          endif

          DATA_25 [sweep_index] = curr_msmnt_result
          inc (sweep_index)
          inc (curr_adptv_step)
          IF (curr_adptv_step < adptv_steps) THEN 
            mode = 4
          ELSE
            curr_adptv_step = 1
            inc(rep_index)
            IF (rep_index >= repetitions) THEN
              END
            ENDIF
            mode = 0
          ENDIF
          
          timer = -1
          wait_after_pulse = wait_after_pulse_duration
          first = 1

        ENDIF
        
      CASE 4    'calculate optimal phase
    
        IF (do_phase_calibr > 0) THEN
          curr_adptv_phase = curr_adptv_phase + delta_phi
        
        ELSE
          IF (do_adaptive >1) THEN
            c_n = curr_msmnt_result*pi+curr_adptv_phase*pi/180
            t_n = 2^(adptv_steps-curr_adptv_step)
            k_opt = 2^(adptv_steps-curr_adptv_step+1)+2^(adptv_steps+1)

            'copy current arrays into old arrays
            FOR k = 1 TO 2^(adptv_steps+2)+1
              p_real_old[k] = p_real[k]
              p_imag_old[k] = p_imag[k]
            NEXT k
        
      
            'Bayesian update rule for phase estimation
            FOR k = 2^adptv_steps TO 3*(2^adptv_steps)
              p_real [k] = 0.5*p_real_old[k] + 0.25*(COS(c_n)*(p_real_old [k-t_n] + p_real_old [k+t_n]) - SIN(c_n)*(p_imag_old [k-t_n] - p_imag_old [k+t_n])) 
              p_imag [k] = 0.5*p_imag_old[k] + 0.25*(COS(c_n)*(p_imag [k-t_n] + p_imag_old [k+t_n]) + SIN(c_n)*(p_real_old [k-t_n] - p_real_old [k+t_n])) 
            NEXT k
            
            'define optimal phase according to Cappellaro protocol
            curr_adptv_phase = -0.5*ARCTAN (p_imag[k_opt]/p_real[k_opt])*(180/pi)
          ELSE
            curr_adptv_phase = 0
          ENDIF
        ENDIF
        curr_msmnt_result = 0
        timer=-1
        mode = 1
      
      
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


