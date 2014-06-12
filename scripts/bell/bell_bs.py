import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq
import params
reload(params)

class Bell_BS(pq.PQMeasurement):

    mprefix = 'Bell_BS'

    def autoconfig(self):
        remote_params = self.remote_measurement_helper.get_measurement_params()
        print remote_params
        for k in remote_params:
            self.params[k] = remote_params[k]
        self.remote_measurement_helper.set_data_path(self.h5datapath)

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
        pq.PQMeasurement.finish(self)

Bell_BS.remote_measurement_helper = qt.instruments['remote_measurement_helper']

def remote_HH_measurement(name):
    debug=False
    m=Bell_BS(name+'_'+qt.instruments['remote_measurement_helper'].get_measurement_name())
    for k in params.bs_params:
        m.params[k] = params.bs_params[k]
    m.run(debug=debug)
    m.finish()
    
if __name__ == '__main__':
    remote_HH_measurement('tpqi_parallel_BS')