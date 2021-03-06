"""
Measurement class for measurements with QuTau TDC

The class puts out data in the same format as the pq_measurement class does.

The used channel configuration on the front end of the QuTau is the following:
Channel 1-3 = Photon channels
Channels 4 = Sync
Channels 5-8 = Markers

"""

import numpy as np
import qt
import measurement.lib.measurement2.measurement as m2
import time
import logging
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3  #; reload(T2_tools_v3)
import hdf5_data as h5
import msvcrt


import matplotlib.pyplot as plt
#Creating a qutau instance in 80_create_instruments: qutau = qt.instruments.create('QuTau', 'QuTau')


qutau=qt.instruments['QuTau']
AWG=qt.instruments['AWG']
GreenAOM=qt.instruments['GreenAOM']
optimiz0r=qt.instruments['optimiz0r']
class QuTauMeasurement(m2.Measurement):
    # NOTE: Untested!!
    mprefix = 'QuTauMeasurement'

    def setup(self, do_calibrate = True, debug = False, **kw):
        if debug:
            return

        
        print qutau.get_timebase()


    def measurement_process_running(self):
        return True

    def print_measurement_progress(self):
        pass

    def start_measurement_process(self):
        pass

    def stop_measurement_process(self):
        pass

    def autoconfig(self):

        print 'Not initializing QuTau'
        #qutau.initialize()
        qt.msleep(.5)
        #empty the buffer of the TDC by setting a buffer size in the device.
        qutau.set_buffer_size(1e6)#self.params['QuTau_buffer_size'])

        print 'qutau data-loss status before start:', qutau.get_data_lost()


    def run_debug(self):
        print 'hi im conor'
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

    def run(self, autoconfig=True, debug=False, setup=True):
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
        


        MIN_SYNC_BIN = np.uint64(0)     #np.uint64(self.params['MIN_SYNC_BIN'])# no longer needed as the data is in absolute time
        MAX_SYNC_BIN = np.uint64(1000)  #np.uint64(self.params['MAX_SYNC_BIN'])#

        #if you don't want to change the msmt_params.py file then overwrite QuTau_buffer_size' with TTTR_read_count
        #TTTR_read_count = self.params['TTTR_read_count']
        buffer_size=1e6#self.params['QuTau_buffer_size']

        QuTau_timefactor=1  #is this the relative fraction of device-dependent timeresolutions? E.g.: PQ Timeharp vs. qutau??


        T2_WRAPAROUND = np.uint64(2**16)
        #the above number was hardcoded in the driver of the TimeHarp TH260P. Should not matter for the current evalutation
        #but the LDE_live_filter needs this.

        #T2_TIMEFACTOR = np.uint64(self.PQ_ins.get_T2_TIMEFACTOR())
        #T2_READMAX = self.PQ_ins.get_T2_READMAX() # in this implementation this is equal to == buffer_size

        print 'run QuTau measurement, extract data with an array length of ', buffer_size 


        # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
        dset_hhtime = self.h5data.create_dataset('QuTau_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhchannel = self.h5data.create_dataset('QuTau_channel-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhspecial = self.h5data.create_dataset('QuTau_special-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhsynctime = self.h5data.create_dataset('QuTau_sync_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhsyncnumber = self.h5data.create_dataset('QuTau_sync_number-{}'.format(rawdata_idx), 
            (0,), 'u4', maxshape=(None,))
  
        current_dset_length = 0
        
        self.start_keystroke_monitor('abort',timer=False)
        self.start_measurement_process()
        _timer=time.time()
        ii=0
        
        while(self.measurement_process_running()): #previously self.PQ_ins.get_MeasRunning

            #print 'timers', time.time()-_timer
            if (time.time()-_timer)>1:#self.params['measurement_abort_check_interval']:
                if self.measurement_process_running():
                    
                    self.print_measurement_progress()
                    self._keystroke_check('abort')
                    if self.keystroke('abort') in ['q','Q']:
                        print 'aborted.'
                        break
                        self.stop_measurement_process()
                else:
                    
                   #Check that all the measurement data has been transsfered from the PQ ins FIFO
                    ii+=1
                    print 'Retreiving late data from QuTau, for {} seconds. Press x to stop'.format(ii*self.params['measurement_abort_check_interval'])
                    self._keystroke_check('abort')
                    if _length == 0 or self.keystroke('abort') in ['x']: 
                        break 
                print 'current sync, dset length:', last_sync_number, current_dset_length
            
                _timer=time.time()



                      
            # FOR RT Extrating data uncomment
            #_timestamps, _channels, _length = qutau.get_last_timestamps(buffer_size=buffer_size) 
            #print _length
            


            #ll[_length]+=1 #XXX
            if _length > 0:
                if _length == buffer_size: #was previously T2_READMAX;
                    logging.warning('extracted data length equal to the buffer_size, \
                            could indicate too low transfer rate resulting in buffer overflow.')

                #convert ctype arrays to numpy arrays for further data processing
                # FOR RT Extrating data uncomment
                #_nptimestamps=np.frombuffer(buffer(_timestamps), dtype=np.uint64).astype(np.uint32) #needs to be 64 bit!!! live filter cannot handle this right now.

                #####################################################################################
                ##Secondary, and maybe faster, conversion function:                                ##
                ##_nptimestamps=np.ctypeslib.as_array(_timestamps)                                 ##
                ## for the conversion from ctype to numpy arrays                                   ##
                ##problem: python spits out a warning/ is bugged for this operation  `             ##
                ##the additional warning might cause significant delays                            ##
                #####################################################################################
                #for further information see:
                #http://stackoverflow.com/questions/4964101/pep-3118-warning-when-using-ctypes-array-as-numpy-array

                # FOR RT Extrating data uncomment
                #_c, _s = QuTau_decode(channels=_channels[:_length])

                #in order to make this live filter work: compile the cython file for uint64 as timestmap input.
                
                # FOR RT Extrating data uncomment
                #hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                #    newlength, t_ofl, t_lastsync, last_sync_number = \
                #        T2_tools_v3.LDE_live_filter(_nptimestamps[:_length], _c, _s, t_ofl, t_lastsync, last_sync_number,
                #                                MIN_SYNC_BIN, MAX_SYNC_BIN,
                #                                T2_WRAPAROUND, QuTau_timefactor) #T2_tools_v3 only

                #print _nptimestamps
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

                if current_dset_length > 1e6:#self.params['MAX_DATA_LEN']:
                    rawdata_idx += 1
                    dset_hhtime = self.h5data.create_dataset('QuTau_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                    dset_hhchannel = self.h5data.create_dataset('QuTau_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                    dset_hhspecial = self.h5data.create_dataset('QuTau_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                    dset_hhsynctime = self.h5data.create_dataset('QuTau_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                    dset_hhsyncnumber = self.h5data.create_dataset('QuTau_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))         
                    current_dset_length = 0

                    self.h5data.flush()


                #if an overflow of the current buffer is detected --> abort measurement, your data is crap anyways.
                if qutau.get_data_lost()!=0:
                    print 'warning Overflow'
                    print qutau.get_data_lost()
                    print 'measurement aborted'
                    self.stop_measurement_process()
        
        #self.h5data.create_dataset('PQ_hist_lengths', data=ll, compression='gzip')#XXX
        #self.h5data.flush()#XXX
        qt.msleep(1)
        for i in np.arange(5):
            _timestamps, _channels, _length = qutau.get_last_timestamps(buffer_size=buffer_size)
            _nptimestamps=np.frombuffer(buffer(_timestamps), dtype=np.uint64).astype(np.uint32)
            _c, _s = QuTau_decode(channels=_channels[:_length])
            hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools_v3.LDE_live_filter(_nptimestamps[:_length], _c, _s, t_ofl, t_lastsync, last_sync_number,
                                                MIN_SYNC_BIN, MAX_SYNC_BIN,
                                                T2_WRAPAROUND, QuTau_timefactor) 
            current_dset_length+=_length
            print 'Length of final dataset', _length
        print 'QuTau total datasets, events in last dataset, last sync number:', rawdata_idx, current_dset_length, last_sync_number
        newlength=0
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


        rawdata_idx = 1
        dset_hhtime = self.h5data.create_dataset('QuTau_time-{}'.format(rawdata_idx), 
                    (0,), 'u8', maxshape=(None,))
        dset_hhchannel = self.h5data.create_dataset('QuTau_channel-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhspecial = self.h5data.create_dataset('QuTau_special-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhsynctime = self.h5data.create_dataset('QuTau_sync_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhsyncnumber = self.h5data.create_dataset('QuTau_sync_number-{}'.format(rawdata_idx), 
            (0,), 'u4', maxshape=(None,))         
        current_dset_length = 0

        self.h5data.flush()

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        print 'stopping msmnts process'
        self.stop_measurement_process()
        print 'stopped msmnts process'



        


def QuTau_decode(channels):
    """
    Decode binary data from QuTau into event time.
    Convert the acquired signal-channels into channel and special bit (conform with pq_measurement.py).
    """
    ch=np.zeros(len(channels),dtype=np.uint32)

    special=np.zeros(len(channels),dtype=np.uint32)

    for i,c in  enumerate(channels):
        if c>2: #no photon detected
            special[i]= 1
            if c>3:
                ch[i]= 2**(c-4) # I don't understand this asigning of channel numbers: if c>3 we map it back to 2**(c-4), i.e. ch4-> 0? -Machiel '13-03-'15
            else:
                ch[i] = 0 # doesnt this overlap with actual channel 0 (physically channel 1, but labeled 0 in this code) -Machiel
        else:
            ch[i] = c

    return ch.astype(np.uint32), special.astype(np.uint32)



# def PQ_decode(data):
#     """
#     Decode the binary data into event time (absolute, highest precision),
#     channel number and special bit. See PicoQuant (HydraHarp, TimeHarp, PicoHarp) 
#     documentation about the details.
#     """
#     event_time = np.bitwise_and(data, 2**25-1)
#     channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
#     special = np.bitwise_and(np.right_shift(data, 31), 1)
#     return event_time, channel, special


class QuTauMeasurementIntegrated(QuTauMeasurement):
    # NOTE: For RT readout, timing is controlled by AWG, number of syncs are checked by ADwin.
    #       Filter used checks dt between syncs (2 per RO) and corrects if syncs are missed
    mprefix = 'QuTauMeasurementIntegrated'
    adwin_process = 'green_readout'
    def autoconfig(self):
        for key,_val in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_long']:              
            self.set_adwin_process_variable_from_params(key)
        QuTauMeasurement.autoconfig(self)

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [      'completed_reps']
                    )

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

        myl=0
        ### _length!?    

        MIN_SYNC_BIN = np.uint64(0)     #np.uint64(self.params['MIN_SYNC_BIN'])# no longer needed as the data is in absolute time
        MAX_SYNC_BIN = np.uint64(self.params['MAX_SYNC_BIN']-1)  #np.uint64(self.params['MAX_SYNC_BIN'])#
        DT_SYNC_BIN  = np.uint64(self.params['DT_SYNC_BIN']) 
        #if you don't want to change the msmt_params.py file then overwrite QuTau_buffer_size' with TTTR_read_count
        #TTTR_read_count = self.params['TTTR_read_count']
        buffer_size=1e6#self.params['QuTau_buffer_size']

        QuTau_timefactor=1  #is this the relative fraction of device-dependent timeresolutions? E.g.: PQ Timeharp vs. qutau??


        T2_WRAPAROUND = np.uint64(2**16)
        #the above number was hardcoded in the driver of the TimeHarp TH260P. Should not matter for the current evalutation
        #but the LDE_live_filter needs this.

        hist_length = np.uint64(self.params['MAX_SYNC_BIN'] - self.params['MIN_SYNC_BIN'])
        sweep_length = np.uint64(self.params['pts'])
        syncs_per_sweep = np.uint64(self.params['syncs_per_sweep'])

        hist0 = np.zeros((hist_length,sweep_length), dtype='u1')
        hist1 = np.zeros((hist_length,sweep_length), dtype='u1')



        self.start_keystroke_monitor('abort',timer=False)
        stop_msmnt=False
        Signal=np.zeros(self.params['pts'])
        for i in np.arange(self.params['nr_of_cycles']):
            # print '#################################################' 
            print '#####           Cycle nr ', i+1 , ' / ', self.params['nr_of_cycles'] ,'        #####'
            # print '#################################################'
            current_dset_length=0
            last_sync_number = 0
            t_ofl = 0
            t_lastsync = 0
            _length=0
            self.start_measurement_process()
            # qt.msleep(1.)
            _timer=time.time() 
       
            while(self.measurement_process_running()):
            
                

                if (time.time()-_timer)>self.params['measurement_abort_check_interval']:
                    if not self.measurement_process_running():
                        break

                    self.print_measurement_progress()
                    _timer = time.time()
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                        stop_msmnt = True
                if stop_msmnt:
                    break        
                
            


                
            _timestamps, _channels, _length = qutau.get_last_timestamps() 

            qt.msleep(1)
            _npchannels=np.frombuffer(buffer(_channels), dtype=np.uint8).astype(np.uint32)
            


            
            print 'Events in Channels [2,4]: ' ,len(np.where(_npchannels==1)[0]),len(np.where(_npchannels==3)[0])
            if _length > 0:
                if _length == buffer_size: #was previously T2_READMAX;
                    logging.warning('extracted data length equal to the buffer_size, \
                            could indicate too low transfer rate resulting in buffer overflow.')

                #convert ctype arrays to numpy arrays for further data processing
                _nptimestamps=np.frombuffer(buffer(_timestamps), dtype=np.uint64).astype(np.uint32) #needs to be 64 bit!!! live filter cannot handle this right now.
                self.nr_of_syncs=len(np.where(_npchannels==3)[0])
                
                _c, _s = QuTau_decode(channels=_channels[:_length])

                hist0, hist1, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools_v3.T2_live_filter_integrated_RT(_nptimestamps[:_length], _c, _s, hist0, hist1, t_ofl, 
                            t_lastsync, last_sync_number,
                            sweep_length,MIN_SYNC_BIN, MAX_SYNC_BIN,DT_SYNC_BIN,
                            T2_WRAPAROUND,QuTau_timefactor)
                current_dset_length+=newlength
            print 'QuTau current datasets, events in last dataset, last sync number:', rawdata_idx, current_dset_length, last_sync_number        
            
            #print len(_s)
            for j in np.arange(self.params['pts']):
                Signal[j]=(sum(hist1[int(self.params['RO_start']/0.081):int(self.params['RO_stop']/.081),j]))

            live_plot = qt.Plot2D(name='Live_data', clear=True)
            live_plot.add(self.params['sweep_pts'], Signal, 'bO', yerr = np.sqrt(Signal))
            live_plot.add(self.params['sweep_pts'], Signal, 'b-')

            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                stop_msmnt=True
                print 'QuTau total datasets, events in last dataset, last sync number:', rawdata_idx, current_dset_length, last_sync_number
                self.stop_measurement_process()

                dset_hist0 = self.h5data.create_dataset('QuTau_hist0', data=hist0, compression='gzip')
                dset_hist1 = self.h5data.create_dataset('QuTau_hist1', data=hist1, compression='gzip')
                #dset_channels = self.h5data.create_dataset('QuTau_channels', data=_npchannels, compression='gzip')
                #dset_timestamps = self.h5data.create_dataset('QuTau_timestamps', data=_nptimestamps, compression='gzip')
                self.h5data.flush()
                qt.msleep(2)
                break
                
            if (self.params['do_spatial_optimize']) and i % 100 == 0: # every hundred cycles one spatial optimize
                GreenAOM.set_power(10e-6)
                qt.msleep(2)
                optimiz0r.optimize(dims=['x','y','z','x','y'])
                GreenAOM.turn_off()
                qt.msleep(2)
                # qutau.get_last_timestamps(buffer_size=buffer_size) 
       
        print 'QuTau total datasets, events in last dataset, last sync number:', rawdata_idx, current_dset_length, last_sync_number

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        if not stop_msmnt:
            self.stop_measurement_process()

            dset_hist0 = self.h5data.create_dataset('QuTau_hist0', data=hist0, compression='gzip')
            dset_hist1 = self.h5data.create_dataset('QuTau_hist1', data=hist1, compression='gzip')
            #dset_channels = self.h5data.create_dataset('QuTau_channels', data=_npchannels, compression='gzip')
            #dset_timestamps = self.h5data.create_dataset('QuTau_timestamps', data=_nptimestamps, compression='gzip')
            self.h5data.flush()


