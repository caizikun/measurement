import msvcrt
import qt
import numpy as np
from measurement.scripts.bell import check_awg_triggering as JitterChecker
reload(JitterChecker)


def optimize():
    print 'Starting to optimize.'

    print 'checking signalhoud:'
    if not(check_pulse_aom_frq()):
        return False
    print 'checking for SMB errors'
    if not(check_smb_errors()):
        return False
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
    for i in range(1):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if qt.current_setup=='lt4':
            qt.instruments['optimiz0r'].optimize(dims=['y','x'],cnt=1, int_time=100, cycles =1)
            optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=100, cycles =1)
        else:
            qt.instruments['optimiz0r'].optimize(dims=['x','y'],cnt=1, int_time=45, cycles =1)
            optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=45, cycles =2)
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
    setpoints = [5e-9, 10e-9, 15e-9,40e-9] #XXXXXXXXXXXXXXX #LT3 Yellow power fluctuates with setup steering LT3
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

def check_pulse_aom_frq():
    f_expected =200e6 + 500e3 #chagned due to frq drift 01-07-15 NK. #200e6 + 523e3 #200MHz + x Hz #XXXXXXXXXX
    f_offset = qt.stools.get_pulse_aom_frq()
    if np.abs(f_offset - f_expected) > 20e3: 
        print 'PulseAOM frequency too far off expected value!'
        return False
    else:
        return True

def check_smb_errors():
    return (qt.instruments['SMB100'].get_error_queue_length() == 0)

if __name__ == '__main__':
    if qt.current_setup=='lt4':
    	#stools.start_bs_counter()
        start_index = 15

        cycles=24
        DoJitterCheck = True  #not always necc as now in bell optimizer


        if DoJitterCheck :
            for i in range(2):
                jitterDetected = JitterChecker.do_jitter_test(resetAWG=False)
                print 'Here comes the result of the jitter test: jitter detected = '+ str(jitterDetected)
                if not jitterDetected:
                    break
        else: 
            jitterDetected = False
            print 'I will skip the jitter test.'

        if not(jitterDetected):
            for i in range(start_index,start_index+cycles):
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                    break
                qt.bell_name_index = i
                qt.bell_succes=False
                execfile(r'bell_lt4.py')
                output_lt4 = qt.instruments['lt4_helper'].get_measurement_name()
                output_lt3 = qt.instruments['lt3_helper'].get_measurement_name()     
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or \
                        not(qt.bell_succes)                     or \
                        (output_lt4 == 'bell_optimizer_failed') or \
                        (output_lt3 == 'bell_optimizer_failed'): 
                    break
                qt.msleep(20)

                print 'starting the measurement at lt3'
                lt3_helper = qt.instruments['lt3_helper']
                lt3_helper.set_is_running(False)
                lt3_helper.set_measurement_name('optimizing')
                lt3_helper.set_script_path(r'Y:/measurement/scripts/bell/loopholefree_interactionfree_bell.py')
                lt3_helper.execute_script()
                print 'Loading CR linescan'
                execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py') #change name!
                lt4_succes = optimize()
                qt.msleep(5)
                #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
                #qt.msleep(5)
                while lt3_helper.get_is_running():
                    if(msvcrt.kbhit() and msvcrt.getch()=='q'): 
                        print 'Measurement aborted while waiting for lt3'
                        lt3_succes= False
                        break
                qt.msleep(5)
                output = lt3_helper.get_measurement_name()         
                lt3_success = (output == 'True')
                print 'Was lt3 successfully optimized? ', lt3_success
                   
                if not(lt4_succes) or not(lt3_success):
                    break  #cycle is ~1 Hour
            #stools.stop_bs_counter()

    else:
    	qt.instruments['remote_measurement_helper'].set_is_running(True)
        execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')
        lt3_succes = optimize()
        #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
        qt.msleep(10) # when you resetart bell to early, it will crash
        print 'Did the optimization procedure succeed? ', lt3_succes
        qt.instruments['remote_measurement_helper'].set_measurement_name(str(lt3_succes))
        qt.instruments['remote_measurement_helper'].set_is_running(False)
        print 'All done. Ready to run Bell.'