import qt
import numpy as np
from matplotlib import pyplot as plt
import msvcrt

# variables
k = 50
A = 10
t_wait = 0.1
t = 0
teta = 0
s = 0
omega = 0.1
V_out = 0

# definitions

# plot
plt.ion()

# Find setpoint for PID controller
adwin.load_PID_fiberstretcher_setpoint()
adwin.start_PID_fiberstretcher_setpoint(delay=200)

while (t < 10):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        break

    s = A * ( sin(omega*t) + 1 )
    plt.scatter(t, s)

    adwin.set_PID_fiberstretcher_setpoint_var(input=s)
    t = t+t_wait

    qt.msleep(t_wait)

# Stop current process and wait
adwin.stop_PID_fiberstretcher_setpoint()
qt.msleep(t_wait)

# PID controller
adwin.load_PID_fiberstretcher()
adwin.start_PID_fiberstretcher(delay=100)

while True:
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):            # To stop iteration
        adwin.stop_PID_fiberstretcher()
        break

    V_out = adwin.get_PID_fiberstretcher_var('V_out')           # Get output PID
    teta = V_out*k                                              # Extra phase due to stretcher

    s = A * ( sin(omega*t + teta) + 1 )                         # Calculate signal
    plt.scatter(t, s)                                           # plot

    adwin.set_PID_fiberstretcher_var(input=s)                   # Signal into PID
    t = t+t_wait                                                # new time for next iteration
    qt.msleep(t_wait)