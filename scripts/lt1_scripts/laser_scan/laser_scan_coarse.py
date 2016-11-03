import qt
import msvcrt
import time
import scipy
import numpy as np


min_v = -6
max_v = 9
dac_name = 'newfocus_frq'

def laser_scan_coarse(name,grpower,redpower,mw):
    dac_names = [dac_name]
    start_frequency = 1030 #GHz
    stop_frequency = 200 #GHz
    stepsize = -1 # GHz
    int_time= 1000#ms
    cntr = 2
    
    GreenAOM.set_power(0)
    NewfocusAOM.set_power(redpower)

    counters.set_is_running(False)

    frequencies = np.arange(start_frequency, stop_frequency, stepsize)
    
    dat = qt.Data(name= 'laser_scan'+name)
    dat.add_coordinate('Frequency [GHz]')
    dat.add_value('Counts [Hz]')
    dat.add_value('Counts w/o green [Hz]')
    dat.add_value('BG normalized cts')
    dat.create_file()
    plt = qt.Plot2D(dat, 'r-', name='laser_scan', coorddim=0, valdim=1, 
                    clear=True)
    plt.add_data(dat,coorddim=0, valdim=3, right=True)

    print 'expected time:', len(frequencies)*(2*int_time+2000)*1e-3/60., 'minutes'
   
    print GreenAOM.get_power()

    if mw:
        print 'MW!'
        SMB100.set_frequency(2.878e9)
        SMB100.set_power(20)
        SMB100.set_status('on')
    for i,f in enumerate(frequencies):
        if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
            break
        if not(goto_frequency(f)):
            print 'could not reach frequency ',f
        qt.msleep(0.2)
        actual_f = get_cur_frequency()
        if actual_f < -1000:
            qt.msleep(0.3)
            actual_f = get_cur_frequency()
            if actual_f < -1000:
                print 'bad frequency point ', f
                continue
        GreenAOM.set_power(0)
        bg_cts = adwin.measure_counts(int_time)[cntr-1]
        GreenAOM.set_power(grpower)
        qt.msleep(0.1)
        cts = adwin.measure_counts(int_time)[cntr-1]
        dat.add_data_point(actual_f,cts,bg_cts,float(cts)/bg_cts)
        GreenAOM.set_power(0)
        plt.update()

    NewfocusAOM.turn_off()
    print 'done'

    dat.close_file()
    plt.save_png(dat.get_filepath()+'png')
    if mw:
        SMB100.set_status('off')
    
def set_nf_frequency_coarse(f): # GHz wrt 470.4 THz
    while 1:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            return
        cur_f = get_cur_frequency()
        print cur_f
        if cur_f< -1000:
            qt.msleep(0.3)
        else:
            break
        
    delta_f = f-cur_f
    cur_wl_nf = NewfocusLaser.get_wavelength()
    cur_f_nf = scipy.constants.c/(cur_wl_nf*1e-9)
    new_f_nf  = cur_f_nf + delta_f*1e9
    new_wl_nf = scipy.constants.c/new_f_nf*1e9
    print 'current: {:.2f}, new: {:.2f}'.format(cur_wl_nf,new_wl_nf)
    NewfocusLaser.set_wavelength(new_wl_nf)
    
def goto_frequency(f, iteration=0):
    print 'goto_frequency iteration ', iteration
    if iteration > 5 or (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return False
    cur_f = get_cur_frequency()
    cur_v = adwin.get_dac_voltage(dac_name)
    max_delta_f = (min_v-cur_v)*-10 #GHz/V
    min_delta_f = (max_v-cur_v)*-15
    print min_delta_f, max_delta_f, (f - cur_f)
    if (min_delta_f < (f - cur_f) < max_delta_f):
        print 'scanning voltage'
        if scan_to_frequency(f):
            print 'success'
            return True
    scan_to_voltage(-3, blocking=True, pxtime = 2)
    qt.msleep(1)
    set_nf_frequency_coarse(f)
    qt.msleep(1)
    return goto_frequency(f, iteration=iteration+1)
    
def scan_to_frequency(f):
    if get_cur_frequency()>f:
        print 'scantomax'
        start_v,stepsize = scan_to_voltage(max_v)
        scan_up=False
    else:
        print 'scantomin'
        start_v,stepsize = scan_to_voltage(min_v)
        scan_up=True
    success = False
    while adwin.is_linescan_running():
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                adwin.stop_linescan()
                break
            if (get_cur_frequency()<f and not(scan_up)) or (get_cur_frequency()>f and scan_up):
                adwin.stop_linescan()
                cur_v = start_v+adwin.get_linescan_var('get_px_clock')*stepsize
                print 'cur_v',cur_v
                adwin.set_dac_voltage((dac_name,cur_v))
                success=True
                break
            time.sleep(0.01)
    time.sleep(0.2)
    if (get_cur_frequency()<f and not(scan_up)) or (get_cur_frequency()>f and scan_up):
        success=True

    return success

def scan_to_voltage(v, blocking=False, pxtime = 20):

    cur_v = adwin.get_dac_voltage(dac_name)
    stepsize = 10e-3 #10 mv steps
    steps = int(np.round(np.abs(v-cur_v)/stepsize)) 
    
     # 5 V/s = 5 mV/ms = 
    adwin.linescan([dac_name], [cur_v], [v],
                steps, pxtime, value='none', scan_to_start=False,
                blocking=blocking)
    if blocking:
        adwin.set_dac_voltage((dac_name,v))
    return cur_v,np.copysign(stepsize,v-cur_v)

    #adwin.move_to_dac_voltage('newfocus_frq', v, speed=100, blocking=False)    

def get_cur_frequency():
    cur_f = physical_adwin.Get_FPar(46)
    return cur_f

if __name__ == '__main__':
    mw=False
    grpower = 2e-6
    redpower = 200.e-9
    name = '_Sophie_area_5_NV1'+'_g_'+str(grpower*1.e6)+'_r_'+str(redpower*1.e9)
    
    counters.set_is_running(False)
    if mw:
        GreenAOM.set_power(100e-6)
        qt.msleep(1)
        GreenAOM.set_power(0e-6)
    laser_scan_coarse(name,grpower,redpower,mw)
    #long_fast_laser_scan(name,grpower,redpower,mw)
    