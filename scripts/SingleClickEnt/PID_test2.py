import qt
import numpy as np
from matplotlib import pyplot as plt
import msvcrt

# variables
t = 0
s = 0
t_wait = 0.1
s_old = 0
m = 0.2
noise = 0
k=0
V_out = 0
s = 0
# definitions

# plot
plt.ion()
plt.scatter(t,k,c='r',label='original signal')              # plotting t,k separately 
plt.scatter(t,s,c='b',label='modulated signal')             # plotting t,s separately 
plt.scatter(t,V_out,c='g',label='Output PID')               # plotting t,V_out separately
plt.legend(loc='upper left');



# PID controller
adwin.load_PID_fiberstretcher()
adwin.start_PID_fiberstretcher(setpoint = 5, delay=100)

while True:
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):            # To stop iteration
        adwin.stop_PID_fiberstretcher()
        break

    # Signal building
    V_out = adwin.get_PID_fiberstretcher_var('V_out')           # Get output PID
    noise = np.random.random_sample()/2                                   # Noise
    if (t%10 < 5):
        k=0
    else:
        k=10
    s = k + V_out + noise
    s = s - (s - s_old)*m

    # Plots
    plt.scatter(t,k,c='r',label='original signal')              # plotting t,k separately 
    plt.scatter(t,s,c='b',label='modulated signal')             # plotting t,s separately 
    plt.scatter(t,V_out,c='g',label='Output PID')               # plotting t,V_out separately

    # Updates
    adwin.set_PID_fiberstretcher_var(input=s)                   # Signal into PID
    t = t+t_wait
    s_old = s

    qt.msleep(t_wait)
