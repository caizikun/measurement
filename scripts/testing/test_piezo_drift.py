import msvcrt
import time
from measurement.lib.config import optimiz0rs as  optqcfg
def wait_a_minute():
	for i in range(6):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			return False
		qt.msleep(10)
	return True

def measure_drift():

	waiting_times=linspace(0,60,12) #mins
	abs_times=[]
	y_movements = []
	countrates=[]

	for wt in waiting_times:
		qt.msleep(0.5)
		for m in arange(wt):
			if not(wait_a_minute()):
				return False

		y_movements.append(opt1d_counts.run(dimension='x', counter = 1, 
		                   pixel_time=50, return_position_change = True,
		                   **optcfg.dimension_sets['lt3']['x']))
		qt.msleep(0.5)
		countrates.append(adwin.get_countrates()[0])
		abs_times.append(time.strftime('%H%M'))
		print 'appended',y_movements[-1], 'nm for waiting time', wt, 'countrates:',countrates[-1]
		qt.msleep(0.5)
		optimiz0r.optimize(dims=['x','y','z'], cycles=3)
	return waiting_times, y_movements, countrates, abs_times

if __name__ == '__main__':
	GreenAOM.set_power(5e-6)
	optimiz0r.optimize(dims=['x','y','z'], cycles=1)
	waiting_times, y_movements, countrates, abs_times = measure_drift()