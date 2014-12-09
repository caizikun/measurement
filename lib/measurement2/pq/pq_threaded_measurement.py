"""
Measurement class for measurements with Picoquant TTTR measurements as main loop
Andreas 2014

"""

import numpy as np
import qt
import measurement.lib.measurement2.measurement as m2
import measurement.lib.measurement2.pq.pq_measurement as pqm
import time
import logging
from multiprocessing import Process, Queue
from measurement.lib.cython.PQ_T2_tools import T2_tools_v2

class DataProcessorThread (Process):
    
    mprefix = 'PQProcessorThread'
    
    def __init__( self, StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, T2_TIMEFACTOR, \
                 MIN_SYNC_BIN, MAX_SYNC_BIN ):

        Process.__init__(self)
        self._StopQueue=StopQueue
        self._FifoQueue=FifoQueue
        self._ProcessedDataQueue=ProcessedDataQueue
        self._T2_WRAPAROUND=T2_WRAPAROUND
        self._T2_TIMEFACTOR=T2_TIMEFACTOR
        self._MIN_SYNC_BIN =MIN_SYNC_BIN
        self._MAX_SYNC_BIN=MAX_SYNC_BIN


    def run(self):

        t_ofl = 0
        t_lastsync = 0
        last_sync_number = 0
        length = 0

        print 'Processor thread started'          

        while True : #The process is stopped when an item is put to the stop queue. Then it will process the remaining queue items and exit.

            if self._StopQueue.empty() == False:
                if self._FifoQueue.empty() == True:  
                    break
                print 'Stopping the Processor... waiting until the queu is empty. Current length ' + str( _FifoQueue.qsize() )
                

            if self._FifoQueue.qsize() > 0:
                try:
                    length, data = self._FifoQueue.get(True, 1)
                    if length > 0:
                        _t, _c, _s = pqm.PQ_decode(data[:length])
                except Exception as E:
                    print 'exception: timeout during get() in the processor queue'
                    print E.args  
                    continue   #  do not process data when getting from the queue has not worked out

                hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools_v2.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                                                self._MIN_SYNC_BIN, self._MAX_SYNC_BIN,
                                                self._T2_WRAPAROUND,self._T2_TIMEFACTOR)

                if newlength > 0:
                    self._ProcessedDataQueue.put( (hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number) )

        print 'Processor thread stopped'            

class DataDumperThread (Process):
    
    mprefix = 'PQDumperThread'
    
    def __init__( self, StopQueue, ProcessedDataQueue, MAX_DATA_LEN ):
       
        Process.__init__(self)
        self._StopQueue = StopQueue
        self._ProcessedDataQueue = ProcessedDataQueue
        self._MAX_DATA_LEN = MAX_DATA_LEN
        print 'Dumper thread generated.'

    def run(self):
        _mObj = pqm.PQMeasurement('DumperThread')
        rawdata_idx = 0
        t_ofl = 0
        t_lastsync = 0
        last_sync_number = 0
        length = 0
        current_dset_length = 0
        count = 0

        print 'Dumper thread started'          

        while True : #The process is stopped when an item is put to the stop queue. Then it will process the remaining queue items and exit.

            if self._StopQueue.empty() == False:
                if self._ProcessedDataQueue.empty() == True:
                    break
                print 'Stopping the Dumper... waiting until the queue is empty. Current length ' + str( _ProcessedDataQueue.qsize() )
                
            if rawdata_idx == 0 or current_dset_length > self._MAX_DATA_LEN :
                
                rawdata_idx += 1              
                current_dset_length = 0

                print 'I create a new dataset.'
                dset_hhtime = _mObj.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                dset_hhchannel = _mObj.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                dset_hhspecial = _mObj.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                dset_hhsynctime = _mObj.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                dset_hhsyncnumber = _mObj.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))         

                _mObj.h5data.flush()

            if self._ProcessedDataQueue.qsize() > 0:
                try:
                    hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                   newlength, t_ofl, t_lastsync, last_sync_number = self._ProcessedDataQueue.get(True, 1)
                except Exception as E:
                    print 'exception: timeout during get() in the dumper queue'
                    print E.args  
                    continue   #  do not process data when getting from the queue has not worked out

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
                    _mObj.h5data.flush()

        print 'Dumper thread stopped'
        print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, last_sync_number
        

class PQ_threaded_Measurement(pqm.PQMeasurement):
    mprefix = 'PQ_threaded_Measurement'

    def run(self, autoconfig=True, setup=True, debug=False):

        TTTR_read_count = self.params['TTTR_read_count']
        T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
        T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
        T2_READMAX = self.PQ_ins.get_T2_READMAX()
        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        MAX_DATA_LEN = self.params['MAX_DATA_LEN']

        StopQueue=Queue()
        FifoQueue=Queue()
        ProcessedDataQueue=Queue()

        print 'I will use several threads! And then crash. TTTR_read_count ', TTTR_read_count

        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        _timer=time.time()
        ii=0
        
        try:
            print 'creating and starting the threads'
            the_processor = DataProcessorThread ( StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, \
                T2_TIMEFACTOR, MIN_SYNC_BIN, MAX_SYNC_BIN )
            the_processor.deamon=True
            the_processor.start()

            the_dumper = DataDumperThread ( StopQueue, ProcessedDataQueue, self.params['MAX_DATA_LEN'])
            the_dumper.deamon=True 
            the_dumper.start()

        except Exception as E:
            print 'Exception in starting and starting the threads'
            print E.args

        while(self.PQ_ins.get_MeasRunning()):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    self.print_measurement_progress()
                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        self.stop_measurement_process()
                        StopQueue.put('stop')
                        break
                _timer=time.time()

            _length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
            if _length > 0:
                FifoQueue.put( (_length, _data) )

        self.PQ_ins.StopMeas()
        
        # Joining the processes means to wait until they have completed, and then deleting the process.
        try:
            the_processor.join()
            the_dumper.join()
        except Exception:
            print 'Exception in terminating the processes'

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()