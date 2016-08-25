import qt
import msvcrt
import time

def fast_laser_scan(name,grpower,redpower):
    dac_names = ['newfocus_frq']
    start_voltages = [9]
    stop_voltages = [-9]
    steps = int(90e9/20e6) # 60 GHz (approx newfocus range) / (stepsize 100 MHz)
    px_time= 100#ms
    plot_voltage=True
    adwin_ins = qt.instruments['adwin']

    GreenAOM.set_power(grpower)
    NewfocusAOM.set_power(redpower)

    counters.set_is_running(False)

    V = np.linspace(start_voltages[0],stop_voltages[0],steps)
    dat = qt.Data(name= 'laser_scan'+name)
    dat.add_coordinate('Voltage [V]')
    dat.add_coordinate('Frequency [GHz]')
    dat.add_value('Counts [Hz]')
    dat.create_file()
    plt = qt.Plot2D(dat, 'rO', name='laser_scan', coorddim=1, valdim=2, 
                    clear=True)
    if plot_voltage:
        plt.add_data(dat,coorddim=1, valdim=0, right=True)

    print 'expected time:', float(steps)*px_time*1e-3/60., 'minutes'

    adwin_ins.load_linescan()
    adwin_ins.linescan(dac_names, start_voltages, stop_voltages, steps, 
                px_time, value='counts+suppl', scan_to_start=True, blocking=False, 
                abort_if_running=True)
    print GreenAOM.get_power()

    prev_px_clock = 0
    while 1:
        px_clock = adwin_ins.get_linescan_var('get_px_clock')
        start = prev_px_clock+1
        length  = px_clock-prev_px_clock
        if length > 0:
            
            f = adwin_ins.get_linescan_var('get_supplemental_data', start =start, length=length)
            valid_range = f>-3000
            v = V[start-1:start+length-1]
            cs = adwin_ins.get_linescan_var('get_counts', start =start, length=length)
            c = (cs[0]+cs[1])/(px_time*1.e-3)
            
            if np.sum(valid_range)>1:
                dat.add_data_point(v[valid_range],f[valid_range],c[valid_range])
                prev_px_clock = px_clock
        if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
            adwin_ins.stop_linescan()
        qt.msleep(0.2)
        if not(adwin_ins.is_linescan_running()):
            break
        plt.update()

    for n in dac_names:
        adwin_ins.set_dac_voltage((n,V[prev_px_clock-1]))

    NewfocusAOM.turn_off()
    print 'done'

    dat.close_file()
    plt.save_png(dat.get_filepath()+'png')

def long_fast_laser_scan(name,grpower,redpower):
    '''
    Repeats full voltage range scans for coarse wavelength steps
    '''
    opt_ins = qt.instruments['optimiz0r']
    opt1d_ins = qt.instruments['opt1d_counts']
    mos_ins = qt.instruments['master_of_space']

    wls = np.linspace(637.07,636.72,6)
    #wls = np.linspace(637.26,637.22,2)
    print wls
    for ii,wl in enumerate(wls):
        #GreenAOM.set_power(200e-6)
        #mos_ins.set_x(mos_ins.get_x()-1)
        #opt_ins.optimize(dims=['z'], cycles = 1, int_time = 100)
        #opt1d_ins.run(dimension='z', scan_length=5, nr_of_points=31, pixel_time=100, return_data=False, gaussian_fit=True)
        #mos_ins.set_x(mos_ins.get_x()+1)
        #mos_ins.set_z(mos_ins.get_z()+0.6)
        #qt.msleep(1)
        #opt_ins.optimize(dims=['x','y'], cycles = 2, int_time = 100)

        NewfocusLaser.set_wavelength(wl)
        print 'laser wavelength set to',NewfocusLaser.get_wavelength()

        fast_laser_scan(name+'_'+str(ii),grpower,redpower)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
    counters.set_is_running(True)        
if __name__ == '__main__':
    grpower = 0e-6
    redpower = 15.e-9
    name = '_Sophie_area_7_NV1'+str(grpower*1.e6)+'_r_'+str(redpower*1.e9)
    #long_fast_laser_scan(name,grpower,redpower)
    counters.set_is_running(False)
    fast_laser_scan(name,grpower,redpower)