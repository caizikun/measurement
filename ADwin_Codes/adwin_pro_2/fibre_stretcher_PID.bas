'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
' Primary purpose of this program: 
' get count rates of internal ADwin counter 3
' Stabelization of countrate at setpoint and therefore stabelization of the phase
 
' Input:
' - Setpoint (setpoint), for this run fibre_stretcher_setpoint file/process.
' - Delay (DELAY) 
' 
' Output:
' - Voltage of fiberstretcher (V_out) 

' Including packages
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

' Defining FPAR
#DEFINE setpoint        FPAR_14              ' Setpoint of PID process
#DEFINE S               FPAR_15              '
#DEFINE V_in            FPAR_13         

' Defining PAR
#DEFINE DELAY           PAR_10               ' Processdelay

' Defining var
DIM P, D,I, I_OLD                         AS FLOAT        ' PID terms
DIM GAIN,Kp,Kd,Ki                         AS FLOAT        ' PID parameters
DIM e, e_old                              AS FLOAT        ' error term
DIM V_out_old,V_out, value                AS FLOAT        ' Counts and outputs

INIT:
  'Process parameters   
  PROCESSDELAY = 300000*DELAY
  GAIN = 1
  Kp = 0.00012
  Ki = 0.0000
  Kd = 0
  
  'Init Variables
  e = 0
  e_old = 0
  I_old = 0
  V_out = 0
  V_out_old = 0
  
EVENT: 
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
