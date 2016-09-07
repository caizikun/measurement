'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 6
' Initial_Processdelay           = 1000
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

DIM DATA_10[100000] AS FLOAT AS FIFO
DIM DATA_11[100000] AS FLOAT AS FIFO
DIM idletime1,idletime2,frequency1,frequency2,temp1,temp2 AS FLOAT
DIM Counts1,Counts2,processtime,time_1,time_2,,time_3,time_4,val,val1,retval1,retval2  AS INTEGER
DIM trig_val AS INTEGER
DIM trig_volt AS FLOAT
' trig_val=0
INIT:
  
  CONF_DIO(1000b)   'configure DIO-24 to DIO 31 as outputs, the rest are inputs
  CLEAR_DIGOUT(11)  'set counter 1 disable (put DIO 27 to low)
  CLEAR_DIGOUT(10)  'set counter 2 disable (put DIO 26 to low)
  FIFO_CLEAR(10)
  FIFO_CLEAR(11)   
  PAR_9 = 10000 
  processtime=PAR_9*40 'PAR_is cycletime in us, multiply by 40 to get cycle time in ADWIN clockcycles (units of 25ns)
  GLOBALDELAY=processtime
  
EVENT:
  
  
  
  'Read out counter 1 and reset it
  CLEAR_DIGOUT(11)  'set counter 1 disable to stop counting to allow readout and reset (put DIO 27 to low)
  time_1=READ_TIMER()
  SLEEP(2)          'wait 200ns to let counter settle           
  val=DIGIN_WORD()  'read out all 12 bits of counter 1 and 4 bits of counter 2 (these 4 will be discarded later)
  SET_DIGOUT(9)     'set resetbit for counter 1 to high (put DIO 25 to high)
  CLEAR_DIGOUT(9)   'set resetbit for counter 1 to low (put DIO 25 to low), counter is now reset
  SET_DIGOUT(11)    'set counter enable, start counting again (put DIO 27 to high)
  time_2=READ_TIMER()
  ' Done
  
  'Read out counter 2 and reset it  
  CLEAR_DIGOUT(10)  'disable counter 2 to stop counting and allow readout and reset (put DIO 26 to low)
  time_3=READ_TIMER()
  SLEEP(2)          'wait 200ns to let counter settle           
  retval1=PEEK(204001b0h) AND 11111111b   'This reads out DIO16 to DIO23
  retval2=PEEK(204000b0h) AND 1111000000000000b 'This reads out DIO12 to DIO15
  SET_DIGOUT(8)     'set resetbit for counter 2 to high (put DIO 24 to high)
  CLEAR_DIGOUT(8)   'set resetbit for counter 2 to low (put DIO 24 to low), counter is now reset
  SET_DIGOUT(10)    'set counter enable, start counting again (put DIO 26 to high)
  time_4=READ_TIMER()
  'Done
  
  'calculate count rate for counter 1 and put in data10
  idletime1=(time_2-time_1)*25./1000.0: FPAR_16=idletime1 'This is the time the counter was not counting because of readout and reset
  val1=val AND 0000111111111111b     : PAR_16=val1 - 1    'This selects only the last 12 bits which are those of counter1
  Counts1=val1-1  
  frequency1=Counts1/(processtime*25.0/1000.0-idletime1)*1000000
  DATA_10=frequency1
  FPAR_10=frequency1
  'Done
  
  'calculate count rate for counter 2 and put in data11
  temp1=retval1*2^4   'This shifts the values by 4 bits
  temp2=retval2*2^(-12)  'This shifts the values by -12 bits  
  idletime2=(time_4-time_3)*25./1000.0: FPAR_17=idletime2 'This is the time the counter was not counting because of readout and reset
  Counts2=temp2+temp1-1    : PAR_17 = Counts2 'This gives the counts  
  frequency2=Counts2/(processtime*25.0/1000.0-idletime2)*1000000
  DATA_11=frequency2
  FPAR_11=frequency2
  'Done
  trig_val=ADC(3) 'see if other computer triggers autooptimize
  PAR_18=trig_val
  trig_volt = (trig_val - 32768)/3276.8
  FPAR_18=trig_volt
FINISH:

    

