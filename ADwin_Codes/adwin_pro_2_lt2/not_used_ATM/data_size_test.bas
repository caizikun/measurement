'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277459  DASTUD\TUD277459
'<Header End>
#INCLUDE ADwinPro_All.inc


#DEFINE len       10000000 ' not used anymore? Machiel 23-12-'13
#DEFINE lentwo    1 ' not used anymore? Machiel 23-12-'13
DIM DATA_20[len] AS LONG                          ' long parameters
DIM DATA_22[len] AS LONG                          ' long parameters
DIM DATA_21[lentwo] AS LONG                          ' long parameters
DIM i AS LONG
DIM ret_val1,ret_val2 as LONG

LOWINIT:
  ret_val1 = Read_Timer()
  FOR i = 1 TO len
    DATA_20[i] = 0
  NEXT i
  ret_val2 = Read_Timer()
  PAR_3=(ret_val2-ret_val1)*0.3*0.00000001
  FPAR_3=(ret_val2-ret_val1)*0.3*0.001
  PAR_4=ret_val2
  PAR_5=ret_val1
  PAR_7=0
  FPAR_7=0
  PAR_8=0

INIT:
  'PAR_2=75
  ret_val1 = Read_Timer()
  FOR i = 1 TO 500000
    DATA_20[i] = 0
  NEXT i
  ret_val2 = Read_Timer()
  PAR_7=(ret_val2-ret_val1)*0.3*0.00000001
  FPAR_7=(ret_val2-ret_val1)*0.3*0.001
  
EVENT:
  
  
  IF (FPAR_7>0)THEN
    END
  ELSE
    PAR_8=1
  ENDIF
  
  
    
