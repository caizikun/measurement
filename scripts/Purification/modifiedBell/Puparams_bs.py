import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq
import Pubell
reload(Pubell)


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

# bs_params['SP_ref_lt4_start_bin']  = 2800e3   # only SP pulse from LT4
# bs_params['SP_ref_lt4_stop_bin']   = 4800e3
# bs_params['SP_ref_lt3_start_bin']  = 1500e3   # contains both SP pulses from LT3 & LT4
# bs_params['SP_ref_lt3_stop_bin']   = 2700e3  

