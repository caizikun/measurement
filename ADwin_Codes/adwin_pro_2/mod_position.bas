'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
' Initial_Processdelay           = 300000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277299  DASTUD\TUD277299
'<Header End>
' this program implements a modulation of the postioner dacs
' and tries to go to a minimum. It get's its counts from two PAR's
' that are set by a CR process that should be running at the same time.
#INCLUDE ADwinPro_All.inc
#INCLUDE .\configuration.inc

#DEFINE position_scan_length 100
#DEFINE pos_mod_min_dac 1
#DEFINE pos_mod_max_dac 3
#DEFINE pos_mod_min_dac_v -10.0
#DEFINE pos_mod_max_dac_v 10.0

'init
DIM DATA_16[3] AS FLOAT 'positioner offsets in/out
DIM DATA_17[position_scan_length] AS FLOAT 'repump freq voltage sine

DIM pos_mod_control_offset, pos_mod_control_amp, pos_mod_control, pos_mod_fb AS FLOAT
DIM pos_mod_control_offset_x, pos_mod_control_offset_y, pos_mod_control_offset_z AS FLOAT
DIM pos_mod_err, pos_mod_min_err AS FLOAT
DIM pos_mod_DAC_channel, pos_mod_activated, pos_mod_timer AS LONG
DIM counts, old_counts AS LONG
DIM i AS LONG


INIT: 
  pos_mod_control_amp          = 0.03 'DATA_31[11] '0.03
  pos_mod_fb                   = 0.001 'DATA_31[12] '0.1
  pos_mod_min_err              = 300 'DATA_31[13] '300
  
 
  'fill data_17 with a sine for repump mod control (calculating sines is slow --> cannot do it during the event cycle)
  FOR i = 1 TO position_scan_length
    DATA_17[i] = Sin(-3.14+2*3.14*i/position_scan_length)
  NEXT i
  
  pos_mod_err = pos_mod_min_err + 1.
  pos_mod_DAC_channel = pos_mod_min_dac
  pos_mod_control_offset = DATA_16[pos_mod_DAC_channel]
  
  pos_mod_activated = 0
  pos_mod_timer = 0
  counts = 0
  old_counts = PAR_70 + PAR_76
  

  par_64 = 0                      ' current pos_mod_DAC_channel 
  FPar_64 = 0.0                   ' current position modulation error signal
  par_65 = 0                      ' activate position modulation
  FPar_65 = pos_mod_min_err       ' current position modulation error signal minumum 
  'before continueing to the next positioner dac
  



EVENT:

  IF (pos_mod_activated > 0) THEN
    IF (pos_mod_timer< position_scan_length) THEN
      INC(pos_mod_timer)
    ELSE
      IF ((pos_mod_err< pos_mod_min_err) AND (pos_mod_err > (-1.0*pos_mod_min_err))) THEN
        pos_mod_err = 0.0
        DATA_16[pos_mod_DAC_channel] = pos_mod_control_offset
        IF (pos_mod_DAC_channel < pos_mod_max_dac) THEN
          INC(pos_mod_DAC_channel)
          FPar_80 = pos_mod_control_offset
        ELSE
          pos_mod_DAC_channel = Par_64
          PAR_65 = 0 'pos_mod_activated = 0
        ENDIF
        pos_mod_control_offset = DATA_16[pos_mod_DAC_channel]
      ENDIF
      pos_mod_timer = 1
    ENDIF
    counts = PAR_70 + PAR_76
    pos_mod_err = pos_mod_err*0.9999+pos_mod_control*(counts-old_counts)
    old_counts = counts
    pos_mod_control = DATA_17[pos_mod_timer]
    pos_mod_control_offset = pos_mod_control_offset + (pos_mod_fb * pos_mod_err / 10000000. )
    IF ((pos_mod_control_offset > pos_mod_min_dac_v) AND (pos_mod_control_offset < pos_mod_max_dac_v)) THEN
      P2_DAC(DAC_MODULE,pos_mod_DAC_channel, 3277*(pos_mod_control_amp*pos_mod_control+pos_mod_control_offset)+32768) ' put current voltage on freq mod aom
    ELSE 'Error, trying to set to high/low voltage on dacs!
      FPar_80 = pos_mod_control_offset 
      PAR_80 = -11
      END
    ENDIF
  ELSE
    IF (pos_mod_timer > 1) THEN
      pos_mod_timer = 1
      P2_DAC(DAC_MODULE,pos_mod_DAC_channel, 3277*(pos_mod_control_offset)+32768)
    ENDIF
  ENDIF
  pos_mod_activated            = PAR_65
  pos_mod_min_err              = FPar_65
  FPar_64                      = pos_mod_err
  PAR_64                       = pos_mod_DAC_channel
