#####################################################################################################
# CONTROLLER for JPE actuator    --- Cristian Bonato, 2014  --- cbonato80@gmail.com
# 
# 'master_of_cavity' (MOC) controls 3-axes motion of the positioning stage, taking care
#  of conversion from xyz position to splindle movement. MOC includes a _jpe_cadm instrument,
#  who physically talks to the JPE controller, and a _jpe_tracker, who keeps track of the 
#  spindles' positions. 
#
#  To keep track of spindle length over time, avoiding end-of-range issues (in absence of
#  optical tracking mechanism), splindle lengths are saved in a file (/lib/config/jpe_tracker.cfg),
#  which is continuously updated. Maximum spindle range is stored in _jpe_tracker.max_spindle_steps
#  and a warning is given when approaching this limit.
#
#  Please run MOC.close() before quitting, to close the tracker file
#####################################################################################################

import os
from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
import time
import types
import gobject
import numpy as np
from lib import config
from measurement.lib.config import moc_cfg


class JPE_pos_tracker ():

	def __init__(self, reinit_spindles=False):
		#all coordinates are in mm, angles in radians
		self.z1 = None
		self.z2 = None
		self.z3 = None

		#design properties in mm (see JPE datasheet)
		self.cfg_pars = moc_cfg.config['general_stage_dims']
		self.fiber_z_offset = self.cfg_pars['fiber_z_offset'] #fiber offset with respect to fiber interface
		self.h = self.cfg_pars['h_mm']+self.fiber_z_offset#33.85+self.fiber_z_offset
		self.R = self.cfg_pars['R_mm']#14.5

		self.max_spindle_steps = self.cfg_pars['max_spindle_steps']
		
		#Cartesian coordinates in the lab-frame (mm)
		self.curr_x = None
		self.curr_y = None
		self.curr_z = None
		self.v_piezo_1 = None
		self.v_piezo_2 = None
		self.v_piezo_3 = None		
		self.tracker_file_name = 'D:\measuring\measurement\config\jpe_tracker.npz'

		if reinit_spindles:			
			self.reset_spindle_tracker()
		else:
			print 'Tracker initialized from file...'
			self.tracker_file_readout()


	def tracker_file_update(self):
		try:
			np.savez (self.tracker_file_name, z1= self.z1, z2=self.z2, z3=self.z3, x=self.curr_x, y=self.curr_y, z=self.curr_z)
		except:
			print 'Tracker file update failed!'

	def tracker_file_readout(self):
		tr_file = np.load(self.tracker_file_name)
		self.z1 = tr_file['z1']
		self.z2 = tr_file['z2']
		self.z3 = tr_file['z3']
		self.curr_x = tr_file['x']
		self.curr_y = tr_file['y']
		self.curr_z = tr_file['z']
		print self.curr_x, self.curr_y, self.curr_z
		return self.z1, self.z2, self.z3

	def check_spindle_limit (self, move):
		n1 = self.z1+move[0]
		n2 = self.z2+move[1]
		n3 = self.z3+move[2]
		return ((n1<0)or(n2<0)or(n3<0)or(n1>self.max_spindle_steps)or(n2>self.max_spindle_steps)or(n3>self.max_spindle_steps))

	def set_as_origin (self):
		self.curr_x = 0
		self.curr_y = 0
		self.curr_z = 0
		self.tracker_update (spindle_incr = [0,0,0], pos_values = [0.,0.,0.])
		
	def reset_spindle_tracker(self):
		self.z1 = 0
		self.z2 = 0
		self.z3 = 0
		self.tracker_file_update()
		print 'Tracker reset to zero'

	def tracker_update (self, spindle_incr, pos_values):
		self.z1 = self.z1+spindle_incr[0]
		self.z2 = self.z2+spindle_incr[1]
		self.z3 = self.z3+spindle_incr[2]
		self.curr_x = pos_values[0]
		self.curr_y = pos_values[1]
		self.curr_z = pos_values[2]		
		self.tracker_file_update ()

	def position_to_spindle_steps (self, x, y, z):
		Dx = x-self.curr_x
		Dy = y-self.curr_y
		Dz = z-self.curr_z
			
		DZ1 = -(self.R/self.h)*Dy+Dz
		DZ2 = (3.**0.5/2.)*(self.R/self.h)*Dx+(0.5*self.R/self.h)*Dy+Dz
		DZ3 = -(3.**0.5/2.)*(self.R/self.h)*Dx+(0.5*self.R/self.h)*Dy+Dz
		
		self.curr_x = x
		self.curr_y = y
		self.curr_z = z
		
		return DZ1, DZ2, DZ3
		
	def line_scan (self, axis, min_val, max_val, nr_steps):
	
		PK_val1 = np.zeros(nr_steps)
		PK_val2 = np.zeros(nr_steps)
		PK_val3 = np.zeros(nr_steps)
		scan_vals = np.linspace (min_val, max_val, nr_steps)
		ind = 0		
		for i in scan_vals:
			if (axis=='x'):
				dz1, dz2, dz3 = self.move_to_position (x = i, y=self.curr_y, z=self.curr_z)
			else:
				if (axis=='y'):
					dz1, dz2, dz3 = self.move_to_position (x = x.curr_x, y=i, z=self.curr_z)				
				else:
					if (axis=='z'):
						dz1, dz2, dz3 = self.move_to_position (x = self.curr_x, y = self.curr_y, z=i)
			PK_val1 [ind] = dz1
			PK_val2 [ind] = dz2
			PK_val3 [ind] = dz3
			ind = ind + 1

		return PK_val1, PK_val2, PK_val3
		
					
class master_of_cavity(CyclopeanInstrument):

    def __init__(self, name, jpe, adwin):
    	print 'Initializing master_of_cavity... '
    	self.addr = 1
    	self.ch_x = 1
    	self.ch_y = 2
    	self.ch_z = 3
    	Instrument.__init__(self, name)
    	self._jpe_cadm = qt.instruments[jpe]
    	self._jpe_tracker = JPE_pos_tracker(reinit_spindles=False)
    	self.T = None
    	self._step_size = None
        self.ins_adwin = qt.instruments[adwin]
        self._fine_piezo_V = None
        self.set_fine_piezo_voltages (0,0,0)

        # remote access functions:
        #set parameters
        self.add_function('set_address')
        self.add_function('set_temperature')
        self.add_function('set_freq')
        #get parameters
        self.add_function('get_address')
        #self.add_function('get_temperature')
        self.add_function('get_params')
        self.add_function('status')
    	#position control function
        self.add_function('step')
        self.add_function('set_as_origin')
        self.add_function('move_to_xyz')	


    def motion_to_spindle_steps (self, x, y, z):
    	dz1, dz2, dz3 = self._jpe_tracker.position_to_spindle_steps (x=x, y=y, z=z)
    	s1 = dz1/self._step_size
    	s2 = dz2/self._step_size
    	s3 = dz3/self._step_size
    	return s1, s2, s3

    def get_temperature (self):
    	print 'Temperature is set to ', self.T, 'K'

    def set_address (self, addr):
    	self.addr = addr

    def get_address (self):
    	print 'Address: ', self.addr

    def set_temperature (self, T):
    	self.T = T
    	self._jpe_cadm.set_temperature (T = T)
    	if (self.T>280):
    		self._step_size = 15e-6 #in mm
  		
  		if (self.T<15):
  			self._step_size = 3e-6 #in mm
    
    def set_freq (self, f):
    	self._jpe_cadm.set_freq (f = f)

    def get_params (self):
    	self._jpe_cadm.info()
    	print 'Selected CADM controller: '+str(self.addr)
    	self._jpe_cadm.get_params()
    	
    def status (self):
		output = self._jpe_cadm.status (addr= self.addr)
		return output
		    
    def step (self, ch, steps):
    	self._jpe_cadm.move (addr=self.addr, ch=ch, steps = steps)
    	
    def set_as_origin (self):
    	self._jpe_tracker.set_as_origin()

    def print_current_position(self):
    	print 'x = ', self._jpe_tracker.curr_x
    	print 'y = ', self._jpe_tracker.curr_y
    	print 'z = ', self._jpe_tracker.curr_z

    def print_tracker_params(self):
    	z1, z2, z3 = self._jpe_tracker.tracker_file_readout()
    	print 'Spindle positions: ', z1, z2, z3

    def set_fine_piezo_voltages (self, v1,v2,v3):
    	#self.ins_adwin.set_dac('jpe_fine_tuning_1', v1)
    	#self.ins_adwin.set_dac('jpe_fine_tuning_2', v2)
    	#self.ins_adwin.set_dac('jpe_fine_tuning_3', v3)
    	self.ins_adwin.set_fine_piezos (voltage = np.array([v1, v2, v3]))
    	self._fine_piezo_V = np.array([v1,v2,v3])

    def get_fine_piezo_voltages(self):
    	return self._fine_piezo_V

    def move_spindle_steps (self, s1, s2, s3, x, y, z):
    	self._jpe_cadm.move(addr = self.addr, ch = self.ch_x, steps = s1)
    	qt.msleep(1)
    	self._jpe_cadm.move(addr = self.addr, ch = self.ch_y, steps = s2)
    	qt.msleep(1)
    	self._jpe_cadm.move(addr = self.addr, ch = self.ch_z, steps = s3)
    	qt.msleep(1)
    	self._jpe_tracker.tracker_update(spindle_incr=[s1,s2,s3], pos_values = [x,y,z])

    def move_to_xyz (self, x, y, z, verbose=True):
    	if (self.T == None):
    		print 'Temperature not set!'
    	else:
    		dz1, dz2, dz3 = self._jpe_tracker.position_to_spindle_steps (x=x, y=y, z=z)
    		s1 = dz1/self._step_size
    		s2 = dz2/self._step_size
    		s3 = dz3/self._step_size

    		if verbose:
	    		print 'Moving the spindles the following amounts:'
	    		print 's-1: ', s1, ' steps'
	    		print 's-2: ', s2, ' steps'
	    		print 's-3: ', s3, ' steps'
	    		print 'Currently the spindle positions are the following:'
	    		self.print_tracker_params()
	    		a = raw_input ('Actuate? [y/n]')
	    	else:
	    		a='y'


	    	print 'a=', a
	    	if (a=='y'):
	    		print 'moving'
	    		self._jpe_cadm.move(addr = self.addr, ch = self.ch_x, steps = s1)
	    		qt.msleep(1)
	    		self._jpe_cadm.move(addr = self.addr, ch = self.ch_y, steps = s2)
	    		qt.msleep(1)
	    		self._jpe_cadm.move(addr = self.addr, ch = self.ch_z, steps = s3)
	    		qt.msleep(1)
	    		self._jpe_tracker.tracker_update(spindle_incr=[s1,s2,s3], pos_values = [x,y,z])


	def close(self):
		self._jpe_tracker.close()



