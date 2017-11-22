import numpy as np
import measurement.lib.measurement2.pq.pq_measurement as pq
import qt
#from measurement.lib.cython.PQ_T2_tools.T2_tools_src import T2_tools_test
#from measurement.lib.cython.PQ_T2_tools.T2_tools_src import T2_tools_bell
#reload(T2_tools_bell)
#reload(T2_tools_test)
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
reload(T2_tools_v3)
import time

try:
    print len(pq_test_data)
except NameError:
    PQ_test_ins = qt.instruments.create('PQ_test_ins', 'PQ_test_instrument')
    PQ_test_ins.set_data_fp(r'D:\measuring\data\20141212\091459_PQPulsarMeasurement_FastSSROCalib_Pippin_LT3\091459_PQPulsarMeasurement_FastSSROCalib_Pippin_LT3.hdf5')
    PQ_test_ins.start_T2_mode()
    PQ_test_ins.StartMeas(10)

    pq_test_data = PQ_test_ins.get_TTTR_Data()[1]
    print len(pq_test_data)

_t, _c, _s = pq.PQ_decode(pq_test_data)
MIN_SYNC_BIN = np.uint64(0)
MAX_SYNC_BIN = np.uint64(10000)
MIN_HIST_SYNC_BIN = np.uint64(2000)
MAX_HIST_SYNC_BIN = np.uint64(7000)
T2_WRAPAROUND = np.uint64(PQ_test_ins.get_T2_WRAPAROUND())
T2_TIMEFACTOR = np.uint64(PQ_test_ins.get_T2_TIMEFACTOR())
hist_length = np.uint64(MAX_HIST_SYNC_BIN - MIN_HIST_SYNC_BIN)
hist = np.zeros((hist_length,2), dtype='u4')
t_ofl = np.uint64(0)
t_lastsync = np.uint64(0)
last_sync_number = np.uint32(0)
count_marker_channel = 1

t1 = time.clock()
for i in range(100):
    hhtime, hhchannel, hhspecial, sync_time, hist, sync_number,\
            newlength, t_ofl, t_lastsync, last_sync_number, new_entanglement_markers = \
            T2_tools_v3.T2_live_filter(_t, _c, _s, hist, t_ofl, t_lastsync, last_sync_number,\
            MIN_SYNC_BIN, MAX_SYNC_BIN, MIN_HIST_SYNC_BIN, MAX_HIST_SYNC_BIN, T2_WRAPAROUND,T2_TIMEFACTOR,count_marker_channel)

    #hhtime, hhchannel, hhspecial, sync_time, sync_number, \
    #                    newlength, t_ofl, t_lastsync, last_sync_number, new_entanglement_markers = \
    #                    T2_tools_bell.Bell_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
    #                                            MIN_SYNC_BIN, MAX_SYNC_BIN,
    #                                            T2_WRAPAROUND,T2_TIMEFACTOR, count_marker_channel)


t2 = time.clock()

print t2-t1
