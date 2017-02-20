import math
import instrument as instrument
import numpy as np
import msvcrt

# instruments needed
# labjack = qt.instruments.create('labjack', 'LabJack_U3')
# physical_adwin = qt.instruments.create('physical_adwin')
# pidyellow = qt.instruments.create('pidyellow')

# vars
steps = 25
yellow_voltage_amp = 1
time_delay = 0.002

# init
i = 0
yellow_freq_start = physical_adwin.Get_FPar(52)
yellow_voltage_start = labjack.get_bipolar_dac3()
diditrun = pidyellow.get_is_running()
pidyellow.stop()

while True:
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        physical_adwin.Set_FPar(52,yellow_freq_start);
        pidyellow.start()
        print 'Quit by user'
        break

    yellow_voltage = yellow_voltage_start + yellow_voltage_amp*math.sin(2*np.pi*i/steps)
    labjack.set_bipolar_dac3(yellow_voltage)
    # print 'labjack voltage:', yellow_voltage
    i = i + 1 
    qt.msleep(time_delay)