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
'3) we track only coefficients p[k], which contribute to the optimal phase, cutting away the ones at the edges
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
#DEFINE max_prob_array       200000
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_27[200] AS LONG 'array to set artificial detuning
DIM DATA_28[200] AS LONG 'array used to load pre-calculated msmnt results for tests
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
DIM DATA_38[max_prob_array] AS FLOAT
DIM DATA_39[max_prob_array] AS FLOAT
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

DIM timer, aux_timer, mode, i, sweep_index, phase_binary AS LONG
DIM wait_time, counts, old_counts AS LONG
DIM first, do_adaptive, do_ext_test AS LONG

DIM repetition_counter, k_sweep AS LONG
DIM N, t_n, curr_adptv_phase_deg, dig_phase, curr_n, rep_index, curr_msmnt_result, curr_m, M, M_count AS LONG
DIM maj_ssro, curr_maj, maj_thr, maj_reps AS LONG
DIM do_calculate_phase, fpga_phase AS LONG
DIM pi, th, real, imag, curr_adptv_phase AS FLOAT
DIM timer1, timer2, save_pk_n, save_pk_m AS LONG
DIM G, F, m_sweep_index AS LONG
DIM fid0, fid1, c0, c1, cos0, cos1, sin0, sin1, p0i_min, T2 AS FLOAT
Dim var_M, ext_m_msmnt_result as LONG

DIM max_k, max_k_sweep, nr_k, range_k_sweep, max_M as LONG
DIM r_ampl, r_offset, norm as FLOAT

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
  M                            = DATA_20[24]  'number of measurements per adaptive step (constant M). If M=0, we use M = G+F*(n-1), n=1..N
  maj_thr                      = DATA_20[25]
  maj_reps                     = DATA_20[26]
  G                            = DATA_20[27]
  F                            = DATA_20[28]
  save_pk_n                    = DATA_20[29] 'gives the possibility to save one instance of the p_k distrib (value is the step n at which it's saved, no saving for n<1)
  save_pk_m                    = DATA_20[30]
    
  pi = 3.141592653589793
  
  fid0                         = DATA_21[1] 'ssro fidelity for ms=0
  fid1                         = DATA_21[2] 'ssro fidelity for ms=1
  T2                           = DATA_21[3] 'T2* (in multiples of tau0)

  FOR i = 1 TO repetitions*N
    DATA_24[i] = 0
  NEXT i
     
  FOR i = 1 TO repetitions*N
    DATA_25[i] = 0
  NEXT i

  FOR i = 1 TO repetitions*N
    DATA_29[i] = 0
  NEXT i
  
  FOR i = 1 TO repetitions*N
    DATA_33[i] = 0
    DATA_34[i] = 0
    DATA_35[i] = 0
    DATA_36[i] = 0
    DATA_37[i] = 0
  NEXT i

  FOR i = 1 TO repetitions*N*(G+F*N)
    DATA_40[i] = 0
    DATA_41[i] = 0
    DATA_42[i] = 0
    DATA_43[i] = 0
  NEXT i
    
  FOR i = 1 TO max_k
    DATA_38[i] = 0
    DATA_39[i] = 0
  NEXT i

      
  FOR i = 1 TO (M+2)+G+F*N
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
  curr_m = 0
  curr_maj = 1
  curr_msmnt_result = 1
  maj_ssro = 0
  phase_binary = 0
  real = 1
  imag=0

  
  M = 0
  IF (M<1) THEN
    var_M = 1
  ELSE
    var_M = 0
  ENDIF

  max_M = G+F*N
  max_k = 2^N*(max_M/2+1)
  

EVENT:
    
  PAR_77=mode  
  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE
  
    SELECTCASE mode

      CASE 0 're-initialize probability array
        FOR i = 1 TO max_k
          p_real[i] = 0
          p_imag[i] = 0
          DATA_38[i] = 0
          DATA_39[i] = 0
        NEXT i    
        p_real[1] =1/(2*pi)
        curr_adptv_phase = 0
        curr_n = 0
        curr_m = 0
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
        
        if (var_M=1) then
          M = G+F*(curr_n-1)
        endif            
        
        t_n = 2^(N-curr_n)
        range_k_sweep = 2^N*(M+3)
        max_k_sweep = 2*t_n*(M+3)
        
        if (max_k_sweep > range_k_sweep) then
          nr_k = range_k_sweep/t_n
          max_k_sweep = nr_k*t_n
        endif
        
        real = p_real[1+2*t_n]
        imag = -p_imag[1+2*t_n]  
        
        if (abs(imag/real)<1e-8) then
          imag = 0
        endif
         
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

        if (abs(real)<1e-10) then
          if (imag>0) then
            th = pi/2
          else
            if (imag<0) then
              th = -pi/2
            endif
          endif
        endif
        
        if ((abs(imag)<1e-10) and (abs(real)<1e-10)) then
          th = 0
        endif

                     
        curr_adptv_phase = 0.5*th
        curr_adptv_phase_deg = round(0.5*th*(180/pi))
            
        timer=-1
        mode = 3
        do_calculate_phase = 0
        

      CASE 3    'set phase to fpga
        
        if (do_ext_test>0) then
          ext_m_msmnt_result = DATA_28[curr_n]      
        endif

        r_ampl = 0.5*(fid1-fid0)*exp(-(t_n/T2)^2)
        fpga_phase = mod(curr_adptv_phase_deg + DATA_27[curr_n], 360)
        IF (fpga_phase < 0) THEN
          fpga_phase = fpga_phase + 360
        ENDIF

        phase_binary=fpga_phase*255/360
        FOR i = 0 TO 7
          dig_phase = mod (phase_binary, 2)
          phase_binary = phase_binary/2
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
              
      CASE 4  'manage M
        inc(curr_m)
        'inc(DATA_41[sweep_index])
        if (do_ext_test>0) then
          ext_m_msmnt_result = ext_m_msmnt_result - 1
          if (ext_m_msmnt_result>-1) then 
            curr_msmnt_result = 1
            'inc(DATA_42[sweep_index])
          else
            curr_msmnt_result = 0
          endif
        endif
        mode = 5
                    
      CASE 5    'A laser spin pumping
        IF (timer = 0) THEN
          DAC(A_laser_DAC_channel, 3277*A_SP_voltage+32768)   ' turn on A laser
        else
          counts = CNT_READ(counter_channel)
        Endif

        IF (timer = SP_duration) THEN
          DAC(A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser                                    
          mode = 6                 
          wait_after_pulse = wait_after_pulse_duration
          timer = -1
        ENDIF
      
      CASE 6    '  wait for AWG sequence (Ramsey)
        IF (timer = 0) THEN
          DIGOUT(AWG_start_DO_channel,1)  'AWG trigger
          CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
          DIGOUT(AWG_start_DO_channel,0)
          aux_timer = 0
          AWG_done = 0
        ELSE
          IF ((DIGIN_LONG(DIO_MODULE) AND AWG_done_DI_pattern) > 0) THEN
            mode = 7
            timer = -1
            wait_after_pulse = 0
            
            IF ((curr_m=M) AND (curr_maj=maj_reps)) THEN
              DIGOUT(AWG_event_jump_DO_channel,1)  'AWG event_jump trigger
              CPU_SLEEP(9)               ' need >= 20ns pulse width; adwin needs >= 9 as arg, which is 9*10ns
              DIGOUT(AWG_event_jump_DO_channel,0)
            ENDIF
            
          ENDIF
        ENDIF
        
      CASE 7    'electron spin readout
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
            mode = 5 'to spin-pumping
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
            
            if (do_ext_test<1) then
              curr_msmnt_result = indiv_ssro[curr_m]
            else
              indiv_ssro[curr_m] = curr_msmnt_result
            endif

            IF (curr_m <= M) THEN
              'inc(m_sweep_index)
              mode = 8
              timer = -1
              do_calculate_phase = 0
            ELSE
              timer = -1
              M_count=0
              FOR i = 1 TO M
                M_count = M_count + indiv_ssro[i]
              NEXT i
              DATA_25[sweep_index] = M_count
              inc (repetition_counter) 
              PAR_73 = repetition_counter 'needed to print completed reps in qtlab
              curr_m = 0

              IF (curr_n < N) THEN 
                do_calculate_phase = 1
                mode = 1 
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
        
      CASE 8    'set Bayesian update parameters --- renormalize ssro
        
        timer1 = Read_Timer()

        c1 = curr_msmnt_result*pi+curr_adptv_phase
        if (c1>pi) then
          c1 = c1 -2*pi
        endif
        DATA_24[sweep_index] = M
        cos1 = COS(c1)
        sin1  = SIN(c1)       

        if (curr_msmnt_result = 1) then
          r_offset = 1-0.5*(fid0+fid1)
        else
          r_offset = 0.5*(fid0+fid1)
        endif
                        
        'inc(DATA_43[sweep_index])
        timer = -1
        mode = 9        
                     
      CASE 9  'copy prob array
        'copy current arrays into old arrays        
        MemCpy (p_real[1], p0_real[1], max_k)
        MemCpy (p_imag[1], p0_imag[1], max_k)
        timer = -1
        mode = 10
        k_sweep = 0
      
      CASE 10 'Bayesian update of ms=0 (1=click) for phase estimation (distributed in 4 modes)          
        p_real [1+k_sweep] = r_offset*p0_real[1+k_sweep] - 0.5*r_ampl*(cos1*(p0_real [1+abs(k_sweep-t_n)] + p0_real [1+k_sweep+t_n])) 
        mode = 11
        
      CASE 11
        p0i_min = p0_imag[1+abs(k_sweep-t_n)]        
        if (k_sweep<t_n) then
          p0i_min = -p0i_min
        endif  
        p_real[1+k_sweep]= p_real[1+k_sweep]-0.5*r_ampl*(sin1*(p0i_min - p0_imag [1+k_sweep+t_n]))
        mode = 12
        
      CASE 12
        p_imag [1+k_sweep] = r_offset*p0_imag[1+k_sweep] - 0.5*r_ampl*(cos1*(p0i_min + p0_imag [1+k_sweep+t_n]))
        mode = 13
        
      CASE 13
        p_imag[1+k_sweep]=p_imag[1+k_sweep]+0.5*r_ampl*(sin1*(p0_real [1+abs(k_sweep-t_n)] - p0_real [1+k_sweep+t_n])) 
        timer=-1
        k_sweep = k_sweep + t_n
        if (k_sweep>max_k_sweep-t_n) then
          mode = 14
          k_sweep = 0
          norm = p_real[1]*2*pi
        else
          mode = 10
        endif

      CASE 14 'normalization
        for k_sweep = 0 to max_k_sweep
          p_imag [1+k_sweep] = p_imag[1+k_sweep]/norm
          p_real [1+k_sweep] = p_real[1+k_sweep]/norm   
        next k_sweep
        mode = 15    
        m_sweep_index = (rep_index-1)*N*M+(curr_n-1)*M+curr_m
        'inc(m_sweep_index)
        DATA_40 [m_sweep_index] = DATA_40 [m_sweep_index] + curr_msmnt_result
        DATA_41 [m_sweep_index] = r_offset*1e9
        DATA_42 [m_sweep_index] = cos1*1e9
        DATA_43 [m_sweep_index] = sin1*1e9
        
      CASE 15 'possibly save p_k
        if ((save_pk_n > 0))then
          if ((curr_n=save_pk_n) and (curr_m=save_pk_m)) then 'output probability array for debugging
            MemCpy (p_real[1], DATA_38[1], max_k)
            MemCpy (p_imag[1], DATA_39[1], max_k)                  
          endif        
        endif
        if (do_calculate_phase>0) then
          mode = 1 'this has to go back to either spin pumping or CR-check!!!
        else
          mode = 4 'new m-step
        endif
            
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


