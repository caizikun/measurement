import numpy as np
import qt 
import msvcrt

for k in range(10):
    
	GreenAOM.set_power(7e-6)
	ins_counters.set_is_running(0)  
	optimiz0r.optimize(dims=['x','y','z'])

	print '-----------------------------------'            
	print 'press q to stop measurement cleanly'
	print '-----------------------------------'
	qt.msleep(2)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
		break

	execfile('D:/measuring/measurement/scripts/QEC/QEC_ssro_calibration.py')
	
	execfile('D:/measuring/measurement/scripts/QEC/3Qubit_QEC_test_states.py')

	execfile('D:/measuring/measurement/scripts/QEC/NuclearCrosstalk.py')

	execfile('D:/measuring/measurement/scripts/QEC/QEC_ssro_calibration.py')

	execfile('D:/measuring/measurement/scripts/QEC/magnet/optimize_magnet_XYpos_nofit.py')

	execfile('D:/measuring/measurement/scripts/QEC/1Qubit_Initialization.py')