import qt
import numpy as np
import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

def program_test_master(reset=False):

	T = pulse.SquarePulse('sync', length=200e-9, amplitude = 0)
    p_sync = pulse.SquarePulse('sync', length=50e-9, amplitude = 1)

    e=element.Element('Test_trigger', pulsar=qt.pulsar)
    e.append(T)
    e.append(p_trig)
    e.append(pulse.cp(T, length=10e-6))
    s= pulsar.Sequence('TEST_AWG_SYNC_LT3')
    s.append(name = 'Master',
                    wfname = e.name,
                    trigger_wait = 0)
    if reset:
    	qt.pulsar.program_awg(s,e)
    else:
    	qt.pulsar.upload(e)
    	qt.pulsar.program_sequence(s)

    qt.instruments['AWG'].start()

def program_test_slave(reset=False):
	T = pulse.SquarePulse('sync', length=200e-9, amplitude = 0)
    p_sync = pulse.SquarePulse('sync', length=50e-9, amplitude = 1)

    e=element.Element('Test_trigger', pulsar=qt.pulsar)
    e.append(T)
    e.append(p_trig)
    e.append(pulse.cp(T, length=5e-6))
    s= pulsar.Sequence('TEST_AWG_SYNC_LT3')
    s.append(name = 'Slave',
                    wfname = e.name,
                    trigger_wait = 1)
    if reset:
    	qt.pulsar.program_awg(s,e)
    else:
    	qt.pulsar.upload(e)
    	qt.pulsar.program_sequence(s)

    qt.instruments['AWG'].start()

    #qt.instruments['AWG'].load_awg_file('DEFAULT.AWG')


def check_triggering():
	pharp=qt.instruments['PH_300']
	pharp.start_histogram_mode()
    pharp.StartMeas(int(10 * 1e3)) #10 second measurement
    qt.msleep(0.1)
    while pharp.get_MeasRunning():
        if(msvcrt.kbhit() and msvcrt.getch()=='q'):
            print 'q pressed, quitting current run'
            pharp.StopMeas()
    hist=pharp.get_Block()

    peaks=np.where(hist>100)
    if len(peaks[0])>10:
    	print jittering!
    x0 =6000
    if np.mean(peaks)<x0 or np.mean(peaks) > x0:
    	print 'offset by', np.mean(peaks)- x0

    return hist


if __name__ == '__main__':
    if qt.current_setup=='lt3':
    	lt1_helper = qt.instruments['lt1_helper']
        lt1_helper.set_is_running(False)
        lt1_helper.set_measurement_name(name)
        lt1_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_lt1.py')
        lt1_helper.execute_script()
        qt.msleep(1)
        program_test_master(reset=False)
    else:
    	program_test_slave(reset=False)
        hist=check_triggering()
        qt.instruments['AWG'].stop()