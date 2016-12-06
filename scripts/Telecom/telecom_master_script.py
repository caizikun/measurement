import msvcrt
import qt
import numpy as np



def optimize():
    print 'Starting to optimize.'

    # print 'checking for SMB errors'
    # if not(check_smb_errors()):
    #     print 'SMB gave errors!!'
    #     return False
    powers_ok=False
    for i in range(5):
    	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if lt3_check_powers():
            powers_ok=True
            print 'All powers are ok.'
            break
    if not powers_ok:
        print 'Could not get good powers!'
        return False
   
    qt.msleep(3)
    print 'mash q now to stop the measurement'
    optimize_ok = True
    for i in range(1):
        print 'press q now to stop measuring!'
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        qt.instruments['optimiz0r'].optimize(dims=['x','y'],cnt=1, int_time=50, cycles =1)
        optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=50, cycles =2)
        qt.msleep(1)
    if not(optimize_ok):
        print 'Not properly optimized position'
        return False
    else: 
    	print 'Position is optimized!'
    # qt.msleep(3)
    
    return True
    
def lt3_check_powers():

    prot_name = qt.exp_params['protocols']['current']

    names=['MatisseAOM', 'NewfocusAOM','YellowAOM']
    setpoints = [qt.exp_params['protocols'][prot_name]['AdwinSSRO']['Ex_RO_amplitude'],
                700e-9, # The amount for repumping in purification
                qt.exp_params['protocols']['AdwinSSRO']['yellow_repump_amplitude']] #XXXXXXXXXXXXXXX #LT3 Yellow power fluctuates with setup steering LT3
    relative_thresholds = [0.15,0.15,0.15]
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    qt.stools.init_AWG()
    qt.stools.turn_off_all_lasers()

    all_fine=True
    for n,s,t in zip(names, setpoints,relative_thresholds):
    	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        setpoint, value = qt.stools.check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
        deviation =np.abs(1-setpoint/value)
        print 'deviation', deviation
        if deviation>t:
            all_fine=False
            qt.stools.recalibrate_laser(n, 'PMServo', 'adwin')
            if n == 'NewfocusAOM':
                qt.stools.recalibrate_laser(n, 'PMServo', 'adwin',awg=True)
            break
    qt.instruments['PMServo'].move_out()
    return all_fine



def check_smb_errors():
    try: 
        ret_val = (qt.instruments['SMB100'].get_error_queue_length() == 0)
    except:
        ret_val = (qt.instruments['SGS100'].get_error_queue_length() == 0)
    return ret_val

if __name__ == '__main__':
    if qt.current_setup =='lt3':

        tel1_helper = qt.instruments['tel1_helper']

        start_index = 1
        skip_first=False

        cycles = 200

        noof_cycles_for_green_reset = 4
        counter_for_green_reset = 0


        for i in range(start_index,start_index+cycles):
            # counter_for_green_reset += 1
            # print '\ncounter for green reset = {}\n'.format(counter_for_green_reset)
            # if counter_for_green_reset==noof_cycles_for_green_reset: 
            #     execfile(r'D:/measuring/measurement/scripts/tel1_scripts/reset_NV_with_green.py')
            #     counter_for_green_reset = 0


            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                break
            if not(skip_first):
                qt.telcrify_name_index = i
                qt.master_script_is_running = True
                    
                execfile(r'telcrify.py')
                output_tel1= qt.instruments['tel1_helper'].get_measurement_name()


                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or \
                        not(qt.telcrification_success) : 
                    break
                # qt.msleep(20)
                qt.telcrification_success=False
            skip_first=False

            #print 'starting the measurement at tel1'

            #tel1_helper.set_script_path(r'D:/measuring/measurement/scripts/tel1_scripts/pq_acquisition.py')
            #qt.msleep(15)
            #tel1_helper.execute_script()
            #qt.msleep(5)


            tel1_helper.set_script_path(r'D:/measuring/measurement/scripts/Telecom/telecom_master_script.py')
            qt.msleep(5)
            print 'Executing telecom_master_script at tel1...'
            tel1_helper.execute_script()

            qt.msleep(10)
            output = tel1_helper.get_measurement_name()         

            #print 'starting the measurement at lt3'

            print 'Loading CR linescan'
            execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py') #change name!
            qt.instruments['ZPLServo'].move_in()
            lt3_succes = optimize()
            qt.instruments['ZPLServo'].move_out()


    else:

    #### XXXX Yo dude, this has to be copied from tel1 - I didnt't have time to do the push-pull !! AD
        if False:
             	qt.instruments['remote_measurement_helper'].set_is_running(True)
            #     execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py')
            #     qt.instruments['ZPLServo'].move_in()
            #     lt3_succes = optimize()
            #     #execfile(r'D:/measuring/measurement/scripts/ssro/ssro_calibration.py')
            #     qt.instruments['ZPLServo'].move_out()
                qt.msleep(10) # when you resetart bell to early, it will crash
            #     print 'Did the optimization procedure succeed? ', lt3_succes

                qt.instruments['remote_measurement_helper'].set_measurement_name(True)
                qt.instruments['remote_measurement_helper'].set_is_running(False)
                qt.master_script_is_running = True
            #     print 'All done. Ready to run Purification.'

        else:

                qt.instruments['lt4_helper'].set_is_running(True)
                qt.msleep(10) # when you resetart bell to early, it will crash

                qt.instruments['lt4_helper'].set_measurement_name(True)
                qt.instruments['lt4_helper'].set_is_running(False)
                qt.master_script_is_running = True