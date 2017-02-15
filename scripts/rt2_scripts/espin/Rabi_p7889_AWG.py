"""
perform a Rabi oscillation at RT with the p7889 correlation card.

Norbert Kalb, n.kalb@tudelft.nl 
2014
"""

import qt
import numpy as np
import measurement.lib.measurement2.p7889.p7889_2d_measurement as p7889_msmt
reload(p7889_msmt)
execfile(qt.reload_current_setup)


# power = [17, 12, 9, 7]
power = [9]

for k in power:
	AWG.initialize_dc_waveforms()

	#generate measurement
	m=p7889_msmt.Rabi_p7889('Hillary_scan9_spot2')


	m.params['p7889_use_dma'] = False
	m.params['p7889_sweep_preset_number'] = 1
	m.params['p7889_number_of_cycles'] = 1 # changed from 1 to 20 MJD
	m.params['p7889_number_of_sequences'] = 1000000
	m.params['p7889_ROI_min'] = 400
	m.params['p7889_ROI_max'] = 1500
	m.params['p7889_range'] = 6000
	m.params['p7889_binwidth'] = 8 ### powers of 2 only! resolution is 0.1 ns so binwidth of 8 --> 0.8 ns bins.

	# #Sweep definitions
	m.params['repetitions']= 1400000000
	m.params['pts']= 100
	m.params['nr_of_updates']=500
	m.params['mw_power']=k

	m.params['GreenAOM_pulse_length']=4.*1e-6 # was 4 before
	m.params['GreenAOM_power']= 100e-6#400e-6

	#parameters for postprocessing of the raw data
	m.params['Eval_ROI_start']= 400
	m.params['Eval_ROI_end']=1000


	m.params['MW_pulse_length_start']=(0)*1e-6 #(0.0)*1e-6
	m.params['range']=5.5e-6

	m.params['MW_pulse_length_stop']=m.params['MW_pulse_length_start']+m.params['range']


	m.params['ssbmod_amplitude']=0.9 #0.9
	m.params['ssbmod_frequency']=43e6


	m.params['mw_frq']=2.85172e9-m.params['ssbmod_frequency'] #in Hz, insert config parameter for the specific nv center here later on. This gives the central MW frequency.
	
	# #measurement start
	m.autoconfig()
	m.generate_sequence()
#m.run()
	m.updated_measurement()
	m.save_2D_data()
	m.finish()


