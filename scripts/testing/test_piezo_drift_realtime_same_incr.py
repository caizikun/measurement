import msvcrt
import time
from measurement.lib.config import optimiz0rs as  optqcfg

def wait_a_minute():
    for i in range(6):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			return False
		qt.msleep(10) 
    return True

def measure_drift(name, time_incr, pts = 100):   

    print '\n Starting a measurement with optimization steps every {} mins\
    during {:.1f} h.\n'.format(time_incr, time_incr*pts/60.)
    
    abs_times=linspace(1,pts,pts)*time_incr #mins
    x_movements = []
    y_movements = []
    z_movements = []
    countrates  = []
    real_times  = []

    stop_script = False

    data = None

    if data == None :
        new_data_supplied = False
        data = qt.Data(name=name)
        data.add_coordinate('absolute time from begin. [min]')
        data.add_coordinate('x drift [nm]')
        data.add_coordinate('y drift [nm]')
        data.add_coordinate('z drift [nm]')
        data.add_coordinate('counts [s-1]')
        data.add_coordinate('real time [HHMM]')

        plot_counts_vs_abst = qt.Plot2D(data, 'mo-', coorddim=0, name='Counts vs abs. time', valdim=4, clear=True)
        
        plot_drift_z_vs_abst = qt.Plot2D(data, 'bo-', coorddim=0, name='Drift of z (depth) vs abs. time', valdim=3, clear=True)    
       
        plot_drift_y_vs_abst = qt.Plot2D(data, 'go-', coorddim=0, name='Drift of y (horiz.) vs abs. time', valdim=2, clear=True)
        
        plot_drift_x_vs_abst = qt.Plot2D(data, 'ro-', coorddim=0, name='Drift of x (vert.) vs abs. time', valdim=1, clear=True)

        data.create_file()

    else :
        new_data_supplied = True



    for wt in abs_times:
        qt.msleep(0.5)
        for m in arange(time_incr):
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
        real_times.append(time.strftime('%H%M'))
        
        print '\n appended drifts for waiting time {} min:\n \
                x : {:.1f} nm; y : {:.1f} nm; z : {:.1f} nm\n\
                and counts : {} cts.s-1. \n'.format(wt, x_movements[-1],y_movements[-1],z_movements[-1],countrates[-1])
        qt.msleep(0.5)

        if not new_data_supplied:
            last_abst     = wt
            last_x      = x_movements[-1]
            last_y      = y_movements[-1]
            last_z      = z_movements[-1]
            last_counts = countrates[-1]
            last_realt  = int(real_times[-1])

            data.add_data_point( last_abst, last_x, last_y, last_z, last_counts, last_realt)     

            plot_counts_vs_abst.update()
            plot_drift_z_vs_abst.update()         
            plot_drift_y_vs_abst.update()
            plot_drift_x_vs_abst.update()


        optimiz0r.optimize(dims=['x','y','z'], cycles=3)

        if stop_script: break

    
    filename=data.get_filepath()[:-4]
    
   
    data.close_file()

    plot_drift_x_vs_abst.save_png(filename+'.png')
    plot_drift_y_vs_abst.save_png(filename+'.png')
    plot_drift_z_vs_abst.save_png(filename+'.png')
    plot_counts_vs_abst.save_png(filename+'.png')


    qt.mend()


    
    #return abs_times, x_movements, y_movements, z_movements, countrates


if __name__ == '__main__':

    name = 'Drift_incr_20min'
    time_incr = 20. # delay between two optimization step
    pts = 400*3
    GreenAOM.set_power(5e-6)
    optimiz0r.optimize(dims=['x','y','z'], cycles=1)
    measure_drift(name = name, time_incr = time_incr, pts = pts)

    