import qt
import numpy as np
import msvcrt

from measurement.lib.tools import stools
reload(stools)

AWG = 'AWG'
ADWIN = 'adwin'
PM = 'powermeter'
PMSERVO = 'PMServo'
GREENAOM = 'GreenAOM'
RED1AOM = 'NewfocusAOM'
RED2AOM = 'MatisseAOM'
YELLOWAOM = 'YellowAOM'
PULSEAOM = 'PulseAOM'

ALLAOMS = [GREENAOM, RED2AOM, RED1AOM, YELLOWAOM, PULSEAOM]
ALLCHECKPWRS = [50e-6, 5e-9, 5e-9, 50e-9]
ADWINAOMS = [GREENAOM, RED2AOM, RED1AOM, YELLOWAOM]
AWGAOMS = [RED1AOM, YELLOWAOM]

def turn_off_all_lasers():
    stools.set_simple_counting(ADWIN)
    stools.turn_off_lasers(ALLAOMS)

def recalibrate_lasers(names = ADWINAOMS, awg_names = AWGAOMS):    
    turn_off_all_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        stools.recalibrate_laser(n, PMSERVO, ADWIN)
    
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        stools.recalibrate_laser(n, PMSERVO, ADWIN, awg=True)

def check_powers(names = ALLAOMS, setpoints = ALLCHECKPWRS):
    turn_off_all_lasers()
    for n,s in zip(names, setpoints):
        stools.check_power(n, s, ADWIN, PM, PMSERVO)

def check_max_powers(names = ALLAOMS):
    turn_off_all_lasers()
    for n in names:
        stools.check_max_power(n, ADWIN, PM, PMSERVO)

def turn_off_AWG_laser_channel():
    qt.instruments['AWG'].set_ch2_offset(0.)

def start_bs_counter():
    qt.instruments['bs_helper'].set_script_path(r'D:/measuring/measurement/scripts/bs_scripts/HH_counter_fast.py')
    qt.instruments['bs_helper'].set_is_running(True)
    qt.instruments['bs_helper'].execute_script()
    qt.instruments['counters'].set_is_running(False)
    qt.instruments['linescan_counts'].set_scan_value('counter_process')

def stop_bs_counter():
    qt.instruments['bs_helper'].set_is_running(False)
    qt.instruments['counters'].set_is_running(True)
    qt.instruments['linescan_counts'].set_scan_value('counts')

def set_lt1_remote():
    for i in ['labjack', 
        'setup_controller',
        'YellowAOM',
        'MatisseAOM',
        'NewfocusAOM',
        'GreenAOM',
        'optimiz0r',
        'opt1d_counts',
        'scan2d',
        'linescan_counts',
        'master_of_space',
        'counters',
        'adwin',
        'AWG']:

        try:
            qt.instruments.remove(i)
        except:
            logging.warning('could not remove instrument {}'.format(i))

def init_AWG():
    qt.instruments['AWG'].load_awg_file('DEFAULT.AWG')
    qt.pulsar.setup_channels()
    qt.instruments['AWG'].set_ch1_status('on')
    qt.instruments['AWG'].set_ch2_status('on')
    qt.instruments['AWG'].set_ch3_status('on')
    qt.instruments['AWG'].set_ch4_status('on')

def calibrate_aom_frq_max(name='YellowAOM', pts=21):
    adwin = qt.instruments['adwin']  
    qt.instruments['PMServo'].move_in()
    qt.msleep(0.5) 
    qt.instruments['powermeter'].set_wavelength(qt.instruments[name].get_wavelength())
    qt.instruments[name].turn_on()
    qt.msleep(0.5)
    cur_v=adwin.get_dac_voltage('yellow_aom_frq')
    ps=[]
    vs=[]
    for v in np.linspace(cur_v-0.5, cur_v+0.5, pts):
        vs.append(v)
        adwin.set_dac_voltage(('yellow_aom_frq',v))
        qt.msleep(0.1)
        p=qt.instruments['powermeter'].get_power()
        ps.append(p)
        print 'V: {:.2f}, P: {:.2g}'.format(v,p)

    max_v=vs[np.argmax(ps)]
    print 'max power at V: {:.2f}, P: {:.2g}'.format(max_v,max(ps))
    adwin.set_dac_voltage(('yellow_aom_frq',max_v))
    qt.instruments[name].turn_off()
    qt.instruments['PMServo'].move_out()

