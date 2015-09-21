"""
Measurement class for measurements with QuTau TTTR measurements as main loop, specifically, 
to perform Pulsar sweep-type measurements.
(Designed to work just like with Picoquant as in pulsar_pq)

Machiel Blok 2015

"""
import msvcrt
import numpy as np
import qt
from measurement.lib.measurement2.adwin_ssro.pulsar_msmt import PulsarMeasurement
import measurement.lib.measurement2.qutau.qutau_measurement as qutau

reload(qutau)

class QuTauPulsarMeasurement(PulsarMeasurement,  qutau.QuTauMeasurement ): 
    mprefix = 'QuTauPulsarMeasurement'
    
    def __init__(self, name):
        PulsarMeasurement.__init__(self, name)
        self.params['measurement_type'] = self.mprefix

    def autoconfig(self):
        PulsarMeasurement.autoconfig(self)
        qutau.QuTauMeasurement.autoconfig(self)

    def setup(self, **kw):
        PulsarMeasurement.setup(self,**kw)
        qutau.QuTauMeasurement.setup(self,**kw)

    def start_measurement_process(self):
        qt.msleep(.5)
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(.5)

    def measurement_process_running(self):
        if not(self.adwin_process_running()):
            qt.msleep(1)
        return self.adwin_process_running()

    def run(self, **kw):
        #pq.PQ_Threaded_Measurement.run(self, **kw)
        qutau.QuTauMeasurement.run(self,**kw)
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))

    def stop_measurement_process(self):
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('Total completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))

class QuTauPulsarMeasurementIntegrated(qutau.QuTauMeasurementIntegrated, QuTauPulsarMeasurement): 
    mprefix = 'QuTauPulsarMeasurementIntegrated'

    def run(self, **kw):
        qutau.QuTauMeasurementIntegrated.run(self,**kw)
    def setup(self, **kw):
        PulsarMeasurement.setup(self,wait_for_awg=True,**kw)
        qutau.QuTauMeasurement.setup(self,**kw)