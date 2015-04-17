import msvcrt
import qt
import numpy as np

def optimize():
    print 'Starting to optimize.'
    powers_ok=False
    for i in range(5):
    	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if bell_check_powers():
            powers_ok=True
            print 'All powers are ok.'
            break
    if not powers_ok:
        print 'Could not get good powers!'
        return False

    
    qt.msleep(3)
    optimize_ok = False
    for i in range(2):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if qt.current_setup=='lt4':
            optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=150, cycles =1)
        else:
            qt.instruments['optimiz0r'].optimize(dims=['z'],cnt=1, int_time=150, cycles =1)
            optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['x','y'],cnt=1, int_time=150, cycles =1)
        qt.msleep(1)
    if not(optimize_ok):
        print 'Not properly optimized position'
        return False
    else: 
    	print 'Position is optimized!'
    qt.msleep(3)
    
    return True
    
def bell_check_powers():
    names=['MatisseAOM', 'NewfocusAOM','PulseAOM','YellowAOM']
    setpoints = [5e-9, 10e-9, 30e-9,50e-9]
    relative_thresholds = [0.1,0.1,0.3,0.2]
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    qt.stools.init_AWG()
    qt.stools.turn_off_all_lasers()

    all_fine=True
    for n,s,t in zip(names, setpoints,relative_thresholds):
    	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if n == 'PulseAOM': qt.msleep(2)
        setpoint, value = qt.stools.check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
        deviation =np.abs(1-setpoint/value)
        print 'deviation', np.abs(1-setpoint/value)
        if deviation>t:
            all_fine=False
            qt.stools.recalibrate_laser(n, 'PMServo', 'adwin')
            if n == 'NewfocusAOM':
                qt.stools.recalibrate_laser(n, 'PMServo', 'adwin',awg=True)
            break
    qt.instruments['PMServo'].move_out()
    return all_fine

if __name__ == '__main__':
	#stools.start_bs_counter()
    start_index = 101
    cycles=500
    for i in range(start_index,start_index+cycles):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if qt.current_setup=='lt4':
            qt.instruments['lt4_helper'].set_is_running(True)
        else:
            qt.instruments['remote_measurement_helper'].set_script_path('bell_lt3.py')
            qt.instruments['remote_measurement_helper'].set_is_running(True)
        qt.bell_name_index = i
        execfile(r'sweep_Bell.py')
        if qt.current_setup=='lt4':
            qt.instruments['lt4_helper'].set_is_running(False)
        else:
            qt.instruments['remote_measurement_helper'].set_is_running(False)

        qt.msleep(10)
        if i%10 ==0:
            execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py') #change name!
            lt4_succes = optimize()
            qt.msleep(5)
                  
            if not(lt4_succes):
                break  #cycle is ~1 Hour
    #stools.stop_bs_counter()