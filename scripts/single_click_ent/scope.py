import qt
import numpy as np
import scipy.fftpack
from matplotlib import pyplot as plt
import msvcrt
import time

name='ZPLInterferoMsmt'

# create data object
qt.mstart()

stop_scan = False

d = qt.Data(name=name)
d.add_coordinate('time [ms]')
d.add_value('counts ZPL 1')
d.add_value('counts ZPL 2')

d.create_file()
filename=d.get_filepath()[:-4]

# variables
int_time = 1000                   #                    [us]
max_steps = 1000                #                    [us]
t = 0                           
i = 0

# plot
xf = np.linspace(0, 1.0/(int_time*10**(-6)), max_steps/2)
x_time = np.arange(max_steps)
fig, (ax1, ax2) = plt.subplots(2,1)

plt.ion()

counters_running = qt.instruments['counters'].get_is_running()
qt.instruments['counters'].set_is_running(False)

time_wait = (int_time*max_steps)/1e6 + 0.1                 # time per array     [s]

import sce_expm_params_lt4 as params_lt4

g_0 = params_lt4.params_lt4['Phase_Msmt_g_0']
visibility =  params_lt4.params_lt4['Phase_Msmt_Vis']

while True:
    cur_time = time.time()

    adwin.start_oscilloscope(cur_time, 
            sample_cycles=int_time,
            max_repetitions=max_steps
            )
    time_array = np.arange(cur_time,cur_time+(float(int_time)*float(max_steps)*10**(-6)), (float(int_time)*10**(-6)))

    qt.msleep(time_wait)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        break

    counts_1 = adwin.get_oscilloscope_var('sample_counts_1', start=1, length=max_steps)
    counts_2 = adwin.get_oscilloscope_var('sample_counts_2', start=1, length=max_steps)
    yf = scipy.fftpack.fft(counts_1)
    yf = np.abs(yf[:len(yf)/2])

    cosvals = [2*(float(n0)/(float(n0)+float(n1)*g_0)-0.5)*visibility for n0,n1 in zip(counts_1,counts_2)]
    cosvals = [cosval if np.abs(cosval) < 1 else (1.0 * np.sign(cosval)) for cosval in cosvals]
    angle = 180*np.arccos(cosvals)/np.pi

    plt.sca(ax1)
    plt.cla()
    plt.ylim([0,190])
    plt.plot(x_time*int_time/1000.0, angle)
    # plt.plot(x_time*int_time/1000.0, counts_1, 'b')
    # plt.plot(x_time*int_time/1000.0, counts_2, 'r')
    plt.show()
    plt.draw()
    plt.xlabel('Time (ms)')
    
    plt.sca(ax2)
    plt.cla()
    plt.plot(xf,yf)
    ymax = 1.2*np.max(yf[10:])
    plt.ylim([0,ymax])
    plt.xlim([0,1500])
    plt.show()
    plt.draw()

    for i in range(max_steps):
        d.add_data_point(time_array[i], counts_1[i], counts_2[i])
    
    
    # while i in range(0,max_steps-1):
    #     y_counts[-1] = counts[i]
    #     x_time[-1] = t + i*time_wait/max_steps
    #     plt.scatter(x_time,y_counts)          # plot

    #     x_time = np.roll(x_time, -1)          # Roll time
    #     y_counts = np.roll(y_counts, -1)      # Roll counts



    t= t+time_wait                        # new time for next iteration

plt.close()
qt.instruments['counters'].set_is_running(counters_running)

d.close_file()

qt.mend()