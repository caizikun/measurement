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
' Info_Last_Save                 = TUD276629  TUD276629\localadmin
'<Header End>
' Teleportation master controller program. lt1 is in charge, lt2 is remote

' modes:
' 0 : repumping
' 1 : do local red CR check
' 2 : MBI spin pumping
' 3 : MBI attempt
' 4 : randomize N
' 5 : MBI re-pump
' 6 : local init OK, wait for remote
' 7 : trigger AWG sequence (LDE element), wait for the done-signal (timeout OR success)
' 8 : first readout, once we get the signal from the AWG
' 9 : repetitive second readout
' 10 : wait for the adwin on LT2 to finish with its SSRO
'
' remote modes:
' 0 : start remote CR check
' 1 : remote CR check running
' 2 : remote CR OK, waiting
' 3 : remote SSRO running
' 4 : remote OK, waiting for CR signal

#INCLUDE ADwinGoldII.inc
#INCLUDE Math.inc

#DEFINE max_repetitions         100000         ' the maximum number of datapoints taken
#DEFINE max_red_hist_cts        100            ' dimension of photon counts histogram for red CR
#DEFINE max_repump_hist_cts     100            ' dimension of photon counts histogram for repump hist
#DEFINE max_statistics          15

' some parameters that are extremely HW-dependent and therefore hard-coded right now
#define wait_after_pulse_duration 3
#define second_readout_reps 2

' parameters
DIM DATA_20[45] AS LONG                   AT DRAM_EXTERN ' integer parameters
DIM DATA_21[15] AS FLOAT                  AT DRAM_EXTERN ' float parameters
DIM DATA_7[max_red_hist_cts] AS LONG      AT EM_LOCAL ' histogram of counts during 1st red CR after timed-out lde sequence
DIM DATA_8[max_red_hist_cts] AS LONG      AT EM_LOCAL ' histogram of counts during red CR (all attempts)
DIM DATA_9[max_repump_hist_cts] AS LONG   AT EM_LOCAL ' histogram of counts during 1st repump after timed-out lde sequence
DIM DATA_10[max_repump_hist_cts] AS LONG  AT EM_LOCAL ' histogram of counts during repump (all attempts)
DIM DATA_23[max_repetitions] AS LONG      AT DRAM_EXTERN 'CR counts after teleportation
DIM DATA_24[max_repetitions] AS LONG      AT DRAM_EXTERN 'BSM SSRO 1 (electron) results
DIM DATA_26[max_repetitions] AS LONG      AT DRAM_EXTERN 'BSM SSRO2 (nitrogen) results
DIM DATA_27[max_repetitions] AS LONG      AT DRAM_EXTERN 'CR check counts before teleportation event
DIM DATA_28[max_statistics] AS LONG       AT EM_LOCAL    'statistics on entering modes
DIM DATA_29[max_repetitions] AS LONG      AT DRAM_EXTERN ' CR timer before LDE element of teleportation event

' general variables
DIM i               AS LONG ' counter for array initalization
DIM mode            AS INTEGER
DIM remote_mode     AS INTEGER
DIM timer           AS LONG
DIM wait_time       AS LONG
DIM CR_probe_timer  AS LONG
DIM CR_probe_time   AS LONG
dim counts          as long

'tuning
DIM tune_duration AS LONG

' settings for CR checks and repumping
DIM counter AS LONG                      'select internal ADwin counter 1 - 4 for conditional readout (PSB lt1)
DIM repump_aom_channel AS LONG            'DAC channel for repump laser AOM
DIM repump_voltage AS FLOAT               'voltage of repump pulse
DIM repump_tune_voltage AS FLOAT          
DIM repump_off_voltage AS FLOAT           'off-voltage of repump laser (0V is not 0W)
DIM e_aom_channel AS LONG 
DIM e_cr_voltage AS FLOAT
DIM e_sp_voltage AS FLOAT
DIM e_ro_voltage AS FLOAT
DIM e_tune_voltage AS FLOAT
DIM e_off_voltage AS FLOAT
DIM a_aom_channel AS LONG
DIM a_cr_voltage AS FLOAT
DIM a_sp_voltage AS FLOAT
DIM a_ro_voltage AS FLOAT
DIM a_tune_voltage AS FLOAT
DIM a_off_voltage AS FLOAT 
dim E_N_randomize_voltage as float
dim A_N_randomize_voltage as float
dim repump_N_randomize_voltage as float

DIM red_cr_check_steps AS LONG             'how long to check, in units of process cycles (lt1)
DIM current_red_cr_check_counts AS LONG        
DIM current_repump_counts AS LONG 
DIM cr_threshold_prepare AS LONG          ' initial CR threshold for first resonance check (lt1)
DIM cr_threshold_probe AS LONG            ' threshold for probe after sequence (charge check) (lt1)
DIM CR_repump AS LONG                                 ' CR repump threshold (typically 1 for yellow, >9000 for green)       
DIM repump_steps AS LONG                       'how long to rempump w/ yellow or green, in process cycles (lt1)
DIM current_cr_threshold AS LONG 
DIM first_cr_probe_after_unsuccessful_lde AS INTEGER  'first CR check after timed out lde sequence
DIM cr_after_teleportation AS INTEGER                 'first CR check after teleportation
DIM CR_probe_max_time AS LONG
DIM wait_before_send_BSM_done AS LONG

' MBI settings
dim e_sp_duration as long
dim a_sp_duration as long
dim mbi_duration as long
dim current_MBI_attempt as long
dim MBI_attempts_before_CR as long
dim mbi_stop as long
dim mbi_threshold as long
dim N_randomize_duration as long

'LDE sequence
DIM AWG_lt1_trigger_do_channel AS LONG
DIM AWG_lt1_event_do_channel AS LONG
DIM AWG_lt1_di_channel AS LONG
DIM AWG_lt1_di_channel_in_bit AS LONG
DIM AWG_lt2_RO1_bit_channel AS LONG
DIM AWG_lt2_RO2_bit_channel AS LONG
DIM AWG_lt2_do_DD_bit_channel AS LONG
DIM AWG_lt2_strobe_channel as long
DIM PLU_arm_do_channel AS LONG
DIM PLU_di_channel AS LONG
DIM PLU_di_channel_in_bit AS LONG
DIM PLU_trigger_received AS LONG
DIM PLU_Bell_state AS LONG

'setting for SSRO on lt1
DIM electron_RO_steps AS LONG
DIM current_RO_counts AS LONG
dim RO_stop as long
dim current_ro_repetition as long

' remote things on lt2
DIM ADwin_LT2_di_channel AS LONG 
DIM ADwin_LT2_di_channel_in_bit AS LONG 
DIM ADwin_LT2_trigger_do_channel AS LONG 
DIM ADwin_in_is_high AS LONG
DIM ADwin_in_was_high AS LONG
DIM ADwin_switched_to_high AS LONG
dim plu_is_high as long
dim plu_was_high as long

DIM AWG_LT1_in_is_high AS LONG
DIM AWG_LT1_in_was_high AS LONG
DIM AWG_LT1_switched_to_high AS LONG

' Teleportation
DIM tele_event_id AS LONG 

' process control
DIM successful_repetitions as LONG
DIM CR_starts AS LONG
DIM remote_delay as long

dim do_sequences as long
dim set_do_sequences as long

' misc and temporary variables
DIM DIO_register AS LONG 


INIT:
  ' general
  mode                      = 1
  remote_mode               = 0
  timer                     = 0
  cr_after_teleportation    = 0
  tele_event_id             = 0
  remote_delay              = 5
  wait_time                 = 10
  counts                    = 0
  
  successful_repetitions     = 0
  CR_starts                  = 0
    
  ' init statistics variables
  for i=1 to max_red_hist_cts
    DATA_7[i] = 0
    DATA_8[i] = 0
  next i
    
  for i=1 to max_repump_hist_cts
    DATA_9[i]  = 0
    DATA_10[i] = 0
  next i
    
  for i=1 to max_repetitions
    DATA_23[i] = 0    'CR check counts after teleportation
    DATA_24[i] = 0    'SSRO1 results
    DATA_26[i] = 0    'SSRO2 results
    DATA_27[i] = 0    'CR check counts before event
    DATA_29[i] = 0    'CR timer before LDE element of teleportation event
  next i
     
  for i=1 to max_statistics
    DATA_28[i] = 0    'statistics
  next i  
      
  ' init variables
  counter                       = DATA_20[1]
  repump_aom_channel            = DATA_20[2]
  e_aom_channel                 = DATA_20[3]
  a_aom_channel                 = DATA_20[4]
  red_cr_check_steps            = DATA_20[5]
  cr_threshold_prepare          = DATA_20[6]
  cr_threshold_probe            = DATA_20[7]
  repump_steps                  = DATA_20[8]
  e_sp_duration                 = DATA_20[9]
  electron_RO_steps             = DATA_20[10]
  ADwin_LT2_trigger_do_channel  = DATA_20[11]
  ADwin_LT2_di_channel          = DATA_20[12]
  AWG_lt1_trigger_do_channel    = DATA_20[13]
  AWG_lt1_di_channel            = DATA_20[14]
  PLU_arm_do_channel            = DATA_20[15]
  PLU_di_channel                = DATA_20[16]  
  MBI_duration                  = DATA_20[17]
  CR_repump                     = DATA_20[18]
  AWG_lt1_event_do_channel      = DATA_20[19]
  AWG_lt2_RO1_bit_channel       = DATA_20[20]
  AWG_lt2_RO2_bit_channel       = DATA_20[21]
  AWG_lt2_do_DD_bit_channel     = DATA_20[22]
  AWG_lt2_strobe_channel        = DATA_20[23]
  a_sp_duration                 = DATA_20[24]
  set_do_sequences              = DATA_20[25]
  CR_probe_max_time             = DATA_20[26]
  mbi_threshold                 = DATA_20[27]
  MBI_attempts_before_CR        = DATA_20[28]
  N_randomize_duration          = DATA_20[29]
  wait_before_send_BSM_done     = DATA_20[30]
      
  repump_voltage                = DATA_21[1]
  repump_off_voltage            = DATA_21[2]
  e_cr_voltage                  = DATA_21[3]
  a_cr_voltage                  = DATA_21[4]
  e_sp_voltage                  = DATA_21[5]
  a_sp_voltage                  = DATA_21[6]
  e_ro_voltage                  = DATA_21[7]
  a_ro_voltage                  = DATA_21[8]
  e_off_voltage                 = DATA_21[9]
  a_off_voltage                 = DATA_21[10]
  E_N_randomize_voltage         = DATA_21[11]
  A_N_randomize_voltage         = DATA_21[12]
  repump_N_randomize_voltage    = DATA_21[13]

  do_sequences                  = set_do_sequences
  current_red_cr_check_counts   = 0
  current_repump_counts         = 0
  current_cr_threshold          = cr_threshold_prepare
  first_cr_probe_after_unsuccessful_lde = 0
  cr_after_teleportation        = 0
  PLU_Bell_state                = -1
  PLU_trigger_received          = 0
  current_RO_counts             = 0
  ADwin_in_is_high              = 0
  ADwin_in_was_high             = 0
  ADwin_switched_to_high        = 0
  CR_probe_timer                = 0
  AWG_LT1_in_is_high            = 0
  AWG_LT1_in_was_high           = 0
  AWG_LT1_switched_to_high      = 0
  plu_is_high                   = 0
  plu_was_high                  = 0

  ' prepare hardware 
  par_50 = 0                      ' KILL IT! KILL IT WITH FIRE!
  
  par_57 = 0                      ' 
  par_58 = 0                      ' 
  par_59 = 0                      ' tune (1 is tuning, 0 is running)
  par_60 = 0                      ' PLU digin before actually expecting it (mode 6, timer=0)
  par_61 = 0                      ' CR probe timer
  par_62 = 0                      ' remote mode
  par_63 = 0                      ' teleportation event id
  par_64 = 0                      ' mode
  par_65 = 0                      ' timer
  par_66 = 0                      ' LDE sequence finished signals from AWG
  Par_67 = 0                      ' MBI attempts
  Par_68 = cr_threshold_probe
  Par_69 = cr_repump
  Par_70 = 0                      ' cumulative counts during red CR check (LT1)
  par_71 = 0                      ' cumulative number of repumps
  par_72 = 0                      ' number of red CR checks performed (LT1)
  par_73 = 0                      ' number of CR OK signals from LT2
  par_74 = 0                      ' number of start CR triggers to LT2
  par_75 = cr_threshold_prepare
  Par_76 = 0                      ' cumulative counts during repumping (LT1)
  par_77 = 0                      ' number of successful teleportation attempts
  par_78 = 0                      ' number of LDE sequence starts
  par_79 = 0                      ' CR below threshold events (LT1)
  par_80 = 0                      ' MBI fails
  
  ADwin_LT2_di_channel_in_bit = 2^ADwin_LT2_di_channel 
  AWG_LT1_di_channel_in_bit = 2^AWG_LT1_di_channel  
  PLU_di_channel_in_bit = 2^PLU_di_channel
   
  DAC(repump_aom_channel, 3277*repump_off_voltage+32768)   'turn off repump laser
  DAC(e_aom_channel, 3277*e_off_voltage + 32768)           'turn off Ey aom 
  DAC(a_aom_channel, 3277*a_off_voltage + 32768)         'turn off FB aom
  CNT_ENABLE(0000b)                          'turn off all counters
  CNT_MODE(counter,00001000b)                'configure counter
  CONF_DIO(11)                               'configure DIO 16:23 as input, all other ports as output
  DIGOUT(ADwin_LT2_trigger_do_channel,0)     'trigger to ADwin LT2
  DIGOUT(AWG_lt1_trigger_do_channel, 0)      'trigger to AWG LT1
  DIGOUT(AWG_lt1_event_do_channel, 0)        'event to AWG LT1
  DIGOUT(PLU_arm_do_channel, 0)              'PLU is not armed until just before LDE start trigger **????
  DIGOUT(AWG_lt2_RO1_bit_channel, 0)
  DIGOUT(AWG_lt2_RO2_bit_channel, 0)
  DIGOUT(AWG_lt2_do_DD_bit_channel, 1)
  
  
EVENT:

  cr_threshold_prepare = par_75
  cr_threshold_probe = Par_68
  cr_repump = Par_69
  
  if (par_50 > 0) then
    cr_threshold_prepare = 1000
    cr_threshold_probe = 1000
  endif
      
  par_61 = CR_probe_timer
  par_64 = mode
  par_65 = timer
  par_62 = remote_mode
  par_63 = tele_event_id
  
  if (remote_delay > 0) then  
    dec(remote_delay)
  ELSE
  
    selectcase remote_mode
    
      case 0 'start remote CR check
            
        ' remote delay because it can happen that after getting the signal here that LT2 is done,
        ' we immediately send a start again. this can lead to LT2 missing the step where the
        ' the DO is low (because it's very short). therefore wait a tiny bit before sending
        ' signals.
        INC(par_74)
        DIGOUT(ADwin_LT2_trigger_do_channel, 1)
        remote_mode = 1
        remote_delay = 5
                                              
      case 1 'remote CR check running
      
        ' check state of other adwin and whether it has changed to ready
        ADwin_in_was_high = ADwin_in_is_high
        ADwin_in_is_high = DIGIN(ADwin_LT2_di_channel)
             
        IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN ' ADwin switched to high during last round. 
          DIGOUT(ADwin_LT2_trigger_do_channel, 0)
          remote_mode = 2
          INC(par_73)
        ENDIF             
      
      case 2 'remote CR OK, waiting
      
      case 3 'remote SSRO running
        ADwin_in_was_high = ADwin_in_is_high
        ADwin_in_is_high = DIGIN(ADwin_LT2_di_channel)
                     
        IF ((ADwin_in_was_high = 0) AND (ADwin_in_is_high > 0)) THEN ' ADwin switched to high during last round. 
          remote_mode = 4
        ENDIF
                
      case 4 'remote SSRO OK, waiting
      
    endselect
  endif
     
    
  IF (wait_time > 0) THEN
    dec(wait_time)
  ELSE
      
    if (timer=0) then
      INC(DATA_28[mode+1])  'increment for each time mode is entered
    endif
  
    selectcase mode
         
      case 0 ' repump

        IF (timer = 0) THEN
        
          IF (current_red_cr_check_counts < CR_repump) THEN    
            CNT_ENABLE(0000b)    'turn off counter
            CNT_CLEAR(1111b)     'clear counter    
            CNT_ENABLE(1111b)    'enable counter       
            DAC(repump_aom_channel, 3277*repump_voltage+32768)
            inc(par_71)
          ELSE
            mode = 1
            timer = -1
            current_CR_threshold = CR_threshold_prepare
          ENDIF
      
        ELSE
        
          IF (timer = repump_steps) THEN
            
            CNT_ENABLE(0000b)     'turn off counter
            current_repump_counts = CNT_READ(counter)
            Par_76 = Par_76 + current_repump_counts
            DAC(repump_AOM_channel, 3277*repump_off_voltage+32768)
                          
            IF (current_repump_counts < max_repump_hist_cts) THEN      'make histograms
            
              IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
                INC(DATA_9[current_repump_counts+1])
              ENDIF            
              INC(DATA_10[current_repump_counts+1])
          
            ENDIF
          
            first_CR_probe_after_unsuccessful_LDE = 0       'reset
            current_CR_threshold = CR_threshold_prepare
            mode = 1
            timer = -1
          ENDIF
      
        ENDIF
      
      case 1 'do local red CR check
      
        IF (timer = 0) THEN
          INC(par_72)          'number of red CR checks performed
          CNT_ENABLE(0000b)    'turn off counter
          CNT_CLEAR(1111b)     'clear counter
          CNT_ENABLE(1111b)    'enable counter
                          
          DAC(e_aom_channel, 3277*e_cr_voltage+32768)  'turn on red lasers
          DAC(a_aom_channel, 3277*a_cr_voltage+32768)                       
      
        ELSE
        
          IF (timer = red_cr_check_steps) THEN
          
            CNT_ENABLE(0000b)
            current_red_cr_check_counts = CNT_READ(counter)
            Par_70 = Par_70 + current_red_cr_check_counts
                            
            DAC(e_aom_channel,  3277*e_off_voltage +32768)   'turn off red lasers
            DAC(a_aom_channel, 3277*a_off_voltage+32768)
                        
            ' save the number of CR counts with teleportation event
            IF (cr_after_teleportation > 0) THEN    
              DATA_23[tele_event_id] = current_red_cr_check_counts
              cr_after_teleportation = 0
            ENDIF
                            
            ' make histogram of CR counts
            IF (current_red_cr_check_counts < max_red_hist_cts) THEN      
              IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
                INC(DATA_7[current_red_cr_check_counts+1]) 'make histogram for only after unsuccessful lde
              ENDIF            
              INC(DATA_8[current_red_cr_check_counts+1]) 'make histogram for all attempts
            else
              IF (first_cr_probe_after_unsuccessful_lde > 0) THEN
                INC(DATA_7[max_red_hist_cts])
              ENDIF            
              INC(DATA_8[max_red_hist_cts])
            ENDIF
          
            IF (cr_probe_timer > CR_probe_max_time) THEN
              current_cr_threshold = CR_threshold_prepare
              cr_probe_timer = 0
            ENDIF
                                      
            IF (current_red_cr_check_counts < current_cr_threshold) THEN
              INC(par_79) ' CR below threshold events
              mode = 0
              timer = -1
              wait_time = wait_after_pulse_duration
            ELSE
              first_cr_probe_after_unsuccessful_lde = 0
              DATA_27[tele_event_id + 1] = current_red_cr_check_counts
              current_cr_threshold = cr_threshold_probe
            
              ' in case we're not actually running anything or we're in tuning mode,
              ' only do CR checking
              if ((do_sequences = 0) or (par_59 = 1)) then
                mode = 1
              else
                mode = 2
              endif             
              timer = -1  
            ENDIF        
          ENDIF      
        ENDIF
      
      CASE 2 ' E spin pumping for MBI
        
        ' turn on both lasers and start counting
        IF (timer = 0) THEN
                
          dac(e_aom_channel, 3277*e_sp_voltage+32768) ' turn on Ex laser
          CNT_CLEAR(1111b)     'clear counter
          CNT_ENABLE(1111b)    'enable counter
      
        ELSE        
          ' turn off the lasers, and read the counter
          IF (timer = e_sp_duration) THEN
            cnt_enable(0)
            dac(e_aom_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
                
            mode = 3
            wait_time = wait_after_pulse_duration
            timer = -1
          ENDIF         
        
        ENDIF
    
      CASE 3    ' MBI
                
        ' MBI starts now; we first need to trigger the AWG to do the selective pi-pulse
        ' then wait until we can assume this is done
        IF(timer=0) THEN
          
          INC(PAR_67)        
          digout(AWG_lt1_trigger_DO_channel,1)  ' AWG trigger for CNOT
          CPU_SLEEP(9)
          digout(AWG_lt1_trigger_DO_channel,0)
          MBI_stop = -2
          
        else
          ' we expect a trigger from the AWG once it has done the MW pulse
          ' as soon as we assume the AWG has done the MW pulse, we turn on the E-laser,
          ' and start counting
          AWG_LT1_in_was_high = AWG_LT1_in_is_high
          AWG_LT1_in_is_high = DIGIN(AWG_LT1_di_channel)
          
          IF ((AWG_LT1_in_was_high = 0) AND (AWG_LT1_in_is_high > 0)) THEN            
            
            MBI_stop = timer + MBI_duration
            CNT_CLEAR(1111b)     'clear counter
            CNT_ENABLE(1111b)    'enable counter
            dac(e_aom_channel, 3277*e_ro_voltage+32768) ' turn on Ex laser
         
          else
            
            IF (timer = MBI_stop) THEN
                            
              dac(e_aom_channel,3277*e_off_voltage+32768) ' turn off Ex laser
              counts = CNT_READ(counter)
              cnt_enable(0)
                                         
              IF (counts < MBI_threshold) THEN
                inc(PAR_80)                
                if (current_MBI_attempt = MBI_attempts_before_CR) then
                  current_cr_threshold = cr_threshold_prepare
                  mode = 1 '(check resonance and start over)
                  current_MBI_attempt = 1
                else
                  mode = 4
                  inc(current_MBI_attempt)
                endif                
                timer = -1
              
              else
                digout(AWG_lt1_event_do_channel,1)  ' jump to LDE element
                CPU_SLEEP(9)
                digout(AWG_lt1_event_do_channel,0)                
                mode = 5 ' goto repumping to ms=0
              endif
              
              timer = -1
            endif  
          
          endif
        endif
      
      case 4 ' randomize the N spin
        if (timer = 0) then
          dac(E_aom_channel,3277*E_N_randomize_voltage+32768)
          dac(A_aom_channel,3277*A_N_randomize_voltage+32768)
          dac(repump_aom_channel,3277*repump_N_randomize_voltage+32768)
        else
          if (timer = N_randomize_duration) then
            dac(E_aom_channel,3277*E_off_voltage+32768)
            dac(A_aom_channel,3277*A_off_voltage+32768)
            dac(repump_aom_channel,3277*repump_off_voltage+32768)
            
            mode = 2
            timer = -1
            wait_time = wait_after_pulse_duration
          endif                    
        endif
      
      
      CASE 5 ' A re-pumping to 0
       
        IF (timer = 0) THEN
          dac(a_aom_channel, 3277*A_SP_voltage+32768)
        ELSE
          IF (timer = A_SP_duration) THEN
            ' dac(e_aom_channel,3277*E_off_voltage+ 32768) ' turn off Ex laser
            dac(a_aom_channel, 3277*A_off_voltage+32768) ' turn off A laser
            wait_time = wait_after_pulse_duration
            
            mode = 6
            timer = -1
          ENDIF
        ENDIF
        
      case 6 'local init OK, wait for remote
      
        ' todo: we could save the waiting times, or at least averages of them.
        IF (remote_mode = 2) THEN
          if ((do_sequences = 0) or (par_59 = 1)) then
            mode = 1 
            remote_mode = 0
          else      
            mode = 7
            wait_time = 5 ' we need to make sure that the AWG is receptive for triggering now!
            DATA_29[tele_event_id + 1] = CR_probe_timer   ' save CR timer just before LDE sequence -> put to after LDE later?
          
          endif        
          timer = -1
        ENDIF      
    
      case 7 ' trigger LDE, then wait for timeout (AWG) OR success (PLU)
      
        if (timer = 0) then
          
          inc(par_78)
          
          DIGOUT(AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start LDE
          CPU_SLEEP(9)
          DIGOUT(AWG_lt1_trigger_do_channel, 0)
          
          DIGOUT(PLU_arm_do_channel, 1) ' arm the PLU once at the beginning of the LDE sequence
          CPU_SLEEP(9)
          DIGOUT(PLU_arm_do_channel, 0)
          
          ' par_60 = (DIGIN_EDGE(1) AND (PLU_di_channel_in_bit))
        
        else
          
          ' do we need digin edge here? - i guess we could speed it up if we could readout
          ' out the PLU and the AWG in together with digin_long
          ' logic: if we get a PLU event, we go to the BSM
          '        if we get an AWG event before a PLU event, we go back to init/CR
          
          PLU_was_high = PLU_is_high
          AWG_LT1_in_was_high = AWG_LT1_in_is_high
          DIO_register = digin_long()
          PLU_is_high = (DIO_register AND PLU_di_channel_in_bit)
          AWG_LT1_in_is_high = (DIO_register AND AWG_lt1_di_channel_in_bit)          
          
          if ((PLU_was_high = 0) AND (PLU_is_high > 0)) then              
            inc(par_77)
            mode = 8
            timer = -1
          else         
            IF ((AWG_LT1_in_was_high = 0) AND (AWG_LT1_in_is_high > 0)) THEN
              inc(par_66)
              first_cr_probe_after_unsuccessful_lde = 1
              
              mode = 1
              timer = -1
              remote_mode = 0
              wait_time = 10
            endif        
          endif        
        endif
        
      case 8
        ' this is the first part of the BSM. we wait until we get a trigger from
        ' the AWG, then do SSRO
        
        if (timer=0) then
          RO_stop = -2
          DIGOUT(AWG_lt2_do_DD_bit_channel, 0) ' next strobe on AWG LT2 signals to do the feed-fwd rotation
        endif
                
        AWG_LT1_in_was_high = AWG_LT1_in_is_high
        AWG_LT1_in_is_high = DIGIN(AWG_LT1_di_channel)
                
        IF ((AWG_LT1_in_was_high = 0) AND (AWG_LT1_in_is_high > 0)) THEN
          RO_stop = timer + electron_RO_steps
          cnt_clear(counter)     'clear counter
          cnt_enable(counter)    'turn on counter
          dac(e_aom_channel, 3277*E_ro_voltage+32768) ' turn on E laser
        else
          
          if (timer = RO_stop) then
            dac(e_aom_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
            counts = cnt_read(counter)
            if (counts > 0) then
              DIGOUT(AWG_lt2_RO1_bit_channel, 0)
            else
              inc(data_24[tele_event_id+1])
              DIGOUT(AWG_lt2_RO1_bit_channel, 1)
            endif           
            cnt_enable(0)
            
            mode = 9 ' next up: repetitive readout of the nuclear spin
            current_ro_repetition = 1
            timer = -1
            current_ro_counts = 0
           
          endif
        
        endif
        
      case 9
        ' (repetitive) readout of the nuclear spin
        ' consists of triggering an AWG sequence (with SP and CNOT), wait for it to be done, perform SSRO;
        ' repeat N times.
        
        if (timer = 0) then
          RO_stop = -2
          DIGOUT(AWG_lt1_trigger_do_channel, 1) ' trigger the AWG to start LDE
          CPU_SLEEP(9)
          DIGOUT(AWG_lt1_trigger_do_channel, 0)
        else
          AWG_LT1_in_was_high = AWG_LT1_in_is_high
          AWG_LT1_in_is_high = DIGIN(AWG_LT1_di_channel)
          
          IF ((AWG_LT1_in_was_high = 0) AND (AWG_LT1_in_is_high > 0)) THEN
            RO_stop = timer + electron_RO_steps
            cnt_clear(counter)     'clear counter
            cnt_enable(counter)    'turn on counter
            dac(e_aom_channel, 3277*E_ro_voltage+32768) ' turn on E laser
          else
            
            if (timer = RO_stop) then
              dac(e_aom_channel, 3277*E_off_voltage+32768) ' turn off Ex laser
              current_ro_counts = current_ro_counts + cnt_read(counter)
              cnt_enable(0)
              
              if (current_ro_repetition = second_readout_reps) then
                ' we're done, evaluate the readout result                
                if (current_ro_counts > 0) then
                  DIGOUT(AWG_lt2_RO2_bit_channel, 0)
                else
                  inc(data_26[tele_event_id+1])
                  DIGOUT(AWG_lt2_RO2_bit_channel, 1)
                endif
                
                mode = 10
                wait_time = wait_before_send_BSM_done
                timer = -1
                current_ro_repetition = 1
                current_RO_counts = 0
                remote_mode = 3
               
              else
                ' repeat readout
                timer = -1
                mode = 9
                inc(current_ro_repetition)
              endif           
            endif
          endif
        endif        
      
      case 10
        
        if (timer=0) then
          DIGOUT(AWG_lt2_strobe_channel, 1)
        else
          if (timer=1) then
            DIGOUT(AWG_lt2_strobe_channel, 0)
          endif
        endif
                              
        ' we wait for LT2 to be done with its SSRO, then we start over
        if (remote_mode = 4) then
          inc(tele_event_id)
          cr_after_teleportation = 1
          mode = 1
          timer = -1
          remote_mode = 0
          DIGOUT(AWG_lt2_do_DD_bit_channel, 1) ' next strobe is DD again
        endif
                    
    ENDSELECT
    
    ' timer in here to make sure it stays -1 during wait_time intervals
    INC(timer)
    
  endif

  ' inc(par_60) ' the total time
  
FINISH:
  DAC(repump_aom_channel, 3277*repump_off_voltage+32768)   'turn off repump laser
  DAC(e_aom_channel, 3277*e_off_voltage + 32768)           'turn off E aom 
  DAC(a_aom_channel, 3277*a_off_voltage + 32768)         'turn off A aom
  CNT_ENABLE(0000b)                          'turn off all counters
  DIGOUT(ADwin_LT2_trigger_do_channel,0)     'trigger to ADwin LT2
  DIGOUT(AWG_lt1_trigger_do_channel, 0)      'trigger to AWG LT1
  DIGOUT(AWG_lt1_event_do_channel, 0)        'event to AWG LT1
  DIGOUT(PLU_arm_do_channel, 0)              
  DIGOUT(AWG_lt2_RO1_bit_channel, 0)
  DIGOUT(AWG_lt2_RO2_bit_channel, 0)
  DIGOUT(AWG_lt2_do_DD_bit_channel, 0)
