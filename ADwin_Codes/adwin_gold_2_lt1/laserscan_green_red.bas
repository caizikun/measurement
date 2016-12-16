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
' This program does a multidimensional line scan; it needs to be given the 
' involved DACs, their start voltage, their end voltage and the number of steps
' (including start and stop)

#INCLUDE ADwinGoldII.inc
' #INCLUDE configuration.inc
#DEFINE max_steps 100000
'init
DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT

DIM freq_dac_channel,green_aom_dac_channel,red_aom_dac_channel,noof_pixels,pixel_time,green_time,red_time,wait_after_green_time AS LONG
DIM green_voltage,red_voltage,scan_start_voltage,scan_stop_voltage,green_off_voltage,red_off_voltage AS FLOAT

DIM current_pixel,mode,timer, pixel_timer,i AS LONG

DIM voltage_step, scan_current_voltage AS FLOAT

DIM DATA_11[max_steps] AS LONG
DIM DATA_12[max_steps] AS LONG
DIM DATA_13[max_steps] AS LONG

' supplemental data; used when PxAction is set to 2
DIM DATA_15[max_steps] AS FLOAT
DIM DATA_16[max_steps] AS FLOAT

INIT:
  
  freq_dac_channel      = DATA_20[1] 
  green_aom_dac_channel = DATA_20[2] 
  red_aom_dac_channel   = DATA_20[3] 
  noof_pixels           = DATA_20[4]
  pixel_time            = DATA_20[5] 'us
  green_time            = DATA_20[6] 'us
  red_time              = DATA_20[7] 'us
  wait_after_green_time = DATA_20[8]
  
  green_voltage         = DATA_21[1]
  red_voltage           = DATA_21[2]
  scan_start_voltage    = DATA_21[3]
  scan_stop_voltage     = DATA_21[4]
  red_off_voltage       = DATA_21[5]
  green_off_voltage     = DATA_21[6]
  
  
  current_pixel = 1
  ' set the pixel clock, but start from zero
  PAR_4 = current_pixel - 1   
  
  scan_current_voltage  = scan_start_voltage
  DAC(freq_dac_channel, 3277*scan_current_voltage+32768)
  voltage_step = (scan_stop_voltage-scan_start_voltage) / (noof_pixels-1)
  Fpar_4 = voltage_step
  FOR i = 1 to max_steps
    DATA_11[i] = 0
    DATA_12[i] = 0
    DATA_13[i] = 0
    DATA_15[i] = 0
    DATA_16[i] = 0
  NEXT i
   
  mode = 0
  timer = 0
  pixel_timer = 0
  
  CNT_ENABLE(000b)                                        'Stop counter 1, 2 and 3
  CNT_MODE(1, 00001000b)                                  '
  CNT_MODE(2, 00001000b)
  CNT_MODE(3, 00001000b)
  CNT_SE_DIFF(000b)                                           'All counterinputs single ended (not differential)
  CNT_CLEAR(111b)                                         'Set all counters to zero
                                          
  
  DAC(green_aom_dac_channel, 3277*green_off_voltage+32768)
  DAC(red_aom_dac_channel, 3277*red_off_voltage+32768)
 
EVENT:
  PAR_77 = mode
  PAR_78 = timer
  PAR_79 = pixel_timer
  
  SELECTCASE mode
    
    CASE 0 'green pulse
      IF (timer = 0) THEN
        DAC(green_aom_dac_channel, 3277*green_voltage+32768) ' turn on green laser
      ELSE
        IF (timer = green_time) THEN
          DAC(green_aom_dac_channel, 3277*green_off_voltage+32768) ' turn off green laser
          mode = 1
          timer = -1
        ENDIF
      ENDIF
      
    CASE 1 'red pulse and count
      IF (timer = wait_after_green_time-2) THEN
        CNT_ENABLE(111b)     
        'Start counters again
      ELSE 
        IF (timer = wait_after_green_time) THEN 
          DAC(red_aom_dac_channel, 3277*red_voltage+32768) 'turn on red lasers
        ELSE
          IF (timer = red_time+wait_after_green_time) THEN
            DAC(red_aom_dac_channel, 3277*red_off_voltage+32768) ' turn off green laser
            CNT_LATCH(111b)                                         'latch counters
            DATA_11[current_pixel] = DATA_11[current_pixel] +  CNT_READ_LATCH(1)                 'read latch A of counter 1
            DATA_12[current_pixel] = DATA_12[current_pixel] +  CNT_READ_LATCH(2)                 'read latch A of counter 2
            DATA_13[current_pixel] = DATA_13[current_pixel] +  CNT_READ_LATCH(3)                 'read latch A of counter 3' DATA_11[CurrentStep]+ DATA_12[CurrentStep]'  Hack sum countrates    
            CNT_ENABLE(000b)                                        'Stop counters
            CNT_CLEAR(111b)                                         'Clear counters
            mode = 2
            timer = -1
          ENDIF
        ENDIF
      ENDIF
            
    CASE 2   ' check if the pixel time is reached and move to  next pixel voltage if neccesary
      IF (pixel_timer >= pixel_time) THEN
        DATA_15[current_pixel] = FPar_46
        scan_current_voltage = scan_start_voltage + current_pixel*voltage_step
        DAC(freq_dac_channel, 3277*scan_current_voltage+32768)
        DATA_16[current_pixel] = scan_current_voltage
        INC(current_pixel)
        IF (current_pixel > noof_pixels + 1) THEN                     ' Stop when end of line is reached
          END       
        ENDIF
        Par_4 = current_pixel - 1
        pixel_timer = -1
      ENDIF
      mode = 0
      timer = -1
        
  ENDSELECT    
      
  INC(timer)
  INC(pixel_timer)
  
FINISH:  

