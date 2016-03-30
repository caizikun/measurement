import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq
import bell
reload(bell)


bs_params = {}
bs_params['MAX_DATA_LEN']        =   int(100e6)
bs_params['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
bs_params['MIN_SYNC_BIN']        =   int(0.0) #5 us #XXX was 5us
bs_params['MAX_SYNC_BIN']        =   int(18.5e-6*1e12) #15 us # XXX was 15us 
bs_params['MIN_HIST_SYNC_BIN']   =   int(0) #XXXX was 5438*1e3
bs_params['MAX_HIST_SYNC_BIN']   =   int(18500*1e3) #XXXXX was 5560*1e3
bs_params['entanglement_marker_number'] = 1
bs_params['measurement_time']    =   24*60*60 #sec = 24H
bs_params['measurement_abort_check_interval']    = 1 #sec
bs_params['wait_for_late_data'] = 0 #in units of measurement_abort_check_interval
bs_params['TTTR_read_count'] = qt.instruments['HH_400'].get_T2_READMAX()
bs_params['TTTR_RepetitiveReadouts'] =  1

bs_params['pulse_start_bin'] = 1000 + 5438*1e3 #XXX shifted by 5438*1e3 for min_hist_sync_bin = 0
bs_params['pulse_stop_bin']  = 3000 + 5438*1e3 #XXX shifted by 5438*1e3 for min_hist_sync_bin = 0
bs_params['tail_start_bin']  = 4500 + 5438*1e3 #XXX shifted by 5438*1e3 for min_hist_sync_bin = 0
bs_params['tail_stop_bin']   = 60000 + 5438*1e3 #XXX shifted by 5438*1e3 for min_hist_sync_bin = 0

bs_params['SP_ref_lt4_start_bin']  = 2800e3   # only SP pulse from LT4
bs_params['SP_ref_lt4_stop_bin']   = 4800e3
bs_params['SP_ref_lt3_start_bin']  = 1500e3   # contains both SP pulses from LT3 & LT4
bs_params['SP_ref_lt3_stop_bin']   = 2700e3   


class Bell_BS(bell.Bell):

    mprefix = 'Bell_BS'

    def autoconfig(self):
        remote_params = self.remote_measurement_helper.get_measurement_params()
        print remote_params
        for k in remote_params:
            self.params[k] = remote_params[k]
        self.remote_measurement_helper.set_data_path(self.h5datapath)
        

    def setup(self):
        pq.PQMeasurement.setup(self)

    def start_measurement_process(self):
        self.remote_measurement_helper.set_is_running(True)

    def print_measurement_progress(self):
        pulse_cts= np.sum(self.hist[self.params['pulse_start_bin'] : self.params['pulse_stop_bin'] ,:])
        tail_cts=np.sum(self.hist[self.params['tail_start_bin']  : self.params['tail_stop_bin']  ,:])
        sp_ref_lt3_length = np.float(self.params['SP_ref_lt3_stop_bin'] - self.params['SP_ref_lt3_start_bin'] )
        sp_ref_lt4_length = np.float(self.params['SP_ref_lt4_stop_bin'] - self.params['SP_ref_lt4_start_bin'] )
        sp_lt4_reflection = np.sum(self.hist[self.params['SP_ref_lt4_start_bin']  : self.params['SP_ref_lt4_stop_bin']  ,:])
        sp_lt3_reflection = np.sum(self.hist[self.params['SP_ref_lt3_start_bin']  : self.params['SP_ref_lt3_stop_bin']  ,:])/sp_ref_lt3_length*sp_ref_lt4_length - sp_lt4_reflection
        self.adwin_ins_lt4.Set_Par(51, int(tail_cts))
        self.adwin_ins_lt4.Set_Par(52, int(pulse_cts))
        self.adwin_ins_lt4.Set_Par(53, int(sp_lt4_reflection))
        self.adwin_ins_lt4.Set_Par(54, int(sp_lt3_reflection))

        self.adwin_ins_lt4.Set_Par(78, int(self.entanglement_markers))

    def measurement_process_running(self):
        return self.remote_measurement_helper.get_is_running()

    def stop_measurement_process(self):
        self.remote_measurement_helper.set_is_running(False)

    def finish(self):
        self.save_instrument_settings_file()
        self.save_params()
        pq.PQMeasurement.finish(self)

Bell_BS.remote_measurement_helper = qt.instruments['remote_measurement_helper']
Bell_BS.adwin_ins_lt4 = qt.instruments['physical_adwin_lt4']

def remote_HH_measurement(name):
    debug=False
    m=Bell_BS(name+qt.instruments['remote_measurement_helper'].get_measurement_name())
    for k in bs_params:
        m.params[k] = bs_params[k]
    m.run(debug=debug, live_filter_on_marker=False)
    print ' This script was running Bell BS v2. '
    m.finish()
    
if __name__ == '__main__':
    remote_HH_measurement('')