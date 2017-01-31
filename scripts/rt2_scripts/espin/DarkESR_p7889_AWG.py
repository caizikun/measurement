"""
perform a dark ESR measurement without the adwin.

Norbert Kalb, n.kalb@tudelft.nl 
2014
"""


import os
import qt
import numpy as np
import measurement.lib.measurement2.p7889.p7889_2d_measurement
reload(measurement.lib.measurement2.p7889.p7889_2d_measurement)
from measurement.lib.measurement2.p7889.p7889_2d_measurement import DarkESR_p7889
execfile(qt.reload_current_setup)
# rabi_period = [1.25, 2.25, 0.75]
# rabi_period = [3.8]
# power = [17, 9]


# Scan 17, NV1: zero-field frequency = 2.84492e9
# amplitude = [0.225/4.]
# amplitude = [0.9]
# amplitude = [0.45]
# ranges = [2e6]
# ranges = [1e6]
# ranges = [10e6]
ranges = [0.4e6]
# amplitude = [0.1125, 0.05625]
amplitude = [ 0.05625]

for k in range(0,len(amplitude)):

	if k == 1:
		print 'Optimizing!'
		AWG.initialize_dc_waveforms()
		GreenAOM.set_power(250e-6)
		optimiz0r.optimize(dims=['x','y','z'])
	#generate measurement
	nr_updates = 70
	rabi_period = 1./0.222807
	# amplitude = 0.9
	m=DarkESR_p7889('Frodo_scan6_NV1_pulse=%s_ampl=%s' % ( np.round(0.5 * 0.9/amplitude[k] * rabi_period,3) , amplitude[k]))

	#parameter definition
	m.params['repetitions']=100000			# nr of reps per datapoint per nr_of_update
	m.params['nr_of_updates']=nr_updates

	m.params['ssbmod_amplitude']=amplitude[k]
	m.params['range']=ranges[k]

	m.params['pts']=30
	m.params['MW_pulse_length']=0.5 * rabi_period * 0.9/amplitude[k] * 10**-6

	m.params['ssbmod_detuning']=43e6
	m.params['MW_power']= 18.
	m.params['Eval_ROI_start']=1670
	m.params['Eval_ROI_end']=2200

	m.params['GreenAOM_pulse_length']=5.*1e-6
	m.params['GreenAOM_power']= 400e-6

	m.params['ssbmod_frq_start']=m.params['ssbmod_detuning']-m.params['range']/2
	m.params['ssbmod_frq_stop']=m.params['ssbmod_detuning']+m.params['range']/2
	m.params['mw_frq']=2.842058e9-m.params['ssbmod_detuning'] #This gives the central MW frequency
	# 2.849937
	# 2.85696
	#measurement start
	m.autoconfig()
	m.generate_sequence()
	m.updated_measurement()
	m.save_2D_data()
	m.finish()



