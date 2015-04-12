"""
Measurement class for measurements with Picoquant TTTR measurements as main loop, specifically, 
to perform Pulsar sweep-type measurements.

Bas Hensen 2014

"""
import msvcrt
import numpy as np
import qt
from measurement.lib.measurement2.adwin_ssro.pulsar_msmt import PulsarMeasurement
import measurement.lib.measurement2.pq.pq_measurement as pq

reload(pq)

class PQPulsarMeasurement(PulsarMeasurement,  pq.PQMeasurement ): # pq.PQ_Threaded_Measurement ): #
    mprefix = 'PQPulsarMeasurement'
    
    def __init__(self, name):
        PulsarMeasurement.__init__(self, name)
        self.params['measurement_type'] = self.mprefix

    def autoconfig(self):
        PulsarMeasurement.autoconfig(self)
        pq.PQMeasurement.autoconfig(self)

    def setup(self, **kw):
        PulsarMeasurement.setup(self,**kw)
        pq.PQMeasurement.setup(self,**kw)

    def start_measurement_process(self):
        qt.msleep(.5)
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(.5)

    def measurement_process_running(self):
        return self.adwin_process_running()

    def run(self, **kw):
        #pq.PQ_Threaded_Measurement.run(self, **kw)
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

class PQPulsarMeasurementIntegrated(pq.PQMeasurementIntegrated, PQPulsarMeasurement): 
    mprefix = 'PQPulsarMeasurementIntegrated'

    def run(self, **kw):
        pq.PQMeasurementIntegrated.run(self,**kw)
    