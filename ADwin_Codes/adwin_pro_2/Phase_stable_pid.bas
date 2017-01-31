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
 
#DEFINE setpoint        FPAR_14              ' Setpoint of PID process
#DEFINE S               FPAR_15              '

' Defining PAR
#DEFINE DELAY           PAR_10               ' Processdelay 

#DEFINE max_pid       500000
#DEFINE max_sample    500000

DIM DATA_20[100] AS LONG
DIM DATA_26[max_pid] AS LONG 
DIM DATA_25[max_sample] AS LONG

'Define variables
DIM P, D,I, I_OLD                         AS FLOAT        ' PID terms
DIM GAIN,Kp,Kd,Ki                         AS FLOAT        ' PID parameters
DIM e, e_old                              AS FLOAT        ' error term
DIM V_out_old,V_out, value                AS FLOAT        ' Counts and outputs
DIM counts, counts_min, counts_max        AS FLOAT        ' Counts 
DIM mode,index,index1,pid_cycles,sample_cycles AS LONG
DIM repetition_counter, max_repetitions   AS LONG
DIM k,j, V_in                             AS LONG
Init:
  'Init
  PAR_73 = 0
  mode = 1
  index = 1
  pid_cycles                  = DATA_20[1]
  sample_cycles               = DATA_20[2]
  max_repetitions             = DATA_20[3]
  repetition_counter  = 0
  P2_DAC_2(14, 0)
  
  FOR j = 1 TO max_pid
    DATA_26[j] = 1
  NEXT j
  FOR j = 1 TO max_sample
    DATA_25[j] = 2
  NEXT j
  
  k = 1
  j = 1
 
  'PID characteristics
  GAIN = 1
  Kp = 0.002
  Ki = 0.0000
  Kd = 0
  
  'PID Init Variables
  e = 0
  e_old = 0
  I_old = 0
  S = 0 
  V_out = 0
  V_out_old = 0
  
  'Latch onto and measure
  P2_CNT_ENABLE(CTR_MODULE, 0000b)
  P2_CNT_MODE(CTR_MODULE, 2,000010000b)
  'CNT_SE_DIFF(0000b)
  P2_CNT_CLEAR(CTR_MODULE, 0010b)
  P2_CNT_ENABLE(CTR_MODULE, 0010b)
  
  'TIME setpoints
  processdelay = 30000*delay

Event:
  Selectcase mode   
    case 1 'Do PID and save counts

      ' Measure counts
      P2_CNT_LATCH(CTR_MODULE, 0010b)
      V_in = P2_CNT_READ_LATCH(CTR_MODULE, 2)
      P2_CNT_ENABLE(CTR_MODULE,0000b)
      P2_CNT_CLEAR(CTR_MODULE,0010b)
      P2_CNT_ENABLE(CTR_MODULE,0010b) 
      DATA_26[k] = V_in 
      inc(k)
      
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
      if (index>pid_cycles) then
        mode = 2
        index = 1
      endif
      
    case 2 'Do nothing and save counts
      
      ' Measure counts
      P2_CNT_LATCH(CTR_MODULE, 0010b)
      V_in = P2_CNT_READ_LATCH(CTR_MODULE, 2)
      P2_CNT_ENABLE(CTR_MODULE,0000b)
      P2_CNT_CLEAR(CTR_MODULE,0010b)
      P2_CNT_ENABLE(CTR_MODULE,0010b)
      DATA_25[j] = V_in 
      inc(j)
      
      'Do index3 rounds
      inc(index)
      if (index>sample_cycles) then
        mode = 1
        index = 1
        
        inc(repetition_counter)
        Par_73 = repetition_counter
        IF (repetition_counter = max_repetitions) THEN
          END
        ENDIF

        
      endif
  endselect
