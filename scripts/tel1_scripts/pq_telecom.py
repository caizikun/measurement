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


def run_HH(name) :   

    m = pq.PQMeasurement(name)

    m.PQ_ins = qt.instruments['TH_260N']

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

    #m.params['use_live_marker_filter']=False

    # m.PQ_ins.start_T2_mode()
    # m.PQ_ins.calibrate()
    #m.PQ_ins.StartMeas(int(m.params['measurement_time'] * 1e3))
    #for i in np.arange(30):
    #    print i
    #    cur_length, cur_data = m.PQ_ins.get_TTTR_Data(count = int(512*200))
    #    print cur_length
    #    qt.msleep(1)

    m.run( )
    m.finish()
    #m.PQ_ins.StopMeas()



def run_for_sweep_tail(name) :   

    m = PQTelecomMeasurement(name)

    #m.PQ_ins == qt.instruments['HH_400']
    m.params['total_sync_number'] = 1e8
    print 'total sync number to reach : ', m.params['total_sync_number']



    m.params['MAX_DATA_LEN'] =       int(100e6) ## used to be 100e6
    m.params['BINSIZE'] =            8 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       int(2.2e6)#1500
    m.params['MAX_SYNC_BIN'] =       int(3.e6)#3000
    m.params['MIN_HIST_SYNC_BIN'] =  int(2.2e6)#2600
    m.params['MAX_HIST_SYNC_BIN'] =  int(3.e6)#2900
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =   m.PQ_ins.get_T2_READMAX() #(=131072)
    m.params['measurement_abort_check_interval']    = 2 #sec
    m.params['wait_for_late_data'] = 2 #in units of measurement_abort_check_interval
    
    m.params['use_live_marker_filter'] = False
    m.params['measurement_time'] = 10000 #1200 #sec
    m.params['count_marker_channel'] = 1


    #m.params['use_live_marker_filter']=False

    m.PQ_ins.start_T2_mode()
    m.PQ_ins.calibrate()
    #m.PQ_ins.StartMeas(int(m.params['measurement_time'] * 1e3))
    #for i in np.arange(30):
    #    print i
    #    cur_length, cur_data = m.PQ_ins.get_TTTR_Data(count = int(512*200))
    #    print cur_length
    #    qt.msleep(1)

    m.run( )
    m.finish()
    #m.PQ_ins.StopMeas()


def run_HBT(name) :   

    m = PQTelecomMeasurement(name)

    m.params['total_sync_number'] = 50000*50
    print 'total sync number to reach : ', m.params['total_sync_number']

    m.params['MAX_DATA_LEN'] =       int(100e6) ## used to be 100e6
    m.params['BINSIZE'] =            8 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       int(2e6)#1500
    m.params['MAX_SYNC_BIN'] =       int(5.7e6)#3000
    m.params['MIN_HIST_SYNC_BIN'] =  int(2e6)#2600
    m.params['MAX_HIST_SYNC_BIN'] =  int(5.7e6)#2900
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =   m.PQ_ins.get_T2_READMAX() #(=131072)
    m.params['measurement_abort_check_interval']    = 2 #sec
    m.params['wait_for_late_data'] = 2 #in units of measurement_abort_check_interval
    
    m.params['use_live_marker_filter'] = False
    m.params['measurement_time'] = 10000 #1200 #sec
    m.params['count_marker_channel'] = 1

    m.params['do_check_tel1_helper'] = True

    #m.params['use_live_marker_filter']=False

    m.PQ_ins.start_T2_mode()
    m.PQ_ins.calibrate()
    #m.PQ_ins.StartMeas(int(m.params['measurement_time'] * 1e3))
    #for i in np.arange(30):
    #    print i
    #    cur_length, cur_data = m.PQ_ins.get_TTTR_Data(count = int(512*200))
    #    print cur_length
    #    qt.msleep(1)

    m.run( )
    m.finish()
    #m.PQ_ins.StopMeas(



if __name__ == '__main__':
    run_HH('getTHdata')
    # seq = 'TPQI'
    # if seq =='HBT':
    #     if qt.instruments['lt4_helper'].get_is_running : 
    #         name_index = int(qt.instruments['lt4_helper'].get_measurement_name())
    #         name = 'HBT_telecom' + str(name_index)
    #         print '\n', name, '\n'
    #     else : 
    #         name = 'HBT_telecom' 
    #     run_HBT(name) 
    # elif seq =='TPQI':
    #     if qt.instruments['lt4_helper'].get_is_running : 
    #         name_index = int(qt.instruments['lt4_helper'].get_measurement_name())
    #         name = 'TPQI_telecom' + str(name_index)
    #         print '\n', name, '\n'
    #     else : 
    #         name = 'TPQI_telecom' 
    #     run_HBT(name) 

    # elif seq == 'tail' :
    #     run_for_sweep_tail('tail_LT3_SIL3')

    #elif seq == 'HOM_test' :
