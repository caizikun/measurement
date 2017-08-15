'<ADbasic Header, Headerversion 001.001>
'<Header End>
#Include ADwinPro_All.Inc

Dim value as long
Dim baud_rate, parity, bits, stop_bit, handshake, mode as long
  
SUB init_detection(module, channel) 
  mode = 0 ' 0 = edge detection
  
  
  P2_Digprog(module,1100b)           'channels 0:15 as inputs
  P2_Digin_Fifo_Enable(module,0) 'output edge edge detection off
  P2_Digin_Fifo_Clear(module)        'clear FIFO
  P2_Digin_Fifo_Enable(module,10011b) 'edge detection channels 1,2,5
ENDSUB


Function detection(module,channel)
  value = P2_Read_Fifo(module,channel)
  if value > -1 then
    PAR_22 = value
  endif 
ENDFUNCTION

  
  
  
  
