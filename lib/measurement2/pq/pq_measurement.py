"""
Measurement class for measurements with Picoquant TTTR measurements as main loop
Bas Hensen 2014

"""

import numpy as np
import qt, time, logging, os
import measurement.lib.measurement2.measurement as m2
from multiprocessing import Process, Queue
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
import hdf5_data as h5

class PQMeasurement(m2.Measurement):

    mprefix = 'PQMeasurement'
    
    def autoconfig(self):
        pass

    def setup(self, do_calibrate = True, debug = False, **kw):
        if debug:
            return
        if self.PQ_ins.OpenDevice():
            self.PQ_ins.start_T2_mode()
            if do_calibrate and hasattr(self.PQ_ins,'calibrate'):
                self.PQ_ins.calibrate()
            self.PQ_ins.set_Binning(self.params['BINSIZE'])
        else:
            raise(Exception('Picoquant instrument '+self.PQ_ins.get_name()+ ' cannot be opened: Close the gui?'))

    def start_measurement_process(self):
        pass

    def measurement_process_running(self):
        return True

    def stop_measurement_process(self):
        pass

    def print_measurement_progress(self):
        pass

    def run_debug(self):
        self.start_keystroke_monitor('abort',timer=False)
        self.start_measurement_process()
        _timer=time.time()
        _timer0=time.time()
        hist_length = np.uint64(self.params['MAX_HIST_SYNC_BIN'] - self.params['MIN_HIST_SYNC_BIN'])
        self.hist = np.zeros((hist_length,2), dtype='u4')
        while True:
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if not self.measurement_process_running():
                    break
                self._keystroke_check('abort')
                if self.keystroke('abort') in ['q','Q']:
                    print 'aborted.'
                    self.stop_keystroke_monitor('abort')
                    break
                    
                self.print_measurement_progress()
                _timer=time.time()
            if (time.time()-_timer0)>self.params['measurement_time']:
                break

        self.stop_measurement_process()

    def run(self, autoconfig=True, setup=True, debug=False,  live_filter_on_marker=False):

        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        wait_for_late_data= self.params['wait_for_late_data'] if 'wait_for_late_data' in self.params else 1e8 


        rawdata_idx = 1
        t_ofl = np.uint64(0)
        t_lastsync = np.uint64(0)
        self.last_sync_number = np.uint32(0)
        
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

        self.hist_length = np.uint64(self.params['MAX_HIST_SYNC_BIN'] - self.params['MIN_HIST_SYNC_BIN'])
        self.hist = np.zeros((self.hist_length,2), dtype='u4')
  
        current_dset_length = 0

        self.total_counted_markers = 0

        if live_filter_on_marker:
            _queue_hhtime      = deque([],self.params['live_filter_queue_length'])
            _queue_sync_time   = deque([],self.params['live_filter_queue_length'])
            _queue_hhchannel   = deque([],self.params['live_filter_queue_length'])
            _queue_hhspecial   = deque([],self.params['live_filter_queue_length'])
            _queue_sync_number = deque([],self.params['live_filter_queue_length'])
            _queue_newlength   = deque([],self.params['live_filter_queue_length'])

        self.measurement_progress_first_run = True

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        _timer=time.time()
        ii=0

        while(self.PQ_ins.get_MeasRunning()):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    self.print_measurement_progress()

                    self.live_update_callback()

                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        self.stop_measurement_process()
                else:
                   #Check that all the measurement data has been transsfered from the PQ ins FIFO
                    ii+=1
                    print 'Retreiving late data from PQ, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')
                    if self.PQ_ins_params[PQ_ins_key]._length == 0 or self.keystroke('abort') in ['x'] or ii>wait_for_late_data: 
                        break 
                print 'current sync,marker_events, dset length:', self.last_sync_number,self.total_counted_markers, current_dset_length

                _timer=time.time()

            #self.PQ_ins_params[PQ_ins_key]._length, self.PQ_ins_params[PQ_ins_key]._data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
            self.PQ_ins_params[PQ_ins_key]._length = 0
            self.PQ_ins_params[PQ_ins_key]._data = np.array([],dtype = 'uint32')
            for j in range(TTTR_RepetitiveReadouts):
                cur_length, cur_data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
                self.PQ_ins_params[PQ_ins_key]._length += cur_length 
                self.PQ_ins_params[PQ_ins_key]._data = np.hstack((self.PQ_ins_params[PQ_ins_key]._data,cur_data[:cur_length]))
           
            #ll[self.PQ_ins_params[PQ_ins_key]._length]+=1 #XXX
            if self.PQ_ins_params[PQ_ins_key]._length > 0:
                if self.PQ_ins_params[PQ_ins_key]._length == T2_READMAX or self.PQ_ins_params[PQ_ins_key]._length ==  TTTR_RepetitiveReadouts * TTTR_read_count:
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

                _t, _c, _s = PQ_decode(self.PQ_ins_params[PQ_ins_key]._data[:self.PQ_ins_params[PQ_ins_key]._length])

                

                hhtime, hhchannel, hhspecial, sync_time, self.hist, sync_number, \
                            newlength, t_ofl, t_lastsync, self.last_sync_number, counted_markers = \
                            T2_tools_v3.T2_live_filter(_t, _c, _s, self.hist, t_ofl, t_lastsync, self.last_sync_number,
                            MIN_SYNC_BIN, MAX_SYNC_BIN, MIN_HIST_SYNC_BIN, MAX_HIST_SYNC_BIN, T2_WRAPAROUND,T2_TIMEFACTOR,count_marker_channel)
                
                if newlength > 0:

                    if counted_markers == 0 and live_filter_on_marker:
                        _queue_hhtime.append(hhtime)
                        _queue_sync_time.append(sync_time)    
                        _queue_hhchannel.append(hhchannel)  
                        _queue_hhspecial.append(hhspecial)  
                        _queue_sync_number.append(sync_number)  
                        _queue_newlength.append(newlength)   
                    else:
                        self.total_counted_markers += counted_markers
                        if live_filter_on_marker:
                            for i in range(len(_queue_newlength)):
                                prev_newlength = _queue_newlength.popleft()
                                dset_hhtime.resize((current_dset_length+prev_newlength,))
                                dset_hhchannel.resize((current_dset_length+prev_newlength,))
                                dset_hhspecial.resize((current_dset_length+prev_newlength,))
                                dset_hhsynctime.resize((current_dset_length+prev_newlength,))
                                dset_hhsyncnumber.resize((current_dset_length+prev_newlength,))

                                dset_hhtime[current_dset_length:] = _queue_hhtime.popleft()
                                dset_hhchannel[current_dset_length:] = _queue_hhchannel.popleft()
                                dset_hhspecial[current_dset_length:] = _queue_hhspecial.popleft()
                                dset_hhsynctime[current_dset_length:] = _queue_sync_time.popleft()
                                dset_hhsyncnumber[current_dset_length:] = _queue_sync_number.popleft()

                                current_dset_length += prev_newlength

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

        dset_hist = self.h5data.create_dataset('PQ_hist', data=self.hist, compression='gzip')
        self.h5data.flush()

        self.PQ_ins.StopMeas()
        
        print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, self.last_sync_number
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()
        

    def live_update_callback(self):
        ''' This is called when the measurement progress is printed, so that other stuff can be added'''
        
        pass

class PQins(object):
    pass

class PQMultiDeviceMeasurement(PQMeasurement):

    mprefix = 'PQMultiDeviceMeasurement'

    def setup(self, do_calibrate = True, debug = False, **kw):

        if debug:
            return
        
        selected_ins = self.params['selected_PQ_ins']

        if not(isinstance(selected_ins,list)) and selected_ins == None:
            self.PQ_instruments = self.available_PQ_ins
        else:
            self.PQ_instruments = {key: self.available_PQ_ins[key] for key in selected_ins}

        for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():    
            if PQ_ins.OpenDevice():
                PQ_ins.start_T2_mode()
                if do_calibrate and hasattr(PQ_ins,'calibrate'):
                    PQ_ins.calibrate()
                PQ_ins.set_Binning(self.params[PQ_ins_key]['BINSIZE'])
            else:
                raise(Exception('Picoquant instrument '+PQ_ins.get_name()+ ' cannot be opened: Close the gui?'))

    def run(self, autoconfig=True, setup=True, debug=False,  live_filter_on_marker=False):

        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        wait_for_late_data= self.params['wait_for_late_data'] if self.params.parameters.has_key('wait_for_late_data') else 1e8 

        num_PQ = len(self.PQ_instruments)

        self.PQ_ins_params = {}
        for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():
            self.PQ_ins_params[PQ_ins_key] = PQins()
            self.PQ_ins_params[PQ_ins_key].rawdata_idx = 1
            self.PQ_ins_params[PQ_ins_key].t_ofl = np.uint64(0)
            self.PQ_ins_params[PQ_ins_key].t_lastsync = np.uint64(0)
            self.PQ_ins_params[PQ_ins_key].last_sync_number = np.uint32(0)
            
            
            self.PQ_ins_params[PQ_ins_key].MIN_SYNC_BIN = np.uint64(self.params[PQ_ins_key]['MIN_SYNC_BIN'])
            self.PQ_ins_params[PQ_ins_key].MAX_SYNC_BIN = np.uint64(self.params[PQ_ins_key]['MAX_SYNC_BIN'])
            self.PQ_ins_params[PQ_ins_key].MIN_HIST_SYNC_BIN = np.uint64(self.params[PQ_ins_key]['MIN_HIST_SYNC_BIN'])
            self.PQ_ins_params[PQ_ins_key].MAX_HIST_SYNC_BIN = np.uint64(self.params[PQ_ins_key]['MAX_HIST_SYNC_BIN'])
            self.PQ_ins_params[PQ_ins_key].count_marker_channel = self.params[PQ_ins_key]['count_marker_channel']
            self.PQ_ins_params[PQ_ins_key].TTTR_read_count = self.params[PQ_ins_key]['TTTR_read_count']
            self.PQ_ins_params[PQ_ins_key].T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
            self.PQ_ins_params[PQ_ins_key].T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
            self.PQ_ins_params[PQ_ins_key].T2_READMAX = self.PQ_ins.get_T2_READMAX()

            print PQ_ins_key + ' run PQ measurement, TTTR_read_count ', self.PQ_ins_params[PQ_ins_key].TTTR_read_count, ' TTTR_RepetitiveReadouts' , self.params['TTTR_RepetitiveReadouts']
            # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
            rawdata_idx = self.PQ_ins_params[PQ_ins_key].rawdata_idx

            pref = (PQ_ins_key + '/') if num_PQ !=  1 else ''

            self.PQ_ins_params[PQ_ins_key].dset_hhtime = self.h5data.create_dataset(pref + 'PQ_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            self.PQ_ins_params[PQ_ins_key].dset_hhchannel = self.h5data.create_dataset(pref + 'PQ_channel-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            self.PQ_ins_params[PQ_ins_key].dset_hhspecial = self.h5data.create_dataset(pref + 'PQ_special-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            self.PQ_ins_params[PQ_ins_key].dset_hhsynctime = self.h5data.create_dataset(pref + 'PQ_sync_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            self.PQ_ins_params[PQ_ins_key].dset_hhsyncnumber = self.h5data.create_dataset(pref + 'PQ_sync_number-{}'.format(rawdata_idx), 
                (0,), 'u4', maxshape=(None,))

            self.PQ_ins_params[PQ_ins_key].hist_length = np.uint64(self.params[PQ_ins_key]['MAX_HIST_SYNC_BIN'] - self.params[PQ_ins_key]['MIN_HIST_SYNC_BIN'])
            self.PQ_ins_params[PQ_ins_key].hist = np.zeros((self.PQ_ins_params[PQ_ins_key].hist_length,2), dtype='u4')
      
            self.PQ_ins_params[PQ_ins_key].current_dset_length = 0

            self.PQ_ins_params[PQ_ins_key].total_counted_markers = 0

            if live_filter_on_marker:
                self.PQ_ins_params[PQ_ins_key]._queue_hhtime      = deque([],self.params[PQ_ins_key]['live_filter_queue_length'])
                self.PQ_ins_params[PQ_ins_key]._queue_sync_time   = deque([],self.params[PQ_ins_key]['live_filter_queue_length'])
                self.PQ_ins_params[PQ_ins_key]._queue_hhchannel   = deque([],self.params[PQ_ins_key]['live_filter_queue_length'])
                self.PQ_ins_params[PQ_ins_key]._queue_hhspecial   = deque([],self.params[PQ_ins_key]['live_filter_queue_length'])
                self.PQ_ins_params[PQ_ins_key]._queue_sync_number = deque([],self.params[PQ_ins_key]['live_filter_queue_length'])
                self.PQ_ins_params[PQ_ins_key]._queue_newlength   = deque([],self.params[PQ_ins_key]['live_filter_queue_length'])

            PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
            
        self.measurement_progress_first_run = True

        self.start_keystroke_monitor('abort',timer=False)

        self.start_measurement_process()
        _timer=time.time()
        ii=0

        while(np.any([PQ_ins.get_MeasRunning() for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems()])):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    self.print_measurement_progress()
                    self.live_update_callback()

                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        self.stop_measurement_process()
                else:
                   #Check that all the measurement data has been transsfered from the PQ ins FIFO
                    ii+=1
                    print 'Retreiving late data from PQ, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')

                    all_finished = not(np.any([self.PQ_ins_params[PQ_ins_key]._length for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems()]))

                    if all_finished == True or self.keystroke('abort') in ['x'] or ii>wait_for_late_data: 
                        break 
                
                for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():
                    print PQ_ins_key + ' current sync,marker_events, dset length:', self.PQ_ins_params[PQ_ins_key].last_sync_number, \
                    self.PQ_ins_params[PQ_ins_key].total_counted_markers, self.PQ_ins_params[PQ_ins_key].current_dset_length

                _timer=time.time()

            for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():

                self.PQ_ins_params[PQ_ins_key]._length = 0
                self.PQ_ins_params[PQ_ins_key]._data = np.array([],dtype = 'uint32')

            for j in range(self.params['TTTR_RepetitiveReadouts']):
                for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():
                    cur_length, cur_data = PQ_ins.get_TTTR_Data(count = self.PQ_ins_params[PQ_ins_key].TTTR_read_count)
                    self.PQ_ins_params[PQ_ins_key]._length += cur_length 
                    self.PQ_ins_params[PQ_ins_key]._data = np.hstack((self.PQ_ins_params[PQ_ins_key]._data,cur_data[:cur_length]))
            
            for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():

                if self.PQ_ins_params[PQ_ins_key]._length > 0:
                    if self.PQ_ins_params[PQ_ins_key]._length ==  self.params['TTTR_RepetitiveReadouts'] * self.PQ_ins_params[PQ_ins_key].TTTR_read_count:
                        logging.warning('TTTR record length is maximum length, \
                                could indicate too low transfer rate resulting in buffer overflow.')

                    if PQ_ins.get_Flag_FifoFull():
                        print 'Aborting the measurement: Fifo full!'
                        break
                    if PQ_ins.get_Flag_Overflow():
                        print 'Aborting the measurement: OverflowFlag is high.'
                        break 
                    if PQ_ins.get_Flag_SyncLost():
                        print 'Aborting the measurement: SyncLost flag is high.'
                        break

                    _t, _c, _s = PQ_decode(self.PQ_ins_params[PQ_ins_key]._data[:self.PQ_ins_params[PQ_ins_key]._length])

                    hhtime, hhchannel, hhspecial, sync_time, self.PQ_ins_params[PQ_ins_key].hist, sync_number, \
                                newlength, self.PQ_ins_params[PQ_ins_key].t_ofl, self.PQ_ins_params[PQ_ins_key].t_lastsync, self.PQ_ins_params[PQ_ins_key].last_sync_number, counted_markers = \
                                T2_tools_v3.T2_live_filter(_t, _c, _s, self.PQ_ins_params[PQ_ins_key].hist, self.PQ_ins_params[PQ_ins_key].t_ofl,\
                                self.PQ_ins_params[PQ_ins_key].t_lastsync, self.PQ_ins_params[PQ_ins_key].last_sync_number,
                                self.PQ_ins_params[PQ_ins_key].MIN_SYNC_BIN, self.PQ_ins_params[PQ_ins_key].MAX_SYNC_BIN, self.PQ_ins_params[PQ_ins_key].MIN_HIST_SYNC_BIN,\
                                self.PQ_ins_params[PQ_ins_key].MAX_HIST_SYNC_BIN, self.PQ_ins_params[PQ_ins_key].T2_WRAPAROUND,\
                                self.PQ_ins_params[PQ_ins_key].T2_TIMEFACTOR,self.PQ_ins_params[PQ_ins_key].count_marker_channel)
                    
                    if newlength > 0:

                        if counted_markers == 0 and live_filter_on_marker:
                            self.PQ_ins_params[PQ_ins_key]._queue_hhtime.append(hhtime)
                            self.PQ_ins_params[PQ_ins_key]._queue_sync_time.append(sync_time)    
                            self.PQ_ins_params[PQ_ins_key]._queue_hhchannel.append(hhchannel)  
                            self.PQ_ins_params[PQ_ins_key]._queue_hhspecial.append(hhspecial)  
                            self.PQ_ins_params[PQ_ins_key]._queue_sync_number.append(sync_number)  
                            self.PQ_ins_params[PQ_ins_key]._queue_newlength.append(newlength)   
                        else:
                            self.PQ_ins_params[PQ_ins_key].total_counted_markers += counted_markers
                            current_dset_length = self.PQ_ins_params[PQ_ins_key].current_dset_length

                            if live_filter_on_marker:
                                for i in range(len(self.PQ_ins_params[PQ_ins_key]._queue_newlength)):
                                    prev_newlength = self.PQ_ins_params[PQ_ins_key]._queue_newlength.popleft()

                                    self.PQ_ins_params[PQ_ins_key].dset_hhtime.resize((current_dset_length+prev_newlength,))
                                    self.PQ_ins_params[PQ_ins_key].dset_hhchannel.resize((current_dset_length+prev_newlength,))
                                    self.PQ_ins_params[PQ_ins_key].dset_hhspecial.resize((current_dset_length+prev_newlength,))
                                    self.PQ_ins_params[PQ_ins_key].dset_hhsynctime.resize((current_dset_length+prev_newlength,))
                                    self.PQ_ins_params[PQ_ins_key].dset_hhsyncnumber.resize((current_dset_length+prev_newlength,))

                                    self.PQ_ins_params[PQ_ins_key].dset_hhtime[current_dset_length:] = self.PQ_ins_params[PQ_ins_key]._queue_hhtime.popleft()
                                    self.PQ_ins_params[PQ_ins_key].dset_hhchannel[current_dset_length:] = self.PQ_ins_params[PQ_ins_key]._queue_hhchannel.popleft()
                                    self.PQ_ins_params[PQ_ins_key].dset_hhspecial[current_dset_length:] = self.PQ_ins_params[PQ_ins_key]._queue_hhspecial.popleft()
                                    self.PQ_ins_params[PQ_ins_key].dset_hhsynctime[current_dset_length:] = self.PQ_ins_params[PQ_ins_key]._queue_sync_time.popleft()
                                    self.PQ_ins_params[PQ_ins_key].dset_hhsyncnumber[current_dset_length:] = self.PQ_ins_params[PQ_ins_key]._queue_sync_number.popleft()

                                    self.PQ_ins_params[PQ_ins_key].current_dset_length += prev_newlength
                                    current_dset_length = self.PQ_ins_params[PQ_ins_key].current_dset_length

                            self.PQ_ins_params[PQ_ins_key].dset_hhtime.resize((current_dset_length+newlength,))
                            self.PQ_ins_params[PQ_ins_key].dset_hhchannel.resize((current_dset_length+newlength,))
                            self.PQ_ins_params[PQ_ins_key].dset_hhspecial.resize((current_dset_length+newlength,))
                            self.PQ_ins_params[PQ_ins_key].dset_hhsynctime.resize((current_dset_length+newlength,))
                            self.PQ_ins_params[PQ_ins_key].dset_hhsyncnumber.resize((current_dset_length+newlength,))

                            self.PQ_ins_params[PQ_ins_key].dset_hhtime[current_dset_length:] = hhtime
                            self.PQ_ins_params[PQ_ins_key].dset_hhchannel[current_dset_length:] = hhchannel
                            self.PQ_ins_params[PQ_ins_key].dset_hhspecial[current_dset_length:] = hhspecial
                            self.PQ_ins_params[PQ_ins_key].dset_hhsynctime[current_dset_length:] = sync_time
                            self.PQ_ins_params[PQ_ins_key].dset_hhsyncnumber[current_dset_length:] = sync_number

                            self.PQ_ins_params[PQ_ins_key].current_dset_length += newlength
                            self.h5data.flush()

                    if self.PQ_ins_params[PQ_ins_key].current_dset_length > self.params[PQ_ins_key]['MAX_DATA_LEN']:
                        self.PQ_ins_params[PQ_ins_key].rawdata_idx += 1
                        rawdata_idx = self.PQ_ins_params[PQ_ins_key].rawdata_idx

                        pref = (PQ_ins_key + '/') if num_PQ !=  1 else ''

                        self.PQ_ins_params[PQ_ins_key].dset_hhtime = self.h5data.create_dataset(pref+'PQ_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        self.PQ_ins_params[PQ_ins_key].dset_hhchannel = self.h5data.create_dataset(pref+'PQ_channel-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        self.PQ_ins_params[PQ_ins_key].dset_hhspecial = self.h5data.create_dataset(pref+'PQ_special-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        self.PQ_ins_params[PQ_ins_key].dset_hhsynctime = self.h5data.create_dataset(pref+'PQ_sync_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        self.PQ_ins_params[PQ_ins_key].dset_hhsyncnumber = self.h5data.create_dataset(pref+'PQ_sync_number-{}'.format(rawdata_idx), 
                            (0,), 'u4', maxshape=(None,))         
                        self.PQ_ins_params[PQ_ins_key].current_dset_length = 0

                        self.h5data.flush()

        
        for PQ_ins_key, PQ_ins in self.PQ_instruments.iteritems():

            pref = (PQ_ins_key + '/') if num_PQ !=  1 else ''

            dset_hist = self.h5data.create_dataset(pref+'PQ_hist', data=self.PQ_ins_params[PQ_ins_key].hist, compression='gzip')
            self.h5data.flush()
  
            PQ_ins.StopMeas()
        
            print 'PQ total datasets, events last datase, last sync number:', self.PQ_ins_params[PQ_ins_key].rawdata_idx, self.PQ_ins_params[PQ_ins_key].current_dset_length, self.PQ_ins_params[PQ_ins_key].last_sync_number
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()
        

def PQ_decode(data):
    """
    Decode the binary data into event time (absolute, highest precision),
    channel number and special bit. See PicoQuant (HydraHarp, TimeHarp) 
    documentation about the details.
    This function does not work for the PicoHarp (different format!)
    """
    event_time = np.bitwise_and(data, 2**25-1)
    channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
    special = np.bitwise_and(np.right_shift(data, 31), 1)
    return event_time, channel, special


class PQMeasurementIntegrated(PQMeasurement):#T2_tools_v2 only!
    mprefix = 'PQMeasurementIntegrated'

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
    

        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
        T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())

        hist_length = np.uint64(self.params['MAX_SYNC_BIN'] - self.params['MIN_SYNC_BIN'])
        sweep_length = np.uint64(self.params['pts'])
        syncs_per_sweep = np.uint64(self.params['syncs_per_sweep'])

        hist0 = np.zeros((hist_length,sweep_length), dtype='u1')
        hist1 = np.zeros((hist_length,sweep_length), dtype='u1')

        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        self.start_keystroke_monitor('abort',timer=False)
        _timer=time.time() 
        ll=0
        while(self.PQ_ins.get_MeasRunning()):

            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if not self.measurement_process_running():
                    break
                self._keystroke_check('abort')
                if self.keystroke('abort') in ['q','Q']:
                    print 'aborted.'
                    self.stop_keystroke_monitor('abort')
                    break
                    
                self.print_measurement_progress()

                _timer=time.time()

            self.PQ_ins_params[PQ_ins_key]._length, self.PQ_ins_params[PQ_ins_key]._data = self.PQ_ins.get_TTTR_Data()
                
            if self.PQ_ins_params[PQ_ins_key]._length > 0:

                if self.PQ_ins_params[PQ_ins_key]._length == T2_READMAX:
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
                
                _t, _c, _s = PQ_decode(self.PQ_ins_params[PQ_ins_key]._data[:self.PQ_ins_params[PQ_ins_key]._length])

                hist0, hist1, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools_v3.T2_live_filter_integrated(_t, _c, _s, hist0, hist1, t_ofl, 
                            t_lastsync, last_sync_number,
                            syncs_per_sweep, sweep_length, 
                            MIN_SYNC_BIN, MAX_SYNC_BIN,
                            T2_WRAPAROUND,T2_TIMEFACTOR)
                ll+=newlength
        self.PQ_ins.StopMeas()


        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        print 'PQ total events: last sync number',  ll, last_sync_number
        self.stop_measurement_process()

        dset_hist0 = self.h5data.create_dataset('PQ_hist0', data=hist0, compression='gzip')
        dset_hist1 = self.h5data.create_dataset('PQ_hist1', data=hist1, compression='gzip')
        self.h5data.flush()

def DataProcessorThread ( StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, T2_TIMEFACTOR, MIN_SYNC_BIN, MAX_SYNC_BIN ):

    t_ofl = 0
    t_lastsync = 0
    last_sync_number = 0
    length = 0

    print 'Processor thread started'          

    while True : #The process is stopped when an item is put to the stop queue. Then it will process the remaining queue items and exit.

        if StopQueue.empty() == False:
            if FifoQueue.empty() == True:  
                break
            print 'Stopping the Processor... waiting until the queue is empty. Current length ' + str( _FifoQueue.qsize() )
                
        if FifoQueue.qsize() > 0:
            try:
                length, data = FifoQueue.get(True, 1)
                if length > 0:
                     _t, _c, _s = PQ_decode(data[:length])
            except Exception as E:
                print 'exception: timeout during get() in the processor queue'
                print E.args  
                continue   #  do not process data when getting from the queue has not worked out

            hhtime, hhchannel, hhspecial, sync_time, sync_number, newlength, t_ofl, t_lastsync, last_sync_number = \
                T2_tools_v2.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number, 
                    MIN_SYNC_BIN, MAX_SYNC_BIN, T2_WRAPAROUND, T2_TIMEFACTOR)

            if newlength > 0:
                ProcessedDataQueue.put( (hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number) )

    print 'Processor thread stopped'    

def DataDumperThread ( StopQueue, ProcessedDataQueue, MAX_DATA_LEN, data_filepath ):

    rawdata_idx = 0
    t_ofl = 0
    t_lastsync = 0
    last_sync_number = 0
    length = 0
    current_dset_length = 0
    head, tail = os.path.split(data_filepath)   
    h5data = h5.HDF5Data( name = head + '/PQData_'+ tail)
    h5datapath = h5data.filepath()
    print 'Filepath '+str( h5datapath )
    
    #h5data = h5py.File(data_filepath, 'r+')

    print 'Dumper Process started'          

    while True : #The process is stopped when an item is put to the stop queue. Then it will process the remaining queue items and exit.

        if StopQueue.empty() == False:
            if ProcessedDataQueue.empty() == True:
                break
            print 'Stopping the Dumper... waiting until the queue is empty. Current length ' + str( ProcessedDataQueue.qsize() )
                
        if rawdata_idx == 0 or current_dset_length > MAX_DATA_LEN :
                
            rawdata_idx += 1              
            current_dset_length = 0

            print 'I create a new dataset.'
            dset_hhtime = h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
            dset_hhchannel = h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
            dset_hhspecial = h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
            dset_hhsynctime = h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
            dset_hhsyncnumber = h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))         

            h5data.flush()

        if ProcessedDataQueue.qsize() > 0:
            try:
                hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                   newlength, t_ofl, t_lastsync, last_sync_number = ProcessedDataQueue.get(True, 1)
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
                h5data.flush()

    print 'Dumper thread stopped'
    print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, last_sync_number


class PQ_Threaded_Measurement(PQMeasurement):
    """
    This class implements a measurement that uses separate Python-Processess to:

    1. Get the data from the PQ instrument (for this, the QTLab process is used, 
        as different processes cannot share memory or instruments)
    2. Process the data to convert them to the desired storage format
    3. Dump the data on the hard drive

    Data is transferred between these Processes using Queues.

    """

    mprefix = 'PQ_Threaded_Measurement'

    def run(self, autoconfig=True, setup=True, debug=False):

        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        print 'PQ threaded setup ' + str(setup)
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

        print 'I will use several threads! TTR_read_count ', TTTR_read_count

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

            the_processor = Process ( target = DataProcessorThread, args = ( StopQueue, FifoQueue, ProcessedDataQueue, T2_WRAPAROUND, \
                T2_TIMEFACTOR, MIN_SYNC_BIN, MAX_SYNC_BIN ) )
            the_processor.deamon=True
            the_processor.start()

            the_dumper = Process( target = DataDumperThread, args = ( StopQueue, ProcessedDataQueue, MAX_DATA_LEN, self.h5data.filepath() ) )
            the_dumper.deamon=True 
            the_dumper.start()

        except Exception as E:
            print 'Exception in starting and starting the threads'
            print E.args

        while( self.PQ_ins.get_MeasRunning() ):
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

            self.PQ_ins_params[PQ_ins_key]._length, self.PQ_ins_params[PQ_ins_key]._data = self.PQ_ins.get_TTTR_Data( TTTR_read_count )
            if self.PQ_ins_params[PQ_ins_key]._length > 0:
                FifoQueue.put( (self.PQ_ins_params[PQ_ins_key]._length, self.PQ_ins_params[PQ_ins_key]._data) ) 

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

