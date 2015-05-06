
import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class LaserScan ():

	def __init__ (self, name):
		self.name = name
		self._adwin = qt.instruments.get_instruments()['adwin']
		#self._laser = qt.get_setup_instrument['Velocity']

		self.voltage = None
		self.PD_signal = None
		self._laser_initialized = False
		self._scan_initialized = False
		self.V_min = None
		self.V_max = None
		self.nr_V_points = None

	def set_laser_params(self, wavelength, power):
		#self._laser.set_wavelength()
		#self._laser.set_power()
		self._laser_initialized = True

	def set_scan_params (self, v_min, v_max, nr_points):
		self.V_min = v_min
		self.V_max = v_max
		self.nr_V_steps = nr_points
		self._scan_initialized = True

	def scan (self):

		if (not(self._laser_initialized) or not(self._scan_initialized)):
			print 'ERROR: laser not initialized!!'
		else:
			v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
			self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
			self.PD_signal = self._adwin.laserscan_photodiode(ADC_channel=1, nr_steps = self.nr_V_steps, wait_cycles = 50, 
	        			start_voltage = self.V_min, voltage_step=v_step)			