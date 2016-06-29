import msvcrt
import time
from measurement.lib.config import optimiz0rs as  optqcfg

def wait_a_minute():
    for i in range(6):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			return False
		qt.msleep(10) 
    return True

def measure_drift(name):   

    waiting_times=linspace(0,60*18,12*18+1) #mins
    abs_times=[]
    x_movements = []
    y_movements = []
    z_movements = []
    countrates=[]
    stop_script = False

    data = None

    if data == None :
        new_data_supplied = False
        data = qt.Data(name=name)
        data.add_coordinate('waiting time [min]')
        data.add_coordinate('x drift [nm]')
        data.add_coordinate('y drift [nm]')
        data.add_coordinate('z drift [nm]')
        data.add_coordinate('counts [s-1]')
        data.add_coordinate('absolute time [min]')

        plot_counts_vs_abst = qt.Plot2D(data, 'mo-', coorddim=0, name='Counts vs waiting time', valdim=4, clear=True)
        
        plot_drift_z_vs_wt = qt.Plot2D(data, 'bo-', coorddim=0, name='Drift of z (depth) vs waiting time', valdim=3, clear=True)    
        plot_drift_z_vs_abst = qt.Plot2D(data, 'bo--', coorddim=5, name='Drift of z vs absolute time', valdim=3, clear=True)
       
        plot_drift_y_vs_wt = qt.Plot2D(data, 'go-', coorddim=0, name='Drift of y (horiz.) vs waiting time', valdim=2, clear=True)
        plot_drift_y_vs_abst = qt.Plot2D(data, 'go--', coorddim=5, name='Drift of y vs absolute time', valdim=2, clear=True)
        
        plot_drift_x_vs_wt = qt.Plot2D(data, 'ro-', coorddim=0, name='Drift of x (vert.) vs waiting time', valdim=1, clear=True)
        plot_drift_x_vs_abst = qt.Plot2D(data, 'ro--', coorddim=5, name='Drift of x vs absolute time', valdim=1, clear=True)

        data.create_file()

    else :
        new_data_supplied = True


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
                and counts : {} cts.s-1. \n'.format(wt, x_movements[-1],y_movements[-1],z_movements[-1],countrates[-1])
        #print '\n appended resp. x, y, z drifts ',y_movements[-1], 'nm for waiting time', wt, '\n  and countrates:',countrates[-1] , '\n'
        qt.msleep(0.5)

        if not new_data_supplied:
            last_wt     = wt
            last_x      = x_movements[-1]
            last_y      = y_movements[-1]
            last_z      = z_movements[-1]
            last_counts = countrates[-1]
            last_abst   = int(abs_times[-1])

            data.add_data_point( last_wt, last_x, last_y, last_z, last_counts, last_abst )     

            plot_counts_vs_abst.update()
            plot_drift_z_vs_wt.update()
            plot_drift_z_vs_abst.update()
            plot_drift_y_vs_wt.update()
            plot_drift_y_vs_abst.update()
            plot_drift_x_vs_wt.update()
            plot_drift_x_vs_abst.update()


        optimiz0r.optimize(dims=['x','y','z'], cycles=3)

        if stop_script: break

    
    filename=data.get_filepath()[:-4]
    
   
    data.close_file()

    plot_drift_x_vs_wt.save_png(filename+'.png')
    plot_drift_x_vs_abst.save_png(filename+'.png')
    plot_drift_y_vs_wt.save_png(filename+'.png')
    plot_drift_y_vs_abst.save_png(filename+'.png')
    plot_drift_z_vs_wt.save_png(filename+'.png')
    plot_drift_z_vs_abst.save_png(filename+'.png')
    plot_counts_vs_abst.save_png(filename+'.png')


    qt.mend()


    return waiting_times, x_movements, y_movements, z_movements, countrates, abs_times


if __name__ == '__main__':

    name = 'Drift_over_night_LT4_controller_in_LT3'
    GreenAOM.set_power(5e-6)
    optimiz0r.optimize(dims=['x','y','z'], cycles=1)
    waiting_times, x_movements, y_movements, z_movements, countrates, abs_times = measure_drift(name = name)
    #print 'Finish and :', waiting_times,  y_movements, countrates, abs_times
    
    #print waiting_times_tronc
    # saving the data

    