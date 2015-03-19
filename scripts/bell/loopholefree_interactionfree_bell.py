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
    for i in range(3):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=100, cycles =1)
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
    relative_thresholds = [0.1,0.1,0.3,0.1]
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
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
    qt.instruments['PMServo'].move_out()
    return all_fine

if __name__ == '__main__':
    if qt.current_setup=='lt4':
        start_index=1
        cycles=5
        for i in range(start_index,start_index+cycles):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break
            qt.bell_name_index = i
            qt.bell_succes=False
            execfile(r'bell_lt4.py')
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or not(qt.bell_succes): 
                break
            qt.msleep(20)

            print 'starting the measurement at lt3'
            lt3_helper = qt.instruments['lt3_helper']
            lt3_helper.set_is_running(False)
            lt3_helper.set_measurement_name('optimizing')
            lt3_helper.set_script_path(r'Y:/measurement/scripts/bell/loopholefree_interactionfree_bell.py')
            lt3_helper.execute_script()
            print 'Loading CR linescan'
            execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')#change name!
            lt4_succes = optimize()
            #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
            qt.msleep(5)
            while lt3_helper.get_is_running():
                if(msvcrt.kbhit() and msvcrt.getch()=='q'): 
                    print 'Measurement aborted'
                    lt3_succes= False
                    break
            qt.msleep(5)
            output = lt3_helper.get_measurement_name()
            lt3_success = (output == 'True')
            print 'Was lt3 successfully optimized? ', lt3_success
            
            if not(lt4_succes) or not(lt3_success):
                break#cycle is ~1 Hour
        stools.stop_bs_counter()
    else:
        execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')
        lt3_succes = optimize()
        #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
        qt.msleep(5) # when you resetart bell to early, it will crash
        print 'Did the optimization procedure succeed? ', lt3_succes
        qt.instruments['remote_measurement_helper'].set_measurement_name(str(lt3_succes))
        qt.instruments['remote_measurement_helper'].set_is_running(False)
        print 'All done. Ready to run Bell.'