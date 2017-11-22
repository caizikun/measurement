import qt
import numpy as np
import matplotlib.pyplot as plt
import msvcrt

HH = qt.instruments.get_instruments()['HH_400']

x =  np.arange(0,100)
y =  np.zeros(100)

fig = plt.figure()
plt.subplots_adjust(top = 0.85)
plt.ion()

while True:

    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        plt.close()
        break

    newval = HH.get_CountRate()
    plt.clf()

    y = np.roll(y,-1)
    y[-1] = newval
    
    plt.plot(x,y)
    plt.ylim([0,plt.ylim()[1]*1.1])
    plt.annotate('Counts: ' + str(newval), xy=(0.25, 1.05), xycoords='axes fraction',fontsize = 40, color = 'Blue', annotation_clip = False)

    plt.pause(0.05)


