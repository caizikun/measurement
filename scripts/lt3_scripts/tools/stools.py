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

def turn_off_all_lt3_lasers():
    turn_off_lasers(['MatisseAOM', 'NewfocusAOM','GreenAOM','YellowAOM', 'PulseAOM'])

def turn_off_all_lasers():
    turn_off_all_lt3_lasers()

def recalibrate_laser(name, servo, adwin, awg=False):
    #qt.instruments[adwin].set_simple_counting()
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

def recalibrate_lt1_lasers(names=['GreenAOM_lt1', 'MatisseAOM_lt1', 'NewfocusAOM_lt1', 'YellowAOM_lt1'], 
        awg_names=['NewfocusAOM_lt1', 'YellowAOM_lt1']):
    turn_off_all_lt1_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo_lt1', 'adwin_lt1')
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo_lt1', 'adwin_lt1',awg=True)

def recalibrate_lt3_lasers(names=['MatisseAOM', 'NewfocusAOM', 'GreenAOM', 'YellowAOM'], awg_names=['NewfocusAOM']):
    turn_off_all_lt3_lasers()
    for n in names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin')
    for n in awg_names:
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        recalibrate_laser(n, 'PMServo', 'adwin',awg=True)


def check_power(name, setpoint, adwin, powermeter, servo,move_pm_servo=True):
    #qt.instruments[adwin].set_simple_counting()
    if move_pm_servo:
        qt.instruments[servo].move_in()    
    qt.instruments[powermeter].set_wavelength(qt.instruments[name].get_wavelength())
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

def check_lt3_powers(names=['MatisseAOM', 'NewfocusAOM', 'PulseAOM','YellowAOM'],
    setpoints = [5e-9, 5e-9, 15e-9,40e-9]):
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    turn_off_all_lt3_lasers()
    for n,s in zip(names, setpoints):
        check_power(n, s, 'adwin', 'powermeter', 'PMServo', False)
    qt.instruments['PMServo'].move_out()

def max_lt3_powers(names=['MatisseAOM', 'NewfocusAOM','YellowAOM', 'PulseAOM']):
    qt.instruments['PMServo'].move_in()
    qt.msleep(2)
    turn_off_all_lt3_lasers()
    for n in names:
        check_power(n, 'max', 'adwin', 'powermeter', 'PMServo', False)
    qt.instruments['PMServo'].move_out()

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

def check_fast_path_power_lt1(ret=False, **kw):
    turn_off_all_lt1_lasers()
    pwr = check_fast_path_power('powermeter_lt1', 'PMServo_lt1', ret=ret, **kw)
    if ret:
        return pwr

def check_fast_path_power_lt3(ret=False, **kw):
    turn_off_all_lt3_lasers()
    pwr = check_fast_path_power('powermeter', 'PMServo', ret=ret, **kw)
    if ret:
        return pwr

def set_lt1_optimization_powers():
    turn_off_all_lt1_lasers()
    qt.instruments['YellowAOM_lt1'].set_power(50e-9)
    qt.instruments['MatisseAOM_lt1'].set_power(5e-9)
    qt.instruments['NewfocusAOM_lt1'].set_power(10e-9)



def turn_on_lt3_pulse_path():
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
    qt.instruments['AWG'].initialize_dc_waveforms()

def start_bs_counter():
    if qt.instruments['bs_relay_switch'].Turn_On_Relay(1) and \
        qt.instruments['bs_relay_switch'].Turn_On_Relay(2): 
        print 'ZPL APDs on'
    else:
        print 'ZPL APDs could not be turned on!'
    qt.instruments['counters'].set_is_running(False)
    qt.instruments['bs_helper'].set_script_path(r'D:/measuring/measurement/scripts/bs_scripts/HH_counter_fast.py')
    qt.instruments['bs_helper'].set_is_running(True)
    qt.instruments['bs_helper'].execute_script()
    qt.instruments['linescan_counts'].set_scan_value('counter_process')

def stop_bs_counter():
    qt.instruments['bs_helper'].set_is_running(False)
    qt.instruments['linescan_counts'].set_scan_value('counts')
    #qt.instruments['counters'].set_is_running(True)
    if qt.instruments['bs_relay_switch'].Turn_Off_Relay(1) and \
        qt.instruments['bs_relay_switch'].Turn_Off_Relay(2): 
        print 'ZPL APDs off'
    else:
        print 'ZPL APDs could not be turned off!'

def generate_quantum_random_number():
    qt.instruments['AWG'].set_ch3_marker1_low(2.)
    qt.msleep(0.1)
    qt.instruments['AWG'].set_ch3_marker1_low(0.)

def quantum_random_number_status():
    qt.instruments['adwin'].start_get_dio(dio_no=20)
    return qt.instruments['adwin'].get_get_dio_var('dio_val') > 0

def quantum_random_number_reset():
    qt.instruments['adwin'].start_set_dio(dio_no=7, dio_val=0)
    qt.msleep(0.1)
    qt.instruments['adwin'].start_set_dio(dio_no=7, dio_val=1)
    qt.msleep(0.1)
    qt.instruments['adwin'].start_set_dio(dio_no=7, dio_val=0)

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
        qt.msleep(0.5)
        p=qt.instruments['powermeter'].get_power()
        ps.append(p)
        print 'V: {:.2f}, P: {:.3g}'.format(v,p)

    max_v=vs[np.argmax(ps)]
    print 'max power at V: {:.3f}, P: {:.2g}'.format(max_v,max(ps))
    adwin.set_dac_voltage(('yellow_aom_frq',max_v))
    qt.instruments[name].turn_off()
    qt.instruments['PMServo'].move_out()

def rf_switch_local():
    qt.instruments['RF_Multiplexer'].set_state_bitstring('11111111')

def rf_switch_non_local():
    qt.instruments['RF_Multiplexer'].set_state_bitstring('00000000')

def get_pulse_aom_frq(do_plot=True):
    qt.instruments['signalhound'].set_frequency_center(200.5e6)
    qt.instruments['signalhound'].set_frequency_span(0.5e6) 
    qt.instruments['signalhound'].set_rbw(5e3)
    qt.instruments['signalhound'].set_vbw(5e3)
    qt.instruments['signalhound'].ConfigSweepMode()
    f,mi,ma=qt.instruments['signalhound'].GetSweep(do_plot=do_plot, max_points=1030)
    f_offset = f[np.argmax(mi)]
    print 'PulseAOM frequency: 200 MHz {:+.0f} kHz'.format((f_offset-200e6)*1e-3)
    return f_offset


def aom_listener():
    import speech
    def do_aom(phrase,listener):
        if phrase == 'green':
            aom = 'GreenAOM'
        elif phrase == 'red':
            aom = 'MatisseAOM'
        elif phrase == 'pulse':
            aom = 'PulseAOM'
        elif phrase == 'yellow':
            aom = 'YellowAOM'
        elif phrase == 'stop':
            print 'stop listening'
            listener.stoplistening()
            return
        elif phrase == 'servo':
            print 'PMservo flip'
            ins = qt.instruments['PMServo']
            if ins.get_position() == ins.get_in_position():
                ins.move_out()
            else:
                ins.move_in()
            return
        elif phrase=='power':
            power = '{:.0f} nano waat'.format(qt.instruments['powermeter'].get_power()*1e9)
            print 'power: ', power
            speech.say(power)
            return
        else:
            print 'Not understood'

        if qt.instruments[aom].get_power() == 0.:
            print 'Turning on', aom
            qt.instruments[aom].turn_on()
        else:
            print 'Turning off', aom
            qt.instruments[aom].turn_off()

    #How can i remove windows commands from pyspeech windows recognition? 
    #For example if i wanted for my program to open up notepad i would say 
    #"Open notepad", but then windows will also open up notepad for me too. 
    #How can i disable this so that my program is the only one running commands? 

    #in lib/site_packages/speech.py
    #On line 66 change the code to:
    #_recognizer = win32com.client.Dispatch("SAPI.SpInProcRecognizer")
    #_recognizer.AudioInputStream = win32com.client.Dispatch("SAPI.SpMMAudioIn")
    #And on line 112 change the code to:
    #_ListenerBase = win32com.client.getevents("SAPI.SpInProcRecoContext") 
    #This should prevent the windows commands from running while also not showing the widget which comes up. Good luck!
    
    listener = speech.listenfor(['red','yellow','green','pulse','stop', 'power', 'servo'],do_aom)