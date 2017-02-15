'<ADbasic Header, Headerversion 001.001>
'<Header End>
' this program implements CR check with NV electronic gate and repump laser locking. 
' Adapted from cr_mod.inc, but made faster by avoiding unnecessary calculations
' AR 2016
'
' protocol:
' mode  0:  yellow pulse, photon counting just for statistics
' mode  1:  E/A pulse, photon counting  ->  CR check
'           fail: -> mode 0


#DEFINE max_stat           10
#DEFINE max_repetitions 500000
#DEFINE max_CR_duration   250
#DEFINE max_repump_duration 2000

'init
DIM DATA_30[100] AS LONG               ' CR integer parameters
DIM DATA_31[100] AS FLOAT              ' CR float parameters

DIM DATA_55[max_repump_duration] AS FLOAT AT EM_LOCAL 'repump freq voltage sine
DIM DATA_56[max_CR_duration] AS FLOAT AT EM_LOCAL 'CR gate voltage sine for error signal calc   EM_local memory because conventional one is too full
DIM DATA_57[max_repump_duration] AS FLOAT AT EM_LOCAL 'repump freq voltage sine for error signal calc
DIM DATA_18[max_repump_duration] AS FLOAT AT EM_LOCAL 'repump freq voltage sine
DIM DATA_19[max_CR_duration] AS FLOAT AT EM_LOCAL 'CR gate voltage sine

'return
DIM DATA_22[max_repetitions] AS LONG  ' CR counts before sequence
DIM DATA_23[max_repetitions] AS LONG ' CR counts after sequence
DIM DATA_26[max_stat] AS LONG         ' statistics

DIM cr_mode, cr_timer, cr_i AS LONG
DIM cr_counts, cr_old_counts AS LONG
DIM cr_r_counts, cr_r_old_counts AS LONG
DIM CR_probe, CR_preselect, CR_repump, current_CR_threshold AS LONG
DIM repump_duration, CR_duration AS LONG
DIM cr_wait_after_pulse, cr_wait_after_pulse_duration AS LONG
DIM counter_channel, counter_pattern AS LONG
DIM E_laser_DAC_channel, A_laser_DAC_channel, repump_laser_DAC_channel AS LONG

DIM repump_mod_DAC_channel, cr_mod_DAC_channel AS LONG
DIM repump_mod_activated, cr_mod_activated AS LONG
DIM repump_mod_amplitude_invert, cr_mod_amplitude_invert as long ' defined as variables to avoid unnecessary multiplications

DIM repump_voltage, repump_off_voltage, E_CR_voltage, A_CR_voltage, E_off_voltage, A_off_voltage AS FLOAT

DIM cr_mod_control_offset, cr_mod_control_amp, cr_mod_control, cr_mod_control_avg, cr_mod_control_avg_part AS FLOAT
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
  repump_mod_DAC_channel       = DATA_30[11]
  cr_mod_DAC_channel           = DATA_30[12]

  repump_voltage               = DATA_31[1]
  repump_off_voltage           = DATA_31[2]
  E_CR_voltage                 = DATA_31[3]
  A_CR_voltage                 = DATA_31[4]
  E_off_voltage                = DATA_31[5]
  A_off_voltage                = DATA_31[6]
  repump_mod_control_offset    = DATA_31[7]  '5.0
  repump_mod_control_amp       = DATA_31[8]  '1.0 - 2.0
  cr_mod_control_offset        = DATA_31[9]  '0.0
  cr_mod_control_amp           = DATA_31[10] '0.1 
  cr_mod_control_avg           = DATA_31[11]
  
  FOR cr_i = 1 TO max_repetitions
    DATA_22[cr_i] = 0
    DATA_23[cr_i] = 0
  NEXT cr_i
  
  FOR cr_i = 1 TO max_stat
    DATA_26[cr_i] = 0
  NEXT cr_i
  
  'fill DATA_57 and data_18 with a sine for repump mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR cr_i = 1 TO repump_duration
    DATA_18[cr_i] = 3277* (repump_mod_control_amp* Sin(-3.14+2*3.14*cr_i/repump_duration)+repump_mod_control_offset)+32768
    DATA_55[cr_i] = 3277* (-repump_mod_control_amp* Sin(-3.14+2*3.14*cr_i/repump_duration)+repump_mod_control_offset)+32768
    DATA_57[cr_i] = repump_mod_control_amp* Sin(-3.14+2*3.14*cr_i/repump_duration)
  NEXT cr_i
  
  'fill data_19 with a sine for cr mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR cr_i = 1 TO CR_duration
    DATA_56[cr_i] = Sin(-3.14+2*3.14*cr_i/CR_duration)
    DATA_19[cr_i] = 3277*(cr_mod_control_amp*Sin(-3.14+2*3.14*cr_i/CR_duration)+cr_mod_control_offset)+32768
  NEXT cr_i
  
   
  counter_pattern     = 2 ^ (counter_channel-1)
  cr_wait_after_pulse    = 0
  cr_mode = 0
  cr_timer = 0
  cr_i=2
  cr_counts=0
  cr_mod_control_avg_part = 1.-1./cr_mod_control_avg
  repump_mod_amplitude_invert = 0
  cr_mod_amplitude_invert = 0
  
  current_cr_threshold = CR_preselect
  
  
  'output pars
  PAR_70 = 0                      ' cumulative counts from probe intervals
  PAR_71 = 0                      ' number of repumps
  PAR_72 = 0                      ' number of CR checks performed
  
  par_76 = 0                      ' cumulative counts during repumping
  par_79 = 0                      ' CR below treshold events

  FPar_78 = 0.0                   ' current repump modulation error signal
  FPar_79 = 0.0                   ' current CR modulation error signal
  
  'control pars
  Par_75 = CR_preselect
  Par_68 = CR_probe
  par_69 = CR_repump
  par_66 = 0                      ' activate repump modulation
  par_67 = 0                      ' activate cr gate modulation
  
ENDSUB



FUNCTION CR_check(first_cr, repetition_index) As LONG

  CR_check = 0 'return variable
  if (first_CR>0) then
    cr_mode = 2  'skip modulation in frist cr after
  endif
  IF (cr_wait_after_pulse > 0) THEN
    DEC(cr_wait_after_pulse)
  ELSE
    SELECTCASE cr_mode 
     
        
      CASE 0    ' repump and repump modulation
        IF (cr_timer = 0) THEN
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    'turn on counter
          P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_voltage+32768) ' turn on green
          inc(par_71)  'number of repumps
            
          repump_mod_activated = PAR_66 ' read from labview whether or not the repump freq should be modulated
          cr_r_old_counts = 0 ' forget old results
          cr_i = 0
          'repump_mod_control_amp = -1.0*repump_mod_control_amp
          if (repump_mod_amplitude_invert = 1) then ' we change the direction of the scan every second round to reduce systematic
            repump_mod_amplitude_invert = 0
          else
            repump_mod_amplitude_invert = 1
          endif

        ELSE 

          IF (cr_timer = repump_duration) THEN
            par_76 = par_76 + cr_r_counts ' total repump counts for debugging
            P2_DAC(DAC_MODULE,repump_laser_DAC_channel, 3277*repump_off_voltage+32768) ' turn off yellow/green
            cr_r_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            P2_CNT_ENABLE(CTR_MODULE,0) ' disable and clear counter
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)
            if (PAR_67 > 0 ) then ' cr modulation activated in labview
              cr_mode = 1 ' go to cr modulation
            else
              cr_mode = 2 ' regular CR check
            endif
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration ' wait for the laser pulse to be fully off
            current_cr_threshold = CR_preselect ' adapt threshold: after repumping, the NV has to match the preselect
                        
          ELSE ' timer is not 0 and not repump_duration. Do repump modulation if set
            if (repump_mod_activated>0) THEN  
              IF (cr_i = 0) THEN 'Every second execution, we set new voltages on AOM
                cr_i = 2 ' cr_i is set to 0 at beginning of each repumping and decremented at the end of this loop. 
                if (repump_mod_amplitude_invert>0) then
                  P2_DAC_2(repump_mod_DAC_channel, DATA_55[cr_timer]) ' put current voltage on freq mod aom
                else
                  P2_DAC_2(repump_mod_DAC_channel, DATA_18[cr_timer]) ' put current voltage on freq mod aom
                endif
              ELSE ' in the other two executions, we calculate an error signal and output it on a PAR
                cr_r_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
                ' calculation of the repump error signal, based on the change of the repump counts compared to the last run
                ' The old value decays over time (FPar_78*0.9999), meaning that we're using an PI-controller with dominant I part
                ' The P-part of the error signal is wheighted with the deviation from 0 (DATA_57[cr_timer]).
                ' So extremal values of the modulation have the dominant part in wheighting: 
                ' First, the modulation spends more time there
                ' second, they are less attenuated by the Sin factor DATA_57[cr_timer]
                ' third, the shot noise is strongest here because the counts are smallest
                ' XXX I'd expect that the locking is much improved if this is changed!
                if (repump_mod_amplitude_invert>0) then
                  FPar_78=FPar_78*0.9999-DATA_57[cr_timer]*(cr_r_counts-cr_r_old_counts) 
                else
                  FPar_78=FPar_78*0.9999+DATA_57[cr_timer]*(cr_r_counts-cr_r_old_counts)
                endif
                
                cr_r_old_counts=cr_r_counts ' remember for next repetition
              ENDIF
              DEC(cr_i)
            endif          
          ENDIF
        ENDIF
        
      CASE 1  ' ----cr modulation control before CR check
        IF (cr_timer = 0) THEN
          'P2_DIGOUT(DIO_MODULE,11,1) ' set repumper modulation high.    XXX nothing connected to dio 11 on both lt3 and lt4 ??
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_CR_voltage+32768) ' turn on E laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    ' clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    ' turn on counter
          cr_old_counts = 0
          IF (cr_mod_activated > 0) THEN
            'cr_mod_control_amp = -1.0*cr_mod_control_amp   xxx inversion not used here. Why?
            'if cr_mod_amplitude_invert = 1 then
            '  cr_mod_amplitude_invert = 0
            'else
            '  cr_mod_amplitude_invert = 1
            'endif
            cr_i=0
          ELSE
            cr_mode = 2 ' go to normal CR check
          ENDIF
          
        ELSE
          IF (cr_timer = CR_duration) THEN
            cr_mode = 2 ' go to normal CR check
            cr_timer = -1 ' xxx used to be zero
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    'clear counter - we do not take the counts during the modulation phase into account
            ' maybe we could make this a setting: for SSRO it is fine to take the counts during the modulation into account, for TPQI we need to clear here
          ELSE  
            '------------ cr modulation control
            IF (cr_i = 0) THEN 
              cr_i = 2 ' again, we change the voltage every second repetition
              if (cr_mod_amplitude_invert > 0) then
                P2_DAC_2(cr_mod_DAC_channel, - DATA_19[cr_timer]) ' put current voltage on gate
              else
                P2_DAC_2(cr_mod_DAC_channel, DATA_19[cr_timer]) ' put current voltage on gate
              endif
    
            ELSE
              cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
              ' update error signal, sameprinciple as above
              if (cr_mod_amplitude_invert>0) then
                FPar_79 = FPar_79*cr_mod_control_avg_part-DATA_56[cr_timer]*(cr_counts-cr_old_counts)
              else
                FPar_79 = FPar_79*cr_mod_control_avg_part+DATA_56[cr_timer]*(cr_counts-cr_old_counts)
              endif
              cr_old_counts=cr_counts
            ENDIF
            DEC(cr_i)
          ENDIF
        ENDIF
        
      CASE 2    ' E/A laser CR check
        if (cr_timer = 0) then
          P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_CR_voltage+32768) ' turn on E laser
          P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_CR_voltage+32768) ' turn on A laser
          P2_CNT_CLEAR(CTR_MODULE,counter_pattern)    ' clear counter
          P2_CNT_ENABLE(CTR_MODULE,counter_pattern)    ' turn on counter
          CR_preselect = PAR_75 'read labview parameters
          CR_probe = PAR_68
          cr_mod_activated = PAR_67
        else
          IF (cr_timer = CR_duration) THEN
            'P2_DIGOUT(DIO_MODULE,11,0) ' set repumper modulation low.   XXX channel not connected
            P2_DAC(DAC_MODULE,E_laser_DAC_channel, 3277*E_off_voltage+32768) ' turn off E laser
            P2_DAC(DAC_MODULE,A_laser_DAC_channel, 3277*A_off_voltage+32768) ' turn off A laser
            cr_counts = P2_CNT_READ(CTR_MODULE,counter_channel)
            P2_CNT_ENABLE(CTR_MODULE,0) 'disable
            P2_CNT_CLEAR(CTR_MODULE,counter_pattern)

            Inc(Par_72) ' total number of cr checks
            PAR_70 = PAR_70 + cr_counts ' total number of cr counts for labview monitoring
            
            IF (first_cr > 0) THEN ' first CR after SSRO sequence; repetition index is increased in main script after SSRO has been done. CR check gets repetition_counter-1 (for compatibility)
              DATA_23[repetition_index] = cr_counts
              first_cr = 0
            ENDIF
            

            if (cr_mod_activated>0) then
              cr_mode = 1
            else 
              cr_mode = 2
            endif 'cr_mode overwritten later if counts are below repump threshold
            
            IF (cr_counts < current_cr_threshold) THEN
              CR_check = -1 ' return failure
              inc(PAR_79) ' number of failed CR checks
              current_CR_threshold = CR_preselect
              CR_repump = PAR_69 ' read if threshold has been changed by labview
              IF (cr_counts < CR_repump) THEN
                cr_mode = 0 ' go to repump
              ELSE ' counts were not below repumping threshold. go to modulation mode if activated, else conventional cr check again
                
                if (cr_mod_activated>0) then
                  cr_mode = 1
                else 
                  cr_mode = 2
                endif
              ENDIF
            ELSE ' CR check successful
              cr_mode = 1 ' next run: CR after check will skip modulation if first_CR is set
              current_cr_threshold = CR_probe
              CR_check = 1 ' return success
              DATA_22[repetition_index+1] = cr_counts  ' save CR before the SSRO sequence; repetition index is increased in main script after SSRO has been done, CR_check gets repetition_counter-1 (for compatibility)
            ENDIF
            cr_timer = -1
            cr_wait_after_pulse = cr_wait_after_pulse_duration
          ENDIF
        endif
        
    ENDSELECT
    inc(cr_timer)
  ENDIF
  
ENDFUNCTION

SUB finish_CR()
ENDSUB

