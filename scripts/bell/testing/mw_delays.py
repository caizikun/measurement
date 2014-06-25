import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


T = pulse.SquarePulse(channel='MW_1', name='delay',
            length = 200e-9, amplitude = 0.)
sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)

X = pulselib.MW_pulse('pulse',
            MW_channel='MW_2',
            PM_channel='MW_pulsemod',
            amplitude=0.8,
            length = 200e-9,
            PM_risetime = 10e-9)

X2 = pulse.SquarePulse('MW_2','small_pulse',
            amplitude=0.1,
            length = 100e-9)


e=element.Element('Sinde', pulsar=qt.pulsar)
e.append(T)
e.append(sync)
e.append(pulse.cp(T,length=100e-9))
e.append(X2)
e.append(X)
e.append(X2)
#e.append(T)
e.append(pulse.cp(T,length=250e-9))

#e.print_overview()
s= pulsar.Sequence('Sinde')
s.append(name = 'Sine',
                wfname = e.name,
                trigger_wait = 0)
qt.pulsar.upload(e)
qt.pulsar.program_sequence(s)
qt.instruments['AWG'].set_runmode('SEQ')


qt.instruments['SMB100'].set_iq('on')
qt.instruments['SMB100'].set_pulm('on')
qt.instruments['SMB100'].set_frequency(2.0e9)
qt.instruments['SMB100'].set_power(10)
qt.instruments['SMB100'].set_status('on')