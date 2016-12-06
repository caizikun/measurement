"""
PQ measurement performed for the QTelecom project
"""


# import qt
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


class PQTelecomMeasurement (pq.PQMeasurement) :
    """
    This class is used to make simple PQ measurements, without requiring an adwin process. 
    """
    mprefix = 'QTelecom'

    def __init__(self, name):
        pq.PQMeasurement.__init__(self, name)
        self.params['measurement_type'] = self.mprefix
        self.PQ_ins=qt.instruments['HH_400']
        self.params['do_check_tel1_helper']= False

    def run(self, autoconfig=True, setup=True, debug=False):

        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        rawdata_idx = 1
        t_ofl = 0
        t_lastsync = 0
        last_sync_number = 0
        _length = 0
        
        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        MIN_HIST_SYNC_BIN = np.uint64(self.params['MIN_HIST_SYNC_BIN'])
        MAX_HIST_SYNC_BIN = np.uint64(self.params['MAX_HIST_SYNC_BIN'])
        count_marker_channel = self.params['count_marker_channel']

        TTTR_read_count = self.params['TTTR_read_count']
        TTTR_RepetitiveReadouts = self.params['TTTR_RepetitiveReadouts']
        T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
        T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
        T2_READMAX = self.PQ_ins.get_T2_READMAX()

        print 'run PQ measurement, TTTR_read_count ', TTTR_read_count, ' TTTR_RepetitiveReadouts' , TTTR_RepetitiveReadouts
        # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
        dset_hhtime = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhchannel = self.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhspecial = self.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhsynctime = self.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhsyncnumber = self.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
            (0,), 'u4', maxshape=(None,))

        hist_length = np.uint64(self.params['MAX_HIST_SYNC_BIN'] - self.params['MIN_HIST_SYNC_BIN'])
        self.hist = np.zeros((hist_length,2), dtype='u4')
  
        current_dset_length = 0

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        ##self.start_measurement_process()
        _timer=time.time()
        ii=0
        abort_cond = False

        while(self.PQ_ins.get_MeasRunning() and last_sync_number<self.params['total_sync_number']):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                self._keystroke_check('abort')
                if (self.keystroke('abort')  not in ['q','Q']) and not abort_cond:
                    self.print_measurement_progress()
                    
                else:
                   #Check that all the measurement data has been transsfered from the PQ ins FIFO
                    print 'aborted.'
                    abort_cond = True
                    ii+=1
                    print 'Retreiving late data from PQ, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')
                    if _length == 0 or self.keystroke('abort') in ['x']: 
                        break 
                print 'current sync, dset length:', last_sync_number, current_dset_length
            
                _timer=time.time()

            #_length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
            _length = 0
            _data = np.array([],dtype = 'uint32')
            for j in range(TTTR_RepetitiveReadouts):
                cur_length, cur_data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
                _length += cur_length 
                _data = np.hstack((_data,cur_data[:cur_length]))
            ####XXXXXXXXprint _length
           
            #ll[_length]+=1 #XXX
            if _length > 0:
                if _length == T2_READMAX:
                    logging.warning('TTTR record length is maximum length, \
                            could indicate too low transfer rate resulting in buffer overflow.')

                if self.PQ_ins.get_Flag_FifoFull():
                    print 'Aborting the measurement: Fifo full!'
                    break
                if self.PQ_ins.get_Flag_Overflow():
                    print 'Aborting the measurement: OverflowFlag is high.'
                    break 
                if self.PQ_ins.get_Flag_SyncLost():
                    print 'Aborting the measurement: SyncLost flag is high.'
                    break

                _t, _c, _s = pq.PQ_decode(_data[:_length])
                #print '_s', _s[:5], _c[:5]

                

                hhtime, hhchannel, hhspecial, sync_time, self.hist, sync_number, \
                            newlength, t_ofl, t_lastsync, last_sync_number, counted_markers = \
                            T2_tools_v3.T2_live_filter(_t, _c, _s, self.hist, t_ofl, t_lastsync, last_sync_number,
                            MIN_SYNC_BIN, MAX_SYNC_BIN, MIN_HIST_SYNC_BIN, MAX_HIST_SYNC_BIN, T2_WRAPAROUND,T2_TIMEFACTOR,count_marker_channel)

                if newlength > 0:

                    dset_hhtime.resize((current_dset_length+newlength,))
                    dset_hhchannel.resize((current_dset_length+newlength,))
                    dset_hhspecial.resize((current_dset_length+newlength,))
                    dset_hhsynctime.resize((current_dset_length+newlength,))
                    dset_hhsyncnumber.resize((current_dset_length+newlength,))

                    dset_hhtime[current_dset_length:] = hhtime
                    dset_hhchannel[current_dset_length:] = hhchannel
                    dset_hhspecial[current_dset_length:] = hhspecial
                    dset_hhsynctime[current_dset_length:] = sync_time
                    dset_hhsyncnumber[current_dset_length:] = sync_number

                    current_dset_length += newlength
                    self.h5data.flush()

                if current_dset_length > self.params['MAX_DATA_LEN']:
                    rawdata_idx += 1
                    dset_hhtime = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                    dset_hhchannel = self.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                    dset_hhspecial = self.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                    dset_hhsynctime = self.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                    dset_hhsyncnumber = self.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))         
                    current_dset_length = 0

                    self.h5data.flush()
                if hasattr(self, 'total_sync_number'):
                    if last_sync_number >= self.total_sync_number :
                        break

                #if self.params['do_check_tel1_helper'] : 
                #    if qt.instruments['tel1_measurement_helper'].get_is_running():
                #        print 'Abort measurement, LT3 is not running' 
                #        break

        dset_hist = self.h5data.create_dataset('PQ_hist', data=self.hist, compression='gzip')
        self.h5data.flush()

        self.PQ_ins.StopMeas()
        
        print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, last_sync_number
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()

    def finish(self):
        #self.save_instrument_settings_file()
        self.save_params()
        pq.PQMeasurement.finish(self)


def run_HH(name) :   

    m = PQTelecomMeasurement(name)

    #m.PQ_ins == qt.instruments['HH_400']

    m.params['MAX_DATA_LEN'] =       int(100e6) ## used to be 100e6
    m.params['BINSIZE'] =            8 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       int(2e6)#1500
    m.params['MAX_SYNC_BIN'] =       int(5.5e6)#3000
    m.params['MIN_HIST_SYNC_BIN'] =  int(2e6)#2600
    m.params['MAX_HIST_SYNC_BIN'] =  int(5.5e6)#2900
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



def run_for_sweep_tail(name) :   

    m = PQTelecomMeasurement(name)

    #m.PQ_ins == qt.instruments['HH_400']
    m.params['total_sync_number'] = 1e8
    print 'total sync number to reach : ', m.params['total_sync_number']



    m.params['MAX_DATA_LEN'] =       int(100e6) ## used to be 100e6
    m.params['BINSIZE'] =            8 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       int(2.2e6)#1500
    m.params['MAX_SYNC_BIN'] =       int(3e6)#3000
    m.params['MIN_HIST_SYNC_BIN'] =  int(2e6)#2600
    m.params['MAX_HIST_SYNC_BIN'] =  int(3e6)#2900
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

    m.params['total_sync_number'] = 50000*250
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

    seq = 'TPQI'

    if seq =='HBT':
        if qt.instruments['tel1_measurement_helper'].get_is_running : 
            name_index = int(qt.instruments['tel1_measurement_helper'].get_measurement_name())
            name = 'HBT_telecom' + str(name_index)
            print '\n', name, '\n'
        else : 
            name = 'HBT_telecom' 
        run_HBT(name) 
    elif seq =='TPQI':
        if qt.instruments['tel1_measurement_helper'].get_is_running : 
            name_index = int(qt.instruments['tel1_measurement_helper'].get_measurement_name())
            name = 'TPQI_telecom' + str(name_index)
            print '\n', name, '\n'
        else : 
            name = 'TPQI_telecom' 
        run_HBT(name) 

    elif seq == 'tail' :
        run_for_sweep_tail('tail_telecom_200mW_9d05')

    #elif seq == 'HOM_test' :
