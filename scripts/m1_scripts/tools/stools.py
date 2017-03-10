import qt
import numpy as np
import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

def set_simple_counting(adwins=['adwin']):
    for adwin in adwins:
        qt.instruments[adwin].set_simple_counting()

def turn_off_lasers(names):
    for l in names:
        qt.instruments[l].turn_off()

def turn_off_all_lasers():
    #set_simple_counting(['adwin'])
    turn_off_lasers(['NewfocusAOM','GreenAOM','DLProAOM']) ### XXX Still have to add yellow and pulse

def recalibrate_laser(name, servo, nr_points = 31,control = 'AOM', awg=False):
    #qt.instruments[adwin].set_simple_counting()
    prevPos = qt.instruments[servo].get_position()
    qt.instruments[servo].move_in()
    qt.msleep(1)

    qt.msleep(0.1)
    print 'Calibrate', name
    qt.instruments[name].turn_off()
    if awg: qt.instruments[name].set_cur_controller('AWG')
    qt.instruments[name].calibrate(nr_points,control = control)
    qt.instruments[name].turn_off()
    if awg: qt.instruments[name].set_cur_controller('ADWIN')
    qt.msleep(1)

    qt.instruments[name].turn_off()
    qt.instruments[servo].set_position(prevPos)
    qt.msleep(1)


def recalibrate_lt4_lasers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM', 'YellowAOM'], awg_names=['NewfocusAOM']):
    turn_off_all_lt4_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo')
    for n in awg_names:
        init_AWG()
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo',awg=True)

def check_power(name, setpoint, adwin, powermeter, servo,move_pm_servo=True):
    if move_pm_servo:
        qt.instruments[servo].move_in()     
    qt.instruments[powermeter].set_wavelength(qt.instruments[name].get_wavelength())
    qt.msleep(0.5)
    bg=qt.instruments[powermeter].get_power()
    if bg>5e-9:
        print 'Background:', bg
    if setpoint == 'max':
        qt.instruments[name].turn_on()
    else:
        qt.instruments[name].set_power(setpoint)
    qt.msleep(2)
    value = qt.instruments[powermeter].get_power()-bg
    print name, 'setpoint:', setpoint, 'value:', value

    qt.instruments[name].turn_off()
    if move_pm_servo:
        qt.instruments[servo].move_out()
    qt.msleep(1)
    return setpoint, value


def check_powers(names=['MatisseAOM', 'NewfocusAOM','PulseAOM', 'YellowAOM' ],
    setpoints = [5e-9, 10e-9, 15e-9,50e-9]):
    init_AWG()
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    turn_off_all_lt4_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
    qt.instruments['PMServo'].move_out()

def max_powers(names=['MatisseAOM', 'NewfocusAOM','YellowAOM', 'PulseAOM']):
    turn_off_all_lt4_lasers()
    for n in names:
        check_power(n, 'max', 'adwin', 'powermeter', 'PMServo', False)
    qt.instruments['PMServo'].move_out()

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
    for v in np.linspace(cur_v+0.4, cur_v-0.4, pts):
        vs.append(v)
        adwin.set_dac_voltage(('yellow_aom_frq',v))
        qt.msleep(0.5)
        p=qt.instruments['powermeter'].get_power()
        ps.append(p)
        print 'V: {:.2f}, P: {:.3g}'.format(v,p)

    max_v=vs[np.argmax(ps)]
    print 'max power at V: {:.3f}, P: {:.2g}'.format(max_v,max(ps))
    adwin.set_dac_voltage(('yellow_aom_frq',max_v))
    qt.instruments[name].turn_off()
    qt.instruments['PMServo'].move_out()
