import qt
import numpy as np
from matplotlib import pyplot as plt
import msvcrt


# variables
timewindow = 10                   # total time window  [s]
time_wait = 1                    # time per array     [s]
int_time = 1                     #                    [ms]
max_steps = 500
t = 0                           
i = 0

# definitions

# datapoints = max_steps*timewindow/time_wait
# x_time = zeros(datapoints)
# y_counts = zeros(datapoints)

# plot
plt.ion()

while True:
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        break

                                           # clear plot

    adwin.start_oscilloscope(
            int_time=int_time,
            max_steps=max_steps
            )

    qt.msleep(time_wait)

    counts = adwin.get_oscilloscope_var('APD_counts', start=0, length=max_steps)
    x_time = np.arange(max_steps)

    plt.clf()
    plt.ylim([0,800])
    plt.plot(x_time, counts)
    plt.show()

    # while i in range(0,max_steps-1):
    #     y_counts[-1] = counts[i]
    #     x_time[-1] = t + i*time_wait/max_steps
    #     plt.scatter(x_time,y_counts)          # plot

    #     x_time = np.roll(x_time, -1)          # Roll time
    #     y_counts = np.roll(y_counts, -1)      # Roll counts



    t= t+time_wait                        # new time for next iteration