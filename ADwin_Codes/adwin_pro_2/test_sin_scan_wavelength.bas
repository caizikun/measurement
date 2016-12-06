'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
'-----------------------------------------------------------------'
'                         Made By Jaco Morits                     '
'-----------------------------------------------------------------'
'Process makes array of sin values and outputs them, the freq
' is controlled by the processdelay.
'
' - Input:
' Delay       - processdelay/ freq control 
' Amp         - Amplitude of sinus ( Between -10 and 10 V)
'
' - Output:
'  Value to dac13
'
' - 0.1 v with 1000 microsecond seems optimal


'Include
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

'Define var's
#DEFINE Delay       par_10                    'Procesdelay [micros]
#DEFINE Amp         FPAR_12                   'Amplitude   [V]
DIM index           AS LONG                   'Index
DIM sinus[360]      AS FLOAT                  'Array for sine values
DIM pi              AS FLOAT
dim value           AS LONG

INIT:
  pi = 3.1415926
  
  FOR index = 1 TO 90                                      'Construct sin wave
    sinus[index] = ( Amp * SIN( (index - 1) * 2*pi/90 )  )     '6 factor for conversion to voltage, offset for High-Z to 50 ohm conversion (no -)
  NEXT index
  index = 1                                                 'Reset Index
  processdelay = 300*delay                               'Delay between each event 
EVENT:
  value= sinus[index]*3276.8+32768                          'Convert voltage to bit value
  P2_DAC_2(13, value)                                       'Output the amplitude value to dac13
  INC index                                                 'Increase the count index
  IF (index > 90) THEN index = 1                           'starts again at index 1 for full sin 
  
