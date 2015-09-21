'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277246  DASTUD\tud277246
'<Header End>
'This code implements adaptive magnetometry protocols.
'--------------------------------------------------------
'The adaptive phase decision tree is passed as an array (DATA_27) in the form of integers in the range 0..255, 
'(then converted to a 8-bit number used to control the FPGA).
'There are N adaptive measurement steps, and the number of measurements per step is set by M.
'For each of the M measurements (Bayesian update), it's possible to obtain the result as a majority vote
'over maj_reps ssro-s, with threshold maj_thr.
'
'No nitrogen initialization is performed, but w driv the thr hyperfine lines separately.
'
' summary of modes:
' mode  0:  CR check
' mode  1:  none
' mode  2:  none
' mode  3:  none
' mode  4:  spin pumping with A pulse
' mode  5:  AWG: (N-init)+ Ramsey
' mode  6:  Ex pulse and photon counting (manages M>1, maj_reps, etc)
' mode  7:  choose optimal phase using submodes 8 and 9 as ancillas to reduce computational time per cycle
' mode  8:  bayesian update manager
' mode  9: ancilla mode to reduce computational effort per cycle
' -> mode 0

#INCLUDE ADwinGoldII.inc
#INCLUDE Math.inc
#INCLUDE .\cr.inc

#DEFINE max_stat            10
#DEFINE max_prob_array      40000
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM ch[8] AS LONG
DIM ch_value[8] AS LONG
DIM indiv_ssro[25] AS LONG
DIM p_real[max_prob_array] AS FLOAT
DIM p_imag[max_prob_array] AS FLOAT
DIM p0_real[max_prob_array] AS FLOAT
DIM p0_imag[max_prob_array] AS FLOAT

'return
DIM DATA_24[max_repetitions] AS LONG  ' adaptive phase (0..255)
DIM DATA_25[max_repetitions] AS LONG  ' SSRO counts spin readout
DIM DATA_27[max_repetitions] AS LONG

DIM sequence_wait_time AS LONG
DIM SP_duration AS LONG
DIM repetitions, SSRO_duration, SSRO_stop_after_first_photon, sweep_length AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM c_n, t_n, pi AS FLOAT

DIM timer, aux_timer, mode, i, k, sweep_index, a AS LONG
DIM first, do_adaptive, do_phase_calibr AS LONG
DIM delta_phi AS LONG

DIM AWG_done_DI_channel, AWG_start_DO_channel, wait_for_AWG_done AS LONG
DIM repetition_counter AS LONG
DIM counts, old_counts , threshold_majority_vote, reps_majority_vote AS LONG
DIM adptv_steps, curr_adptv_phase, dig_phase, curr_adptv_step, rep_index, curr_msmnt_result, curr_m_step, M AS LONG
DIM t1, p, M_count, p0 AS LONG
DIM SP_E_duration, AWG_event_jump_DO_channel AS LONG
DIM awg_in_is_hi, awg_in_was_hi, awg_in_switched_to_hi as long
DIM wait_time AS LONG
DIM maj_ssro, curr_maj_step, maj_ssro_for_saving, do_event_jump, k_opt, k_for AS LONG


INIT:  
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  wait_for_AWG_done            = DATA_20[3]
  SP_duration                  = DATA_20[4]
  sequence_wait_time           = DATA_20[5]
  wait_after_pulse_duration    = DATA_20[6]
  repetitions                  = DATA_20[7]   'now this is the nr of times we repeat the series of adaptive msmnt steps
  SSRO_duration                = DATA_20[8]
  SSRO_stop_after_first_photon = DATA_20[9]   ' not used
  cycle_duration               = DATA_20[10]  '(in processor clock cycles, 3.333ns)
  sweep_length                 = DATA_20[11]
  do_adaptive                  = DATA_20[12]  'do_adaptive=1 activates adptv protocol
  adptv_steps                  = DATA_20[13]  'nr of msmnt steps in adaptive protocol
  ch[1]                        = DATA_20[14]  'adwin channels for 8-bit phase to FPGA
  ch[2]                        = DATA_20[15]  'physical channels ADWIN-FPGA
  ch[3]                        = DATA_20[16]
  ch[4]                        = DATA_20[17]
  ch[5]                        = DATA_20[18]
  ch[6]                        = DATA_20[19]
  ch[7]                        = DATA_20[20]
  ch[8]                        = DATA_20[21]
  do_phase_calibr              = DATA_20[22]  'phase calibration modality (sine wave)
  M                            = DATA_20[23]  'number of measurements per adaptive step
  threshold_majority_vote      = DATA_20[24]
  reps_majority_vote           = DATA_20[25]
  AWG_event_jump_DO_channel    = DATA_20[28]
  
  pi = 3.14
  
  'E_SP_voltage                 = DATA_21[1]
  'A_SP_voltage                 = DATA_21[2]
  'E_RO_voltage                 = DATA_21[3]
  'A_RO_voltage                 = DATA_21[4]
   
  FOR i = 1 TO repetitions*adptv_steps
    DATA_25[i] = 0
  NEXT i
  
  FOR i = 1 TO M+2
    indiv_ssro[i]=0
  NEXT i
  
  FOR i = 1 TO 8
    ch_value[i] = 0
  NEXT i
 
  FOR i = 1 TO repetitions*adptv_steps
    DATA_24[i] = 0
  NEXT i
  

  FOR i = 1 TO 2^(adptv_steps+2)+1
    p_real[i] = 0
    p_imag[i] = 0
    p0_real[i] = 0
    p0_imag[i] = 0
  NEXT i    
    
  p_real[2^(adptv_steps+1)] = 1
  p_imag[2^(adptv_steps+1)] = 0


  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
  
  'DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
  'DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
  'DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off repump
  CNT_CLEAR(counter_pattern)    'clear counter
  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter

  CONF_DIO(0011b)  'configure DIO 00:07 as output, all other ports as input
  'DIGOUT(AWG_start_DO_channel,0)
  'DIGOUT(AWG_event_jump_DO_channel,0)
  FOR i = 0 TO 7
    DIGOUT(ch[8-i], 0)
  NEXT i
 
  sweep_index = 1
  mode = 0
  timer = 0
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter
  Par_76 = curr_adptv_step
  curr_adptv_phase = 0
  rep_index = 1
  curr_adptv_step = 1
  curr_m_step = 1
  curr_maj_step = 1
  curr_msmnt_result = 0
  maj_ssro = 0
  a = 0
  p = 0
  p0 = 1
  awg_in_is_hi = 0      
  awg_in_was_hi = 0
  awg_in_switched_to_hi = 0


EVENT:
    
  PAR_77=mode  
  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE
  
    SELECTCASE mode

      CASE 0 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 4
          timer = -1
          first = 0
        ENDIF
          
        
      CASE 4    'A laser spin pumping
        IF (timer = 0) THEN
          'DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
        else
          'counts = CNT_READ(counter_channel)
        Endif

        IF (timer = SP_duration) THEN
          'DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                
                    
          ' SET PHASE TO FPGA (8-bit)
          a=curr_adptv_phase
          FOR i = 0 TO 7
            dig_phase = mod (a, 2)
            a = a/2
            'set hardware phase channel (8-i) to dig_phase
            DIGOUT(ch[i+1], dig_phase)
            ch_value[i+1] = dig_phase
          NEXT i
          
          'DATA_24 [sweep_index] = 1*ch_value[1]+2*ch_value[2]+4*ch_value[3]+8*ch_value[4]+16*ch_value[5]+32*ch_value[6]+64*ch_value[7]+128*ch_value[8]
          
          mode = 6                
          wait_after_pulse = wait_after_pulse_duration
          timer = -1
        ENDIF
      
 
        
      CASE 6    'electron spin readout
        IF (timer = 0) THEN
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          'DAC(E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
          'DAC(A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
        ENDIF
         
        IF (timer = SSRO_duration) THEN
                   
          'DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
          'DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
          counts = CNT_READ(counter_channel)
          CNT_ENABLE(0)
          par_67 = counts
          IF (counts>0) THEN
            INC(maj_ssro)
          ENDIF

          IF (curr_maj_step<reps_majority_vote) THEN
            mode = 4 
            timer = -1
            inc(curr_maj_step)
          ELSE
            if (maj_ssro > threshold_majority_vote) then
              indiv_ssro[curr_m_step] = 1
            else
              indiv_ssro[curr_m_step] = 0
            endif
            maj_ssro = 0
            curr_maj_step = 1
                  
            'first=1
            par_80 = curr_m_step 
            
            IF (curr_m_step < M) THEN
              mode = 4 
              timer = -1
              inc(curr_m_step)
            ELSE
              do_event_jump = 1
              timer = -1
              M_count=0
              FOR i = 1 TO M
                M_count = M_count + indiv_ssro[i]
              NEXT i
            
              'DATA_25[sweep_index] = M_count
              curr_msmnt_result = M_count
              'DATA_24[sweep_index] = p0+p
              inc (sweep_index)
              inc(repetition_counter)
              PAR_73 = repetition_counter
              PAR_76 = curr_adptv_step
              curr_m_step = 1

              IF (curr_adptv_step < adptv_steps) THEN 
                mode = 7
                timer=-1
              ELSE
                curr_adptv_step = 1
                inc(rep_index)
                p0 = 1
                p = 0
                         
                IF (rep_index > repetitions) THEN
                
                  'reset fpga phase 
                  FOR i = 0 TO 7
                    DIGOUT(ch[i+1], 0) 'set hardware phase channel (8-i) to zero
                  NEXT i
              
                  END
                ENDIF
                curr_adptv_phase = 0
                mode = 4
                timer=-1
              ENDIF
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            first = 1
          ENDIF
          
        ENDIF
        
      CASE 7    'set Bayesian update parameters
        'set parameters for bayesian update
        c_n = curr_msmnt_result*pi+curr_adptv_phase*pi/180
        t_n = 2^(adptv_steps-curr_adptv_step)
        k_opt =-2^(adptv_steps-curr_adptv_step+1)+2^(adptv_steps+1)
        DATA_25 [sweep_index] = k_opt
        par_76 =1
        timer = -1
        mode = 8
        
      CASE 8  'copy prob array
        'copy current arrays into old arrays
        FOR k = 1 TO 2^(adptv_steps+2)+1
          p0_real[k] = p_real[k]
          p0_imag[k] = p_imag[k]
        NEXT k
        k_for = 2^adptv_steps
        timer = -1
        mode = 9
      
      CASE 9 'Bayesian update rule for phase estimation
      
        p_real [k] = 0.5*p0_real[k] + 0.25*(COS(c_n)*(p0_real [k-t_n] + p0_real [k+t_n]) - SIN(c_n)*(p0_imag [k-t_n] - p0_imag [k+t_n])) 
        p_imag [k] = 0.5*p0_imag[k] + 0.25*(COS(c_n)*(p0_imag [k-t_n] + p0_imag [k+t_n]) + SIN(c_n)*(p0_real [k-t_n] - p0_real [k+t_n])) 
        k_for = k_for + 1
        if (k_for>=3*2^adptv_steps) then
          mode = 10
          timer=-1
        endif
        'timer = -1

      CASE 10 'define optimal phase according to Cappellaro protocol
        curr_adptv_phase = mod(-0.5*ARCTAN (p_imag[k_opt]/(p_real[k_opt]))*(180/3.14), 360)
        IF (curr_adptv_phase < 0) THEN
          curr_adptv_phase = curr_adptv_phase+ 360
        ENDIF    
        DATA_24[sweep_index] = curr_adptv_step
        inc (curr_adptv_step)
        timer=-1
        mode = 0
      
        
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


