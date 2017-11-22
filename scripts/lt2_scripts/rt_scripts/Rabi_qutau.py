"""
perform a Rabi oscillation at RT with the QuTau Time tagger.

Valeria Cimini, v.cimini@tudelft.nl 
2016
"""


import os
import qt
import numpy as np
import measurement.lib.measurement2.p7889_2d_measurement
reload(measurement.lib.measurement2.p7889_2d_measurement)
from measurement.lib.measurement2.p7889_2d_measurement import Rabi_p7889

# mw_freq = [2.83854, 2.84266, 2.84403, 2.84506]
# mw_freq = [2.8418, 2.84252, 2.84348, 2.84492, 2.84588, 2.8466] #10-02-2015
# mw_freq = [2.84266, 2.84403, 2.84506]
# mw_freq = [2.84403]
# 2.84403 seems to yield best result

# power = [17, 12, 9, 7]
power = [18]

for k in power:
    AWG.initialize_dc_waveforms()

    #generate measurement
    m=Rabi_p7889('Horst_scan29_NV1_power=%s' % k)

    #Sweep definitions
    m.params['repetitions']=100000
    m.params['pts']= 40
    m.params['nr_of_updates']=500
    m.params['MW_power']=k

    m.params['GreenAOM_pulse_length']=5.*1e-6
    m.params['GreenAOM_power']= 400e-6

    #parameters for postprocessing of the raw data
    m.params['Eval_ROI_start']=1670
    m.params['Eval_ROI_end']=2200


    m.params['MW_pulse_length_start']=(0.0)*1e-6
    m.params['range']=20e-6

    m.params['MW_pulse_length_stop']=m.params['MW_pulse_length_start']+m.params['range']


    m.params['ssbmod_amplitude']=0.9
    m.params['ssbmod_frequency']=43e6


    m.params['mw_frq']=2.83554e9-m.params['ssbmod_frequency'] #in Hz, insert config parameter for the specific nv center here later on. This gives the central MW frequency.
    # 2.85207
    # 2.84649
    # 2.84557
    #measurement start
    m.autoconfig()
    m.generate_sequence()
    m.updated_measurement()
    m.save_2D_data()
    m.finish()
