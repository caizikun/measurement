'<ADbasic Header, Headerversion 001.001>
'<Header End>
' this program implements CR check fully controlled by ADwin Gold II
'
' protocol:
' mode  0:  green pulse, 
'           photon counting just for statistics
' mode  1:  E/A pulse, photon counting  ->  CR check
'           fail: -> mode 0

#DEFINE max_repetitions 500000
#DEFINE max_stat           10



'init
DIM DATA_30[100] AS LONG               ' CR integer parameters
DIM DATA_31[100] AS FLOAT              ' CR float parameters


DIM DATA_18[max_repump_duration] AS FLOAT 'AT EM_LOCAL 'repump freq voltage sine
DIM DATA_19[max_CR_duration] AS FLOAT 'AT EM_LOCAL 'CR gate voltage sine

'return
DIM DATA_22[max_repetitions] AS LONG  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG ' CR counts after sequence
DIM DATA_26[max_stat] AS LONG         ' statistics


DIM cr_mode, cr_timer AS LONG
DIM cr_counts, cr_old_counts AS LONG
DIM CR_probe, CR_preselect, CR_repump, current_CR_threshold AS LONG
DIM repumps, CR_failed, total_repump_counts AS LONG
DIM repump_duration, CR_duration AS LONG
DIM cr_wait_after_pulse, cr_wait_after_pulse_duration AS LONG
DIM counter_channel, counter_pattern AS LONG
DIM E_laser_DAC_channel, A_laser_DAC_channel, repump_laser_DAC_channel AS LONG
DIM repump_mod_DAC_channel, cr_mod_DAC_channel AS LONG

DIM repump_voltage, repump_off_voltage, E_CR_voltage, A_CR_voltage, E_off_voltage, A_off_voltage AS FLOAT
DIM cr_mod_control_offset, cr_mod_control_amp, cr_mod_control AS FLOAT
DIM repump_mod_control,repump_mod_control_offset, repump_mod_control_amp AS FLOAT

SUB init_CR()
  counter_channel              = DATA_30[1]
  repump_laser_DAC_channel     = DATA_30[2]
  E_laser_DAC_channel          = DATA_30[3]
  A_laser_DAC_channel          = DATA_30[4]
  repump_duration              = DATA_30[5]
  CR_duration                  = DATA_30[6]
  cr_wait_after_pulse_duration = DATA_30[7]
  CR_preselect                 = DATA_30[8]
  CR_probe                     = DATA_30[9]
  CR_repump                    = DATA_30[10]
  repump_mod_DAC_channel       = 4'DATA_30[11]
  cr_mod_DAC_channel           = 1'DATA_31[12] 'could also get out of a par!

  repump_voltage               = DATA_31[1]
  repump_off_voltage           = DATA_31[2]
  E_CR_voltage                 = DATA_31[3]
  A_CR_voltage                 = DATA_31[4]
  E_off_voltage                = DATA_31[5]
  A_off_voltage                = DATA_31[6]
  repump_mod_control_offset    = 5.0'DATA_31[7]
  repump_mod_control_amp       = 0.0'DATA_31[8]
  'cr_mod_control_offset        = 2.340466867469'DATA_31[9]
  'cr_mod_control_amp           = 0.002'DATA_31[10]
  
  
  FOR i = 1 TO max_stat
    DATA_26[i] = 0
  NEXT i
  
  'fill data_18 with a sine for repump mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR i = 1 TO repump_duration
    DATA_18[i] = Sin(-3.14+2*3.14*i/repump_duration)
  NEXT i
  'fill data_19 with a sine for cr mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR i = 1 TO CR_duration
    DATA_19[i] = Sin(-3.14+2*3.14*i/CR_duration)
  NEXT i
  
  counter_pattern     = 2 ^ (counter_channel-1)
  total_repump_counts = 0
  CR_failed           = 0
  repumps             = 0
  cr_wait_after_pulse    = 0
  cr_mode = 0
  cr_timer = 0
  
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' number of repumps
  PAR_72 = 0                      ' number of CR checks performed (lt1)
  Par_75 = CR_preselect
  Par_68 = CR_probe
  par_69 = CR_repump
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' CR below treshold events
  
  FPar_78 = 0.0                   'repump gate error
  FPar_79 = 0.0                   'cr gate error
ENDSUB



FUNCTION CR_check(first_cr, repetition_index) As LONG
  
  CR_preselect                 = PAR_75
  CR_probe                     = PAR_68
  CR_repump                    = PAR_69
  CR_check = 0
  
  IF (cr_wait_after_pulse > 0) THEN
    DEC(cr_wait_after_pulse)
  ELSE

    SELECTCASE cr_mode 
      CASE 0    ' green repump
              
        IF (cr_timer = 0) THEN
          IF (cr_counts < CR_repump)  THEN  'only repump 
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
            P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on green
            repumps = repumps + 1
            inc(par_71)
            
            '------------repump modulation control
            cr_old_counts = 0
            i=2
            repump_mod_control_amp = -1.0*repump_mod_control_amp
            '--------------------------------
            
          ELSE
            cr_mode = 1
            cr_timer = -1
            current_CR_threshold = CR_preselect
          ENDIF
        
        ELSE 
          
          IF (cr_timer = repump_duration) THEN
            
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off green
            cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            P2_CNT_ENABLE(CTR_MODULE,0)
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)
            
            total_repump_counts = total_repump_counts + cr_counts
            PAR_76 = total_repump_counts
            
            cr_mode = 1
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
            current_cr_threshold = CR_preselect
          ELSE 
            '------------repump modulation control
            IF (i = 0) THEN
              i=2
              repump_mod_control=DATA_18[cr_timer]
              P2_DAC(DAC_MODULE,repump_mod_DAC_channel, 3277*(repump_mod_control_amp*repump_mod_control+repump_mod_control_offset)+32768) ' put current voltage on freq mod aom
            ELSE
              cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
              FPar_78=FPar_78*0.9999+repump_mod_control*(cr_counts-cr_old_counts)
              cr_old_counts=cr_counts
            ENDIF
            DEC(i)
          ENDIF
        ENDIF
      
      CASE 1    ' E/A laser CR check
        
        IF (cr_timer = 0) THEN
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_CR_voltage+32768) ' turn on E laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          INC(PAR_72)
          
          '------------cr modulation control
       
          cr_old_counts = 0
          FPar_77 = -1.0*FPar_77
          'cr_mod_control_amp = -1.0*cr_mod_control_amp
          cr_mod_control_amp = FPar_77
          cr_mod_control_offset  = FPar_75
          i=2
          '-------
        
        ELSE 
          
          IF (cr_timer = CR_duration) THEN
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            P2_CNT_ENABLE(CTR_MODULE,0)
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)
            PAR_70 = PAR_70 + cr_counts
            
            IF (first_cr > 0) THEN ' first CR after SSRO sequence
              DATA_23[repetition_index] = cr_counts
            ENDIF
                      
            IF (cr_counts < current_cr_threshold) THEN
              cr_mode = 0
              inc(CR_failed)
              inc(PAR_79)
            ELSE
              cr_mode = 1
              CR_check = 1
              DATA_22[repetition_index+1] = cr_counts  ' CR before nEt SSRO sequence
              current_cr_threshold = CR_probe
            ENDIF
            
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
          ELSE
            '------------cr modulation control
            IF (i = 0) THEN
              i = 2
              cr_mod_control=DATA_19[cr_timer] 
              P2_DAC(DAC_MODULE,cr_mod_DAC_channel, 3277*(cr_mod_control_amp*cr_mod_control+cr_mod_control_offset)+32768) ' put current voltage on gate
            ELSE
              cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
              FPar_79 = FPar_79*0.99999+cr_mod_control*(cr_counts-cr_old_counts)
              cr_old_counts=cr_counts
            ENDIF
            DEC(i)
          ENDIF
        ENDIF
    ENDSELECT
    inc(cr_timer)
  ENDIF
  
ENDFUNCTION
  
SUB finish_CR()
  DATA_26[1] = repumps
  DATA_26[2] = total_repump_counts
  DATA_26[3] = CR_failed
ENDSUB

