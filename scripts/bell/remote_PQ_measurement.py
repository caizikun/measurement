"""
LT3 script for adwin ssro.
"""
import numpy as np
import qt

import measurement.lib.measurement2.measurement as m2
reload(m2)
import measurement.lib.measurement2.pq.pq_measurement as pq
reload(pq)


class Remote_PQ_Measurement(pq.PQMeasurement):
    mprefix = 'Remote_PQ_Measurement'

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

Remote_PQ_Measurement.PQ_ins = qt.instruments['HH_400']
Remote_PQ_Measurement.remote_measurement_helper = qt.instruments['remote_measurement_helper']


def remote_HH_measurement(name):

    m=Remote_PQ_Measurement(name)
    m.params['MAX_DATA_LEN']        =   int(100e6)
    m.params['BINSIZE']             =   1  #2**BINSIZE*BASERESOLUTION
    m.params['MIN_SYNC_BIN']        =   0 
    m.params['MAX_SYNC_BIN']        =   1000 
    m.params['measurement_time']    =   1200 #sec
    m.params['measurement_abort_check_interval']    = 1. #sec
    m.run()
    m.finish()

if __name__ == '__main__':
    print 'Starting'
    remote_HH_measurement('test')
    print 'Finished'