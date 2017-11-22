"""
PH 2017
This script plots the AOM frequency over time (measured using the signal hound), to investigate how stable it is 
"""

import qt
import msvcrt
import numpy as np
# import lt3_scripts.tools.stools as stools
import time

name='AOMfreqStabMsmt'

# create data object
qt.mstart()

start_time = time.time()
freq_LT3 = []
freq_LT4 = []
times = []

stop_scan = False


d = qt.Data(name=name)
d.add_coordinate('time')
d.add_value('freq LT3')
d.add_value('freq LT4')

d.create_file()
filename=d.get_filepath()[:-4]

while not(stop_scan):

    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True

    times.append(time.time() - start_time)

    stools.rf_switch_local()
    qt.msleep(1)
    qt.instruments['signalhound'].set_frequency_center(200.08e6)
    qt.instruments['signalhound'].set_frequency_span(200e3) 
    qt.instruments['signalhound'].set_rbw(300)
    qt.instruments['signalhound'].set_vbw(300)
    qt.instruments['signalhound'].ConfigSweepMode()
    f,mi,ma=qt.instruments['signalhound'].GetSweep(do_plot=False, max_points=5000)
    f_offset = f[np.argmax(mi)]
    
    freq_LT3.append(f_offset/1e3 - 200.08e3)

    stools.rf_switch_non_local()
    qt.msleep(1)
    qt.instruments['signalhound'].set_frequency_center(200.08e6)
    qt.instruments['signalhound'].set_frequency_span(200e3) 
    qt.instruments['signalhound'].set_rbw(300)
    qt.instruments['signalhound'].set_vbw(300)
    qt.instruments['signalhound'].ConfigSweepMode()
    f,mi,ma=qt.instruments['signalhound'].GetSweep(do_plot=False, max_points=5000)
    f_offset = f[np.argmax(mi)]

    freq_LT4.append(f_offset/1e3 - 200.08e3)

    d.add_data_point(times[-1], freq_LT3[-1], freq_LT4[-1])

    p_c = qt.Plot2D(times, freq_LT3, 'bO-',times, freq_LT4, 'rO-', name='AOMfreqStabMsmt', clear=True)

    qt.msleep(18)

d.close_file()

p_c = qt.Plot2D(times, freq_LT3, 'bO-',times, freq_LT4, 'rO-', name='AOMfreqStabMsmt', clear=True)
p_c.save_png(filename+'.png')

qt.mend()
