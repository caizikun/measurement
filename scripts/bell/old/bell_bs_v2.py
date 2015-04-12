import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq
import bell
reload(bell)


bs_params = {}
bs_params['MAX_DATA_LEN']        =   int(100e6)
bs_params['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
bs_params['MIN_SYNC_BIN']        =   int(5e-6*1e12) #5 us 
bs_params['MAX_SYNC_BIN']        =   int(15e-6*1e12) #15 us 
bs_params['MIN_HIST_SYNC_BIN']   =   int(5438*1e3)
bs_params['MAX_HIST_SYNC_BIN']   =   int(5560*1e3)
bs_params['measurement_time']    =   24*60*60 #sec = 24H
bs_params['measurement_abort_check_interval']    = 1 #sec
bs_params['TTTR_read_count'] = qt.instruments['HH_400'].get_T2_READMAX()

bs_params['pulse_start_bin'] = 1000
bs_params['pulse_stop_bin']  = 3000
bs_params['tail_start_bin']  = 4500
bs_params['tail_stop_bin']   = 60000

class Bell_BS(bell.Bell):

    mprefix = 'Bell_BS'

    def autoconfig(self):
        remote_params = self.remote_measurement_helper.get_measurement_params()
        print remote_params
        for k in remote_params:
            self.params[k] = remote_params[k]
        self.remote_measurement_helper.set_data_path(self.h5datapath)
        

    def setup(self):
        pq.PQMeasurement.setup(self)

    def start_measurement_process(self):
        self.remote_measurement_helper.set_is_running(True)

    def print_measurement_progress(self):
        pulse_cts= np.sum(self.hist[self.params['pulse_start_bin'] : self.params['pulse_stop_bin'] ,:])
        tail_cts=np.sum(self.hist[self.params['tail_start_bin']  : self.params['tail_stop_bin']  ,:])
        self.adwin_ins_lt4.Set_Par(51, int(tail_cts))
        self.adwin_ins_lt4.Set_Par(52, int(pulse_cts))
        self.adwin_ins_lt4.Set_Par(77, int(self.marker_events))
        
    def run(self, autoconfig=True, setup=True, debug=False):
        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        rawdata_idx = 1
        t_ofl = np.uint64(0)
        t_lastsync = np.uint64(0)
        last_sync_number = np.uint32(0)
        _length = 0
        #cur_length = 0 #DEBUG!

        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        MIN_HIST_SYNC_BIN = np.uint64(self.params['MIN_HIST_SYNC_BIN'])
        MAX_HIST_SYNC_BIN = np.uint64(self.params['MAX_HIST_SYNC_BIN'])
        if qt.current_setup in ('lt4', 'lt3'):
            TH_RepetitiveReadouts = self.params['TH_RepetitiveReadouts']
        else: 
            TH_RepetitiveReadouts = 1
        TTTR_read_count = self.params['TTTR_read_count']
        T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
        T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
        T2_READMAX = self.PQ_ins.get_T2_READMAX()

        print 'run PQ measurement, TTTR_read_count', TTTR_read_count
        # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
        dset_hhtime = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))#, compression='gzip', compression_opts=9)
        dset_hhchannel = self.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))#, compression='gzip', compression_opts=9)
        dset_hhspecial = self.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))#, compression='gzip', compression_opts=9)
        dset_hhsynctime = self.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))#, compression='gzip', compression_opts=9)
        dset_hhsyncnumber = self.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
            (0,), 'u4', maxshape=(None,))#, compression='gzip', compression_opts=9)          
        current_dset_length = 0
        
        hist_length = np.uint64(self.params['MAX_HIST_SYNC_BIN'] - self.params['MIN_HIST_SYNC_BIN'])
        self.hist = np.zeros((hist_length,2), dtype='u4')
        self.marker_events = 0
        new_entanglement_markers = 0

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        _timer=time.time()
        ii=0
        k_error_message = 0

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
                    ii+=1
                    print 'Retreiving late data from PQ, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')
                    if ii>1 or self.keystroke('abort') in ['x']:
                        break 
                print 'current sync, dset length:', last_sync_number, current_dset_length

                _timer=time.time()
            _length = 0
            newlength = 0
            entanglement_markers = 0

            #_length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count) # Old code before inserting the TH_RepetitiveReadouts
            _data = np.array([],dtype = 'uint32')
            for j in range(TH_RepetitiveReadouts):
                cur_length, cur_data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
                _length += cur_length 
                _data = np.hstack((_data,cur_data[:cur_length]))

            if _length > 0:
                if _length ==  TH_RepetitiveReadouts * TTTR_read_count: 
                    k_error_message += 1
                    logging.warning('TTTR record length is maximum length.')
                    #print 'number of TTTR warnings:', k_error_message , '\n'

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
    
                hhtime, hhchannel, hhspecial, sync_time, self.hist, sync_number, \
                        newlength, t_ofl, t_lastsync, last_sync_number, new_entanglement_markers = \
                        T2_tools_bell.Bell_live_filter(_t, _c, _s, self.hist, t_ofl, t_lastsync, last_sync_number,
                        MIN_SYNC_BIN, MAX_SYNC_BIN, MIN_HIST_SYNC_BIN, MAX_HIST_SYNC_BIN, T2_WRAPAROUND,T2_TIMEFACTOR) 


                if newlength > 0:
                    if new_entanglement_markers > 0:
                        entanglement_markers += new_entanglement_markers
                        print 'SUCCESSFUL ENTANGLEMENT!!! Event No ' + entanglement_markers
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
                    self.marker_events += np.sum(hhspecial)
 
                if current_dset_length > self.params['MAX_DATA_LEN']:
                    rawdata_idx += 1
                    dset_hhtime = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))#, compression='gzip', compression_opts=4)
                    dset_hhchannel = self.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))#, compression='gzip', compression_opts=4)
                    dset_hhspecial = self.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))#, compression='gzip', compression_opts=4)
                    dset_hhsynctime = self.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))#, compression='gzip', compression_opts=4)
                    dset_hhsyncnumber = self.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))#, compression='gzip', compression_opts=4)         
                    current_dset_length = 0

                    self.h5data.flush()

        dset_hist = self.h5data.create_dataset('PQ_hist', data=self.hist, compression='gzip')
        self.h5data.flush()

        self.PQ_ins.StopMeas()
        
        print 'PQ total datasets, events last dataset, last sync number, markers, entanglement:', rawdata_idx, current_dset_length, last_sync_number, self.marker_events, entanglement_markers
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()

    def measurement_process_running(self):
        return self.remote_measurement_helper.get_is_running()

    def stop_measurement_process(self):
        self.remote_measurement_helper.set_is_running(False)

    def finish(self):
        self.save_instrument_settings_file()
        self.save_params()
        pq.PQMeasurement.finish(self)

Bell_BS.remote_measurement_helper = qt.instruments['remote_measurement_helper']
Bell_BS.adwin_ins_lt4 = qt.instruments['physical_adwin_lt4']

def remote_HH_measurement(name):
    debug=False
    m=Bell_BS(name+qt.instruments['remote_measurement_helper'].get_measurement_name())
    for k in bs_params:
        m.params[k] = bs_params[k]
    m.run(debug=debug)
    print ' This script was running Bell BS v2. '
    m.finish()
    
if __name__ == '__main__':
    remote_HH_measurement('')