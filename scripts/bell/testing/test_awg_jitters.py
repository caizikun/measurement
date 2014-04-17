import qt
import numpy as np
import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

def program_test_master():
    #p=pulse.SinePulse(channel='EOM_Matisse', name='pp', length=100e-6, frequency=1/(100e-6), amplitude = 1.8)
    T = pulse.SquarePulse('scope_sync', length=200e-9, amplitude = 0)
    p_sync = pulse.SquarePulse('scope_sync', length=50e-9, amplitude = 1)
    p_pulse = pulse.SquarePulse('scope_pulse', length=200e-9, amplitude = 1)
    p_trig = pulse.SquarePulse('awg_lt1_trigger', length=50e-9, amplitude = 1)

    e=element.Element('Sinde', pulsar=qt.pulsar)
    e.append(T)
    e.append(p_trig)
    e.append(pulse.cp(T, length = 800e-9))
    e.append(p_sync)
    e.append(T)
    e.append(p_pulse)
    e.append(pulse.cp(T, length = 1000e-9))

    e.print_overview()
    
    s= pulsar.Sequence('TEST_AWG_SYNC_LT3')
    s.append(name = 't1',
                    wfname = e.name,
                    trigger_wait = 0)
    qt.pulsar.upload(e)
    qt.pulsar.program_sequence(s)

    qt.instruments['AWG'].start()

def program_test_slave():
    T = pulse.SquarePulse('scope_pulse', length=200e-9, amplitude = 0)
    p_pulse = pulse.SquarePulse('scope_pulse', length=200e-9, amplitude = 1)

    e=element.Element('Sinde', pulsar=qt.pulsar)
    e.append(T)
    e.append(p_pulse)
    e.append(pulse.cp(T, length = 600e-9))

    e.print_overview()
    
    s= pulsar.Sequence('TEST_AWG_SYNC_LT1')
    s.append(name = 't1',
                    wfname = e.name,
                    trigger_wait = 1)
    qt.pulsar.upload(e)
    qt.pulsar.program_sequence(s)

    qt.instruments['AWG'].start()

if __name__ == '__main__':
    if qt.current_setup=='lt3':
        program_test_master()
    else:
        program_test_slave()