"""
perform a dark ESR measurement without the adwin.

Norbert Kalb, n.kalb@tudelft.nl 
2014
"""


import os
import qt
import numpy as np
import measurement.lib.measurement2.p7889.p7889_2d_measurement as p7889_msmt;
reload(p7889_msmt)
#reload(measurement.lib.measurement2.p7889.p7889_2d_measurement)
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
ranges = [8e6]#8e6]
# amplitude = [0.1125, 0.05625]
amplitude = [0.9]#0.05625]

for k in range(0,len(amplitude)):

	if k == 1:
		print 'Optimizing!'
		AWG.initialize_dc_waveforms()
		GreenAOM.set_power(250e-6)
		optimiz0r.optimize(dims=['x','y','z'])
		GreenAOM.turn_off()

	#generate measurement
	nr_updates = 70
	rabi_period = 2.4
	# amplitude = 0.9
	m=p7889_msmt.DarkESR_p7889('Hillary_scan9_spot2_pulse=%s_ampl=%s' % ( np.round(0.5 *rabi_period,3) , amplitude[k]))

	#parameter definition
	m.params['repetitions']=60000000			# nr of reps per datapoint per nr_of_update
	m.params['nr_of_updates']=nr_updates

	m.params['ssbmod_amplitude']=amplitude[k] 
	print "ssmod_amplitude =", m.params['ssbmod_amplitude']

	m.params['range']=ranges[k]
	# m.params['p7889_binwidth'] = 8  # added MJD
	# m.params['p7889_range'] = 1000  # added MJD
	# m.params['p7889_use_dma'] = False # added here to 
	# m.params['p7889_sweep_preset_number'] = 1
	# # m.params['p7889_number_of_cycles'] = 1 # changed from 1 to 20 MJD
	# # m.params['p7889_number_of_sequences'] = 1000000
	# m.params['p7889_ROI_min'] = 0
	# m.params['p7889_ROI_max'] = 1000 # to here MJD


	### i copeid all the Rabi stuff, NK
	m.params['p7889_use_dma'] = False
	m.params['p7889_sweep_preset_number'] = 1
	m.params['p7889_number_of_cycles'] = 1 # changed from 1 to 20 MJD
	m.params['p7889_number_of_sequences'] = 1000000
	m.params['p7889_ROI_min'] = 400
	m.params['p7889_ROI_max'] = 1000
	m.params['p7889_range'] = 6000
	m.params['p7889_binwidth'] = 8 ### powers of 2 only! resolution is 0.1 ns so binwidth of 8 --> 0.8 ns bins.

	m.params['pts']=101
	# m.params['MW_pulse_length']=0.5* rabi_period * 0.9/amplitude[k] * 10**-6 
	# m.params['MW_pulse_length'] = 0.2e-6
	m.params['MW_pulse_length']=2e-6



	m.params['ssbmod_detuning']= 43e6 #-23e6 MJD
	m.params['mw_power']= 9.

	m.params['Eval_ROI_start']= 400 #1670 MJD
	m.params['Eval_ROI_end']= 1000 #2200 MJD

	m.params['GreenAOM_pulse_length']=4.*1e-6 # 4 first 
	m.params['GreenAOM_power']= 100e-6

	m.params['ssbmod_frq_start']=m.params['ssbmod_detuning']-m.params['range']/2
	print 'ssmob_frq_start = ', m.params['ssbmod_frq_start']
	m.params['ssbmod_frq_stop']=m.params['ssbmod_detuning']+m.params['range']/2
	print 'ssmob_frq_stop', m.params['ssbmod_frq_stop']
	m.params['mw_frq']=2.8518e9-m.params['ssbmod_detuning'] #This gives the central MW frequency
	# 2.849937
	# 2.85696
	#measurement start
	m.autoconfig()
	m.generate_sequence()
	m.updated_measurement()
	# m.run()
	m.save_2D_data()
	m.finish()

	# test if it works with m.run()