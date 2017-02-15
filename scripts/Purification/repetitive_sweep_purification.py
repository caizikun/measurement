"""
executes the file sweep_purification.py repetitively
utilizes the green laser for optimization purposes.

"""
import numpy as np
import qt
import msvcrt
import time

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

if __name__ == '__main__':

    start_time = time.time()
    optimize_time = time.time()
    while time.time()-start_time < 16*60*60:
        if show_stopper():
            break
        if time.time()-optimize_time > 30*60:
            GreenAOM.set_power(1e-5)
            optimiz0r.optimize(dims=['x','y','z','y','x'])
            GreenAOM.turn_off()
            optimize_time = time.time()

        execfile(r'sweep_purification.py')