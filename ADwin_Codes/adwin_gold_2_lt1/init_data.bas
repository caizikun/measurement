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
' Info_Last_Save                 = TUD277246  DASTUD\tud277246
'<Header End>
#DEFINE max_sequences     100
#DEFINE max_nr_of_Carbon_init_steps 20
#DEFINE max_nr_of_Carbon_MBE_steps 20
#DEFINE max_repetitions 500000
'Linescan:
DIM DATA_1[8] AS FLOAT
DIM DATA_197[8] AS FLOAT
DIM DATA_198[8] AS FLOAT
DIM DATA_199[8] AS FLOAT
DIM DATA_200[8] AS LONG

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

'Singleshot adwin:
DIM DATA_16[8] AS FLOAT AT EM_LOCAL 'modulation offsets during repump

DIM DATA_20[100] AS LONG
DIM DATA_21[100] AS FLOAT
DIM DATA_27[1000000] AS LONG
DIM DATA_30[100] AS LONG
DIM DATA_31[100] AS FLOAT
DIM DATA_28[100] AS LONG

'C13 control
'in
DIM DATA_33[max_sequences] AS LONG                ' A SP after MBI durations
DIM DATA_34[max_sequences] AS LONG                ' E RO durations
DIM DATA_35[max_sequences] AS FLOAT               ' A SP after MBI voltages
DIM DATA_36[max_sequences] AS FLOAT               ' E RO voltages
DIM DATA_38[max_sequences] AS LONG                ' sequence wait times
DIM DATA_39[max_sequences] AS FLOAT               ' E SP after MBI voltages
DIM DATA_37[max_sequences] AS LONG                ' Not used?
DIM DATA_40[max_sequences] AS LONG                ' C13 MBI threshold list
'out
DIM DATA_29[max_nr_of_Carbon_init_steps] AS LONG 'Data array to store the number of carbon initialization START events
DIM DATA_32[max_nr_of_Carbon_init_steps] AS LONG 'Data array to store the number of carbon initialization SUCCES events
'C13 MBE data
DIM DATA_51[max_nr_of_Carbon_MBE_steps] AS LONG 'Data array to store the number of carbon MBE START events
DIM DATA_52[max_nr_of_Carbon_MBE_steps] AS LONG 'Data array to store the number of carbon MBE SUCCES events
'C13 Parity data
DIM DATA_53[max_repetitions] AS LONG 'Parity measurement outcomes (NOTE: multiple parity measurements are stored in a single array of length Nr_parity * repetitions


'Magnetometry
'DIM DATA_50[50000] AS FLOAT
'DIM DATA_51[50000] AS FLOAT
'DIM DATA_22[20000] AS LONG AT EM_LOCAL  ' CR counts before sequence
'DIM DATA_23[20000] AS LONG AT EM_LOCAL  ' CR counts after sequence
'DIM DATA_24[500] AS LONG AT EM_LOCAL      ' SP counts
'DIM DATA_25[1000000] AS LONG AT DRAM_EXTERN  ' SSRO counts
'DIM DATA_26[50] AS LONG AT EM_LOCAL         ' statistics 

INIT:

EVENT:
  END
