"""
repetitively executes the electron_T2_slave_script.
Includes functionality to optimize on yellow position.
"""
import msvcrt
import qt
import numpy as np
import time
def optimize():
    print 'Starting to optimize.'

    print 'checking for SMB errors'
    if not(check_smb_errors()):
        print 'SMB gave errors!!'
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
    print 'mash q now to stop the measurement'
    optimize_ok = False
    for i in range(1):
        print 'press q now to stop measuring!'
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if qt.current_setup=='lt4':
            qt.instruments['optimiz0r'].optimize(dims=['y','x'],cnt=1, int_time=100, cycles =1)
            optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=100, cycles =2)
        else:
            qt.instruments['optimiz0r'].optimize(dims=['x','y'],cnt=1, int_time=50, cycles =1)
            optimize_ok=qt.instruments['optimiz0r'].optimize(dims=['z','x','y'],cnt=1, int_time=50, cycles =2)
        qt.msleep(1)
    if not(optimize_ok):
        print 'Not properly optimized position'
        return False
    else: 
        print 'Position is optimized!'
    qt.msleep(3)
    
    return True

def bell_check_powers():

    prot_name = qt.exp_params['protocols']['current']

    names=['MatisseAOM', 'NewfocusAOM','YellowAOM']
    setpoints = [qt.exp_params['protocols'][prot_name]['AdwinSSRO']['Ex_RO_amplitude'],
                100e-9, 
                qt.exp_params['protocols']['AdwinSSRO']['yellow_repump_amplitude']] 
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

    DD_parameters_dict =     {
        '1'      : [1,480*8,400,2,8,400], 
        '4'      : [4,480*4,250,2,2,400],
        '8'      : [8,480*4,200,2,2,400],
        '16'     : [16,480*2,150,2,2,200],
        '32'     : [32,480,120,2,2,200],
        '64'     : [64,240,120,2,2,200],
        '128'     : [128,20,120,2,2,200],
        '256'     : [256,15,90,2,1,200],
        '512'     : [512,7,60,2,1,200],
        '1024'     : [1024,3,40,2,2,300],
        'sweepN' : [0,4,512+256,2,120,500] ### first entry could be made the tau that we want to sweep here
    }

    success = True
    tau_offsets =[-8e-9,-4e-9,0e-9,4e-9,8e-9]
    sweep_Ns = ['1','4','8','16','32','64','128','256','512','1024','sweepN']


    keys_to_measure = ['1','4','8','16','32','64','128','256','512','1024']# ## change this to only do parts of the measurement


    last_opt_time = time.time()
    for i in sweep_Ns:
        if not success:
            break
        for tau_offset in tau_offsets:
            if i in keys_to_measure:


                if not success:
                    break
                
                qt.decoupling_parameter_list = DD_parameters_dict[i] + [tau_offset]
                execfile(r'electron_T2_slave_script.py')

                if time.time() - last_opt_time > 30*60: ### optimiz every 30 mins.
                    print 'Loading CR linescan'
                    execfile(r'D:/measuring/measurement/scripts/testing/load_cr_linescan.py') #change name!
                    qt.instruments['ZPLServo'].move_in()
                    success = optimize()
                    last_opt_time = time.time()