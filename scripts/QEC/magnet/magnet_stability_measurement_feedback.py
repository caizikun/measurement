import numpy as np
import qt 
import msvcrt
from analysis.lib.m2.ssro import ssro as ssro_test; reload(ssro)
ins_counters = qt.instruments['counters']

for k in range(1000):
    
	if mod(k,15)==0:
		GreenAOM.set_power(10e-6)
		qt.msleep(10)
		ins_counters.set_is_running(0)  
		optimiz0r.optimize(dims=['x','y','z'], int_time=300, gaussian_fit = False)

	print '-----------------------------------'            
	print 'press q to stop measurement cleanly'
	print '-----------------------------------'
	qt.msleep(2)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
		break

	# execfile('D:/measuring/measurement/scripts/QEC/magnet/optimize_magnet_XYpos_m1.py')