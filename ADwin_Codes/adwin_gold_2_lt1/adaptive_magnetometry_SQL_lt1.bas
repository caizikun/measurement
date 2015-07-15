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
'This code implements adaptive magnetometry protocols (plus swarm optimization phase increment).
'--------------------------------------------------------------------------------------------------------------
'The protocols calculates in real-time the otpimal phase, summing:
'1) a term corresponding to the Cappellaro algorithm (calculated before every read-out) 
'2) a phase increment retrieved from a 'swarm-optimization' array provided by Dominic Berry
'   (stored in DATA-40/41) dependent only on the previous msmnt outcome 
'
'The optimal phase is then converted to a 8-bit number used to control the FPGA. To speed up the Bayesian update 
' of the probability ditribution, we take different assumptions into use:
'1) probability density real: we can restrict ourselves to p[k], k>0
'2) we track only non-zero coefficients p[k]
'3) we track only coefficients p[k], which contribute to the optimal phase, cutting away the ones at the edges
'To ensure that each mode is completed within 1us, we distribute the Bayesian update step in modes 8-20.
'
'There are N adaptive measurement steps, and the number of measurements per step is set by M = G+F*(N-n).
'For each of the M measurements (Bayesian update), it's possible to obtain the result as a majority vote
'over maj_reps ssro-s, with threshold maj_thr.
'Compared to previous code, we store the probability arrays in a smarter way, storing only the elements we know
'are non-zero, using our assumptions on the probability distribution.
'
'No nitrogen initialization is performed, but the three hyperfine lines are driven separately.
'
' summary of modes:
' mode  0:    re-initialization probability distribution coefficients p[k]
' mode  1:    CR-check
' mode  2:    calculation optimal phase according to Cappellaro's formula
' mode  3:    set phase to FPGA
' mode  4:    set parameters relative to management msmnt for fixed tau (m)
' mode  5:    spin pumping with A pulse
' mode  6:    AWG: (N-init)+ Ramsey
' mode  7:    Ex pulse and photon counting (manages M>1, maj_reps, etc)
' mode  8-20: Bayesian update of probability density coeff p[k]   
'--------------------------------------------------------------------------------------------------------------

#INCLUDE ADwinGoldII.inc
#INCLUDE .\cr.inc
#INCLUDE Math.inc

#DEFINE max_stat              10
#DEFINE max_prob_array        2000
#DEFINE max_berry_array       50000
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_27[200] AS LONG 'array to set artificial detuning
DIM DATA_28[200] AS LONG 'array used to load pre-calculated msmnt results for tests
DIM DATA_50[max_berry_array] AS FLOAT 'swarm_optimized phases to be used for read-out outcome 0
DIM DATA_51[max_berry_array] AS FLOAT 'swarm_optimized phases to be used for read-out outcome 1
DIM ch[8] AS LONG
DIM ch_value[8] AS LONG
DIM indiv_ssro[250] AS LONG
DIM p_imag[max_prob_array] AS FLOAT 
DIM p_real[max_prob_array] AS FLOAT
DIM p0_imag[max_prob_array] AS FLOAT
DIM p0_real[max_prob_array] AS FLOAT
'return
DIM DATA_24[max_repetitions] AS LONG  ' adaptive phase (0..255)
DIM DATA_25[max_repetitions] AS LONG  ' msmnt results (each one is the nr of click obtained in M msmnts, not taking ssro fid into account)
DIM DATA_29[max_repetitions] AS LONG  'timer data
DIM DATA_33[50000] AS FLOAT            ' array to save optimal Cappellaro phase picked by adwin
'DIM DATA_38[max_prob_array] AS FLOAT
'DIM DATA_39[max_prob_array] AS FLOAT


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
DIM do_k_restretch, fpga_phase AS LONG
DIM pi, th, real, imag, curr_adptv_phase AS FLOAT
DIM timer1, timer2, save_pk_n, save_pk_m AS LONG
DIM G, F, m_sweep_index, swarm_opt_phase AS LONG
DIM fid0, fid1, c0, c1, cos0, cos1, sin0, sin1, p0i_min, T2 AS FLOAT
Dim var_M, ext_m_msmnt_result as LONG

DIM max_k_sweep, max_M, k, k_range as LONG
DIM r_ampl, r_offset, norm, res_idx, global_sweep_idx as FLOAT
DIM copy_size, n_copy, rest_copy, copy_index as LONG

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
  N                            = DATA_20[14]  'nr of msmnt steps in adaptive protocol (each with different sensing time t_n)
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
    
  pi = 3.141592653589793
  
  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]
  fid0                         = DATA_21[5] 'ssro fidelity for ms=0
  fid1                         = DATA_21[6] 'ssro fidelity for ms=1
  T2                           = DATA_21[7] 'T2* (in multiples of tau0)

  FOR i = 1 TO repetitions*N
    DATA_24[i] = 0
  NEXT i
     
  FOR i = 1 TO repetitions*(N*G+N*(N-1)*F/2)
    DATA_25[i] = 0
  NEXT i

  FOR i = 1 TO repetitions*N
    DATA_29[i] = 0
  NEXT i
  
  FOR i = 1 TO 250
    indiv_ssro[i]=0
  NEXT i
  
  FOR i = 1 TO 8
    ch_value[i] = 0
  NEXT i
    
  FOR i = 1 TO repetitions*(N*G+N*(N-1)*F/2)
    DATA_33[i] = 0
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
  global_sweep_idx = 1
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
  k_range = (max_M+10)
    

EVENT:

  PAR_77=mode  
  IF (wait_after_pulse > 0) THEN
    DEC(wait_after_pulse)
  ELSE
  
    SELECTCASE mode

      CASE 0 're-initialize probability array
        curr_n = 0
        curr_m = 0
        curr_maj = 1
        mode = 1
        timer = -1      
              
      CASE 1 'CR check and measurement sequence parameters initialization
       
        IF ( CR_check(first,repetition_counter) > 0 ) THEN
          mode = 42
          timer = -1
          first = 0          
        ENDIF
        
      CASE 42'measurement sequence parameters initialization
        inc(curr_n)
        inc(sweep_index)
        curr_m = 0        
        M = G        
        t_n = 1
        res_idx = 0
        mode = 2


      CASE 3    'set phase to fpga
        
        fpga_phase = mod(90 + DATA_27[curr_n], 360)
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
                 
        DATA_24 [sweep_index] =1*ch_value[1]+2*ch_value[2]+4*ch_value[3]+8*ch_value[4]+16*ch_value[5]+32*ch_value[6]+64*ch_value[7]+128*ch_value[8]
        mode = 4
        timer = -1
              
      CASE 4  'manage M
        inc(curr_m)
        mode = 5
        timer = -1
                    
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

          if *counts>0) then 
            DATA_25 [sweep_index] = DATA_25[sweep_index] + 1
          endif
          

          IF (curr_m < M) THEN
            mode = 8
            timer = -1
          ELSE
            timer = -1
            inc (repetition_counter) 
            PAR_73 = repetition_counter 'needed to print completed reps in qtlab

            IF (curr_n < N) THEN 
              mode = 8 
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
              timer2 = Read_Timer()
              DATA_29[sweep_index] = timer2-timer1
              timer=-1
            ENDIF
          ENDIF
          timer = -1
          wait_after_pulse = wait_after_pulse_duration
          first = 1
        ENDIF
          
      ENDIF       
        
        
        
  ENDSELECT
    
  Inc(timer)
ENDIF

FINISH:
  finish_CR()
  


