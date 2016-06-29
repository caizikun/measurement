'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
' Initial_Processdelay           = 30000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
'<Header End>
' This program does a multidimensional line scan; it needs to be given the 
' involved DACs, their start voltage, their end voltage and the number of steps
' (including start and stop)
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc
'#INCLUDE .\cr_mod_Bell.inc
#INCLUDE .\cr_mod.inc

#DEFINE max_scan_length 1000
' scan settings
DIM NoOfDACs, i, CurrentStep, NoOfSteps AS INTEGER
DIM PxTime, StepSize AS FLOAT

' what to do for each pixel; 
' 1=counting, 0=nothing, 2=counting + record supplemental data per px from fpar2 3=read counters from par45-48 (for use with resonant counting);
DIM PxAction, scan_average, current_scan_direction, first AS INTEGER
dim scan_activated as integer

' The numbers of the involved DACs (adwin only has 8)
DIM DATA_200[8] AS INTEGER
' The start voltages
DIM DATA_199[8] AS FLOAT
' The end voltages
DIM DATA_198[8] AS FLOAT
' The stepsizes
DIM DATA_197[8] AS FLOAT
' The current position
DIM DATA_1[8] AS FLOAT

' keeping track of timing
DIM TimeCntROStart, TimeCntROStop AS INTEGER

' Setting voltages
DIM DACVoltage AS FLOAT
DIM DACBinaryVoltage AS INTEGER

'DIM DACVoltage,StartVoltage, EndVoltage, stepsize, now,idletime1,idletime2,frequency1,temp1,temp2,frequency2 AS FLOAT
'DIM DACno ,NOfVoltSteps, pixeltime,totaltime,i,n,m,DACBinaryVoltage,time_1,time_2,time_3,time_4,val,val1,retval1,retval2,Counts1,Counts2 AS INTEGER

DIM DATA_11[max_scan_length] AS LONG
' supplemental data; used when PxAction is set to 2
DIM DATA_15[max_scan_length] AS FLOAT

dim timer, wait_time AS LONG
dim counter1 AS LONG
LOWINIT:
  init_CR()
  
  P2_Digprog(DIO_MODULE,11)
  P2_DIGOUT(DIO_MODULE,11,1) ' set repumper modulation high.
  CurrentStep = 1
  
  ' set the pixel clock, but start from zero
  PAR_4 = CurrentStep - 1   
  
  ' get all involved DACs and set to start voltages
  NoOfDACs = PAR_1
  NoOfSteps = PAR_2
  PxTime = FPAR_1
  PxAction = PAR_3
  IF (NoOfSteps = 0) THEN 
    EXIT
  ENDIF
  
  IF (PxAction = 0) THEN
    scan_average = 1
  ELSE
    scan_average = 2*ROUND((PAR_64+1)/2)-1 'number of avg should be uneven!
  ENDIF
  
  wait_time=MAX_LONG(ROUND(PxTime*1000/(2*CR_duration+repump_duration)),10)
    
  FOR i = 1 TO NoOfDACs
    DACVoltage = DATA_199[i]
    DACBinaryVoltage = DACVoltage * 3276.8 + 32768    
    
    P2_DAC(DAC_Module,DATA_200[i], DACBinaryVoltage)
    DATA_1[DATA_200[i]]   = DACVoltage 
    DATA_197[i] = (DATA_198[i] - DATA_199[i]) / (NoOfSteps - 1) 
  
    ' debug;
    PAR_5 = DATA_200[i]
    FPar_5 = DATA_199[i]

  NEXT i
  
  FOR i = 1 TO max_scan_length
    DATA_11[i] = 0
    DATA_15[i] = 0
  NEXT i
  
  timer = wait_time
  counter1=0
  scan_activated = 0
  current_scan_direction = 1
  first = 0
  
  ' again: what to do for each pixel; 
  ' 1=counting, 0=nothing, 2=counting + record supplemental data per px from fpar2 3=read counters from par45-48 (for use with resonant counting);
  
EVENT:
  IF (timer = 0) THEN
    PROCESSDELAY = 30000 ' 1 cycle is now 100us
    DATA_11[CurrentStep] = DATA_11[CurrentStep] +counter1 'save last value and reset counter value
    counter1=0
    IF (PxAction = 2) THEN   ' record supplemental data per px from fpar2
      DATA_15[CurrentStep] = FPar_2
    ENDIF    
    ' Set the voltage on all involved DACs
    FOR i = 1 TO NoOfDACs
      'Increase DAC voltage by one step (first value will be neglected)
      DACVoltage = DATA_199[i] + (CurrentStep - 1) * DATA_197[i]   'data 199 = start voltage, data_197= stepsize
      FPar_7 = DATA_199[i] ' output current start voltage to FPar
      FPar_8 = CurrentStep-1
      FPar_9 = DATA_197[i]   ' stepsize
      ' output on DAC
      DACBinaryVoltage = DACVoltage * 3276.8 + 32768
      P2_DAC(DAC_Module,DATA_200[i], DACBinaryVoltage)
      DATA_1[DATA_200[i]]   = DACVoltage ' data1: current pos; data_200: list of DACs
      FPar_5 = DACVoltage
    NEXT i
    
    CurrentStep = CurrentStep + current_scan_direction
    
    IF ((CurrentStep > NoOfSteps + 1) OR (CurrentStep = 0)) THEN
      DEC(scan_average)                     ' Stop when end of line is reached
      IF (scan_average<1) THEN
        END                                                     'End program
      ENDIF
      current_scan_direction = -1*current_scan_direction
      CurrentStep = CurrentStep + 2*current_scan_direction
    ENDIF
  
    ' update the pixel clock; put after the line end check so we have a maximum
    ' that corresponds to the number of steps
    Par_4 = CurrentStep - 1
    timer = wait_time
  ELSE
    IF (timer = wait_time) THEN
      Processdelay = 300
      DEC(timer)
    ELSE
      IF ( CR_check(first,CurrentStep) <> 0 ) THEN
        IF ((PAR_59 > 0) OR (scan_activated>0)) THEN
          scan_activated = 1
          DEC(timer)
          counter1 = counter1 + cr_counts + cr_old_counts + cr_r_counts
        ENDIF 
      ENDIF
    ENDIF
  ENDIF

   
    
FINISH:
  finish_CR() 
  P2_DIGOUT(DIO_MODULE,11,0) ' set repumper modulation low. 
  Par_49 = 0  'tell resonant counting process to stop summing its data into par 45-48  
