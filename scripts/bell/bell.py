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
        qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params['yellow_voltage_AWG'])

    def setup(self):
        pulsar_pq.PQPulsarMeasurement.setup(self, mw=m.params['MW_during_LDE'])     

    def save(self, name='ssro'):
        reps = self.adwin_var('entanglement_events')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps),
                    ('statistics', 10),
                    'entanglement_events',
                    'completed_reps'
                    'total_CR_counts'])

class Bell_BS(pq.PQMeasurement):

    mprefix = 'Bell_BS'
    PQ_ins = qt.instruments['HH_400']
    remote_measurement_helper = qt.instruments['remote_measurement_helper']
    
    def autoconfig(self):
        remote_params = remote_measurement_helper.get_measurement_params()
        print remote_params
        for k in remote_params:
            self.params[k] = remote_params[k]

    def start_measurement_process(self):
        self.remote_measurement_helper.set_is_running(True)

    def measurement_process_running(self):
        return self.remote_measurement_helper.get_is_running()

    def stop_measurement_process(self):
        self.remote_measurement_helper.set_is_running(False)

    def finish(self):
        self.save_instrument_settings_file()
        self.save_params()
        remote_measurement_helper.set_data_path(self.h5datapath)
        pq.PQMeasurement.finish(self)

def remote_HH_measurement(name):

    m=Bell_BS(qt.instruments['remote_measurement_helper'].get_measurement_name())
    m.params['MAX_DATA_LEN']        =   int(100e6)
    m.params['BINSIZE']             =   1  #2**BINSIZE*BASERESOLUTION
    m.params['MIN_SYNC_BIN']        =   0 
    m.params['MAX_SYNC_BIN']        =   1000 
    m.params['measurement_time']    =   1200 #sec
    m.params['measurement_abort_check_interval']    = 1. #sec
    m.run()
    m.finish()

#if __name__ == '__main__':
#    print 'Starting'
#    remote_HH_measurement('test')
#    print 'Finished'