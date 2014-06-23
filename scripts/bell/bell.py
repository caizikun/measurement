import qt
import numpy
import measurement.lib.measurement2.measurement as m2
import measurement.lib.measurement2.pq.pq_measurement as pq
from measurement.lib.measurement2.adwin_ssro import pulsar_pq


class Bell(pulsar_pq.PQPulsarMeasurement):
    adwin_process = 'bell'
    mprefix = 'Bell'

    def __init__(self, name):
        pulsar_pq.PQPulsarMeasurement.__init__(self, name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1

    def autoconfig(self, **kw):

        self.params['sequence_wait_time'] = self.joint_params['LDE_attempts_before_CR']*self.joint_params['LDE_element_length']*1e6 + 20

        pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)

        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage(
                        self.params['AWG_SP_power'], controller='sec')
        self.params['RO_voltage_AWG'] = \
                self.E_aom.power_to_voltage(
                        self.params['AWG_RO_power'], controller='sec')
        self.params['yellow_voltage_AWG'] = \
                self.yellow_aom.power_to_voltage(
                        self.params['AWG_yellow_power'], controller='sec')

        #print 'setting AWG SP voltage:', self.params['SP_voltage_AWG']
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])
        if self.params['LDE_yellow_duration'] > 0.:
            qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params['yellow_voltage_AWG'])
        else:
            print self.mprefix, self.name, ': Ignoring yellow'

    
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s readout repetitions' % reps_completed)

    def setup(self, **kw):
        pulsar_pq.PQPulsarMeasurement.setup(self, mw=self.params['MW_during_LDE'],**kw)     

    def save(self, name='ssro'):
        reps = self.adwin_var('entanglement_events')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('CR_hist', 200),
                    ('RO_data', reps),
                    ('statistics', 10),
                    'entanglement_events',
                    'completed_reps',
                    'total_CR_counts'])


#if __name__ == '__main__':
#    print 'Starting'
#    remote_HH_measurement('test')
#    print 'Finished'