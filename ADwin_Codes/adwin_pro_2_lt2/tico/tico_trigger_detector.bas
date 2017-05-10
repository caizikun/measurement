'<TiCoBasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Priority                       = High
' Version                        = 1
' TiCoBasic_Version              = 1.2.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD277459  DASTUD\tud277459
'<Header End>
' Reliable trigger detector that runs on the TiCo-coprocessor
' Author: Jesse Slim, May 2017
'
' CONTEXT:
' Detection of triggers (e.g. AWG done triggers) is sometimes kind of a pain in the 

#INCLUDE C:\ADwin\TiCoBasic\inc\DIO32TiCo.inc

#DEFINE TD_Pattern_1    Par_40
#DEFINE TD_Pattern_2    Par_41
#DEFINE TD_Pattern_3    Par_42
#DEFINE TD_Pattern_4    Par_43

#DEFINE TD_Detected_1   Par_50
#DEFINE TD_Detected_2   Par_51
#DEFINE TD_Detected_3   Par_52
#DEFINE TD_Detected_4   Par_53

INIT:
  
EVENT:
  
