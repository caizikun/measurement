import qt
execfile(qt.reload_current_setup)
import numpy as np
import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

def program_test_master(reset=False):
    T = pulse.SquarePulse('sync', length=200e-9, amplitude = 0)
    p_sync = pulse.SquarePulse('sync', length=50e-9, amplitude = 1)

    e=element.Element('Test_trigger', pulsar=qt.pulsar)
    e.append(T)
    e.append(p_sync)
    e.append(pulse.cp(T, length=1e-6))
    e2=element.Element('Test_wait', pulsar=qt.pulsar)
    e2.append(pulse.cp(T, length=10e-6))
    s= pulsar.Sequence('TEST_AWG_SYNC_lt4')
    s.append(name = 'Master trig',
                    wfname = e.name,
                    trigger_wait = 0)
    s.append(name = 'Master wait',
                    wfname = e2.name,
                    trigger_wait = 0,
                    repetitions=10)
    if reset:
        print 'RESETTING AWG'
        qt.pulsar.program_awg(s,e,e2)
    else:
        qt.pulsar.upload(e,e2)
        qt.pulsar.program_sequence(s)

    qt.instruments['AWG'].start()

def program_test_slave(reset=False):
    T = pulse.SquarePulse('sync', length=10e-9, amplitude = 0)
    p_sync = pulse.SquarePulse('sync', length=50e-9, amplitude = 1)
    e=element.Element('Test_trigger', pulsar=qt.pulsar)
    e.append(T)
    e.append(p_sync)
    e.append(pulse.cp(T, length=5e-6))
    s= pulsar.Sequence('TEST_AWG_SYNC_lt3')
    s.append(name = 'Slave',
                    wfname = e.name,
                    trigger_wait = 1)
    if reset:
        print 'RESETTING AWG'
        qt.pulsar.program_awg(s,e)
    else:
        qt.pulsar.upload(e)
        qt.pulsar.program_sequence(s)

    qt.instruments['AWG'].start()

    #qt.instruments['AWG'].load_awg_file('DEFAULT.AWG')


def check_triggering():
    jitterDetected = False
    remote_helper=qt.instruments['remote_measurement_helper']
    remote_helper.set_is_running(True)
    pharp=qt.instruments['PH_300']
    pharp.OpenDevice()
    pharp.start_histogram_mode()
    pharp.ClearHistMem()
    pharp.set_Range(4) # 64 ps binsize
    pharp.set_CFDLevel0(50)
    pharp.set_CFDLevel1(50)
    qt.msleep(1)
    pharp.StartMeas(int(4 * 1e3)) #10 second measurement
    qt.msleep(0.1)
    print 'starting PicoHarp measurement'
    while pharp.get_MeasRunning():
        if(msvcrt.kbhit() and msvcrt.getch()=='q'):
            print 'q pressed, quitting current run'
            pharp.StopMeas()
            break
    hist=pharp.get_Block()
    print 'PicoHarp measurement finished'

    print '-------------------------------'
    ret=''
    ret=ret+ str(hist[hist>0])
    peaks=np.where(hist>0)[0]*pharp.get_Resolution()/1000.
    ret=ret+'\n'+ str(peaks)
    print ret
    if len(peaks)>1:
        peaks_width=peaks[-1]-peaks[0]
        peak_max=np.argmax(hist)*pharp.get_Resolution()/1000.
        if (peaks_width)>.5:
            ret=ret+'\n'+ 'JITTERING!! Execute check_awg_triggering with a reset'
            jitterDetected=True
        elif (peak_max<489.8) or (peak_max>490.8):
            ret=ret+'\n'+ 'Warning peak max at unexpected place, PEAK WRONG'
            jitterDetected=True
        else:
            ret=ret+'\n'+'No Jitter detected'
        ret=ret+'\n peak width: {:.2f} ns'.format(peaks_width)
    
    ret=ret+'\npeak loc at {:.2f} ns'.format(peak_max)


    ret=ret+'\ntotal counts in hist: {}'.format(sum(hist))
    print ret
    d=qt.Data(name='AWG jitter check')
    d.create_file()
    d.close_file()
    fp=d.get_filepath()
    f=open(fp, 'a')
    f.write(ret)
    f.close()
    remote_helper.set_data_path(fp)
    remote_helper.set_measurement_name(ret)
    remote_helper.set_is_running(False)
    return jitterDetected

def do_jitter_test(resetAWG=False):
    if qt.current_setup=='lt4':
        print 'Starting Jitter Test LT4, reset= ' + str(resetAWG)
        qt.instruments['AWG'].stop()
        lt3_helper = qt.instruments['lt3_helper']
        lt3_helper.set_is_running(False)
        lt3_helper.set_script_path(r'Y:/measurement/scripts/bell/check_awg_triggering.py')
        lt3_helper.execute_script()
        program_test_master(reset=resetAWG)
        qt.msleep(3.2)      
        while lt3_helper.get_is_running():
            if(msvcrt.kbhit() and msvcrt.getch()=='q'): 
                print 'measurement aborted'
                break
            qt.msleep(0.2)
        qt.instruments['AWG'].stop()
        output = lt3_helper.get_measurement_name()
        print output
        if 'JITTERING' in output or 'PEAK WRONG' in output:
            jitterDetected=True
        else: jitterDetected =False
    else:
        stools.rf_switch_non_local()
        print 'Starting Jitter Test LT3, reset= ' + str(resetAWG)
        program_test_slave(reset=resetAWG)
        jitterDetected = check_triggering()
        qt.instruments['AWG'].stop()
        stools.rf_switch_local()
    return jitterDetected


if __name__ == '__main__':
    testResult=do_jitter_test(resetAWG=False)
    print 'jitterDetected ', testResult
