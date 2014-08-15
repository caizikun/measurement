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
    x_movements = []
    y_movements = []
    z_movements = []
    countrates=[]
    stop_script = False

    for wt in waiting_times:
        qt.msleep(0.5)
        for m in arange(wt):
            if not(wait_a_minute()):
                print '\n I am doing one last optimization run and I am stopping.\n \
                Keep on pressing "q" if you don\'t want to wait 3 cycles !!\n'
                stop_script = True
                break



        x_movements.append(opt1d_counts.run(dimension='x', counter = 1, 
                           pixel_time=50, return_position_change = True,
                           **optqcfg.dimension_sets['lt3']['x']))
        qt.msleep(0.5)

        y_movements.append(opt1d_counts.run(dimension='y', counter = 1, 
                           pixel_time=50, return_position_change = True,
                           **optqcfg.dimension_sets['lt3']['y']))
        qt.msleep(0.5)

        z_movements.append(opt1d_counts.run(dimension='z', counter = 1, 
                           pixel_time=50, return_position_change = True,
                           **optqcfg.dimension_sets['lt3']['z']))

        qt.msleep(0.5)
        countrates.append(adwin.get_countrates()[0])
        print adwin.get_countrates()[0]
        abs_times.append(time.strftime('%H%M'))
        print '\n appended drifts for waiting time {} min:\n \
                x : {:.1f} nm; y : {:.1f} nm; z : {:.1f} nm\n\
                and counts : {} cts.s-1.'.format(wt, x_movements[-1],y_movements[-1],z_movements[-1],countrates[-1])
        #print '\n appended resp. x, y, z drifts ',y_movements[-1], 'nm for waiting time', wt, '\n  and countrates:',countrates[-1] , '\n'
        qt.msleep(0.5)
        optimiz0r.optimize(dims=['x','y','z'], cycles=3)

        if stop_script: break

    return waiting_times, x_movements, y_movements, z_movements, countrates, abs_times


if __name__ == '__main__':
    GreenAOM.set_power(5e-6)
    optimiz0r.optimize(dims=['x','y','z'], cycles=1)
    waiting_times, x_movements, y_movements, z_movements, countrates, abs_times = measure_drift()
    #print 'Finish and :', waiting_times,  y_movements, countrates, abs_times
    
    waiting_times_tronc = waiting_times[:- (len(waiting_times)- len(y_movements))]
    #print waiting_times_tronc
    # saving the data
    name = 'Test'
    d = qt.Data(name=name)
    d.add_coordinate('waiting time [min]')
    d.add_coordinate('x drift [nm]')
    d.add_coordinate('y drift [nm]')
    d.add_coordinate('z drift [nm]')
    d.add_coordinate('counts [s-1]')
    d.add_coordinate('absolute time [HHmm]')
    d.create_file()
    filename=d.get_filepath()[:-4]
    
    d.add_data_point(waiting_times_tronc, x_movements, y_movements, z_movements, countrates, map(int,abs_times))
    d.close_file()


    plot_counts_vs_abst = qt.Plot2D(d, 'ro-', coorddim=0, name='Counts vs waiting time', valdim=4, clear=True)
    plot_counts_vs_abst.save_png(filename+'.png')


    # plot z drift
    plot_drift_vs_wt = qt.Plot2D(d, 'bo', coorddim=0, name='Drift of z (depth) vs waiting time', valdim=3, clear=True)
    plot_drift_vs_wt.save_png(filename+'.png')
    
    plot_drift_vs_abst = qt.Plot2D(d, 'ko-', coorddim=5, name='Drift vs absolute time', valdim=3, clear=True)
    plot_drift_vs_abst.save_png(filename+'.png')

    
    # plot y drift
    plot_drift_vs_wt = qt.Plot2D(d, 'b<', coorddim=0, name='Drift of y (horiz.) vs waiting time', valdim=2, clear=True)
    plot_drift_vs_wt.save_png(filename+'.png')
    
    plot_drift_vs_abst = qt.Plot2D(d, 'k<-', coorddim=5, name='Drift vs absolute time', valdim=2, clear=True)
    plot_drift_vs_abst.save_png(filename+'.png')
    

    # plot x drift
    plot_drift_vs_wt = qt.Plot2D(d, 'bv', coorddim=0, name='Drift of x (vert.) vs waiting time', valdim=1, clear=True)
    plot_drift_vs_wt.save_png(filename+'.png')
    
    plot_drift_vs_abst = qt.Plot2D(d, 'kv-', coorddim=5, name='Drift vs absolute time', valdim=1, clear=True)
    plot_drift_vs_abst.save_png(filename+'.png')


    qt.mend()
    