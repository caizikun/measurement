import qt
import numpy as np
import time
import logging
import purify_slave
from collections import deque
import measurement.lib.measurement2.measurement as m2
import purify_slave, sweep_purification
import measurement.lib.measurement2.pq.pq_measurement as pq
from measurement.lib.measurement2.adwin_ssro import DD_2
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
import copy,msvcrt
reload(T2_tools_v3)
reload(pq)
reload(purify_slave);reload(sweep_purification)

name = qt.exp_params['protocols']['current']

class PQPurifyMeasurement(purify_slave.purify_single_setup,  pq.PQMeasurement ): # pq.PQ_Threaded_Measurement ): #
    mprefix = 'PQ_C13_Measurement'
    adwin_process = 'purification'
    
    def __init__(self, name):
        purify_slave.purify_single_setup.__init__(self, name)
        self.params['measurement_type'] = self.mprefix

    def autoconfig(self):
        purify_slave.purify_single_setup.autoconfig(self)
        pq.PQMeasurement.autoconfig(self)

    def setup(self, **kw):
        purify_slave.purify_single_setup.setup(self,**kw)
        pq.PQMeasurement.setup(self,**kw)

    def start_measurement_process(self):
        qt.msleep(.5)
        self.start_adwin_process(load=False)
        qt.msleep(.5)

    def measurement_process_running(self):
        return self.adwin_process_running()

    def run(self, **kw):
        pq.PQMeasurement.run(self,**kw)
        
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))

    def stop_measurement_process(self):
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('Total completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))


class purify(PQPurifyMeasurement):
    mprefix = 'Purification'
    adwin_process = 'purification'

    def __init__(self, name):
        PQPurifyMeasurement.__init__(self, name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1
    
    def save(self, name = 'adwinadata'):
        purify_slave.purify_single_setup.save(self)
        
    # def print_measurement_progress(self):
    #     pass
        # tail_cts=np.sum(self.hist[self.params['tail_start_bin']  : self.params['tail_stop_bin']  ,:])
        # self.physical_adwin.Set_Par(50, int(tail_cts))
        
        # reps_completed = self.adwin_var('completed_reps')    
        # print('completed %s readout repetitions' % reps_completed)
        

    
    def finish(self):
        h5_joint_params_group = self.h5basegroup.create_group('joint_params')
        joint_params = self.joint_params.to_dict()
        for k in joint_params:
            h5_joint_params_group.attrs[k] = joint_params[k]
        self.h5data.flush()

        self.AWG_RO_AOM.turn_off()
        self.E_aom.turn_off()
        self.A_aom.turn_off()
        self.repump_aom.turn_off()


        PQPurifyMeasurement.finish(self)


    def run(self, autoconfig=False, setup=False, debug=False, live_filter_on_marker=False):
        if debug:
            self.run_debug()
            return

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()

        # Experimental addition for remote running
        if (self.current_setup == self.joint_params['master_setup']) and self.joint_params['control_slave']:
            qt.instruments['lt3_helper'].set_is_running(False)
            qt.msleep(0.5)
            qt.instruments['lt3_helper'].set_measurement_name(name)
            qt.instruments['lt3_helper'].set_script_path(r'D:/measuring/measurement/scripts/Purification/purify.py')
            qt.instruments['lt3_helper'].execute_script()
            qt.instruments['lt4_helper'].set_is_running(True)
            
            m.lt3_helper.set_is_running(True)
            qt.msleep(2)
        ### this is now in autoconfig. NK 18-05-2016
        # for i in range(10):
        #     self.physical_adwin.Stop_Process(i+1)
        #     qt.msleep(0.3)
        # qt.msleep(1)
        # # self.adwin.load_MBI()   
        # # New functionality, now always uses the adwin_process specified as a class variables 
        # loadstr = 'self.adwin.load_'+str(self.adwin_process)+'()'   
        # exec(loadstr)
        # qt.msleep(2)


        rawdata_idx = 1
        t_ofl = np.uint64(0)
        t_lastsync = np.uint64(0)
        last_sync_number = np.uint32(0)
        _length = 0

        MIN_SYNC_BIN = np.uint64(self.params['MIN_SYNC_BIN'])
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN'])
        MIN_HIST_SYNC_BIN = np.uint64(self.params['MIN_HIST_SYNC_BIN'])
        MAX_HIST_SYNC_BIN = np.uint64(self.params['MAX_HIST_SYNC_BIN'])
        

        #### entanglement marker number
        entanglement_marker_number = self.params['entanglement_marker_number'] # add to BS and LT
        wait_for_late_data=self.params['wait_for_late_data']                   # add to BS and LT
        TTTR_RepetitiveReadouts = self.params['TTTR_RepetitiveReadouts']           # add to BS
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
        self.hist_update = np.zeros((hist_length,2), dtype='u4')
        new_entanglement_markers = 0
        self.entanglement_markers = 0

        self.start_keystroke_monitor('abort',timer=False)
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        self.start_measurement_process()
        _timer=time.time()
        ii=0
        k_error_message = 0

        if live_filter_on_marker:
            _queue_hhtime      = deque([],self.params['live_filter_queue_length'])
            _queue_sync_time   = deque([],self.params['live_filter_queue_length'])
            _queue_hhchannel   = deque([],self.params['live_filter_queue_length'])
            _queue_hhspecial   = deque([],self.params['live_filter_queue_length'])
            _queue_sync_number = deque([],self.params['live_filter_queue_length'])
            _queue_newlength   = deque([],self.params['live_filter_queue_length'])

        no_of_cycles_for_live_update_reset = 100
        live_updates = 0
        last_sync_number_update = 0
        last_sync_number = 0

        while(self.PQ_ins.get_MeasRunning()):
            if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    live_updates += 1
                    if live_updates > no_of_cycles_for_live_update_reset:
                        self.hist_update = copy.deepcopy(self.hist)
                        live_updates = 0
                        last_sync_number_update = last_sync_number

                    self.print_measurement_progress()
                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        self.stop_measurement_process()

                else:
                    #Check that all the measurement data has been transsfered from the PQ ins FIFO
                    print 'Retreiving late data from PQ, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')
                    ii+=1
                    if (_length == 0) or (self.keystroke('abort') in ['x']) or ii>wait_for_late_data: 
                        break 
                
                print 'current sync, marker_events, dset length:', last_sync_number,self.entanglement_markers, current_dset_length
                pulse_cts_ch0=np.sum((self.hist - self.hist_update)[self.params['pulse_start_bin']:self.params['pulse_stop_bin'],0])
                pulse_cts_ch1=np.sum((self.hist - self.hist_update)[self.params['pulse_start_bin']+self.params['PQ_ch1_delay'] : self.params['pulse_stop_bin']+self.params['PQ_ch1_delay'],1])
                tail_cts_ch0=np.sum((self.hist - self.hist_update)[self.params['tail_start_bin']  : self.params['tail_stop_bin'],0])
                tail_cts_ch1=np.sum((self.hist - self.hist_update)[self.params['tail_start_bin']+self.params['PQ_ch1_delay'] : self.params['tail_stop_bin']+self.params['PQ_ch1_delay'],1])
                print 'duty_cycle', self.physical_adwin.Get_FPar(58)


                #### update parameters in the adwin
                if (last_sync_number > 0) and (last_sync_number != last_sync_number_update): 
                    if qt.current_setup == 'lt3':

                        tail_psb_lt3 = round(float(2*tail_cts_ch0*1e4)/float(last_sync_number-last_sync_number_update),3)
                        tail_psb_lt4 = round(float(2*tail_cts_ch1*1e4)/float(last_sync_number-last_sync_number_update),3)
                        self.physical_adwin.Set_FPar(56, tail_psb_lt3)
                        self.physical_adwin.Set_FPar(57, tail_psb_lt4)
                         
                        # print 'tail_counts PSB (lt3/lt4)', tail_psb_lt3,tail_psb_lt4
                    else:
                        ZPL_tail = round(float( (tail_cts_ch0+ tail_cts_ch1)*1e4)/float(last_sync_number-last_sync_number_update),3)
                        Pulse_counts = round(float((pulse_cts_ch1 + pulse_cts_ch0)*1e4)/float(last_sync_number-last_sync_number_update),3)
                        self.physical_adwin.Set_FPar(56, ZPL_tail)
                        self.physical_adwin.Set_FPar(57, Pulse_counts)


                _timer=time.time()
            _length = 0
            newlength = 0

            #_length, _data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count) # Old code before inserting the TTTR_RepetitiveReadouts
            _data = np.array([],dtype = 'uint32')
            for j in range(TTTR_RepetitiveReadouts):
                cur_length, cur_data = self.PQ_ins.get_TTTR_Data(count = TTTR_read_count)
                _length += cur_length 
                _data = np.hstack((_data,cur_data[:cur_length]))

            if _length > 0:
                if _length ==  TTTR_RepetitiveReadouts * TTTR_read_count: 
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
                            T2_tools_v3.T2_live_filter(_t, _c, _s, self.hist, t_ofl, t_lastsync, last_sync_number,
                                    MIN_SYNC_BIN, MAX_SYNC_BIN, MIN_HIST_SYNC_BIN, MAX_HIST_SYNC_BIN, T2_WRAPAROUND,T2_TIMEFACTOR,entanglement_marker_number)

                if newlength > 0:

                    if new_entanglement_markers == 0 and live_filter_on_marker:
                        _queue_hhtime.append(hhtime)
                        _queue_sync_time.append(sync_time)    
                        _queue_hhchannel.append(hhchannel)  
                        _queue_hhspecial.append(hhspecial)  
                        _queue_sync_number.append(sync_number)  
                        _queue_newlength.append(newlength)   
                    else:
                        self.entanglement_markers += new_entanglement_markers
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
        
        print 'PQ total datasets, events last dataset, last sync number, entanglement:', rawdata_idx, current_dset_length, last_sync_number, self.entanglement_markers
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_measurement_process()

    def stop_measurement_process(self):
        PQPurifyMeasurement.stop_measurement_process(self)



def load_TH_params(m):
    pq_measurement.PQMeasurement.PQ_ins=qt.instruments['TH_260N'] ### overwrites the use of the HH_400
    m.params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
    m.params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       8e3
    m.params['MIN_HIST_SYNC_BIN'] =  1
    m.params['MAX_HIST_SYNC_BIN'] =  8000
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =   1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
    m.params['measurement_abort_check_interval']    = 2. #sec
    m.params['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
    m.params['use_live_marker_filter']=False


def load_BK_params(m):
    m.joint_params['opt_pi_pulses'] = 2
    m.params['LDE_decouple_time'] = 0.50e-6
    m.joint_params['opt_pulse_separation'] = 0.50e-6 
    m.joint_params['LDE_element_length'] = 6e-6
    m.joint_params['do_final_mw_LDE'] = 1
    m.params['PLU_during_LDE'] = 1
    m.params['LDE_SP_duration'] = 1.5e-6


    #### compensate a change in plu windows.
    ### insert parameter adjustment here.


def MW_Position(name,debug = False,upload_only=False):
    """
    Initializes the electron in ms = -1 
    Put a very long repumper. Leave one MW pi pulse to find the microwave position.
    THIS MEASUREMENT RUNS EXCLUSIVELY ON THE TIMEHARP!
    NK 2016
    """

    m = purify(name)
    sweep_purification.prepare(m)

    load_TH_params(m)
    # load_BK_params(m)
    ### general params
    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 2000

    sweep_purification.turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    
    m.params['MW_before_LDE1'] = 1 # allows for init in -1 before LDE
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 1

    m.params['PLU_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 1
    m.params['is_two_setup_experiment'] = 1

    m.joint_params['LDE_attempts'] = 250

    #m.params['LDE_SP_delay'] = 0e-6

    ### prepare sweep / necessary for the measurement that we under go.
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    # m.params['general_sweep_pts'] = np.array([m.joint_params['LDE_element_length']-200e-9-m.params['LDE_SP_delay']])
    m.params['general_sweep_pts'] = np.array([1.5e-6])
    # print m.params['general_sweep_pts']
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9

    ### upload and run

    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)

def tail_sweep(name,debug = True,upload_only=True, minval = 0.1, maxval = 0.8, local = False):
    """
    Performs a tail_sweep in the LDE_1 element
    """
    m = purify(name)
    sweep_purification.prepare(m)

    ### general params
    pts = 7
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000


    sweep_purification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    ### --> for this measurement: none.

    m.joint_params['opt_pi_pulses'] = 1
    m.params['MW_during_LDE'] = 0
    m.params['PLU_during_LDE'] = 0
    if local:
        m.params['is_two_setup_experiment'] = 0 ## set to 1 in case you want to do optical pi pulses on lt4!
    else:
        m.params['is_two_setup_experiment'] = 1 ## set to 1 in case you want to do optical pi pulses on lt4!
    ### need to find this out!
    # m.params['MIN_SYNC_BIN'] =       5000
    # m.params['MAX_SYNC_BIN'] =       9000 

    # put sweep together:
    sweep_off_voltage = False

    m.params['do_general_sweep']    = True

    if sweep_off_voltage:
        m.params['general_sweep_name'] = 'eom_off_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(-0.02,-0.02,pts)
    else:
        m.params['general_sweep_name'] = 'aom_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(minval,maxval,pts)


    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    ### upload

    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)

def optical_rabi(name,debug = True,upload_only=True, local = False):
    """
    Very similar to tail sweep.
    """
    m = purify(name)
    sweep_purification.prepare(m)

    ### general params
    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 10000


    sweep_purification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    ### --> for this measurement: none.

    m.joint_params['opt_pi_pulses'] = 1
    m.params['MW_during_LDE'] = 0
    m.params['PLU_during_LDE'] = 0
    if local:
        m.params['is_two_setup_experiment'] = 0 ## set to 1 in case you want to do optical pi pulses on lt4!
    else:
        m.params['is_two_setup_experiment'] = 1 ## set to 1 in case you want to do optical pi pulses on lt4!

    # put sweep together:
    m.params['do_general_sweep']    = True


    m.params['general_sweep_name'] = 'eom_pulse_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(39e-9,40e-9,pts)



    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    ### upload

    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)


def SPCorrsPuri_PSB_singleSetup(name, debug = False, upload_only = False):
    """
    Performs a regular Spin-photon correlation measurement.
    """
    m = purify(name)
    
    sweep_purification.prepare(m)
    load_TH_params(m) # has to be after prepare(m)

    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 50000

    sweep_purification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['PLU_during_LDE'] = 0
    m.joint_params['LDE_attempts'] = 1

    m.joint_params['opt_pi_pulses'] = 2
    m.joint_params['opt_pulse_separation'] = m.params['LDE_decouple_time']
    ### this can also be altered to the actual theta pulse by negating the if statement
    if True:
        m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
        m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']

    m.params['is_two_setup_experiment'] = 0

    ### upload

    sweep_purification.run_sweep(m, debug = debug, upload_only = upload_only)

def SPCorrsPuri_ZPL_twoSetup(name, debug = False, upload_only = False):
    """
    Performs a regular Spin-photon correlation measurement.
    """
    m = purify(name)
    sweep_purification.prepare(m)
    if qt.current_setup == 'lt3':
        print 'I am lt3 and therefore I am using the timeharp'
        load_TH_params(m)
    # load_BK_params(m)
    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 5000

    sweep_purification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.joint_params['do_final_mw_LDE'] = 0
    m.joint_params['LDE_attempts'] = 250

    m.params['LDE_decouple_time'] = m.params['LDE_decouple_time'] + 500e-9
    m.joint_params['LDE_element_length'] = m.joint_params['LDE_element_length']  + 1e-6
    m.params['LDE_SP_duration'] = 1.5e-6

    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 1

    m.joint_params['opt_pi_pulses'] = 2
    m.joint_params['opt_pulse_separation'] = m.params['LDE_decouple_time']
    ### this can also be altered to the actual theta pulse by negating the if statement
    if True:
        m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
        m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']


    ### upload

    sweep_purification.run_sweep(m, debug = debug, upload_only = upload_only)

def BarretKok_SPCorrs(name, debug = False, upload_only = False):
    """
    Performs a regular Spin-photon correlation measurement with the Barret & Kok timing parameters.

    """
    m = purify(name)
    sweep_purification.prepare(m)

    load_BK_params(m)


    m.joint_params['do_final_mw_LDE'] = 1
    # m.params['LDE_final_mw_amplitude'] = 0

    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 5000

    sweep_purification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['PLU_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 2

    ### this can also be altered to the actual theta pulse by negating the if statement
    if True:
        m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
        m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']

    m.params['is_two_setup_experiment'] = 1 

    ### upload

    sweep_purification.run_sweep(m, debug = debug, upload_only = upload_only)


def TPQI(name,debug = False,upload_only=False):
    
    m = purify(name)
    sweep_purification.prepare(m)

    pts = 1
    m.params['reps_per_ROsequence'] = 50000
    sweep_purification.turn_all_sequence_elements_off(m)


    m.params['MIN_SYNC_BIN'] =       1.5e6
    m.params['MAX_SYNC_BIN'] =       9e6
    m.params['is_TPQI'] = 1
    m.params['is_two_setup_experiment'] = 1
    m.params['do_general_sweep'] = 0
    m.params['MW_during_LDE'] = 0


    m.joint_params['LDE_element_length'] = 10e-6
    m.joint_params['opt_pi_pulses'] = 5
    m.joint_params['opt_pulse_separation'] = 1400e-9
    m.joint_params['LDE_attempts'] = 100

    m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
    m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
    m.params['tail_start_bin'] = 2635e3 - m.params['MIN_SYNC_BIN']  
    m.params['tail_stop_bin'] = 2700e3  - m.params['MIN_SYNC_BIN'] 

    if qt.current_setup == 'lt3':
        m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
        m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
        m.params['tail_start_bin'] = 2100e3 - m.params['MIN_SYNC_BIN']  
        m.params['tail_stop_bin'] = 2800e3  - m.params['MIN_SYNC_BIN'] 
        m.params['MIN_SYNC_BIN'] =       1.5e3
        m.params['MAX_SYNC_BIN'] =       9e3
        m.params['pulse_start_bin'] = m.params['pulse_start_bin']/1e3
        m.params['pulse_stop_bin'] = m.params['pulse_stop_bin']/1e3
        m.params['tail_start_bin'] = m.params['tail_start_bin']/1e3
        m.params['tail_stop_bin'] = m.params['tail_stop_bin']/1e3

    ### upload and run
    # m.params['do_general_sweep'] = 1
    # m.params['general_sweep_name'] = 'LDE_attempts'
    # print 'sweeping the', m.params['general_sweep_name']
    # m.params['general_sweep_pts'] = np.arange(2,503,50)
    # m.params['pts'] = len(m.params['general_sweep_pts'])
    # m.params['sweep_name'] = m.params['general_sweep_name'] 
    # m.params['sweep_pts'] = m.params['general_sweep_pts']
    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)


def EntangleZZ(name,debug = False,upload_only=False):

    m = purify(name)
    sweep_purification.prepare(m)
   
    pts = 1
    m.params['reps_per_ROsequence'] = 1000
    sweep_purification.turn_all_sequence_elements_off(m)

    load_BK_params(m)

    m.params['do_general_sweep'] = 0
    m.params['MW_during_LDE'] = 1

    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 1
    m.joint_params['LDE_attempts'] = 200

    m.params['LDE_final_mw_amplitude'] = 0

    ### upload and run

    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)


def EntangleXX(name,debug = False,upload_only=False):
    m = purify(name)
    sweep_purification.prepare(m)
   
    pts = 1
    m.params['reps_per_ROsequence'] = 1000
    sweep_purification.turn_all_sequence_elements_off(m)

    load_BK_params(m)

    m.params['do_general_sweep'] = 0
    m.params['MW_during_LDE'] = 1

    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 1
    m.joint_params['LDE_attempts'] = 250


    ### this can also be altered to the actual theta pulse by negating the if statement
    if True:
        m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
        m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']

    ### upload and run

    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)


def PurifyZZ(name):
    pass

def PurifyXX(name): 
    pass

def PurifyYY(name):
    pass


if __name__ == '__main__':

    ########### local measurements
    #MW_Position(name+'_MW_position',upload_only=False)

    
    tail_sweep(name+'_tail_Sweep',debug = False,upload_only=False, minval = 0.1, maxval=0.8, local=False)
    # optical_rabi(name+'_optical_rabi_22_deg',debug = False,upload_only=False,local=False)

    #SPCorrsPuri_PSB_singleSetup(name+'_SPCorrs_PSB',debug = False,upload_only=False)
    


    ###### non-local measurements // purification parameters
    # SPCorrsPuri_ZPL_twoSetup(name+'_SPCorrs_ZPL',debug = False,upload_only=False)


    ###### non-local measurements // Barrett Kok parameters
    # BarretKok_SPCorrs(name+'_SPCorrs_ZPL_BK',debug = False, upload_only=  False)
    # TPQI(name+'_TPQI',debug = False,upload_only=False)
    # TPQI(name+'_ionisation',debug = False,upload_only=False)
    #EntangleZZ(name+'_Entangle_ZZ',debug = False,upload_only=False)
    # EntangleXX(name+'_Entangle_XX',debug = False,upload_only=False)


    # for i in range(10):

    #     print '-----------------------------------'            
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
    #     qt.msleep(1)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break

    #     TPQI(name+'_TPQI_gate_noise'+str(i),debug = False,upload_only=False)
