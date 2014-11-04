"""
perform a dark ESR measurement without adwin.

Norbert Kalb, n.kalb@tudelft.nl 
2014
"""


import os
import qt
import numpy as np
import measurement.lib.measurement2.p7889_2d_measurement
reload(measurement.lib.measurement2.p7889_2d_measurement)
from measurement.lib.measurement2.p7889_2d_measurement import DarkESR_p7889

#generate measurement
m=DarkESR_p7889('test')

#parameter definition

m.params['repetitions']=10000
m.params['ssbmod_amplitude']=0.03
m.params['range']=4e6
m.params['pts']=8
m.params['MW_pulse_length']=(2.)*1e-6
m.params['ssbmod_detuning']=43e6
m.params['MW_power']=20
m.params['GreenAOM_pulse_length']=2.*1e-6
m.params['Eval_ROI_start']=500
m.params['Eval_ROI_end']=3500

m.params['ssbmod_frq_start']=m.params['ssbmod_detuning']-m.params['range']/2
m.params['ssbmod_frq_stop']=m.params['ssbmod_detuning']+m.params['range']/2
m.params['mw_frq']=2.86e9-m.params['ssbmod_detuning'] #insert config parameter for the specific nv center here later on. This gives the central MW frequency

#measurement start
m.autoconfig()
m.generate_sequence()
m.measure()
m.save_2D_data()
m.finish()


print 'I still commented the turning on and off of the vector source. See the p7889_2D_measurement.py file. Norbert 23-09-2014'
print 'Changing of the green AOM power with the AWG needs to be implemented as well. Norbert 24-09-2014'