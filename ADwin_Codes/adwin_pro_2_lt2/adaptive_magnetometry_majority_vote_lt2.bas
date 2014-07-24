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
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
'<Header End>
'This program implements adaptive magnetometry protocols.
'The adaptive phase decision tree is passed as an array (DATA_27), as an integer in the range 0..255, 
'which is then converted to a 8-bit number used to control the FPGA.
'The number of measurements per step is set by M.
'
' protocol:
' mode  0:  CR check
' mode  1:  spin pumping with A pulse
' mode  2:  AWG (N-init, Ramsey)
' mode  3:  Ex pulse and photon counting for spin-readout with time dependence (repetitive e-spin ssro)
' mode  4:  choose optimal phase
' -> mode 0

'MAJORITY VOTE!!!!

#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
#INCLUDE .\cr.inc
#INCLUDE Math.inc

#DEFINE max_stat            10
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_27[50000] AS LONG 'adaptive phase decision tree
DIM ch[8] AS LONG
DIM ch_value[8] AS LONG
DIM indiv_ssro[25] AS LONG

'return
DIM DATA_24[max_repetitions] AS LONG  ' adaptive phase (0..255)
DIM DATA_25[max_repetitions] AS LONG  ' SSRO counts spin readout
DIM DATA_28[max_repetitions] AS LONG  ' majority vote results

DIM AWG_start_DO_channel, AWG_done_DI_channel, APD_gate_DO_channel AS LONG
DIM wait_for_AWG_done AS LONG
DIM sequence_wait_time AS LONG

DIM SP_duration AS LONG
DIM repetitions, SSRO_duration, SSRO_stop_after_first_photon, sweep_length AS LONG
DIM cycle_duration AS LONG
DIM wait_after_pulse, wait_after_pulse_duration AS LONG

DIM E_SP_voltage, A_SP_voltage, E_RO_voltage, A_RO_voltage AS FLOAT
DIM c_n, t_n, pi AS FLOAT

DIM timer, aux_timer, mode, i, k, sweep_index, a AS LONG
DIM AWG_done AS LONG
DIM first, do_adaptive, do_phase_calibr AS LONG
DIM delta_phi AS LONG

DIM repetition_counter AS LONG
DIM AWG_done_DI_pattern AS LONG
DIM counts, old_counts , threshold_majority_vote AS LONG
DIM adptv_steps, curr_adptv_phase, dig_phase, curr_adptv_step, rep_index, curr_msmnt_result, curr_ssro, M AS LONG
DIM t1, p AS LONG

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
  
  pi = 3.14
  
  E_SP_voltage                 = DATA_21[1]
  A_SP_voltage                 = DATA_21[2]
  E_RO_voltage                 = DATA_21[3]
  A_RO_voltage                 = DATA_21[4]

  
   
  FOR i = 1 TO repetitions*adptv_steps
    DATA_25[i] = 0
  NEXT i
  
  FOR i = 1 TO repetitions*adptv_steps
    DATA_28[i] = 0
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
  FOR i = 0 TO 7
    'set hardware phase channel (8-i) to zero
    P2_DIGOUT(DIO_Module,ch[8-i], 0)
  NEXT i
 
  sweep_index = 1
  mode = 0
  timer = 0
  processdelay = cycle_duration  
  
  Par_73 = repetition_counter
  curr_adptv_phase = DATA_27[1]
  rep_index = 1
  curr_adptv_step = 1
  curr_ssro = 1
  curr_msmnt_result = 0
  a = 0
  p = 0

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
                    
          ' SET PHASE TO FPGA (8-bit)
          a=curr_adptv_phase
          FOR i = 0 TO 7
            dig_phase = mod (a, 2)
            a = a/2
            'set hardware phase channel (8-i) to dig_phase
            P2_DIGOUT(DIO_Module,ch[i+1], dig_phase)
            ch_value[i+1] = dig_phase
          NEXT i
          
          DATA_24 [sweep_index] = 1*ch_value[1]+2*ch_value[2]+4*ch_value[3]+8*ch_value[4]+16*ch_value[5]+32*ch_value[6]+64*ch_value[7]+128*ch_value[8]
          
          mode = 2                 
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
        ENDIF
         
        IF (timer = SSRO_duration) THEN
                   
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
          counts = P2_CNT_READ(CTR_MODULE,counter_channel)
          P2_CNT_ENABLE(CTR_MODULE,0)

          if (counts > 0) then
            indiv_ssro[curr_ssro] = 1 
          else
            indiv_ssro[curr_ssro] = 0 
          endif
                  
          'first=1
          par_80 = curr_ssro 
          
          IF (curr_ssro < M) THEN
            mode = 1
            timer = -1
            inc(curr_ssro)
          ELSE
            
            p=0
            FOR i = 1 TO M
              p = p + indiv_ssro[i]
            NEXT i

            IF (p>threshold_majority_vote-1) THEN
              curr_msmnt_result = 1
            ELSE
              curr_msmnt_result = 0
            ENDIF
            
            DATA_25[sweep_index] = p       
            DATA_28[sweep_index] = curr_msmnt_result       

            inc (sweep_index)
            inc(repetition_counter)
            PAR_73 = repetition_counter
            curr_ssro = 1

            IF (curr_adptv_step < adptv_steps) THEN 
              mode = 4
              timer=-1
            ELSE
              curr_adptv_step = 1
              inc(rep_index)
                       
              'reset fpga phase 
   
              IF (rep_index > repetitions) THEN
              
                FOR i = 0 TO 7
                  P2_DIGOUT(DIO_Module,ch[i+1], 0) 'set hardware phase channel (8-i) to zero
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
        
      CASE 4    'calculate optimal phase
        inc (curr_adptv_step)
        IF (do_adaptive>0) THEN
          p = 0
          FOR i = 1 TO curr_adptv_step-1
            p = p + DATA_28[sweep_index-curr_adptv_step+i]*(2^(i-1)) 
          NEXT i
          curr_adptv_phase = DATA_27[p + 2^(curr_adptv_step-1)] 'choose tabled phase for decision-tree stored in DATA_27
          'DATA_24[sweep_index] = p + 2^(curr_adptv_step-1) 
        ELSE
          curr_adptv_phase = DATA_27[curr_adptv_step]
        ENDIF                
        curr_msmnt_result = 0
        timer=-1
        mode = 0
      
    ENDSELECT
    
    Inc(timer)
  ENDIF

FINISH:
  finish_CR()
  


