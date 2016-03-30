import msvcrt
import numpy as np
import qt
import hdf5_data as h5
import logging

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
reload(ssro)
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps


class SP_dynamics(PulsarMeasurement):
	'''
	Measurement class for probing spin dynamics during spin pumping
	Idea: vary spin pumping duration (tau), wait (t) and RO in 0 and -1.
	Vary t between 0-1000 ns to probe singlet occupation
	Vary tau to track spin pumping dynamics

	FIRST VERSION: just vary the spin pumping duration
	'''
	mprefix = 'SP_dynamics'

	def autoconfig(self):
		PulsarMeasurement.autoconfig(self)

	def generate_sequence(self, upload = True, **kw):
		'''
		'''

		SP = pulse.SquarePulse(channel='AOM_Newfocus', name='SP')
        
        SP.amplitude = self.params['A_SP_AWG_voltage']
        SP.length = self.params['SP_duration']*1e-6

        RO = pulse.SquarePulse(channel='AOM_Matisse', name='RO')
        
        RO.amplitude = self.params['Ex_RO_AWG_voltage']
        RO.length = self.params['SSRO_duration']*1e-6
