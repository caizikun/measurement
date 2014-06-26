import qt
import numpy as np

import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import pprint

reload(pulse)
reload(element)
reload(pulsar)

#qt.pulsar.AWG_type = 'opt09'

qt.pulsar.define_channel(id='ch3_marker1', name='th_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch4_marker2', name='th_ch1', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
#qt.pulsar.define_channel(id='ch4_marker2', name='th_ch1', type='marker', 
#    high=2.0, low=0, offset=0., delay=0., active=True)

test_pulse = pulse.SquarePulse(channel = 'th_sync', amplitude = 1.0)
test_pulse2 = pulse.SquarePulse(channel = 'th_ch1', amplitude = 1.0)
#test_pulse3 = pulse.SquarePulse(channel = 'th_ch1', amplitude = 1.0)

elt1 = element.Element('idle', pulsar = qt.pulsar)


#print 'Channel definitions: '
#pprint.pprint(test_element._channels)

elt1.add(pulse.cp(test_pulse2, amplitude = 1.0, length = 100e-9), start = 100e-9)
elt1.add(pulse.cp(test_pulse, amplitude = 1.0, length = 1000e-9), start = 600e-9)
elt1.add(pulse.cp(test_pulse2, amplitude = 1.0, length = 100e-9), start = 1800e-9)
elt1.add(pulse.cp(test_pulse2, amplitude = 0, length = 1000e-9), start = 1900e-9)
#elt1.add(pulse.cp(test_pulse3, amplitude = 1.0, length = 100e-9), start = 600e-9)
#elt1.add(pulse.cp(test_pulse3, amplitude = 0.0, length = 10000e-9), start = 800e-9)

seq = pulsar.Sequence('AWG TimHarp Test')
seq.append(name = 'idle', wfname = elt1.name, trigger_wait = True, repetitions = 30000, goto_target = 'idle')

upload = True
if upload:
	qt.pulsar.upload(elt1)


	qt.pulsar.program_sequence(seq)



