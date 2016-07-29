import qt
import numpy as np
import msvcrt

from measurement.lib.tools import stools
reload(stools)

AWG = 'AWG'
ADWIN = 'adwin'
PM = 'powermeter'
PMSERVO = None #rt2 doesn't have it
GREENAOM = 'GreenAOM'

ALLAOMS = [GREENAOM]
ALLCHECKPWRS = [50e-6]
ADWINAOMS = [GREENAOM]
AWGAOMS = [GREENAOM]

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

def init_AWG():
    qt.instruments['AWG'].initialize_dc_waveforms()

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

def generate_quantum_random_number():
    qt.instruments['AWG'].set_ch2_marker1_low(2.)
    qt.msleep(0.1)
    qt.instruments['AWG'].set_ch2_marker1_low(0.)