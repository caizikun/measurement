'''
Module for DynamicalDecoupling class that returns different types of pulses.
'''
import numpy as np
import sys
from scipy.special import erfinv
import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
# from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD

'''
General idea: for every basic pulse type, check the corresponding parameter in msmt_params
and return the selected pulse.
-- KvB

Edited by NK and SK 20160128
'''


def check_pulse_shape(msmt):

	try:
		pulse_shape = msmt.params['pulse_shape']
	# if 'pulse_shape' not in msmt.params.parameters:
		if pulse_shape == 'Square':
			#print 'pulse select selected square pulses'
			msmt.params['fast_pi_duration'] = msmt.params['Square_pi_length']
			msmt.params['fast_pi2_duration'] = msmt.params['Square_pi2_length']
			msmt.params['fast_pi_amp'] = msmt.params['Square_pi_amp']
			msmt.params['mw2_fast_pi_duration'] = msmt.params['mw2_Square_pi_length']
			msmt.params['mw2_fast_pi2_duration'] = msmt.params['mw2_Square_pi2_length']
		elif pulse_shape == 'Hermite':
			#print 'pulse select selected hermite pulses'
			msmt.params['fast_pi_duration'] = msmt.params['Hermite_pi_length']
			msmt.params['fast_pi2_duration'] = msmt.params['Hermite_pi2_length']
			msmt.params['fast_pi_amp'] = msmt.params['Hermite_pi_amp']
			msmt.params['mw2_fast_pi_duration'] = msmt.params['mw2_Hermite_pi_length']
			msmt.params['mw2_fast_pi2_duration'] = msmt.params['mw2_Hermite_pi2_length']
	except:
		raise Exception('Error in pulse select: '), sys.exc_info()[0]

	return pulse_shape

def X_pulse(msmt):
	'''
	X pi pulse
	'''	
	pulse_shape = check_pulse_shape(msmt)


	if pulse_shape == 'Square':
		"""
		NOTE: Commented out version dates from pre-MW switch DD script
		"""
		X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
			I_channel='MW_Imod', Q_channel='MW_Qmod',
			PM_channel='MW_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
			frequency = msmt.params['MW_modulation_frequency'],
			PM_risetime = msmt.params['MW_pulse_mod_risetime'],
			Sw_risetime = msmt.params['MW_switch_risetime'],
			length = msmt.params['Square_pi_length'],
			amplitude = msmt.params['Square_pi_amp'],
			phase =  msmt.params['X_phase'])


	elif pulse_shape == 'Hermite':
		# print 'This is pulse select speaking: I make hermite pulses'
		# print 'length is', msmt.params['Hermite_pi_length']
		# print 'Amp is', msmt.params['Hermite_pi_amp']

		X = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = msmt.params['MW_switch_channel'],
						 frequency = msmt.params['mw_mod_freq'],
						 amplitude = msmt.params['Hermite_pi_amp'],
						 length = msmt.params['Hermite_pi_length'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'],
						 pi2_pulse = False)


	return X

def mX_pulse(msmt):
	'''
	-X pi pulse
	'''

	return pulse.cp(X_pulse(msmt),phase = msmt.params['X_phase']+180)


def Xpi2_pulse(msmt):
	'''
	pi/2 pulse around X
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':

		pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel=msmt.params['MW_switch_channel'],
            frequency = msmt.params['pi2_mod_frq'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
            length = msmt.params['Square_pi2_length'],
            amplitude = msmt.params['Square_pi2_amp'],
            phase = msmt.params['X_phase'])
	elif pulse_shape == 'Hermite':
		pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite Pi/2-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = msmt.params['MW_switch_channel'],
						 frequency = msmt.params['mw_mod_freq'],
						 amplitude = msmt.params['Hermite_pi2_amp'],
						 length = msmt.params['Hermite_pi2_length'], 
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'],
						 pi2_pulse = True)
	return pi2

def mXpi2_pulse(msmt):
	'''
	pi/2 pulse around mX
	'''
	return pulse.cp(Xpi2_pulse(msmt), phase = msmt.params['X_phase']+180)

def Ypi2_pulse(msmt):
	return pulse.cp(Xpi2_pulse(msmt), phase = msmt.params['Y_phase'])

def mYpi2_pulse(msmt):
	return pulse.cp(Xpi2_pulse(msmt), phase = msmt.params['Y_phase']+180)

def Y_pulse(msmt):
	return pulse.cp(X_pulse(msmt), phase = msmt.params['Y_phase'])

def mY_pulse(msmt):
	'''
	Pi pulse around mY
	'''
	return pulse.cp(X_pulse(msmt),phase = msmt.params['Y_phase']+180)

def comp_pi2_pi_pi2_pulse(msmt):
	'''
	Pi2 pulse around Y, Pi pulse around X, Pi2 pulse around Y
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		comp_pulse = pulselib.composite_pi2_pi_pi2_pulse_IQ('electron comp_pi2-pi-pi2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel=msmt.params['MW_switch_channel'],
            frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
			length_p1 = msmt.params['Square_pi2_length'],
			length_p2 = msmt.params['Square_pi_length'],
			length_p3 = msmt.params['Square_pi2_length'], 
			pulse_delay = 12e-9,
			amplitude_p1 = msmt.params['Square_pi2_amp'],
			amplitude_p2 = msmt.params['Square_pi_amp'],						 
			amplitude_p3 = msmt.params['Square_pi2_amp'],
			phase_p1 = msmt.params['Y_phase'],
			phase_p2 = msmt.params['X_phase'],
			phase_p3 = msmt.params['Y_phase'])
	elif pulse_shape == 'Hermite':
		comp_pulse = pulselib.composite_pi2_pi_pi2_Hermite_pulse_IQ('Hermite comp_pi2-pi-pi2-pulse',
						'MW_Imod',
						'MW_Qmod',
						'MW_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
						frequency = msmt.params['mw_mod_freq'],
						amplitude_p1 = msmt.params['Hermite_pi2_amp'],
						amplitude_p2 = msmt.params['Hermite_pi_amp'],						 
						amplitude_p3 = msmt.params['Hermite_pi2_amp'],
						length_p1 = msmt.params['Hermite_pi2_length'],
						length_p2 = msmt.params['Hermite_pi_length'],
						length_p3 = msmt.params['Hermite_pi2_length'], 
						pulse_delay = 12e-9,
						PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						Sw_risetime = msmt.params['MW_switch_risetime'],
						phase_p1 = msmt.params['Y_phase'],
						phase_p2 = msmt.params['X_phase'],
						phase_p3 = msmt.params['Y_phase'])
	return comp_pulse


def desr_pulse(msmt):
	'''
	desr pi pulse
	'''	
	pulse_shape = check_pulse_shape(msmt)


	if pulse_shape == 'Square':
		"""
		NOTE: Commented out version dates from pre-MW switch DD script
		"""
		desr = pulselib.MW_IQmod_pulse('electron desr-Pi-pulse',
			I_channel='MW_Imod', Q_channel='MW_Qmod',
			PM_channel='MW_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
			frequency = msmt.params['desr_modulation_frequency'],
			PM_risetime = msmt.params['MW_pulse_mod_risetime'],
			Sw_risetime = msmt.params['MW_switch_risetime'],
			length = msmt.params['desr_pulse_length'],
			amplitude = msmt.params['desr_pulse_amp'],
			phase =  msmt.params['X_phase'])

	return desr


def pi_pulse_MW2(msmt):
	'''
	pi pulse on MW source No2
	'''	
	pulse_shape = check_pulse_shape(msmt)
	print 'doing Squares on MW2'
	if pulse_shape == 'Square':
		X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
			I_channel='MW_Imod', Q_channel='MW_Qmod',
			PM_channel='mw2_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
			frequency = 0.,
			PM_risetime = msmt.params['mw2_pulse_mod_risetime'],
			Sw_risetime = msmt.params['MW_switch_risetime'],
			length = msmt.params['mw2_Square_pi_length'],
			phase =  msmt.params['X_phase'],
			amplitude = msmt.params['mw2_Square_pi_amp'])
   
	
	elif pulse_shape == 'Hermite':
		print 'doing hermites on MW2'
		X = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
						 I_channel='MW_Imod',
						 Q_channel='MW_Qmod',
						 PM_channel='mw2_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
						 frequency = msmt.params['mw2_mod_freq'],
						 amplitude = msmt.params['mw2_Hermite_pi_amp'],
						 length = msmt.params['mw2_Hermite_pi_length'],
						 PM_risetime = msmt.params['mw2_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'],
						 pi2_pulse = False)
	else:
		print 'mw2 no valid pulse'

	return X

def mw2_squareX(msmt):
	'''
	pi pulse on MW source No2
	'''	
	X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
		I_channel='MW_Imod', Q_channel='MW_Qmod',
		PM_channel='mw2_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
		frequency = 0.,
		PM_risetime = msmt.params['mw2_pulse_mod_risetime'],
		Sw_risetime = msmt.params['MW_switch_risetime'],
		length = msmt.params['mw2_Square_pi_length'],
		phase =  msmt.params['X_phase'],
		amplitude = msmt.params['mw2_Square_pi_amp'])
   
	return X

def squareX(msmt):
	'''
	X pi pulse
	'''	
	X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
		I_channel='MW_Imod', Q_channel='MW_Qmod',
		PM_channel='MW_pulsemod', Sw_channel = msmt.params['MW_switch_channel'],
		frequency = msmt.params['MW_modulation_frequency'],
		PM_risetime = msmt.params['MW_pulse_mod_risetime'],
		Sw_risetime = msmt.params['MW_switch_risetime'],
		length = msmt.params['Square_pi_length'],
		amplitude = msmt.params['Square_pi_amp'],
		phase =  msmt.params['X_phase'])

	return X