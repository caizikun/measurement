"""
Measurement class for measurements with Picoquant TTTR measurements as main loop
Bas Hensen 2014

"""

import numpy as np
import qt
import measurement.lib.measurement2.measurement as m2
import time
import logging
from measurement.lib.cython.PQ_T2_tools import T2_tools_v2

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
            print self.PQ_ins.get_ResolutionPS()
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
        self.stop_measurement_process()

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
        new_sync_number = 0

        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        TTTR_read_count = self.params['TTTR_read_count']
        T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
        T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
        T2_READMAX = self.PQ_ins.get_T2_READMAX()

        print 'run PQ measurement, TTTR_read_count ', TTTR_read_count
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
        current_dset_length = 0

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        _timer=time.time()

        #ll=np.zeros(T2_READMAX+1) #XXX
        while(self.PQ_ins.get_MeasRunning()):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    self.print_measurement_progress()
                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        self.stop_measurement_process()
                else:
                    #Check that all the measurement data has been transsfered from the PQ ins FIFO
                    if new_sync_number == last_sync_number: 
                        break 
                print 'current sync, dset length:', last_sync_number, current_dset_length
            
                _timer=time.time()

            last_sync_number=new_sync_number

            _length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
            #ll[_length]+=1 #XXX
            if _length > 0:
                if _length == T2_READMAX:
                    logging.warning('TTTR record length is maximum length, \
                            could indicate too low transfer rate resulting in buffer overflow.')

                _t, _c, _s = PQ_decode(_data[:_length])

                hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, new_sync_number = \
                        T2_tools_v2.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                                                MIN_SYNC_BIN, MAX_SYNC_BIN,
                                                T2_WRAPAROUND,T2_TIMEFACTOR) #T2_tools_v2 only
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

        self.PQ_ins.StopMeas()
        #self.h5data.create_dataset('PQ_hist_lengths', data=ll, compression='gzip')#XXX
        #self.h5data.flush()#XXX
        print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, last_sync_number
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()
        

def PQ_decode(data):
    """
    Decode the binary data into event time (absolute, highest precision),
    channel number and special bit. See PicoQuant (HydraHarp, TimeHarp, PicoHarp) 
    documentation about the details.
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

            _length, _data = self.PQ_ins.get_TTTR_Data()
                
            if _length > 0:
                _t, _c, _s = PQ_decode(_data[:_length])
                
                hist0, hist1, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools_v2.LDE_live_filter_integrated(_t, _c, _s, hist0, hist1, t_ofl, 
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


