'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 7
' Initial_Processdelay           = 10000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD10239  DASTUD\TUD10239
'<Header End>
'This program is used to continously measure and output stuff to labview

DIM DATA_10[10000] AS FLOAT AS FIFO AT DM_LOCAL
DIM idletime,frequency AS FLOAT
DIM Counts,processtime,time_1,time_2,val,val1, valc1, valc2, testval, newval, val2, testval1, testval2, testval3, testval4 AS INTEGER

INIT:
  CONF_DIO(1000b)   'configure DIO-24 to DIO 31 as outputs, the rest are inputs
  CLEAR_DIGOUT(11)   'set counter disable  
  PAR_10 = 1000000
  processtime=PAR_10
  GLOBALDELAY=Par_10 
EVENT:
  
  CLEAR_DIGOUT(11)  'set counter disable to stop counting to allow readout and reset
  CLEAR_DIGOUT(12)  'set counter disable to stop counting to allow readout and reset
  time_1=READ_TIMER() 'Timestamp
  SLEEP(20)          'wait 200ns to let counter settle           
  val=DIGIN_WORD()  'read out all 12 bits of counter 1 and 4 bits of counter 2 (these will probably be discarded later)

  SET_DIGOUT(9)     'set resetbit for counter 1 to high
  CLEAR_DIGOUT(9)   'set resetbit for counter 1 to low, counter is now reset
  SET_DIGOUT(11)    'set counter 1 enable, start counting again
  time_2=READ_TIMER() 'Timestamp
  idletime=(time_2-time_1)*25./1000.0: FPAR_16=idletime 'This is the time the counter was not counting because of readout and reset
  val1=val AND 0000111111111111b     : PAR_16=val1      'This selects only the last 12 bits which are those of counter1
  Counts=val1-1
  

  
 
  
  frequency=Counts/(processtime*25.0/1000.0-idletime)*1000000
  FPAR_14=frequency
  DATA_10=frequency
  
FINISH:

    

