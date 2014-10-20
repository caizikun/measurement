import qt
import numpy as np
import time
import measurement.lib.measurement2.measurement as m2
import measurement.lib.measurement2.pq.pq_measurement as pq
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.cython.PQ_T2_tools import T2_tools_bell
reload(T2_tools_bell)


class Bell(pulsar_pq.PQPulsarMeasurement):
    mprefix = 'Bell'

    def __init__(self, name):
        pulsar_pq.PQPulsarMeasurement.__init__(self, name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1

    def autoconfig(self, **kw):

        self.params['sequence_wait_time'] = self.joint_params['LDE_attempts_before_CR']*self.joint_params['LDE_element_length']*1e6\
        +self.params['free_precession_time_1st_revival']*1e6*self.joint_params['wait_for_1st_revival']+ 20
        print 'I am the sequence waiting time', self.params['sequence_wait_time']
        pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)

        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage(
                        self.params['AWG_SP_power'], controller='sec')
        self.params['RO_voltage_AWG'] = \
                self.AWG_RO_AOM.power_to_voltage(
                        self.params['AWG_RO_power'], controller='sec')
        self.params['yellow_voltage_AWG'] = \
                self.yellow_aom.power_to_voltage(
                        self.params['AWG_yellow_power'], controller='sec')

        #print 'setting AWG SP voltage:', self.params['SP_voltage_AWG']
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])
        if self.params['LDE_yellow_duration'] > 0.:
            qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params['yellow_voltage_AWG'])
        else:
            print self.mprefix, self.name, ': Ignoring yellow'

    
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s readout repetitions' % reps_completed)

    def setup(self, **kw):
        pulsar_pq.PQPulsarMeasurement.setup(self, mw=self.params['MW_during_LDE'],**kw)     

    def save(self, name='ssro'):
        reps = self.adwin_var('entanglement_events')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('CR_hist', 200),
                    ('RO_data', reps),
                    ('statistics', 10),
                    'entanglement_events',
                    'completed_reps',
                    'total_CR_counts'])
    def finish(self):
        h5_joint_params_group = self.h5basegroup.create_group('joint_params')
        joint_params = self.joint_params.to_dict()
        for k in joint_params:
            h5_joint_params_group.attrs[k] = joint_params[k]
        self.h5data.flush()
        pulsar_pq.PQPulsarMeasurement.finish(self)

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

        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        MIN_HIST_SYNC_BIN = np.uint64(self.params['MIN_HIST_SYNC_BIN'])
        MAX_HIST_SYNC_BIN = np.uint64(self.params['MAX_HIST_SYNC_BIN'])
        TTTR_read_count = self.params['TTTR_read_count']
        T2_WRAPAROUND = np.uint64(self.PQ_ins.get_T2_WRAPAROUND())
        T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
        T2_READMAX = self.PQ_ins.get_T2_READMAX()

        print 'run PQ measurement, TTTR_read_count', TTTR_read_count
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
        
        hist_length = np.uint64(self.params['MAX_HIST_SYNC_BIN'] - self.params['MIN_HIST_SYNC_BIN'])
        self.hist = np.zeros((hist_length,2), dtype='u4')
        self.marker_events = 0

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        _timer=time.time()
        ii=0

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
                    if _length == 0 or self.keystroke('abort') in ['x']: 
                        break 
                print 'current sync, dset length:', last_sync_number, current_dset_length
            
                _timer=time.time()


            _length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)

            if _length > 0:
                if _length == T2_READMAX:
                    logging.warning('TTTR record length is maximum length, \
                            could indicate too low transfer rate resulting in buffer overflow.')

                _t, _c, _s = pq.PQ_decode(_data[:_length])

                hhtime, hhchannel, hhspecial, sync_time, self.hist, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools_bell.Bell_live_filter(_t, _c, _s, self.hist,
                                                t_ofl, t_lastsync, last_sync_number,
                                                MIN_SYNC_BIN, MAX_SYNC_BIN,
                                                MIN_HIST_SYNC_BIN,MAX_HIST_SYNC_BIN,
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
                    self.marker_events += np.sum(hhspecial)

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
        
        print 'PQ total datasets, events last datase, last sync number:', rawdata_idx, current_dset_length, last_sync_number
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()