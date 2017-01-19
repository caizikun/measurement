'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 300000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc


' Defining FPAR
#DEFINE V_in            FPAR_13   
#DEFINE setpoint        FPAR_14              ' Setpoint of PID process
#DEFINE S               FPAR_15              '

' Defining PAR
#DEFINE DELAY           PAR_10               ' Processdelay

'Define variables
DIM P, D,I, I_OLD                         AS FLOAT        ' PID terms
DIM GAIN,Kp,Kd,Ki                         AS FLOAT        ' PID parameters
DIM e, e_old                              AS FLOAT        ' error term
DIM V_out_old,V_out, value                AS FLOAT        ' Counts and outputs
DIM counts, counts_min, counts_max        AS FLOAT        ' Counts 
DIM mode,index,index1,index2,index3       AS LONG

Init:
  'Init
  mode = 0
  index = 0

  'SETPOINT init
  setpoint = 0
  P2_DAC_2(14, 0)
  
  'SETPOINT Init counts min and max
  P2_CNT_LATCH(CTR_MODULE, 1111b)       ' Measure
  counts_min = abs(P2_CNT_READ_LATCH(CTR_MODULE, 2) /2)
  P2_CNT_ENABLE(CTR_MODULE,0000b)
  P2_CNT_CLEAR(CTR_MODULE,1111b)
  P2_CNT_ENABLE(CTR_MODULE,1111b) 
  counts_max = 0

  'PID characteristics
  GAIN = 1
  Kp = 0.0012
  Ki = 0.0000
  Kd = 0
  
  'PID Init Variables
  e = 0
  e_old = 0
  I_old = 0
  V_out = 0
  V_out_old = 0
  
  'TIME setpoints
  processdelay = 300000*delay
  index1 = 5000
  index2 = 50
  index3 = 100
  
Event:
  Selectcase mode
    case 0 'Find setpoint
      
      P2_CNT_LATCH(CTR_MODULE, 1111b)       ' Measure
      counts = P2_CNT_READ_LATCH(CTR_MODULE, 2)
      P2_CNT_ENABLE(CTR_MODULE,0000b)
      P2_CNT_CLEAR(CTR_MODULE,1111b)
      P2_CNT_ENABLE(CTR_MODULE,1111b) 
  
      if (counts > counts_max) then
        counts_max = counts
      endif
  
      if (counts < counts_min) then
        counts_min = counts
      endif
  
      setpoint = (counts_max + counts_min)/2
      
      'Do index1 rounds
      inc(index)
      if (index>index1) then
        mode = 1
        index = 0
      endif
      
    case 1 'Do PID and save counts
      
      ' Measure counts
      P2_CNT_LATCH(CTR_MODULE, 1111b)
      V_in = P2_CNT_READ_LATCH(CTR_MODULE, 2)
      P2_CNT_ENABLE(CTR_MODULE,0000b)
      P2_CNT_CLEAR(CTR_MODULE,1111b)
      P2_CNT_ENABLE(CTR_MODULE,1111b) 

      ' PID control
      e = SETPOINT - V_in
      P = Kp * e                                               ' Proportional term      
      I = Ki * ( I_old + e * (delay/1000) )                    ' Integration term                                              ' 
      D = Kd * (( e - e_old ) / (delay/1000) )                 ' Differentiation term
  
      ' Calculate Output
      S  = V_out_old + GAIN * (P + I + D)
  
      ' Output inside reach of fibre stretcher?
      if ((s <= (9.5)) and (s >= (-9.5))) then
        V_out = S
      else
        if (s > (9.5)) then
          V_out = S - (11.0775)
          '      I = 0
          '      D = 0
        else
          V_out = S + (11.0775)
          '      I = 0
          '      D = 0
        endif
      endif
  
      ' Output
      value = V_out*3276.8+32768 
      P2_DAC_2(14, value)
  
      ' Values needed for next cycle
      e_old = e
      I_old = I
      V_out_old = V_out
      
      'Do index2 rounds
      inc(index)
      if (index>index2) then
        mode = 2
        index = 0
      endif
      
    case 2 'Do nothing and save counts
      
      ' Measure counts
      P2_CNT_LATCH(CTR_MODULE, 1111b)
      V_in = P2_CNT_READ_LATCH(CTR_MODULE, 2)
      P2_CNT_ENABLE(CTR_MODULE,0000b)
      P2_CNT_CLEAR(CTR_MODULE,1111b)
      P2_CNT_ENABLE(CTR_MODULE,1111b) 
      
      'Do index3 rounds
      inc(index)
      if (index>index3) then
        mode = 1
        index = 0
      endif
      
  endselect
  
Finish:
  'reset dac voltage
  P2_DAC_2(14, 0)
  mode = 0
