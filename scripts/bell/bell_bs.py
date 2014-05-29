import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq



bs_params = {}
bs_params['MAX_DATA_LEN']        =   joint_params['MAX_DATA_LEN']
bs_params['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
bs_params['MIN_SYNC_BIN']        =   5000*4 #5 us 
bs_params['MAX_SYNC_BIN']        =   7000*4 #7 us
bs_params['measurement_time']    =   24*60*60 #sec = 24H
bs_params['measurement_abort_check_interval']    = 1 #sec


class Bell_BS(pq.PQMeasurement):

    mprefix = 'Bell_BS'

    def autoconfig(self):
        remote_params = self.remote_measurement_helper.get_measurement_params()
        print remote_params
        for k in remote_params:
            self.params[k] = remote_params[k]

    def start_measurement_process(self):
        self.remote_measurement_helper.set_is_running(True)

    def print_measurement_progress(self):
        pass

    def measurement_process_running(self):
        return self.remote_measurement_helper.get_is_running()

    def stop_measurement_process(self):
        self.remote_measurement_helper.set_is_running(False)

    def finish(self):
        self.save_instrument_settings_file()
        self.save_params()
        self.remote_measurement_helper.set_data_path(self.h5datapath)
        pq.PQMeasurement.finish(self)

Bell_BS.remote_measurement_helper = qt.instruments['remote_measurement_helper']

def remote_HH_measurement(name):

    m=Bell_BS(name+'_'+qt.instruments['remote_measurement_helper'].get_measurement_name())
    for k in bs_params:
        m.params[k] = bs_params[k]
    m.run()
    m.finish()
    
if __name__ == '__main__':
    remote_HH_measurement('test_BS')