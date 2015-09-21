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
'Nitrogen spin initialization can be done by either MBI or deterministic (Wrachtrup) init.
'
' summary of modes:
' mode  0:  CR check
' mode  1:  E-SP (only MBI
' mode  2:  MBI pulse (only MBI)
' mode  3:  MBI-RO (only MBI)
' mode  4:  spin pumping with A pulse
' mode  5:  AWG: (N-init)+ Ramsey
' mode  6:  Ex pulse and photon counting (manages M>1, maj_reps, etc)
' mode  7:  choose optimal phase (from adaptive table)
' mode  8:  N-spin randomization (only MBI)
' -> mode 0

#INCLUDE ADwinGoldII.inc
#INCLUDE .\cr.inc
#INCLUDE Math.inc

#DEFINE max_stat            10
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_27[1000000] AS LONG 'adaptive phase decision tree
DIM ch[8] AS LONG
DIM ch_value[8] AS LONG
DIM indiv_ssro[25] AS LONG

'return
DIM DATA_24[max_repetitions] AS LONG  ' adaptive phase (0..255)
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
DIM E_MBI_voltage, E_N_randomize_voltage, A_N_randomize_voltage, repump_N_randomize_voltage AS FLOAT

DIM timer, aux_timer, mode, i, k, sweep_index, a AS LONG
DIM AWG_done AS LONG
DIM first, do_adaptive, do_phase_calibr AS LONG
DIM delta_phi AS LONG

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern, do_MBI AS LONG
DIM counts, old_counts , threshold_majority_vote, reps_majority_vote AS LONG
DIM adptv_steps, curr_adptv_phase, dig_phase, curr_adptv_step, rep_index, curr_msmnt_result, curr_ssro, M AS LONG
DIM t1, p, M_count, p0 AS LONG
DIM SP_E_duration, AWG_event_jump_DO_channel, MBI_duration, MBI_attempts_before_CR, MBI_threshold, N_randomize_duration AS LONG
DIM current_MBI_attempt as LONG
DIM awg_in_is_hi, awg_in_was_hi, awg_in_switched_to_hi as long
DIM wait_time AS LONG
DIM maj_ssro, curr_maj,maj_ssro_for_saving, do_event_jump AS LONG


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
  do_adaptive                  = DATA_20[12]  'do_adaptive=1 activates adptv protocol, =0 uses phases in DATA_27 as non-adaptive
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
  do_MBI                       = DATA_20[26]  
  SP_E_duration                = DATA_20[27]  'E spin pumping duration before MBI
  AWG_event_jump_DO_channel    = DATA_20[28]
  MBI_duration                 = DATA_20[29]
  MBI_attempts_before_CR       = DATA_20[30]
  MBI_threshold                = DATA_20[31]
  N_randomize_duration         = DATA_20[32]
  
  pi = 3.14
  
  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  E_MBI_voltage                = DATA_21[5]  
  E_N_randomize_voltage        = DATA_21[6]
  A_N_randomize_voltage        = DATA_21[7]
  repump_N_randomize_voltage   = DATA_21[8]
   
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

  do_event_jump = 0
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel

  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
  
  DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
  DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
  DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off repump
  CNT_CLEAR(  counter_pattern)    'clear counter
  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter


  CONF_DIO(0011b)  'configure DIO 00:07 as output, all other ports as input

  DIGOUT(AWG_start_DO_channel,0)

  FOR i = 0 TO 7
    'set hardware phase channel (8-i) to zero
    DIGOUT(ch[8-i], 0)
  NEXT i
 
  sweep_index = 1
  mode = 0
  timer = 0
  processdelay = cycle_duration  
  current_MBI_attempt = 1
  
  Par_73 = repetition_counter
  curr_adptv_phase = DATA_27[1]
  rep_index = 1
  curr_adptv_step = 1
  curr_ssro = 1
  curr_maj = 1
  curr_msmnt_result = 0
  maj_ssro = 0
  a = 0
  p = 0
  
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
          IF (do_MBI<1) THEN
            mode = 4
          ELSE
            mode = 1
          ENDIF
          
          timer = -1
          first = 0
        ENDIF
        
            
      CASE 1    ' E spin pumping
        
        IF (timer = 0) THEN
          DAC(E_laser_DAC_channel, 3277*E_SP_voltage+32768) ' turn on Ex laser      
        ELSE          
          IF (timer >= SP_E_duration) THEN
            CNT_ENABLE(0)
            DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser           
            mode = 2
            wait_time = wait_after_pulse_duration
            timer = -1
          ENDIF
        ENDIF
              
      CASE 2    ' MBI
        ' MBI starts now; we first need to trigger the AWG to do the selective pi-pulse
        ' then wait until this is done
        IF(timer=0) THEN
                 
          DIGOUT(AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)                    ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          DIGOUT(AWG_start_DO_channel,0)
                 
        ELSE
          awg_in_was_hi = awg_in_is_hi
          awg_in_is_hi = (DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern)
  
          'Detect if the AWG send a trigger
          if ((awg_in_was_hi = 0) and (awg_in_is_hi > 0)) then
            awg_in_switched_to_hi = 1
          else
            awg_in_switched_to_hi = 0
          endif
         
          ' we expect a trigger from the AWG once it has done the MW pulse
          ' as soon as we assume the AWG has done the MW pulse, we turn on the E-laser,
          ' and start counting
          IF(awg_in_switched_to_hi > 0) THEN
            
            mode = 3
            timer = 0     'set to 0 to make the duratio of the next mode, MBI RO, accurate to the us 
                       
            CNT_CLEAR(counter_pattern)    'clear counter
            CNT_ENABLE(counter_pattern)    'turn on counter
            DAC(E_laser_DAC_channel, 3277*E_MBI_voltage+32768) ' turn on Ex laser
          ENDIF
        ENDIF
      
      CASE 3  'MBI RO  
        counts = CNT_READ(counter_channel)
        IF (counts >= MBI_threshold) THEN
          DAC(E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
          CNT_ENABLE(0)
              
          DIGOUT(AWG_event_jump_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          DIGOUT(AWG_event_jump_DO_channel,0)
                
          mode = 4
          wait_time = MBI_duration-timer
          timer = -1
          current_MBI_attempt = 1
                         
          ' MBI succeeds if the counts surpass the threshold;
          ' we then trigger an AWG jump (sequence has to be long enough!) and move on to SP on A
          ' if MBI fails, we
          ' - try again (until max. number of attempts, after some scrambling)
          ' - go back to CR checking if max number of attempts is surpassed
            
        ELSE 
          IF (timer = MBI_duration) THEN
            DAC(E_laser_DAC_channel,3277*E_off_voltage+32768) ' turn off Ex laser
            CNT_ENABLE(0)
      
            IF (current_MBI_attempt = MBI_attempts_before_CR) then
              current_cr_threshold = cr_preselect
              mode = 0 '(check resonance and start over)
              current_MBI_attempt = 1
            ELSE
              mode = 8
              INC(current_MBI_attempt)
            ENDIF                
            timer = -1      
          ENDIF
        ENDIF          


      CASE 4    'A laser spin pumping
        IF (timer = 0) THEN
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
        else
          counts = CNT_READ(counter_channel)
        Endif

        IF (timer = SP_duration) THEN
          DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                
                    
          ' SET PHASE TO FPGA (8-bit)
          a=curr_adptv_phase
          FOR i = 0 TO 7
            dig_phase = mod (a, 2)
            a = a/2
            'set hardware phase channel (8-i) to dig_phase
            DIGOUT(ch[i+1], dig_phase)
            ch_value[i+1] = dig_phase
          NEXT i
          
          DATA_24 [sweep_index] = 1*ch_value[1]+2*ch_value[2]+4*ch_value[3]+8*ch_value[4]+16*ch_value[5]+32*ch_value[6]+64*ch_value[7]+128*ch_value[8]
          
          mode = 5                 
          wait_after_pulse = wait_after_pulse_duration
          timer = -1
        ENDIF
      
      CASE 5    '  wait for AWG sequence (Ramsey)
        IF (timer = 0) THEN
          DIGOUT(AWG_start_DO_channel,1)  ' AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          DIGOUT(AWG_start_DO_channel,0)
          aux_timer = 0
          AWG_done = 0
        ELSE
          IF ((DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN
            mode = 6
            timer = -1
            wait_after_pulse = 0
            
            IF (curr_ssro>=M) THEN
              DIGOUT(AWG_event_jump_DO_channel,1)  ' AWG trigger
              CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              DIGOUT(AWG_event_jump_DO_channel,0)
              do_event_jump = 0
            ENDIF
            
          ENDIF
        ENDIF
        
      CASE 6    'electron spin readout
        IF (timer = 0) THEN
          CNT_CLEAR(counter_pattern)    'clear counter
          CNT_ENABLE(counter_pattern)    'turn on counter
          DAC(E_laser_DAC_channel, 3277*E_RO_voltage+32768) ' turn on Ex laser
          DAC(A_laser_DAC_channel, 3277*A_RO_voltage+32768) ' turn on A laser
        ENDIF
         
        IF (timer = SSRO_duration) THEN
                   
          DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
          DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
          counts = CNT_READ(counter_channel)
          CNT_ENABLE(0)
          par_67 = counts
          IF (counts>0) THEN
            INC(maj_ssro)
          ENDIF

          IF (curr_maj<reps_majority_vote) THEN
            IF (do_MBI<1) THEN
              mode = 4 
            ELSE
              mode = 1
            ENDIF
            timer = -1
            inc(curr_maj)
          ELSE
            'DATA_25[sweep_index] = maj_ssro
            if (maj_ssro > threshold_majority_vote) then
              indiv_ssro[curr_ssro] = 1
            else
              indiv_ssro[curr_ssro] = 0
            endif
            maj_ssro = 0
            curr_maj = 1
                  
            'first=1
            par_80 = curr_ssro 
            
            IF (curr_ssro < M) THEN
              IF (do_MBI<1) THEN
                mode = 4 
              ELSE
                mode = 1
              ENDIF
              timer = -1
              inc(curr_ssro)
            ELSE
              do_event_jump = 1
              timer = -1
              M_count=0
              FOR i = 1 TO M
                M_count = M_count + indiv_ssro[i]
              NEXT i
            
              DATA_25[sweep_index] = M_count
            
              inc (sweep_index)
              inc(repetition_counter)
              PAR_73 = repetition_counter
              curr_ssro = 1

              IF (curr_adptv_step < adptv_steps) THEN 
                mode = 7
                timer=-1
              ELSE
                curr_adptv_step = 1
                inc(rep_index)
                       
                'reset fpga phase 
   
                IF (rep_index > repetitions) THEN
              
                  FOR i = 0 TO 7
                    DIGOUT(ch[i+1], 0) 'set hardware phase channel (8-i) to zero
                  NEXT i
              
                  END
                ENDIF
                curr_adptv_phase = DATA_27[1]
                mode = 0
                timer=-1
              ENDIF
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            first = 1
          ENDIF
          
        ENDIF
        
      CASE 7    'calculate optimal phase
        inc (curr_adptv_step)
        IF (do_adaptive>0) THEN
          p = 0
          FOR i = 1 TO curr_adptv_step-1
            p = p + DATA_25[sweep_index-curr_adptv_step+i]*((M+1)^(i-1)) 
          NEXT i
          p0 = ((M+1)^(curr_adptv_step-1)-1)/M+1         
          curr_adptv_phase = DATA_27[p0 + p] 'choose tabled phase for decision-tree stored in DATA_27
          'DATA_24[sweep_index] = p0+p
        ELSE
          curr_adptv_phase = DATA_27[curr_adptv_step]
        ENDIF                
        curr_msmnt_result = 0
        timer=-1
        mode = 0
        
      CASE 8 ' turn on the lasers to (hopefully) randomize the N-spin state before re-trying MBI
        
        if (timer = 0) then
          DAC(E_laser_DAC_channel,3277*E_N_randomize_voltage+32768)
          DAC(A_laser_DAC_channel,3277*A_N_randomize_voltage+32768)
          DAC(repump_laser_DAC_channel,3277*repump_N_randomize_voltage+32768)
        else
          if (timer = N_randomize_duration) then
            DAC(E_laser_DAC_channel,3277*E_off_voltage+32768)
            DAC(A_laser_DAC_channel,3277*A_off_voltage+32768)
            DAC(repump_laser_DAC_channel,3277*repump_off_voltage+32768)
            
            mode = 1
            timer = -1
            wait_time = wait_after_pulse_duration
            current_MBI_attempt = 1
          endif                    
        endif
  
      
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


