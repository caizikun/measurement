import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

mw_channel = 'MW_Qmod'

T = pulse.SquarePulse(channel='MW_Qmod', name='delay',
            length = 200e-9, amplitude = 0.)
sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)

X = pulselib.MW_pulse('pulse',
            MW_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude=0.9,
            length = 52e-9,
            PM_risetime = 10e-9)

X2 = pulse.SquarePulse('MW_Qmod','small_pulse',
            amplitude=0.2,
            length = 200e-9)


e=element.Element('Sinde', pulsar=qt.pulsar)
e.append(T)
e.append(sync)
e.append(pulse.cp(T,length=300e-9))
e.append(X2)
e.append(X)
e.append(X2)
#e.append(T)
e.append(pulse.cp(T,length=25000e-9))

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
qt.instruments['SMB100'].set_frequency(2.5e9)
qt.instruments['SMB100'].set_power(10)
qt.instruments['SMB100'].set_status('on')
qt.instruments['AWG'].start()