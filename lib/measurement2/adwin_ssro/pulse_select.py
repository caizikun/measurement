'''
Module for DynamicalDecoupling class that returns different types of pulses.
'''
import numpy as np
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
'''


def check_pulse_shape(msmt):

	try:
		pulse_shape = msmt.params['pulse_shape']
	# if 'pulse_shape' not in msmt.params.parameters:
	except:
		raise Exception('No pulse type specified in msmt_params. Please add a key called "pulse_shape".')

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
			PM_channel='MW_pulsemod', Sw_channel = 'MW_switch',
			frequency = msmt.params['MW_modulation_frequency'],
			PM_risetime = msmt.params['MW_pulse_mod_risetime'],
			Sw_risetime = msmt.params['MW_switch_risetime'],
			length = msmt.params['fast_pi_duration'],
			amplitude = msmt.params['fast_pi_amp'],
			phase =  msmt.params['X_phase'])
        # X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel='MW_switch',
        #     frequency = msmt.params['MW_modulation_frequency'],
        #     PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = msmt.params['MW_switch_risetime'],
        #     length = msmt.params['fast_pi_duration'],
        #     amplitude = msmt.params['fast_pi_amp'],
        #     phase = msmt.params['X_phase'])

	elif pulse_shape == 'Hermite':
		X = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi_amp'],
						 length = msmt.params['Hermite_fast_pi_duration'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'],
						 pi2_pulse = False)

	return X

def mX_pulse(msmt):
	'''
	-X pi pulse
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		# X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
		# 	I_channel='MW_Imod', Q_channel='MW_Qmod',
		# 	PM_channel='MW_pulsemod',
		# 	frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
		# 	PM_risetime = msmt.params['MW_pulse_mod_risetime'],
		# 	length = msmt.params['fast_pi_duration'],
		# 	amplitude = msmt.params['fast_pi_amp'],
		# 	phase =  msmt.params['X_phase'] + 180)
		X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            frequency = msmt.params['MW_modulation_frequency'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
            length = msmt.params['fast_pi_duration'],
            amplitude = msmt.params['fast_pi_amp'],
            phase =  msmt.params['X_phase']+180)
	elif pulse_shape == 'Hermite':
		X = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi_amp'],
						 length = msmt.params['Hermite_fast_pi_duration'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'] + 180, # NOTE: not tested yet! (22-04-2015)
						 pi2_pulse = False)

	return X

def Xpi2_pulse(msmt):
	'''
	pi/2 pulse around X
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		# pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
		# 	I_channel='MW_Imod', Q_channel='MW_Qmod',
		# 	PM_channel='MW_pulsemod',
		# 	frequency = msmt.params['fast_pi2_mod_frq'],
		# 	PM_risetime = msmt.params['MW_pulse_mod_risetime'],
		# 	length = msmt.params['fast_pi2_duration'],
		# 	amplitude = msmt.params['fast_pi2_amp'],
		# 	phase = msmt.params['X_phase'])
		pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            frequency = msmt.params['fast_pi2_mod_frq'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
            length = msmt.params['fast_pi2_duration'],
            amplitude = msmt.params['fast_pi2_amp'],
            phase = msmt.params['X_phase'])
	elif pulse_shape == 'Hermite':
		pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite Pi/2-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi2_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi2_amp'],
						 length = msmt.params['Hermite_fast_pi2_duration'], 
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'],
						 pi2_pulse = True)
	return pi2

def mXpi2_pulse(msmt):
	'''
	pi/2 pulse around X
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
			I_channel='MW_Imod', Q_channel='MW_Qmod',
			PM_channel='MW_pulsemod', Sw_channel = 'MW_switch',
			frequency = msmt.params['fast_pi2_mod_frq'],
			PM_risetime = msmt.params['MW_pulse_mod_risetime'],
			Sw_risetime = msmt.params['MW_switch_risetime'],
			length = msmt.params['fast_pi2_duration'],
			amplitude = msmt.params['fast_pi2_amp'],
			phase = msmt.params['X_phase']+180)
	elif pulse_shape == 'Hermite':
		pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite Pi/2-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi2_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi2_amp'],
						 length = msmt.params['Hermite_fast_pi2_duration'], # NOTE: NOT CALIBRATED YET! (23-04-2015)
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['X_phase'] + 180,
						 pi2_pulse = True)
	return pi2

def Ypi2_pulse(msmt):
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
				I_channel='MW_Imod', Q_channel='MW_Qmod',
				PM_channel='MW_pulsemod', Sw_channel = 'MW_switch',
				frequency = msmt.params['fast_pi2_mod_frq'],
				PM_risetime = msmt.params['MW_pulse_mod_risetime'],
				Sw_risetime = msmt.params['MW_switch_risetime'],
				length = msmt.params['fast_pi2_duration'],
				amplitude = msmt.params['fast_pi2_amp'],
				phase = msmt.params['Y_phase'])
	elif pulse_shape == 'Hermite':
		pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite YPi/2-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi2_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi2_amp'],
						 length = msmt.params['Hermite_fast_pi2_duration'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['Y_phase'],
						 pi2_pulse = True)
	return pi2

def mYpi2_pulse(msmt):
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
				I_channel='MW_Imod', Q_channel='MW_Qmod',
				PM_channel='MW_pulsemod',
				Sw_channel = 'MW_switch',
				frequency = msmt.params['fast_pi2_mod_frq'],
				PM_risetime = msmt.params['MW_pulse_mod_risetime'],
				Sw_risetime = msmt.params['MW_switch_risetime'],
				length = msmt.params['fast_pi2_duration'],
				amplitude = msmt.params['fast_pi2_amp'],
				phase = msmt.params['Y_phase'] + 180)
	elif pulse_shape == 'Hermite':
		pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite Ypi/2-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod',
						 Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi2_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi2_amp'],
						 length = msmt.params['Hermite_fast_pi2_duration'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['Y_phase'] + 180,
						 pi2_pulse = True)
	return pi2

def Y_pulse(msmt):
	'''
	Pi pulse around Y
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		# Y = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
		# 	I_channel='MW_Imod', Q_channel='MW_Qmod',
		# 	PM_channel='MW_pulsemod',
		# 	frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
		# 	PM_risetime = msmt.params['MW_pulse_mod_risetime'],
		# 	length = msmt.params['fast_pi_duration'],
		# 	amplitude = msmt.params['fast_pi_amp'],
		# 	phase =  msmt.params['Y_phase'])
		Y = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
            length = msmt.params['fast_pi_duration'],
            amplitude = msmt.params['fast_pi_amp'],
            phase =  msmt.params['Y_phase'])
	elif pulse_shape == 'Hermite':
		Y = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod', Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi_amp'],
						 length = msmt.params['Hermite_fast_pi_duration'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['Y_phase'],
						 pi2_pulse = False)
	return Y

def mY_pulse(msmt):
	'''
	Pi pulse around Y
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		# Y = pulselib.MW_IQmod_pulse('electron Y-Pi-pulse',
		# 	I_channel='MW_Imod', Q_channel='MW_Qmod',
		# 	PM_channel='MW_pulsemod',
		# 	frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
		# 	PM_risetime = msmt.params['MW_pulse_mod_risetime'],
		# 	length = msmt.params['fast_pi_duration'],
		# 	amplitude = msmt.params['fast_pi_amp'],
		# 	phase =  msmt.params['Y_phase'] + 180),
		Y = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
            length = msmt.params['fast_pi_duration'],
            amplitude = msmt.params['fast_pi_amp'],
            phase =  msmt.params['Y_phase']+180)
	elif pulse_shape == 'Hermite':
		Y = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
						 'MW_Imod',
						 'MW_Qmod',
						 'MW_pulsemod', Sw_channel = 'MW_switch',
						 frequency = msmt.params['Hermite_fast_pi_mod_frq'],
						 amplitude = msmt.params['Hermite_fast_pi_amp'],
						 length = msmt.params['Hermite_fast_pi_duration'],
						 PM_risetime = msmt.params['MW_pulse_mod_risetime'],
						 Sw_risetime = msmt.params['MW_switch_risetime'],
						 phase = msmt.params['Y_phase'] + 180,
						 pi2_pulse = False)
	return Y

def comp_pi2_pi_pi2_pulse(msmt):
	'''
	Pi2 pulse around Y, Pi pulse around X, Pi2 pulse around Y
	'''
	pulse_shape = check_pulse_shape(msmt)

	if pulse_shape == 'Square':
		comp_pulse = pulselib.composite_pi2_pi_pi2_pulse_IQ('electron comp_pi2-pi-pi2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            frequency = msmt.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = msmt.params['MW_pulse_mod_risetime'],
            Sw_risetime = msmt.params['MW_switch_risetime'],
			length_p1 = msmt.params['fast_pi2_duration'],
			length_p2 = msmt.params['fast_pi_duration'],
			length_p3 = msmt.params['fast_pi2_duration'], 
			pulse_delay = 12e-9,
			amplitude_p1 = msmt.params['fast_pi2_amp'],
			amplitude_p2 = msmt.params['fast_pi_amp'],						 
			amplitude_p3 = msmt.params['fast_pi2_amp'],
			phase_p1 = msmt.params['Y_phase'],
			phase_p2 = msmt.params['X_phase'],
			phase_p3 = msmt.params['Y_phase'])
	elif pulse_shape == 'Hermite':
		comp_pulse = pulselib.composite_pi2_pi_pi2_Hermite_pulse_IQ('Hermite comp_pi2-pi-pi2-pulse',
						'MW_Imod',
						'MW_Qmod',
						'MW_pulsemod', Sw_channel = 'MW_switch',
						frequency = msmt.params['Hermite_fast_pi_mod_frq'],
						amplitude_p1 = msmt.params['Hermite_fast_pi2_amp'],
						amplitude_p2 = msmt.params['Hermite_fast_pi_amp'],						 
						amplitude_p3 = msmt.params['Hermite_fast_pi2_amp'],
						length_p1 = msmt.params['Hermite_fast_pi2_duration'],
						length_p2 = msmt.params['Hermite_fast_pi_duration'],
						length_p3 = msmt.params['Hermite_fast_pi2_duration'], 
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
			PM_channel='MW_pulsemod', Sw_channel = 'MW_switch',
			frequency = msmt.params['desr_modulation_frequency'],
			PM_risetime = msmt.params['MW_pulse_mod_risetime'],
			Sw_risetime = msmt.params['MW_switch_risetime'],
			length = msmt.params['desr_pulse_duration'],
			amplitude = msmt.params['desr_pulse_amp'],
			phase =  msmt.params['X_phase'])
        # X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel='MW_switch',
        #     frequency = msmt.params['MW_modulation_frequency'],
        #     PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = msmt.params['MW_switch_risetime'],
        #     length = msmt.params['fast_pi_duration'],
        #     amplitude = msmt.params['fast_pi_amp'],
        #     phase = msmt.params['X_phase'])	
	return desr


def pi_pulse_MW2(msmt):
	'''
	pi pulse on MW source No2
	'''	

	#print 'doing Squares on MW2'
	X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
		I_channel='MW2', Q_channel='MW2',
		PM_channel='MW2_pulsemod', Sw_channel = 'MW_switch',
		frequency = 0.,
		PM_risetime = msmt.params['MW2_pulse_mod_risetime'],
		Sw_risetime = msmt.params['MW_switch_risetime'],
		length = msmt.params['MW2_duration'],
		#phase =  msmt.params['X_phase'],
		amplitude = msmt.params['MW2_pulse_amplitudes'])
   
	# PulseShaping not possible
	
	# elif pulse_shape == 'Hermite':
	# 	X = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
	# 					 'MW2',  #IMod
	# 					 'MW2',  #QMod    There's only one channel
	# 					 'MW2_pulsemod',
	# 					 Sw_channel = 'MW_switch',
	# 					 frequency = 0.,
	# 					 amplitude = msmt.params['mw2_Hermite_fast_pi_amp'],
	# 					 length = msmt.params['mw2_Hermite_fast_pi_duration'],
	# 					 PM_risetime = msmt.params['MW2_pulse_mod_risetime'],
	# 					 Sw_risetime = msmt.params['MW_switch_risetime'],
	# 					 phase = msmt.params['X_phase'],
	# 					 pi2_pulse = False)
	return X


