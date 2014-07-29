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

	waiting_times=linspace(0,60*18,12*18) #mins
	abs_times=[]
	y_movements = []
	countrates=[]
	stop_script = False

	for wt in waiting_times:
		qt.msleep(0.5)
		for m in arange(wt):
			if not(wait_a_minute()):
				print '\n I am doing one last optimization run and I am stopping.\n \
				Keep on pressing "q" !!\n'
				stop_script = True
				break



		y_movements.append(opt1d_counts.run(dimension='x', counter = 1, 
		                   pixel_time=50, return_position_change = True,
		                   **optqcfg.dimension_sets['lt3']['x']))
		qt.msleep(0.5)
		countrates.append(adwin.get_countrates()[0])
		print adwin.get_countrates()[0]
		abs_times.append(time.strftime('%H%M'))
		print 'appended',y_movements[-1], 'nm for waiting time', wt, 'countrates:',countrates[-1]
		qt.msleep(0.5)
		optimiz0r.optimize(dims=['x','y','z'], cycles=3)
		
		if stop_script: break

	return waiting_times, y_movements, countrates, abs_times


if __name__ == '__main__':
    GreenAOM.set_power(5e-6)
    optimiz0r.optimize(dims=['x','y','z'], cycles=1)
    waiting_times, y_movements, countrates, abs_times = measure_drift()
    #print 'Finish and :', waiting_times,  y_movements, countrates, abs_times
    
    waiting_times_tronc = waiting_times[:- (len(waiting_times)- len(y_movements))]
    #print waiting_times_tronc
    # saving the data
    name = 'Drift_servoloop_ON_after_PIchange'
    d = qt.Data(name=name)
    d.add_coordinate('waiting time [min]')
    d.add_coordinate('drift [nm]')
    d.add_coordinate('counts [s-1]')
    d.add_coordinate('absolute time [min]')
    d.create_file()
    filename=d.get_filepath()[:-4]
    
    d.add_data_point(waiting_times_tronc, y_movements, countrates, map(int,abs_times))
    d.close_file()
    
    plot_drift_vs_wt = qt.Plot2D(d, 'bO-', coorddim=0, name='Drift vs wainting time', valdim=1, clear=True)
    plot_drift_vs_wt.save_png(filename+'.png')
    
    plot_drift_vs_abst = qt.Plot2D(d, 'kO-', coorddim=3, name='Drift vs absolute time', valdim=1, clear=True)
    plot_drift_vs_abst.save_png(filename+'.png')
    
    plot_counts_vs_abst = qt.Plot2D(d, 'rO-', coorddim=3, name='Counts vs absolute time', valdim=2, clear=True)
    plot_counts_vs_abst.save_png(filename+'.png')
    
    qt.mend()
    