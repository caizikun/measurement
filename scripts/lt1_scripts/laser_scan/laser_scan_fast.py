import qt
import msvcrt
import time
import scipy
import numpy as np

def fast_laser_scan(name,grpower,redpower,mw):
    dac_names = ['newfocus_frq']
    start_voltages = [0]
    stop_voltages = [-4]
    steps = int(20e9/100e6) # 60 GHz (approx newfocus range) / (stepsize 100 MHz)
    px_time= 1000#ms
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
    plt = qt.Plot2D(dat, 'r-', name='laser_scan', coorddim=1, valdim=2, 
                    clear=True)
    if plot_voltage:
        plt.add_data(dat,coorddim=1, valdim=0, right=True)

    print 'expected time:', float(steps)*px_time*1e-3/60., 'minutes'

    adwin_ins.load_linescan()
    adwin_ins.linescan(dac_names, start_voltages, stop_voltages, steps, 
                px_time, value='counts+suppl', scan_to_start=True, blocking=False, 
                abort_if_running=True)
    print GreenAOM.get_power()

    if mw:
        print 'MW!'
        SMB100.set_frequency(2.878e9)
        SMB100.set_power(15)
        SMB100.set_status('on')
    prev_px_clock = 0
    while 1:
        px_clock = adwin_ins.get_linescan_var('get_px_clock')
        start = prev_px_clock+1
        length  = px_clock-prev_px_clock
        if length > 0:
            
            f = adwin_ins.get_linescan_var('get_supplemental_data', start =start, length=length)
            valid_range = f>-3000
            #print valid_range
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
    if mw:
        SMB100.set_status('off')

def long_fast_laser_scan(name,grpower,redpower,mw):
    '''
    Repeats full voltage range scans for coarse wavelength steps
    '''
    opt_ins = qt.instruments['optimiz0r']
    opt1d_ins = qt.instruments['opt1d_counts']
    mos_ins = qt.instruments['master_of_space']


    #fs = np.arange(200,350,75)
    #wls = np.linspace(637.26,637.22,2)
    #print fs
    for ii in range(0,50):
        # for j in range(3):
        #     set_nf_frequency_coarse(f)
        #     qt.msleep(1)
        fast_laser_scan(name+'_'+str(ii),grpower,redpower,mw)
        GreenAOM.set_power(20e-6)
        qt.msleep(1)
        opt_ins.optimize(dims=['x','y','z','x','y'], cycles = 1, int_time = 100, cnt=2)
        qt.msleep(1)
        
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
    
def set_nf_frequency_coarse(f): # GHz wrt 470.4 THz

    cur_f = get_cur_frequency()
    print cur_f
    delta_f = f-cur_f
    cur_wl_nf = NewfocusLaser.get_wavelength()
    cur_f_nf = scipy.constants.c/(cur_wl_nf*1e-9)
    new_f_nf  = cur_f_nf + delta_f*1e9
    new_wl_nf = scipy.constants.c/new_f_nf*1e9
    print 'current: {:.2f}, new: {:.2f}'.format(cur_wl_nf,new_wl_nf)
    NewfocusLaser.set_wavelength(new_wl_nf)
    

def get_cur_frequency():
    cur_f = physical_adwin.Get_FPar(46)
    return cur_f

if __name__ == '__main__':
    mw=True
    grpower = 0e-6
    redpower = 2e-9
    name = 'Harry_Scan1_NV2'+'_g_'+str(grpower*1.e6)+'_r_'+str(redpower*1.e9)
    
    counters.set_is_running(False)
    if mw:
        GreenAOM.set_power(100e-6)
        qt.msleep(1)
        GreenAOM.set_power(0e-6)
    fast_laser_scan(name,grpower,redpower,mw)
    #long_fast_laser_scan(name,grpower,redpower,mw)
    