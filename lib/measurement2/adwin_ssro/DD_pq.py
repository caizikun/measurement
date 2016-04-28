"""
Measurement class for measurements with Picoquant TTTR measurements as main loop, specifically, 
to perform Dynamical decoupling sweep-type measurements.

Adapted from pulsar_pq.py

Norbert Kalb 2016

"""
import msvcrt
import numpy as np
import qt
from measurement.lib.measurement2.adwin_ssro.DD_2 import DD
import measurement.lib.measurement2.pq.pq_measurement as pq

reload(pq)

class PQDDMeasurement(DD.MBI_C13,  pq.PQMeasurement ): # pq.PQ_Threaded_Measurement ): #
    mprefix = 'PQ_C13_Measurement'
    
    def __init__(self, name):
        DD.MBI_C13.__init__(self, name)
        self.params['measurement_type'] = self.mprefix

    def autoconfig(self):
        DD.MBI_C13.autoconfig(self)
        pq.PQMeasurement.autoconfig(self)

    def setup(self, **kw):
        DD.MBI_C13.setup(self,**kw)
        pq.PQMeasurement.setup(self,**kw)

    def start_measurement_process(self):
        qt.msleep(.5)
        
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(.5)

    def measurement_process_running(self):
        return self.adwin_process_running()

    def run(self, **kw):
        pq.PQMeasurement.run(self,**kw)
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))

    def stop_measurement_process(self):
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('Total completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))

class PQDDMeasurementIntegrated(pq.PQMeasurementIntegrated, DD.MBI_C13): 
    mprefix = 'PQ_C13_msmt_Integrated'

    def run(self, **kw):
        pq.PQMeasurementIntegrated.run(self,**kw)
    