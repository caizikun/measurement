
import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class CavityScan ():

	def __init__ (self, name):
		self.name = name
		self._adwin = qt.instruments.get_instruments()['adwin']
		self._wm_adwin = qt.instruments.get_instruments()['physical_adwin_cav1']
		#self._laser = qt.get_setup_instrument['Velocity']

		self.voltage = None
		self.PD_signal = None
		self._laser_initialized = False
		self._scan_initialized = False
		self.V_min = None
		self.V_max = None
		self.nr_V_points = None
		self._wm_port = 45

	def set_laser_params(self, wavelength, power):
		#self._laser.set_wavelength()
		#self._laser.set_power()
		self._laser_initialized = True

	def set_scan_params (self, v_min, v_max, nr_points):
		self.V_min = v_min
		self.V_max = v_max
		self.nr_V_steps = nr_points
		self._scan_initialized = True

	def laser_scan (self, use_wavemeter = False, fine_scan = False, normalize = False, avg_nr_samples = 1):

		if (not(self._laser_initialized) or not(self._scan_initialized)):
			print 'ERROR: laser not initialized!!'
		else:
			v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
			self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
			#self.PD_signal = self._adwin.laserscan_photodiode(ADC_channel=1, nr_steps = self.nr_V_steps, wait_cycles = 50, 
	        #			start_voltage = self.V_min, voltage_step=v_step)			
			
			self.frequencies = np.zeros (self.nr_V_steps)
			self.PD_signal = np.zeros (self.nr_V_steps)
			if fine_scan:
				dac_no = self._adwin.dacs['newfocus_freqmod']
			else:
				dac_no = self._adwin.dacs['laser_scan']
			self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.V_min)
			qt.msleep (0.1)
			print 'Using DAC channel nr. ', dac_no
			for n in np.arange (self.nr_V_steps):
				self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.v_vals[n])
				#qt.msleep (0.01)
				value = 0
				for j in np.arange (avg_nr_samples):
					self._adwin.start_read_adc (adc_no = self._adwin.adcs['photodiode'])
					value = value + self._adwin.get_read_adc_var ('fpar')[0][1]
				value = value/avg_nr_samples
				self.PD_signal[n] = value
				#qt.msleep (0.01)
				if use_wavemeter:
					qt.msleep (0.5)
					self.frequencies[n] = self._wm_adwin.Get_FPar (self._wm_port)
					qt.msleep (0.5)

	def initialize_scan_voltage (self, fine_scan = False):
		if fine_scan:
			dac_no = self._adwin.dacs['laser_scan']
		else:
			dac_no = self._adwin.dacs['newfocus_freqmod']
		self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.V_min)
		qt.msleep(0.2)


	def piezo_scan (self, normalize = False, avg_nr_samples=1):

		v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
		self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
		for j in np.arange(avg_nr_samples):	
			if (j==0):
				self.PD_signal = self._adwin.fine_piezo_jpe_scan(nr_steps = self.nr_V_steps, wait_cycles = 200, start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step)			
			else:
				self.PD_signal = self.PD_signal + self._adwin.fine_piezo_jpe_scan(nr_steps = self.nr_V_steps, wait_cycles = 200, start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step)


	def piezo_scan_CCD (self, normalize = False, avg_nr_samples=1):

		v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
		self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)	

		for j in np.arange(avg_nr_samples):	
			if (j==0):
				self.PD_signal = self._adwin.fine_piezo_jpe_scan_CCD (nr_steps = self.nr_V_steps, wait_cycles = 200, start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step)			
			else:	
				self.PD_signal = self.PD_signal + self._adwin.fine_piezo_jpe_scan_CCD (nr_steps = self.nr_V_steps, wait_cycles = 200, start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step)

		self.PD_signal = (self.PD_signal) - min(self.PD_signal)




	def initialize_piezos (self, wait_time=0.2):
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_1'], dac_voltage=self.V_min)
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_2'], dac_voltage=self.V_min)
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_3'], dac_voltage=self.V_min)
		qt.msleep(wait_time)