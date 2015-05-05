#LAser scan with matplotlib


import matplotlib.pyplot as plt
import numpy as np
import matplotlib
print 'matplotlib.__version__=', matplotlib.__version__
import msvcrt


def fast_laser_scan (v_min, v_max, nr_points):

    v_vals = np.linspace (v_min, v_max, nr_points)
    pd_signal = 0*v_vals
    v_step = float(v_max-v_min)/float(nr_points)
    # You probably won't need this if you're embedding things in a tkinter plot...
    plt.ion()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    line1, = ax1.plot(v_vals, pd_signal, 'b-', linewidth = 2) # Returns a tuple of line objects, thus the comma

    stop = False
    while not(stop):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): stop=True
        pd_signal = adwin.laserscan_photodiode(ADC_channel=1, nr_steps = nr_points, wait_cycles = 50, start_voltage = v_min, voltage_step=v_step)
        pd_signal = pd_signal+np.sin (v_vals)+0.1*np.random.rand(len(v_vals))
        line1.set_xdata(v_vals)
        line1.set_ydata(pd_signal)
        ax1.set_xlim(min(v_vals), max(v_vals))
        ax1.set_ylim(min(pd_signal), max(pd_signal))

        fig.canvas.draw()
    plt.close ('all')


fast_laser_scan (v_min =0., v_max = 5., nr_points = 100)