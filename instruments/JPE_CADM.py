### Instrument class to control the JPE CPSHR cryogenic positiong stage with high mechanical resonance.
### C Bonato (08-2014)

from instrument import Instrument
import types
import logging
import re
import math
import subprocess as sp
import time
import numpy as np

class JPE_CADM(Instrument):


	#Controller for coarse PiezoKnob positioning
	
	def __init__(self, name):
		Instrument.__init__(self, name)
		self.T = 300
		self.type = 'PK1801'
		self.TRQFR = 1
		self.freq = 200
		self.rel_step = 100

		self.pzknb_command = 'D:\measuring\measurement\hardware\jpe\pzknb_CMD\pzknb'

		print '--- Initializing JPE PiezoKnob high mechanical resonance stage ---- '
		#T = raw_input ('Please set the temperature of operation [K]...')
		self.T = 300
		print 'Temperature set to '+str(self.T)+' K!'
		self.add_function('set_temperature')
		self.add_function('set_freq')
		self.add_function('set_relative_piezo_step')
		self.add_function('get_params')
		self.add_function('status')
		self.add_function('info')
		self.add_function('move_cnt')
		self.add_function('move')
		self.add_function('stop')
        
	def set_temperature (self, T):
		if ((T>=0)&(T<=300)):
			self.T = int(T)
			#self._set_piezo_step()
		else:
			print 'Value outside permitted range [0-300K]'

	def set_freq (self, f):

		if ((f>0)&(f<=600)):
			self.freq = int(f)
		else:
			print 'Value outside permitted range [1-600 Hz]'

	def set_relative_piezo_step (self, p):

		if ((p>=1)&(p<=100)):
			self.rel = int(p)
		else:
			print 'Value outside permitted range [1-100%]'
			
	def get_params(self):
		print '-------JPE controller: '+self.type
		print '- temperature: '+str(self.T)+'K'
		print '- frequency: '+str(self.freq)+'Hz'
		print '- relative piezo step: '+str(self.rel_step)+'%'

	def status(self, addr = 0):
		out = sp.check_output ([self.pzknb_command, 'S', str(addr)])
		print 'Status controller-'+str(addr)+': ', out

	def is_busy (self, addr = 0):
		out = sp.check_output ([self.pzknb_command, 'S', str(addr)])
		print out
		
	def info (self, addr, ch):
		output = sp.check_output ([self.pzknb_command, 'i', str(addr), str(ch)])
		print output
		
	def move_cnt (self, cw = 0):
		if (cw == 0):
			print 'Specify direction (clockwise: > 0, counter-clockwise: <0)'
		else:
			cw = int((np.sign(cw)+1)/2)
			out = sp.check_output [self.pzknb_command, 'M', str(addr), str(ch), self.type, self.T, 
											str(cw), str(self.freq), str(self.rel_step), str(0)]

	def stop (self, addr):
		if ((addr>0)&(addr<4)):
			print 'Stop'
		else:
			print 'Specified address not available!'
			
	def move (self, addr, ch, steps):

		cw = int((np.sign(steps)+1)/2)
		steps = abs(steps)
		steps_int = int(steps)
		steps_cent = int(steps*100)-100*int(steps)

		if not(steps==0):
			out = sp.check_output ([self.pzknb_command, 'M', str(addr), str(ch), self.type, str(self.T), str(cw), str(self.freq), str(100), str(steps_int)])
			wait_time = (1./self.freq)*steps_int
			time.sleep(0.2+wait_time)
			out = sp.check_output( [self.pzknb_command, 'M', str(addr), str(ch), self.type, str(self.T), str(cw), str(self.freq), str(1), str(steps_cent)])
			wait_time = (1./self.freq)*steps_cent
			time.sleep(0.2+wait_time)
																
											
 
