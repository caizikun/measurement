import msvcrt
import qt
import numpy as np

def optimize():
    powers_ok=False
    for i in range(5):
        if bell_check_powers():
            powers_ok=True
            break
    if not powers_ok:
        print 'Could not get good powers!!'
        return False

    
    qt.msleep(3)
    optimize_ok = False
    for i in range(3):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=100, cycles =1)
        qt.msleep(1)
    if not(optimize_ok):
        print 'Not properly optimized position'
        return False
    qt.msleep(3)
    
    return True
    
def bell_check_powers():
    names=['MatisseAOM', 'NewfocusAOM','YellowAOM', 'PulseAOM']
    setpoints = [5e-9, 10e-9, 50e-9,30e-9]
    relative_thresholds = [0.1,0.1,0.1,0.3]
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    qt.stools.turn_off_all_lasers()

    all_fine=True
    for n,s,t in zip(names, setpoints,relative_thresholds):
        setpoint, value = qt.stools.check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
        deviation =np.abs(1-setpoint/value)
        print 'deviation', np.abs(1-setpoint/value)
        if deviation>t:
            all_fine=False
            qt.stools.recalibrate_laser(n, 'PMServo', 'adwin')
            if n == 'NewfocusAOM':
                qt.stools.recalibrate_laser(n, 'PMServo', 'adwin',awg=True)
    qt.instruments['PMServo'].move_out()
    return all_fine

if __name__ == '__main__':
    if qt.current_setup=='lt4':
        start_index=4
        cycles=3
        for i in range(start_index,start_index+cycles):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break
            qt.bell_name_index = i+1
            execfile(r'bell_lt4.py')
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break
            qt.msleep(20)

            lt3_helper = qt.instruments['lt3_helper']
            lt3_helper.set_is_running(False)
            lt3_helper.set_script_path(r'Y:/measurement/scripts/bell/loopholefree_interactionfree_bell.py')
            lt3_helper.execute_script()
            execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')
            lt4_succes = optimize()
            #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
            qt.msleep(5)
            while lt3_helper.get_is_running():
                if(msvcrt.kbhit() and msvcrt.getch()=='q'): 
                    print 'measurement aborted'
                    lt3_succes= False
                    break
            if not lt3_helper.get_is_running():
                output = lt3_helper.get_measurement_name()
                lt3_success = (output == 'True')
            if not(lt4_succes) or not(lt3_success):
                break#cycle is ~1 Hour
    else:
        execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')
        lt3_succes = optimize()
        #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
        qt.msleep(5) # when you resetart bell to early, it will crash
        qt.instruments['remote_measurement_helper'].set_measurement_name(str(lt3_succes))
        qt.instruments['remote_measurement_helper'].set_is_running(False)