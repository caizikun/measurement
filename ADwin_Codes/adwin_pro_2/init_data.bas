'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277513  DASTUD\TUD277513
'<Header End>
'#INCLUDE ADwinPro_All.inc
'#INCLUDE configuration.inc

'Linescan:
DIM DATA_1[8] AS FLOAT
DIM DATA_197[8] AS FLOAT
DIM DATA_198[8] AS FLOAT
DIM DATA_199[8] AS FLOAT
DIM DATA_200[8] AS LONG
DIM DATA_11[100000] AS LONG
DIM DATA_12[100000] AS LONG
DIM DATA_13[100000] AS LONG
DIM DATA_14[100000] AS LONG
DIM DATA_15[100000] AS FLOAT

'Conditional repump TPQI:
DIM DATA_8[100] AS LONG
DIM DATA_7[100] AS LONG

'Conditional repump:
'DIM DATA_51[10000] AS FLOAT

'Resonant counting, simple counting
DIM DATA_41[10000] AS FLOAT
DIM DATA_42[10000] AS FLOAT
DIM DATA_43[10000] AS FLOAT
DIM DATA_44[10000] AS FLOAT
DIM DATA_45[4] AS LONG

'Position optimizer
DIM DATA_16[20] AS FLOAT
'DIM DATA_17 is used by cr_mod_pos_scan, but I dont know if we use this?

'Param passing!
DIM DATA_20[300] AS LONG
DIM DATA_21[300] AS FLOAT
'
'Singleshot adwin:
DIM DATA_24[2000] AS LONG AT EM_LOCAL      ' SP counts
DIM DATA_25[1000000] AS LONG  ' SSRO counts spin readout

''cr_mod:
'DIM DATA_18[2000] AS FLOAT AT EM_LOCAL 
'DIM DATA_19[500] AS FLOAT AT EM_LOCAL 
'DIM DATA_22[100000] AS LONG AT EM_LOCAL  
'DIM DATA_23[100000] AS LONG AT EM_LOCAL  
'DIM DATA_26[10] AS LONG AT EM_LOCAL     
'DIM DATA_30[300] AS LONG
'DIM DATA_31[300] AS FLOAT
''cr_mod_multicounter also uses DIM DATA_32[4] AS LONG 
'DIM DATA_55[2000] AS FLOAT AT EM_LOCAL 'repump freq voltage sine
'DIM DATA_56[500] AS FLOAT AT EM_LOCAL 'CR gate voltage sine for error signal calc   EM_local memory because conventional one is too full
'DIM DATA_57[2000] AS FLOAT AT EM_LOCAL 'repump freq voltage sine for error signal calc


''MBI C_13:
'' Singleshot uses Data_24 and Data_25 as well. At the moment it doesnt seem to clash, so I have commented out the init
'' of these arrays
'' Also note that the older MBI_lt3 script uses 25 and 28 for different purposes and requires a different size
''DIM DATA_24[100000] AS LONG ' number of MBI attempts needed in the successful cycle
''DIM DATA_25[1] AS LONG ' Data array to store the number of N initialization START events
'DIM DATA_27[100000] AS LONG ' Final SSRO result
'DIM DATA_28[1] AS LONG ' Data array to store the number of N initialization SUCCES events
'DIM DATA_29[20] AS LONG 'Data array to store the number of carbon initialization START events
'DIM DATA_32[20] AS LONG 'Data array to store the number of carbon initialization SUCCES events
'DIM DATA_33[100] AS LONG                ' A SP after MBI durations
'DIM DATA_34[100] AS LONG                ' E RO durations
'DIM DATA_35[100] AS FLOAT               ' A SP after MBI voltages
'DIM DATA_36[100] AS FLOAT               ' E RO voltages
'DIM DATA_37[100] AS LONG                ' send AWG start
'DIM DATA_38[100] AS LONG                ' sequence wait times
'DIM DATA_39[100] AS FLOAT               ' E SP after MBI voltages
'DIM DATA_40[100] AS LONG                ' C13 MBI threshold list
' Counters also use these arrays, so not initialising.
'DIM DATA_41[20] AS LONG 'Data array to store the number of carbon MBE START events
'DIM DATA_42[20] AS LONG 'Data array to store the number of carbon MBE SUCCES events
'DIM DATA_43[100000] AS LONG 'Parity measurement outcomes (NOTE: multiple parity measurements are stored in a single array of length Nr_parity * repetitions

INIT:

EVENT:
  END
