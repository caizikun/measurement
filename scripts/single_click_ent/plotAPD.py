import qt
import numpy as np
from matplotlib import pyplot as plt
import msvcrt
from IPython import display

# variables
timewindow = 10                 # total time window
time_wait = 0.01                 # time per datapoint

# definitions
datapoints = timewindow/time_wait    

x_time = zeros(datapoints)          
y_counts = zeros(datapoints)

# init
t = 0

# plot
plt.axis([0, datapoints, -1, 1])
plt.show()
plt.ion()


counter = qt.instruments['counters']



while True:
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break

    plt.clf()                            # clear plot

    x_time[-1] = t # timewindow   # get time
    y_counts[-1] = counter.get_cntr3_countrate() #sin(t)      # get counts
    plt.scatter(x_time,y_counts)         # plot

    t= t+0.1                             # new time for next itteration

    x_time = np.roll(x_time, -1)          # Roll time
    y_counts = np.roll(y_counts, -1)      # Roll counts

    qt.msleep(time_wait)