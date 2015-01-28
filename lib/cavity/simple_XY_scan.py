import os
from instrument import Instrument
import qt
import time
import types
import numpy as np
from lib import config


class simple_XY_scan ():

	def __init__ (self, name):
		self.name = name
		self._moc = qt.get_setup_instrument['moc']
		self._adwin = qt.get_setup_instrument['adwin']

		self.int_time = None
		self.X = None
		self.Y = None
		self.counts = None

	def set_integratione_time (self, val):
		self.int_time = val

	def get_integration_time (self):
		return self.get_integration_time

	def set_position_as_origin (self):
		self._moc.set_as_origin()

	def scan (self, x_min, x_max, y_min, y_max, z, nr_x_steps, nr_y_steps, do_save = False):

		if not(self.int_time):
			print 'ERROR: integration time not set!'
		else:

			print 'Starting JPE spatial scan. Press X to quit...'

			stop = False
			x_vals = np.linspace (x_min, x_max, nr_x_steps)
			ind = 0
			for i in np.arange (nr_x_steps):
				if stop: break
				curr_x = x_vals[i]
				if np.mod(i, 2)==0:
					y_vals = np.linspace(y_min, y_max, nr_y_steps)
				else:
					y_vals = np.linspace(y_max, y_min, nr_y_steps)

				for j in np.arange (nr_y_steps):
					if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): stop=True
					if stop: break
					
					curr_y = y_vals[j]

					self._moc.move_to_xyz(x=curr_x, y=curr_y, z= z, verbose = False)
					qt.msleep (1)
					cts = self._adwin.measure_counts (int_time = self.get_integration_time)
					self.X[i,j] = curr_x
					self.Y[i,j] = curr_y
					self.counts [i,j] = cts

			if not(stop):					
				print 'Scan finished!'
				self.plot_scan()
				if do_save:
					self.save()
			else:
				print 'Scan quit!'
			return stop

	def plot_scan(self):
		if not(self.counts):
			print 'ERROR: no data to be plotted!'
		else:

			f = plt.figure()
    		ax = f.add_subplot(1,1,1)
    		ax.pcolor (X, Y, counts)
    		ax.set_xlabel ('x [um]')
    		ax.set_ylabel ('y [um]')
    		f.show()

    def save (self):
		if not(self.counts):
			print 'ERROR: no data to be saved!'
		else:

			if self.name:
				name = '_'+self.name
			fName = time.strftime ('%Y%m%d_%H%M%S')+ '_XYscan_jpe'+name
			f0 = os.path.join('D:/measuring/data/', time.strftime'%Y%m%d')
			directory = os.path.join(directory, fName)

			if not os.path.exists(directory):
    			os.makedirs(directory)

			f = plt.figure()
    		ax = f.add_subplot(1,1,1)
    		ax.pcolor (X, Y, counts)
    		ax.set_xlabel ('x [um]')
    		ax.set_ylabel ('y [um]')
    		f.savefig(os.path.join(directory, fName+'.png'))
    		
			f = h5py.File(os.path.join(directory, fName+'.hdf5'), mode)
			f.attrs ['integration_time'] = self.int_time
			scan_grp = f.create_group('XY_scan')
			scan_grp.create_dataset('x', data = self.X)
			scan_grp.create_dataset('y', data = self.Y)
			scan_grp.create_dataset('counts', data = self.counts)
			f.close()
	
		print 'Data saved!'






