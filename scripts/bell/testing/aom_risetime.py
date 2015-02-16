import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import msvcrt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)
sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)

X = pulse.SquarePulse(channel='EOM_AOM_Matisse',
            amplitude=0.9,
            length = 200e-9)



e=element.Element('Sinde', pulsar=qt.pulsar)
e.append(T)
e.append(sync)
e.append(pulse.cp(T,length=300e-9))
e.append(X)
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
qt.instruments['AWG'].start()