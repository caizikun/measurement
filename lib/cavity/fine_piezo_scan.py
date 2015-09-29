import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class FinePiezoJPE_Scan ():

	def __init__ (self, name, laser):
		self.name = name
		self._adwin = qt.get_setup_instrument['adwin']
		self._laser = laser

		self.voltage = None
		self.PD_signal = None
		self._laser_initialized = False

	def set_laser_params(self, wavelength, power):
		#self._laser.set_wavelength()
		#self._laser.set_power()
		self._laser_initialized = True

	def scan (self, V_min, V_max, nr_V_steps, offset_12 = 0., offset_13 = 0., do_save = False):

		if not(self._laser_initialized):
			print 'ERROR: laser not initialized!!'
		else:
			v_step = float(V_max-V_min)/float(nr_V_steps)
			self.offset_12 = offset_12
			self.offset_13 = offset_13		
			self.v_vals = np.linspace(V_min, V_max, nr_V_steps)
			self.PD_signal = self._adwin.fine_piezo_jpe_scan(self, ADC_channel=1, nr_steps = nr_V_steps, wait_cycles = 50, 
	        			start_voltages = [V_min,V_min+offset_12,V_min+offset_13], voltage_step=v_step)
			self.plot_scan()
			if do_save:
				self.save()

	def plot_scan(self):
		if not(self.PD_signal):
			print 'ERROR: no data to be plotted!'
		else:

			f = plt.figure()
    		ax = f.add_subplot(1,1,1)
    		ax.plot (self.v_vals, self.PD_signal)
    		ax.set_xlabel ('fine-tuning piezo voltage [V]')
    		ax.set_ylabel ('photodiode intensity [a.u.]')
    		f.show()

    def save (self):
		if not(self.PD_signal):
			print 'ERROR: no data to be saved!'
		else:

			if self.name:
				name = '_'+self.name
			fName = time.strftime ('%Y%m%d_%H%M%S')+ '_fineTuningPiezo_scan'+name
			f0 = os.path.join('D:/measuring/data/', time.strftime'%Y%m%d')
			directory = os.path.join(directory, fName)

			if not os.path.exists(directory):
    			os.makedirs(directory)

			f = plt.figure()
    		ax = f.add_subplot(1,1,1)
    		ax.plot (self.v_vals, self.PD_signal)
    		ax.set_xlabel ('fine-tuning piezo voltage [V]')
    		ax.set_ylabel ('photodiode intensity [a.u.]')
    		f.savefig(os.path.join(directory, fName+'.png'))
    		
			f = h5py.File(os.path.join(directory, fName+'.hdf5'), mode)
			f.attrs ['offset_12'] = self.offset_12
			f.attrs ['offset_13'] = self.offset_12

			scan_grp = f.create_group('fineTuningPiezo_scan')
			scan_grp.create_dataset('V1', data = self.v_vals)
			scan_grp.create_dataset('PD_signal', data = self.PD_signal)
			f.close()
		print 'Data saved!'






