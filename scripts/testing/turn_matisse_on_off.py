import numpy as np
import qt 
import msvcrt
name = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

i = 0
while True:
	i += 1
	if show_stopper():
		break

	if i % 2 ==0:
		MatisseAOM.set_power(1e-8)
	else:
		MatisseAOM.set_power(0e-8)