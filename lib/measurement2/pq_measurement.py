"""
Generic measurement class for measurements with Picoquant TTTR measurements as main loop
Bas Hensen 2014

"""

import numpy as np
import qt
import measurement.lib.measurement2.measurement as m2

from measurement.lib.cython.PQ_T2_tools import T2_tools

class PQMeasurement(m2.Measurement):
    mprefix = 'PQMeasurement'
    
    def autoconfig(self):
        pass

    def setup(self, **kw):
        do_calibrate = kw.pop('pq_calibrate',True)
        if self.PQ_ins.OpenDevice():
            self.PQ_ins.start_T2_mode()
            self.PQ_ins.set_Binning(self.params['BINSIZE'])
            if do_calibrate:
                self.PQ_ins.calibrate()
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

    def run(self, autoconfig=True, setup=True):

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
        
        while(self.PQ_ins.get_MeasRunning() and self.measurement_process_running()):

            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            self.print_measurement_progress()
           
            _length, _data = self.PQ_ins.get_TTTR_Data()
                
            if _length > 0:
                _t, _c, _s = self._PQ_decode(_data[:_length])
                
                hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                                                MIN_SYNC_BIN, MAX_SYNC_BIN,)
                                                #T2_WRAPAROUND,T2_TIMEFACTOR) #T2_tools_v2 only

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

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        
        self.stop_measurement_process()
        

    def _PQ_decode(self,data):
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

    def run(self, autoconfig=True, setup=True):
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

        while(self.PQ_ins.get_MeasRunning() and self.adwin_process_running()):

            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            self.print_measurement_progress()

            _length, _data = self.PQ_ins.get_TTTR_Data()
                
            if _length > 0:
                _t, _c, _s = self._PQ_decode(_data[:_length])
                
                hist0, hist1, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools.LDE_live_filter_integrated(_t, _c, _s, hist0, hist1, t_ofl, 
                            t_lastsync, last_sync_number,
                            syncs_per_sweep, sweep_length, 
                            MIN_SYNC_BIN, MAX_SYNC_BIN,
                            T2_WRAPAROUND,T2_TIMEFACTOR)

        self.PQ_ins.StopMeas()


        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        
        self.stop_measurement_process()

        dset_hist0 = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
            (hist_length,sweep_length), 'u1', maxshape=(None,None))
        dset_hist1 = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
            (hist_length,sweep_length), 'u1', maxshape=(None,None))
        dset_hist0[:,:] = hist0
        dset_hist1[:,:] = hist1
        self.h5data.flush()


