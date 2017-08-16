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
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
'<Header End>
#Include ADwinPro_All.Inc

Dim value as long
Dim baud_rate, parity, bits, stop_bit, handshake as long
  
SUB init_detection(module, channel)
  'Hardware settings.
  baud_rate = 115200    ' RS232: 35 . 115,200 Baud. RS485: 35.2,304,000 Baud.
  parity = 0
  bits = 8              'amount of bits
  stop_bit = 0
  handshake = 1         'only at RS232
  
  P2_RS_Reset(module)
  P2_RS_Init(module,channel,baud_rate,parity,bits,stop_bit,handshake)

Function detection(module,channel)
  value = P2_Read_Fifo(module,channel)
  if value > -1 then
    PAR_22 = value
  endif 
  
  
  
  
