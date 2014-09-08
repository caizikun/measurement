import qt
import numpy as np
import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

def set_simple_counting(adwins=['adwin', 'adwin_lt1']):
    for adwin in adwins:
        qt.instruments[adwin].set_simple_counting()

def turn_off_lasers(names):
    for l in names:
        qt.instruments[l].turn_off()

def turn_off_all_lt4_lasers():
    set_simple_counting(['adwin'])
    turn_off_lasers(['MatisseAOM', 'NewfocusAOM','GreenAOM','YellowAOM'])

def turn_off_all_lasers():
    turn_off_all_lt4_lasers()

def recalibrate_laser(name, servo, adwin, awg=False):
    qt.instruments[adwin].set_simple_counting()
    qt.instruments[servo].move_in()
    qt.msleep(1)

    qt.msleep(0.1)
    print 'Calibrate', name
    qt.instruments[name].turn_off()
    if awg: qt.instruments[name].set_cur_controller('AWG')
    qt.instruments[name].calibrate(31)
    qt.instruments[name].turn_off()
    if awg: qt.instruments[name].set_cur_controller('ADWIN')
    qt.msleep(1)

    qt.instruments[name].turn_off()
    qt.instruments[servo].move_out()
    qt.msleep(1)


def recalibrate_lt4_lasers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM', 'YellowAOM'], awg_names=['NewfocusAOM']):
    turn_off_all_lt4_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin')
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin',awg=True)


def check_power(name, setpoint, adwin, powermeter, servo,move_out=True):
    qt.instruments[adwin].set_simple_counting()
    qt.instruments[servo].move_in()    
    qt.instruments[powermeter].set_wavelength(qt.instruments[name].get_wavelength())
    bg=qt.instruments[powermeter].get_power()
    if bg>5e-9:
        print 'Background:', bg
    qt.instruments[name].set_power(setpoint)
    qt.msleep(2)

    print name, 'setpoint:', setpoint, 'value:', qt.instruments[powermeter].get_power()-bg

    qt.instruments[name].turn_off()
    if move_out:
        qt.instruments[servo].move_out()
    qt.msleep(1)


def check_lt4_powers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM','YellowAOM'],
    setpoints = [5e-9, 5e-9, 50e-6,50e-9]):
    
    turn_off_all_lt4_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
    qt.instruments['PMServo'].move_out()
        
def disconnect_lt1_remote():
    for i in qt.instruments.get_instrument_names():
        if len(i) >= 4 and i[-4:] == '_lt1':
            qt.instruments.remove(i)

def apply_awg_voltage(awg, chan, voltage):
    """
    applies a voltage on an awg channel;
    if its a marker, by setting its LO-value to the given voltage.
    if an analog channel, by setting the offset.
    """
    if 'marker' in chan:
        return getattr(qt.instruments[awg], 'set_{}_low'.format(chan))(voltage)
    else:
        return getattr(qt.instruments[awg], 'set_{}_offset'.format(chan))(voltage)


def check_fast_path_power(powermeter, servo, awg='AWG', chan='ch4_marker1',
    voltage=1.0, off_voltage=0.02, ret=False):

    qt.instruments[powermeter].set_wavelength(637e-9)
    qt.instruments[servo].move_in()
    qt.msleep(1)
    apply_awg_voltage(awg, chan, voltage)
    qt.msleep(8)

    pwr = qt.instruments[powermeter].get_power()
    print 'Fast path power; {}: {:.3f} uW'.format(powermeter, pwr * 1e6)

    apply_awg_voltage(awg, chan, off_voltage)
    qt.msleep(0.1)
    qt.instruments[servo].move_out()
    qt.msleep(1)

    if ret:
        return pwr


def check_fast_path_power_lt4(ret=False, **kw):
    turn_off_all_lt4_lasers()
    pwr = check_fast_path_power('powermeter', 'PMServo', ret=ret, **kw)
    if ret:
        return pwr

def set_lt1_optimization_powers():
    turn_off_all_lt1_lasers()
    qt.instruments['YellowAOM_lt1'].set_power(50e-9)
    qt.instruments['MatisseAOM_lt1'].set_power(5e-9)
    qt.instruments['NewfocusAOM_lt1'].set_power(10e-9)



def turn_on_lt4_pulse_path():
    #qt.instruments['PMServo'].move_in()
    p=pulse.SinePulse(channel='EOM_Matisse', name='pp', length=100e-6, frequency=1/(100e-6), amplitude = 1.8)
    opt = 'offset' if qt.pulsar.channels['EOM_AOM_Matisse']['type']=='analog' else 'low'

    qt.pulsar.set_channel_opt('EOM_AOM_Matisse', opt, 1.0)

    e=element.Element('Sinde', pulsar=qt.pulsar)
    e.append(p)
    e.print_overview()
    s= pulsar.Sequence('Sinde')
    s.append(name = 'Sine',
                    wfname = e.name,
                    trigger_wait = 0)
    qt.pulsar.upload(e)
    qt.pulsar.program_sequence(s)
    qt.instruments['AWG'].set_runmode('SEQ')
    qt.instruments['AWG'].start()

    while 1:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        qt.msleep(0.1)
    qt.instruments['AWG'].stop()
    qt.instruments['AWG'].set_runmode('CONT')
    qt.pulsar.set_channel_opt('EOM_AOM_Matisse', opt, 0.0)
    #qt.instruments['PMServo'].move_out()

def init_AWG():
    #import_and_load_waveform_file_to_channel(channel_no ,waveform_listname,waveform_filename) 4x
    qt.instruments['AWG'].load_awg_file('DEFAULT.AWG')
    qt.pulsar.setup_channels()
    qt.instruments['AWG'].set_ch1_status('on')
    qt.instruments['AWG'].set_ch2_status('on')
    qt.instruments['AWG'].set_ch3_status('on')
    qt.instruments['AWG'].set_ch4_status('on')

def start_bs_counter():
    qt.instruments['counters'].set_is_running(False)
    qt.instruments['bs_helper'].set_script_path(r'D:/measuring/measurement/scripts/bs_scripts/HH_counter_fast.py')
    qt.instruments['bs_helper'].set_is_running(True)
    qt.instruments['bs_helper'].execute_script()

def stop_bs_counter():
    qt.instruments['bs_helper'].set_is_running(False)

def generate_quantum_random_number():
    qt.instruments['AWG'].set_ch1_marker2_low(2.)
    qt.msleep(0.1)
    qt.instruments['AWG'].set_ch1_marker2_low(0.)

def reset_plu():
    qt.instruments['adwin'].start_set_dio(dio_no=2, dio_val=0)
    qt.msleep(0.1)
    qt.instruments['adwin'].start_set_dio(dio_no=2, dio_val=1)
    qt.msleep(0.1)
    qt.instruments['adwin'].start_set_dio(dio_no=2, dio_val=0)