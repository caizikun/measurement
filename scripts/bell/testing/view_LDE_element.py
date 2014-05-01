import numpy as np
from measurement.lib.pulsar import pulse, pulselib, element, eom_pulses, view

reload(pulse)
reload(element)
reload(view)
reload(pulselib)
reload(eom_pulses)
import parameters_lt3 as bparams
import sequence as bseq
reload(bparams)
reload(bseq)


class test_M:
	def test(self):
		print 'test'
m=test_M()
m.params = bparams.params
m.params_lt3 = bparams.params_lt3
m.params_lt3['RO_voltage_AWG'] = 1
m.params_lt3['SP_voltage_AWG'] = 1
bseq.pulse_defs_lt3(m)
e =bseq._lt3_LDE_element(m, eom_pulse=eom_pulses.EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse'))

view.show_element(e)
