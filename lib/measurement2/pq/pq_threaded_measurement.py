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

class DataProcessorThread (pqm.PQMeasurement, Process):
    
    mprefix = 'PQProcessorThread'
    
    def __init__( self, StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, T2_TIMEFACTOR, \
                T2_READMAX, MIN_SYNC_BIN, MAX_SYNC_BIN, TTTR_read_count, MAX_DATA_LEN ):

        #print 'Generating the processor.'
        Process.__init__(self)
        self._StopQueue=StopQueue
        self._FifoQueue=FifoQueue
        self._ProcessedDataQueue=ProcessedDataQueue
        self._T2_WRAPAROUND=T2_WRAPAROUND
        self._T2_TIMEFACTOR=T2_TIMEFACTOR
        self._T2_READMAX=T2_READMAX
        self._MIN_SYNC_BIN =MIN_SYNC_BIN
        self._MAX_SYNC_BIN=MAX_SYNC_BIN
        self._TTTR_read_count=TTTR_read_count
        self._MAX_DATA_LEN = MAX_DATA_LEN
        self._mObj = pqm.PQMeasurement(name=self.mprefix)
        #print 'processor generated'

    def run(self):

        #t_ofl = 0
        #t_lastsync = 0
        #last_sync_number = 0
        #length = 0
        #count = 0

        print 'Processor thread started'          

        while False : #The process is stopped when an item is put to the stop queue. Then it will process the remaining queue items and exit.
            break

            if self._StopQueue.empty() == False and self._FifoQueue.qsize() == 0 :
                print 'Stopping the Processor...'
                break

            count+=1
            if self._FifoQueue.qsize() > 0:
                print 'Starting to process block number ' + str(count)
                try:
                    length, data = self._FifoQueue.get(True, 1)
                    if length > 0:
                        _t, _c, _s = PQ_decode(data[:length])
                except Exception as E:
                    print 'exception: timeout during get() in the processor queue'
                    print E.args  
                    continue   #  do not process data when getting from the queue has not worked out

                #hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                #    newlength, t_ofl, t_lastsync, last_sync_number = \
                #        T2_tools_v2.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                #                                self._MIN_SYNC_BIN, self._MAX_SYNC_BIN,
                #                                self._T2_WRAPAROUND,self._T2_TIMEFACTOR)

                if newlength > 0:
                    ProcessedDataQueue.put( (hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number) )
                    

class DataDumperThread (pqm.PQMeasurement, Process):
    
    mprefix = 'PQDumperThread'
    
    def __init__( self, StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, T2_TIMEFACTOR, \
                T2_READMAX, MIN_SYNC_BIN, MAX_SYNC_BIN, TTTR_read_count, MAX_DATA_LEN ):
       
        Process.__init__(self)
        self._StopQueue=StopQueue
        self._FifoQueue=FifoQueue
        self._ProcessedDataQueue=ProcessedDataQueue
        self._T2_WRAPAROUND=T2_WRAPAROUND
        self._T2_TIMEFACTOR=T2_TIMEFACTOR
        self._T2_READMAX=T2_READMAX
        self._MIN_SYNC_BIN =MIN_SYNC_BIN
        self._MAX_SYNC_BIN=MAX_SYNC_BIN
        self._TTTR_read_count=TTTR_read_count
        self._MAX_DATA_LEN = MAX_DATA_LEN
        self._mObj = pqm.PQMeasurement(name=self.mprefix)
        print 'Dumper generated.'

    def run(self):

        rawdata_idx = 0
        t_ofl = 0
        t_lastsync = 0
        last_sync_number = 0
        length = 0
        current_dset_length = 0
        count = 0

        print 'Dumper thread started'          

        while True : #The process is stopped when an item is put to the stop queue. Then it will process the remaining queue items and exit.

            if self._StopQueue.empty() == False and self._FifoQueue.qsize() == 0 :
                print 'Stopping the Processor...'
                break

            if rawdata_idx == 0 or current_dset_length > self._MAX_DATA_LEN :
                
                rawdata_idx += 1              
                current_dset_length = 0

                print 'I create a new dataset.'
                dset_hhtime = self.mObj.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                dset_hhchannel = self.mObj.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                dset_hhspecial = self.mObj.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                dset_hhsynctime = self.mObj.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                dset_hhsyncnumber = self.mObj.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))         

                self.mObj.h5data.flush()


            count+=1
            if self._FifoQueue.qsize() > 0:
                print 'Starting to process block number ' + str(count)
                try:
                    hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number = self._FifoQueue.get(True, 1)
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
                    self.mObj.h5data.flush()

        print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, last_sync_number
        

class PQ_threaded_Measurement(pqm.PQMeasurement):
    mprefix = 'PQ_threaded_Measurement'

    def run(self, autoconfig=True, setup=True, debug=False):
        
        PQM=PQMeasurement();
        if self.setup:
            PQM.setup()

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
            print 'creating the threads'
            the_processor = DataProcessorThread ( StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, \
                T2_TIMEFACTOR, T2_READMAX, MIN_SYNC_BIN, MAX_SYNC_BIN, TTTR_read_count, MAX_DATA_LEN )
            #the_dumper = DataDumperThread ( StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, \
            #    T2_TIMEFACTOR, T2_READMAX, MIN_SYNC_BIN, MAX_SYNC_BIN, TTTR_read_count, self.params['MAX_DATA_LEN'])
        except Exception as E:
            print 'exception in generating the threads'
            print E.args
        try:
            print 'starting the threads'
            the_processor.deamon=True 
            the_processor.start()
            #the_dumper.start

        except Exception as E:
            print 'exception in starting the threads'
            print E.args

        print 'starting the measurement'
        time.sleep(3)

        while(self.PQ_ins.get_MeasRunning()):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    self.print_measurement_progress()
                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        self.stop_measurement_process()
                        StopQueue.put('stop')
                else:
                   #Check that all the measurement data has been transferred from the PQ into the PCs memory
                    ii+=1
                    print 'Retreiving late data from PQ, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')
                    if _length == 0 or self.keystroke('abort') in ['x']: 
                        break             
                _timer=time.time()

            _length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
            if _length > 0:
                FifoQueue.put( (_length, _data) )

        self.PQ_ins.StopMeas()
        #self.h5data.create_dataset('PQ_hist_lengths', data=ll, compression='gzip')#XXX
        #self.h5data.flush()#XXX
        
        # Joining the processes means to wait until they have completed, and then deleting the process.
        #try:
        #    the_processor.join()
        #    the_dumper.join()
        #except Exception:
        #    pass

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()