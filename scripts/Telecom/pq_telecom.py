"""
PQ measurement performed for the QTelecom project
"""


import qt
# import numpy as np
import time
# import logging
# from collections import deque
# import measurement.lib.measurement2.measurement as m2
# import measurement.lib.measurement2.pq.pq_measurement as pq
# from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
reload(T2_tools_v3)


import measurement.lib.measurement2.pq.pq_measurement as pq
reload(pq)


def run_HH(name, total_sync_number = 1e8) :   

    m = pq.PQMeasurement(name)

    m.params['total_sync_number'] = total_sync_number
    print 'total sync number to reach : ', total_sync_number

    m.params['MAX_DATA_LEN'] =       int(100e6) ## used to be 100e6
    m.params['BINSIZE'] =            8 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       int(0e6)#1500
    m.params['MAX_SYNC_BIN'] =       int(5.5e6)#3000
    m.params['MIN_HIST_SYNC_BIN'] =  int(0e6)#2600
    m.params['MAX_HIST_SYNC_BIN'] =  int(5.5e6)#2900
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =   m.PQ_ins.get_T2_READMAX() #(=131072)
    m.params['measurement_abort_check_interval']    = 2 #sec
    m.params['wait_for_late_data'] = 2 #in units of measurement_abort_check_interval
    
    m.params['use_live_marker_filter'] = False
    m.params['measurement_time'] = 10000 #1200 #sec
    m.params['count_marker_channel'] = 1

    m.run( )
    m.finish()

if __name__ == '__main__':

    if qt.instruments['lt4_helper'].get_is_running : 
            name_index = int(qt.instruments['lt4_helper'].get_measurement_name())
            total_sync_number = int(qt.instruments['lt4_helper'].get_total_sync_number())

            name = 'HBT_telecom' + str(name_index)
            print '\n', name, '\n'
            run_HBT(name, total_sync_number) 
        
    else : 
        name = 'HBT_telecom' 
        run_HBT(name) 