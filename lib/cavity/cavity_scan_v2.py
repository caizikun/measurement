
import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class CavityExpManager ():

	def __init__ (self, adwin, wm_adwin, laser, moc):
		self._adwin = adwin
		self._wm_adwin = wm_adwin
		self._laser = laser
		self._moc = moc
		self._wm_port = 45

	def set_laser_wavelength (self, wavelength):
		if ((wavelength>636) and (wavelength<640)):
			self._laser.set_wavelength (wavelength=wavelength)
			return 0
		else:
			return 1
	def get_laser_wavelength (self):
		try:
			l = self._laser.get_wavelength()
			return l
		except:
			return 'error'

	def set_piezo_voltage (self, V):
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_1'], dac_voltage=V)
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_2'], dac_voltage=V)
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_3'], dac_voltage=V)
		qt.msleep(0.01)

	def initialize_piezos (self, wait_time=0.2):
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_1'], dac_voltage=self.V_min)
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_2'], dac_voltage=self.V_min)
		self._adwin.start_set_dac(dac_no=self._adwin.dacs['jpe_fine_tuning_3'], dac_voltage=self.V_min)
		qt.msleep(wait_time)


class CavityScan ():

	def __init (self, exp_mngr):

		self._exp_mngr = exp_mngr

		self.voltage = None
		self.PD_signal = None
		self._laser_initialized = False
		self._scan_initialized = False
		self.V_min = None
		self.V_max = None
		self.nr_V_points = None


	def set_scan_params (self, v_min, v_max, nr_points):
		self.V_min = v_min
		self.V_max = v_max
		self.nr_V_steps = nr_points
		self._scan_initialized = True

	def laser_scan (self, use_wavemeter = False, fine_scan = False, normalize = False, avg_nr_samples = 1):

		v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
		self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
		
		self.frequencies = np.zeros (self.nr_V_steps)
		self.PD_signal = np.zeros (self.nr_V_steps)
		if fine_scan:
			dac_no = self._adwin.dacs['newfocus_freqmod']
		else:
			dac_no = self._adwin.dacs['laser_scan']
		self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.V_min)
		qt.msleep (0.1)
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
				qt.msleep (0.05)
				self.frequencies[n] = self._wm_adwin.Get_FPar (self._wm_port)
				qt.msleep (0.05)

	def initialize_scan_voltage (self, fine_scan = False):
		if fine_scan:
			dac_no = self._adwin.dacs['laser_scan']
		else:
			dac_no = self._adwin.dacs['newfocus_freqmod']
		self._adwin.start_set_dac(dac_no=dac_no, dac_voltage=self.V_min)
		qt.msleep(0.2)


	def piezo_scan (self, normalize = False, avg_nr_samples=1, wait_cycles=1):

		v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
		self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
		for j in np.arange(avg_nr_samples):	
			if (j==0):
				self.PD_signal = self._adwin.fine_piezo_jpe_scan(nr_steps = self.nr_V_steps, wait_cycles = wait_cycles, start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step)			
			else:
				self.PD_signal = self.PD_signal + self._adwin.fine_piezo_jpe_scan(nr_steps = self.nr_V_steps, wait_cycles = wait_cycles, start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step)


	def piezo_scan_msync (self, nr_scans =1 , delay_ms = 0):

		v_step = float(self.V_max-self.V_min)/float(self.nr_V_steps)
		self.v_vals = np.linspace(self.V_min, self.V_max, self.nr_V_steps)
		self.success, self.PD_signal, self.tstamps_ms = self._adwin.fine_piezo_jpe_scan_sync(nr_steps = self.nr_V_steps, wait_cycles = 1, 
							start_voltages = [self.V_min, self.V_min, self.V_min], voltage_step=v_step,
							nr_scans = nr_scans, delay_ms = delay_ms)			


