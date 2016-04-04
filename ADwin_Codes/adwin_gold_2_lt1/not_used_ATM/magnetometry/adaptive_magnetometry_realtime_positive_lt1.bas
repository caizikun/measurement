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
' Info_Last_Save                 = TUD277246  DASTUD\TUD277246
'<Header End>
'This code implements adaptive magnetometry protocols.
'--------------------------------------------------------------------------------------------------------------
'The protocols calculates in real-time the adaptive phase, according to the Cappellaro algorithm, and then 
'converts it to a 8-bit number used to control the FPGA. To speed up the Bayesian update of the probability
'ditribution, we take different assumptions into use:
'1) probability density real: we can restrict ourselves to p[k], k>0
'2) we track only non-zero coefficients p[k]
'3) we track only coefficients p[k], which contribute to hte optimal phase
'To ensure that each mode is completed within 1us, we distribute the Bayesian update step in modes 7-12.
'
'There are N adaptive measurement steps, and the number of measurements per step is set by M.
'For each of the M measurements (Bayesian update), it's possible to obtain the result as a majority vote
'over maj_reps ssro-s, with threshold maj_thr.
'
'No nitrogen initialization is performed, but the three hyperfine lines are driven separately.
'
' summary of modes:
' mode  0:    re-initialization probability distribution coefficients p[k]
' mode  1:    CR-check
' mode  2:    calculation optimal phase according to Cappellaro's formula
' mode  3:    set phase to FPGA
' mode  4:    spin pumping with A pulse
' mode  5:    AWG: (N-init)+ Ramsey
' mode  6:    Ex pulse and photon counting (manages M>1, maj_reps, etc)
' mode  7-12: Bayesian update of probability density coeff p[k]   
'--------------------------------------------------------------------------------------------------------------

#INCLUDE ADwinGoldII.inc
#INCLUDE .\cr.inc
#INCLUDE Math.inc

#DEFINE max_stat            10
#DEFINE max_prob_array       16400
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_27[20] AS LONG 'array to set artificial detuning
DIM DATA_28[20] AS LONG 'array used to load pre-calculated msmnt results for tests
DIM ch[8] AS LONG
DIM ch_value[8] AS LONG
DIM indiv_ssro[25] AS LONG
DIM p_imag[max_prob_array] AS FLOAT 
DIM p_real[max_prob_array] AS FLOAT
DIM p0_imag[max_prob_array] AS FLOAT
DIM p0_real[max_prob_array] AS FLOAT
'return
DIM DATA_24[max_repetitions] AS LONG  ' adaptive phase (0..255)
DIM DATA_25[max_repetitions] AS LONG  ' msmnt results (each one is the nr of click obtained in M msmnts, not taking ssro fid into account)
DIM DATA_29[max_repetitions] AS LONG  'timer data
DIM DATA_33[5000] AS FLOAT            ' float debug array
DIM DATA_34[5000] AS FLOAT            ' float debug array
DIM DATA_35[5000] AS FLOAT            ' float debug array
DIM DATA_36[5000] AS FLOAT            ' float debug array
DIM DATA_37[5000] AS FLOAT            ' float debug array
DIM DATA_38[5000] AS FLOAT
DIM DATA_39[5000] AS FLOAT
DIM DATA_40[5000] AS LONG
DIM DATA_41[5000] AS LONG
DIM DATA_42[5000] AS LONG
DIM DATA_43[5000] AS LONG

DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel , AWG_done_DI_pattern AS LONG
DIM wait_for_AWG_done, sequence_wait_time AS LONG
DIM repetitions, SSRO_stop_after_first_photon, sweep_length AS LONG
DIM SSRO_duration, cycle_duration, SP_duration, wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM E_MBI_voltage, E_N_randomize_voltage, A_N_randomize_voltage, repump_N_randomize_voltage AS FLOAT
DIM SP_E_duration, AWG_event_jump_DO_channel, AWG_done AS LONG

DIM timer, aux_timer, mode, i, sweep_index, a AS LONG
DIM wait_time, counts, old_counts AS LONG
DIM first, do_adaptive, do_ext_test AS LONG

DIM repetition_counter, k_sweep AS LONG
DIM N, t_n, curr_adptv_phase_deg, dig_phase, curr_n, rep_index, curr_msmnt_result, curr_m, M, M_count AS LONG
DIM maj_ssro, curr_maj, maj_thr, maj_reps AS LONG
DIM do_calculate_phase, fpga_phase AS LONG
DIM pi, th, real, imag, curr_adptv_phase AS FLOAT
DIM timer1, timer2, save_p_k AS LONG
DIM G, F, renorm_ssro_M, nr_ones, nr_zeros, update_zero, update_one, m_sweep_index AS LONG
DIM fid0, fid1, c0, c1, cos0, cos1, sin0, sin1, p0i_min AS FLOAT



LowINIT:  
  init_CR()
  AWG_start_DO_channel         = DATA_20[1]
  AWG_done_DI_channel          = DATA_20[2]
  wait_for_AWG_done            = DATA_20[3]
  AWG_event_jump_DO_channel    = DATA_20[4]
  SP_duration                  = DATA_20[5]
  sequence_wait_time           = DATA_20[6]
  wait_after_pulse_duration    = DATA_20[7]
  repetitions                  = DATA_20[8]   'now this is the nr of times we repeat the series of adaptive msmnt steps
  SSRO_duration                = DATA_20[9]
  SSRO_stop_after_first_photon = DATA_20[10]   ' not used
  cycle_duration               = DATA_20[11]  '(in processor clock cycles, 3.333ns)
  sweep_length                 = DATA_20[12]
  do_adaptive                  = DATA_20[13]  'do_adaptive=1 activates adptv protocol, =0 uses phases in DATA_27 as non-adaptive
  N                            = DATA_20[14]  'nr of msmnt steps in adaptive protocol
  ch[1]                        = DATA_20[15]  'adwin channels for 8-bit phase to FPGA
  ch[2]                        = DATA_20[16]  'physical channels ADWIN-FPGA
  ch[3]                        = DATA_20[17]
  ch[4]                        = DATA_20[18]
  ch[5]                        = DATA_20[19]
  ch[6]                        = DATA_20[20]
  ch[7]                        = DATA_20[21]
  ch[8]                        = DATA_20[22]
  do_ext_test                  = DATA_20[23]  'if do_ext_test>0, msmnt results are taken from DATA_27 array (debug mode with pre-calculated results)
  M                            = DATA_20[24]  'number of measurements per adaptive step (constant M)
  maj_thr                      = DATA_20[25]
  maj_reps                     = DATA_20[26]
  G                            = DATA_20[27]
  F                            = DATA_20[28]
  renorm_ssro_M                = DATA_20[29] 'if >0, ssro fidelities are used to normalize the nr of clicks acquired while sweeping M
  save_p_k                     = DATA_20[30] 'gives the possibility to save one instance of the p_k distrib (value is the step n at which it's saved, no saving for n<1)
    
  pi = 3.141592653589793
  
  fid0                         = DATA_21[1] 'ssro fidelity for ms=0
  fid1                         = DATA_21[2] 'ssro fidelity for ms=1

  FOR i = 1 TO repetitions*N
    DATA_24[i] = 0
  NEXT i
     
  FOR i = 1 TO repetitions*N
    DATA_25[i] = 0
  NEXT i

  FOR i = 1 TO repetitions*N
    DATA_29[i] = 0
  NEXT i
  
  FOR i = 1 TO repetitions*N*M
    DATA_33[i] = 0
    DATA_34[i] = 0
    DATA_35[i] = 0
    DATA_36[i] = 0
    DATA_37[i] = 0
  NEXT i

  FOR i = 1 TO repetitions*N*M
    DATA_40[i] = 0
    DATA_41[i] = 0
    DATA_42[i] = 0
    DATA_43[i] = 0
  NEXT i
    
  FOR i = 1 TO 2^(N+1)+1
    DATA_38[i] = 0
    DATA_39[i] = 0
  NEXT i

      
  FOR i = 1 TO M+2
    indiv_ssro[i]=0
  NEXT i
  
  FOR i = 1 TO 8
    ch_value[i] = 0
  NEXT i
    
  FOR i = 1 TO 2^(N+1)+1
    p_real[i] = 0
    p_imag[i] = 0
    p0_real[i] = 0
    p0_imag[i] = 0
  NEXT i    
    
  p_real[1] = 1/(2*pi)
  
  AWG_done_DI_pattern = 2 ^ AWG_done_DI_channel

  repetition_counter  = 0
  first               = 0
  wait_after_pulse    = 0
  
  DAC(E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
  DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
  DAC(repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off repump
  CNT_CLEAR(counter_pattern)    'clear counter
  CNT_ENABLE(0000b)'turn off all counters
  CNT_MODE(counter_channel,00001000b) 'configure counter

  CONF_DIO(0011b)  'configure DIO 00:07 as output, all other ports as input
  DIGOUT(AWG_start_DO_channel,0)
  DIGOUT(AWG_event_jump_DO_channel,0)
  
  FOR i = 0 TO 7
    DIGOUT(ch[8-i], 0)
  NEXT i
 
  sweep_index = 0
  m_sweep_index = 0
  mode = 0
  timer = 0
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter
  curr_adptv_phase = 0
  rep_index = 1
  curr_n = 0
  curr_m = 1
  curr_maj = 1
  curr_msmnt_result = 1
  maj_ssro = 0
  a = 0
  real = 1
  imag=0
  nr_ones = 0
  nr_zeros = 0


EVENT:
    
  PAR_77=mode  
  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE
  
    SELECTCASE mode

      CASE 0 're-initialize probability array
        FOR i = 1 TO 2^(N+1)+1
          p_real[i] = 0
          p_imag[i] = 0
          DATA_38[i] = 0
          DATA_39[i] = 0
        NEXT i    
        p_real[1] = 1'/(2*pi)
        curr_adptv_phase = 0
        curr_n = 0
        curr_m = 1
        curr_maj = 1
        mode = 1
        timer = -1      
              
              
      CASE 1 'CR check
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 2
          timer = -1
          first = 0          
        ENDIF


      CASE 2 'estimate optimal phase according to Cappellaro protocol
        inc(curr_n)
        inc(sweep_index)
        
        if ((save_p_k > 0) and (save_p_k <= N))then
          if (curr_n=save_p_k) then 'output probability array for debugging
            MemCpy (p_real[1], DATA_38[1], 2^N+1)
            MemCpy (p_imag[1], DATA_39[1], 2^N+1)                  
          endif        
        endif
        
        
        t_n = 2^(N-curr_n)
        
      
        real = p_real[1+2*t_n]
        imag = -p_imag[1+2*t_n]  
 
        if (real>0) then
          th = arctan (imag/real)
        else
          if (real<0) then
            if (imag>=0) then
              th = arctan(imag/real) + pi
            else
              th = arctan(imag/real) - pi
            endif
          endif
        endif

        if (real=0) then
          if (imag>0) then
            th = pi/2
          else
            if (imag<0) then
              th = -pi/2
            endif
          endif
        endif
        
        if ((imag=0) and (real=0)) then
          th = 0
        endif      
                     
        curr_adptv_phase = 0.5*th
        curr_adptv_phase_deg = round(0.5*th*(180/pi))
            
        timer=-1
        mode = 3
        do_calculate_phase = 0
        

      CASE 3    'set phase to fpga

        fpga_phase = mod(curr_adptv_phase_deg + DATA_27[curr_n], 360)
        IF (fpga_phase < 0) THEN
          fpga_phase = fpga_phase + 360
        ENDIF

        a=fpga_phase*255/360
        FOR i = 0 TO 7
          dig_phase = mod (a, 2)
          a = a/2
          'set hardware phase channel (8-i) to dig_phase
          DIGOUT(ch[i+1], dig_phase)
          ch_value[i+1] = dig_phase
        NEXT i
                 
        DATA_33 [sweep_index] = curr_adptv_phase_deg
        DATA_34 [sweep_index] = p_real [1+t_n]      
        DATA_35 [sweep_index] = p_real [1+2*t_n]
        DATA_36 [sweep_index] = p_imag [1+t_n]      
        DATA_37 [sweep_index] = p_imag [1+2*t_n]
        DATA_24 [sweep_index] = 1*ch_value[1]+2*ch_value[2]+4*ch_value[3]+8*ch_value[4]+16*ch_value[5]+32*ch_value[6]+64*ch_value[7]+128*ch_value[8]
        'DATA_24[sweep_index]= curr_adptv_phase
        mode = 4
        timer = -1
              
              
      CASE 4    'A laser spin pumping
        IF (timer = 0) THEN
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
        else
          counts = CNT_READ(counter_channel)
        Endif

        IF (timer = SP_duration) THEN
          DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                                    
          mode = 5                 
          wait_after_pulse = wait_after_pulse_duration
          timer = -1
        ENDIF
      
      CASE 5    '  wait for AWG sequence (Ramsey)
        IF (timer = 0) THEN
          DIGOUT(AWG_start_DO_channel,1)  'AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          DIGOUT(AWG_start_DO_channel,0)
          aux_timer = 0
          AWG_done = 0
        ELSE
          IF ((DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN
            mode = 6
            timer = -1
            wait_after_pulse = 0
            
            IF ((curr_m=M) AND (curr_maj=maj_reps)) THEN
              DIGOUT(AWG_event_jump_DO_channel,1)  'AWG event_jump trigger
              CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              DIGOUT(AWG_event_jump_DO_channel,0)
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

          IF (curr_maj<maj_reps) THEN
            mode = 4 
            timer = -1
            inc(curr_maj)
          ELSE
            if (maj_ssro > maj_thr) then
              indiv_ssro[curr_m] = 1
            else
              indiv_ssro[curr_m] = 0
            endif
            maj_ssro = 0
            curr_maj = 1

            par_80 = curr_m 
            inc(m_sweep_index)
            IF (curr_m < M) THEN
              mode = 4 
              timer = -1
              inc(curr_m)
              do_calculate_phase = 0
            ELSE
              timer = -1
              M_count=0
              FOR i = 1 TO M
                M_count = M_count + indiv_ssro[i]
              NEXT i
              if (do_ext_test>0) then
                curr_msmnt_result = DATA_28[curr_n]      
              endif
              DATA_25[sweep_index] = curr_msmnt_result
              inc (repetition_counter) 'needed to print completed reps in qtlab
              PAR_73 = repetition_counter
              curr_m = 1

              IF (curr_n < N) THEN 
                mode = 7 
                timer=-1
              ELSE
                curr_n = 0
                inc(rep_index)
                         
                IF (rep_index > repetitions) THEN
                  'reset fpga phase 
                  FOR i = 0 TO 7
                    DIGOUT(ch[i+1], 0) 'set hardware phase channel (8-i) to zero
                  NEXT i
              
                  END
                ENDIF
                'curr_adptv_phase = 0
                mode = 0 're-init probability arrays
                timer=-1
              ENDIF
            ENDIF
            timer = -1
            wait_after_pulse = wait_after_pulse_duration
            first = 1
          ENDIF
          
        ENDIF       
        
      CASE 7    'set Bayesian update parameters --- renormalize ssro
        
        timer1 = Read_Timer()
        if (renorm_ssro_M>0) then
          nr_ones = round(curr_msmnt_result/fid0)
        else
          nr_ones = curr_msmnt_result
        endif

        DATA_25[sweep_index] = curr_msmnt_result
        DATA_24[sweep_index] = curr_adptv_phase
                        
        if (nr_ones>M) then
          nr_ones = M
        endif
        nr_ones = curr_msmnt_result
        nr_zeros = M-nr_ones
               
        c1 = 1*pi-curr_adptv_phase
        c0 = 0*pi-curr_adptv_phase
        cos0 = COS(c0)
        sin0  = SIN(c0)
        cos1 = COS(c1)
        sin1  = SIN(c1)       
                
        DATA_40[sweep_index] = t_n  
        update_zero = 0
        update_one = 0
        timer = -1
        mode = 8
        
      CASE 8 'check for-loop condition (ones)
        if (update_one<nr_ones) then
          mode = 9
          inc(DATA_41[sweep_index])
        else 
          mode = 14
        endif
                      
      CASE 9  'copy prob array
        'copy current arrays into old arrays        
        inc(m_sweep_index)
        MemCpy (p_real[1], p0_real[1], 2^(N+1)+1)
        MemCpy (p_imag[1], p0_imag[1], 2^(N+1)+1)
        timer = -1
        mode = 10
        k_sweep = 0
      
      CASE 10 'Bayesian update of ms=0 (1=click) for phase estimation (distributed in 4 modes)          
        p_real [1+k_sweep] = p0_real[1+k_sweep] + 0.5*(cos1*(p0_real [1+abs(k_sweep-t_n)] + p0_real [1+k_sweep+t_n])) 
        mode = 11
        
      CASE 11
        p0i_min = p0_imag[abs(k_sweep-t_n)]        
        if (k_sweep<t_n) then
          p0i_min = -p0i_min
        endif  
        p_real[1+k_sweep]=p_real[1+k_sweep]-0.5*(sin1*(p0i_min - p0_imag [1+k_sweep+t_n]))  
        mode = 12
        
      CASE 12
        p_imag [1+k_sweep] = p0_imag[1+k_sweep] + 0.5*(cos1*(p0i_min + p0_imag [1+k_sweep+t_n]))
        mode = 13
        
      CASE 13
        p_imag[1+k_sweep]=p_imag[1+k_sweep]+0.5*(sin1*(p0_real [1+abs(k_sweep-t_n)] - p0_real [1+k_sweep+t_n])) 
        timer=-1
        inc(k_sweep)
        if (k_sweep>2^N+1) then
          mode = 8
          inc(update_one)
          k_sweep = 0
        else
          mode = 10
        endif
        
      CASE 14 'check for-loop condition (zeros)
        k_sweep=0
        if (update_zero<nr_zeros) then
          inc(DATA_42[sweep_index])
          mode = 15
        else 
          mode = 1
          timer2 = Read_Timer()
          DATA_29[sweep_index] = timer2-timer1
        endif
                           
      CASE 15  'copy prob array
        'copy current arrays into old arrays        
        inc(m_sweep_index)
        MemCpy (p_real[1], p0_real[1], 2^(N+1)+1)
        MemCpy (p_imag[1], p0_imag[1], 2^(N+1)+1)
        k_sweep=0
        timer = -1
        mode = 16
      
      CASE 16 'Bayesian update of ms=1 (0=click) for phase estimation (distributed in 4 modes)  
        p_real [1+k_sweep] = p0_real[1+k_sweep] + 0.5*(cos0*(p0_real [1+abs(k_sweep-t_n)] + p0_real [1+k_sweep+t_n])) 
        mode = 17
        
      CASE 17
        p0i_min = p0_imag[abs(k_sweep-t_n)]        
        if (k_sweep<t_n) then
          p0i_min = -p0i_min
        endif  
        p_real[1+k_sweep]=p_real[1+k_sweep]-0.5*(sin0*(p0i_min - p0_imag [1+k_sweep+t_n]))  
        mode = 18
        
      CASE 18
        p_imag [1+k_sweep] = p0_imag[1+k_sweep] + 0.5*(cos0*(p0i_min + p0_imag [1+k_sweep+t_n]))
        mode = 19
        
      CASE 19
        p_imag[1+k_sweep]=p_imag[1+k_sweep]+0.5*(sin0*(p0_real [1+abs(k_sweep-t_n)] - p0_real [1+k_sweep+t_n])) 
        timer=-1
        inc (k_sweep)
        if (k_sweep>2^N+1) then
          inc(update_zero)
          mode = 14
          k_sweep= 0
        else
          mode = 16
        endif
          
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


