'<ADbasic Header, Headerversion 001.001>
'<Header End>
'  slot   module    description  address  tico
'    1   CPU T12   Processor    -        -
'    2   CNT-T     4 Counters   1       Yes
'    3   CIO 32    32 TTL DIOs  2       Yes
'    4   AOUT 8/16 16bit DACs   3
'    5   AOUT 8/16 16bit DACs   4

#DEFINE CTR_MODULE 1  'Address of CNT-T
#DEFINE DIO_MODULE 2  'Address of DIO 32
#DEFINE DAC_MODULE 3  'Address of AOUT 8/16
#DEFINE DAC_MODULE_2 4  'Address of AOUT 8/16

SUB P2_DAC_2(dac_no, value)
  IF (dac_no<9) THEN
    P2_DAC(DAC_MODULE,dac_no, value)
  ELSE
    P2_DAC(DAC_MODULE_2,dac_no-8, value) 
  ENDIF
ENDSUB
