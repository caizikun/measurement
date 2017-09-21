import qt
import msvcrt
import numpy as np
from instrument import Instrument
# import lt3_scripts.tools.stools as stools
import time

def AOMfrequency():
    qt.msleep(1)
    qt.instruments['signalhound'].set_frequency_center(199.52e6)
    qt.instruments['signalhound'].set_frequency_span(1323.75e3) 
    qt.instruments['signalhound'].set_rbw(300)
    qt.instruments['signalhound'].set_vbw(300)
    qt.instruments['signalhound'].ConfigSweepMode()
    f,mi,ma=qt.instruments['signalhound'].GetSweep(do_plot=False, max_points=50000)
    f_offset = f[np.argmax(mi)]
    return f_offset

qt.mstart()
# PhaseAOM.turn_off()
PulseAOM.turn_off()
voltage=qt.get_instruments()['adwin'].get_dac_voltage(('pulse_aom_frq'))
f_offset1=0
f_offset2=11e3


while abs(f_offset1-f_offset2)>10e3 and voltage<11 :
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break 
    qt.get_instruments()['adwin'].set_dac_voltage(('pulse_aom_frq',voltage))
    stools.rf_switch_local()
    f_offset1=AOMfrequency()
    stools.rf_switch_non_local()
    f_offset2=AOMfrequency()
    print f_offset1, f_offset2
    print voltage
    if f_offset1<f_offset2:
        voltage+=0.1
    else: voltage-=0.1    
    
qt.mend()
