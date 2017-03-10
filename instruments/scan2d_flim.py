# Fluorescent lifetime 2d scanner. uses the linescan to obtain data.
# author: Bas Hensen 2016

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
from scan2d_counts import scan2d_counts
# import scan2d_counts; reload(scan2d_counts)
import msvcrt
import types
import gobject
import numpy as np
import qt
import hdf5_data as h5
import measurement.lib.measurement2.measurement as m2
import h5py
import logging
import time
import os
from lib import config

class scan2d_flim(scan2d_counts):
    def __init__(self, name, linescan, mos, timetagger, pixelclk_channel=0, apd_channel=2, sync_channel=3, **kw):
        scan2d_counts.__init__(self, name, linescan, mos, **kw)

        self.add_parameter('roi_min',
            unit='ns',
            type = types.FloatType,
            flags = Instrument.FLAG_GETSET)
        self.add_parameter('roi_max',
            unit='ns',
            type = types.FloatType,
            flags = Instrument.FLAG_GETSET)
        self.add_parameter('timebinsize',
            unit='ps',
            minval=4,
            maxval=1024,
            type = types.IntType,
            flags = Instrument.FLAG_GETSET)
        self.add_parameter('retrieve_time',
            unit='s',
            minval=0.01,
            maxval=1,
            type = types.FloatType,
            flags = Instrument.FLAG_GETSET)

        self.add_parameter('do_flim',
            type = types.BooleanType,
            flags = Instrument.FLAG_GETSET)

        self.add_function('get_2d_flim_data')

        if 'qutau' in timetagger:
            self._qutau = qt.instruments[timetagger]
            self._retrieve_flim_data = self._retrieve_qutau_data
            self._init_timetagger = self._init_qutau
            self._get_timetagger_timebase = self._qutau.get_timebase
            self._start_timetagger = lambda x: self._qutau.get_last_timestamps()
            self._stop_timetagger = lambda: None
        elif 'PH' in timetagger:
            self._ph = qt.instruments[timetagger]
            self._retrieve_flim_data = self._retrieve_ph_data
            self._init_timetagger = self._init_ph
            self._get_timetagger_timebase = lambda: self._ph.get_BaseResolution()*1e-12
            self._start_timetagger = self._ph.StartMeas
            self._stop_timetagger = self._ph.StopMeas
        else:
            raise Exception(self.get_name()+': Timetagger instrument not recognised, curently supports picoharp and qutau.')

        self._pixelclk_channel = pixelclk_channel
        self._apd_channel = apd_channel
        self._sync_channel = sync_channel
        self._timer_id = -1
        self._saved_data_checksum = 0
        self._meas_time= 0

        self.set_roi_min(250)
        self.set_roi_max(400)
        self.set_timebinsize(100)
        self.set_retrieve_time(0.05)
        self.set_do_flim(True)
        self._cfgparlist=['roi_min','roi_max','timebinsize','retrieve_time','do_flim' ]

         # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
            if p in self._cfgparlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._cfgparlist:
            value = self.get(param)
            self.ins_cfg[param] = value

    def do_get_roi_min(self):
        return self._roi_min

    def do_set_roi_min(self, val):
        self._roi_min = val

    def do_get_roi_max(self):
        return self._roi_max

    def do_set_roi_max(self, val):
        self._roi_max = val

    def do_get_retrieve_time(self):
        return self._retrieve_time

    def do_set_retrieve_time(self, val):
        self._retrieve_time = val

    def do_get_do_flim(self):
        return self._do_flim

    def do_set_do_flim(self, val):
        self._do_flim = val

    def do_get_timebinsize(self):
        return self._timebinsize

    def do_set_timebinsize(self, val):
        self._timebinsize = val


    def _start_running(self):
        if self.get_do_flim():   
            self._pixel_pts = self._xsteps*self._ysteps
            self._init_timetagger()
            self._roi_min_bin = int(np.round(self.get_roi_min()*1e-9/self._get_timetagger_timebase()))
            self._roi_max_bin = int(np.round(self.get_roi_max()*1e-9/self._get_timetagger_timebase()))
            self._hist_pts = int(np.round((self.get_roi_max()*1e-9-self.get_roi_min()*1e-9)/(self.get_timebinsize()*1e-12)))
            self._hist_bins = np.linspace(self._roi_min_bin, self._roi_max_bin,self._hist_pts+1)
            print self._hist_pts
            self._flim_data = np.zeros((self._pixel_pts,self._hist_pts), dtype=np.int)
            self._flim_data_syncs = np.zeros(self._pixel_pts, dtype=np.int)
            self._cur_pixel = 0
            self._start_timetagger(self._meas_time)
            self._timer_id = gobject.timeout_add(int(self.get_retrieve_time()*1000), self._retrieve_flim_data)
            print 'STARTING FLIM SCAN'  
        scan2d_counts._start_running(self)

    def _init_ph(self):
        if self._ph.OpenDevice():
            self._ph.start_T2_mode()
            if hasattr(self._ph,'calibrate'):
                self._ph.calibrate()
            #self._ph.set_Range(6)
            self._meas_time = int(self.get_pixel_time()*self._pixel_pts+5000)
        else:
            raise(Exception('Picoquant instrument '+self._ph.get_name()+ ' cannot be opened: Close the gui?'))

    def _init_qutau(self):
        #self._temp_program_awg()
        print 'init qutau'
        self._qutau.get_last_timestamps()

    def _retrieve_qutau_data(self):
        if not self._is_running:
            return False
        t,c,valid_length = self._qutau.get_last_timestamps()
        #print self._qutau.get_buffer_size()
        #print t,c,valid_length
        if valid_length == 0:
            return True
        if valid_length == self._qutau.get_buffer_size():
            logging.warning(self.get_name() + ': QuTau buffer full, decrease retrieve_time or eventrates.')

        event_time,channel = t[:valid_length],c[:valid_length]
        pixel_clk_idxs = np.where(channel == self._pixelclk_channel)
        return self._process_flim_data(event_time, channel, valid_length, pixel_clk_idxs)

    def _retrieve_ph_data(self):
        ret_l = 2**15
        t0=time.time()
        if not self._is_running or not self._ph.get_MeasRunning():
            return False
        valid_length, data = self._ph.get_TTTR_Data(ret_l)
        #print time.time()-t0
        if valid_length == 0:
            return True
        if valid_length == ret_l:#self._ph.get_TTREADMAX():
            pass
            #logging.warning(self.get_name() + ': TTTR record length is maximum length, \
            #        could indicate too low transfer rate resulting in buffer overflow.')
        if self._ph.get_Flag_FifoFull():
            print 'Fifo full'
            logging.warning(self.get_name() + ': Fifo full!')
        if self._ph.get_Flag_Overflow():
            logging.warning(self.get_name() + ': Aborting the measurement: OverflowFlag is high.')
       
        event_time, channel, special, marker_channel, overflow = self._ph.TTTR_decode(data[:valid_length])
        pixel_clk_idxs = np.where(special & (marker_channel == self._pixelclk_channel))     
        return self._process_flim_data(event_time, channel, valid_length, pixel_clk_idxs)

    def _process_flim_data(self, event_time, channel, valid_length, pixel_clk_idxs):
        last_pixel_clk_idx = 0
        print 'process flim data'
        #print pixel_clk_idxs
        #print valid_length
        for i,pixel_clk_idx in enumerate(np.append(pixel_clk_idxs,valid_length)): #we also take the data at the end, belonging to the next pixel. 
            print 'process',i, pixel_clk_index
            tp,cp = event_time[last_pixel_clk_idx:pixel_clk_idx], channel[last_pixel_clk_idx:pixel_clk_idx]
            #Because we have to be fast here, we count only events where one photon directly followed a sync pulse.
            ph_idxs   = np.where(cp == self._apd_channel)[0]
            sync_idxs = np.where(cp == self._sync_channel)[0]
            ph_sync_idxs = np.intersect1d(ph_idxs-1,sync_idxs)
            dts = tp[ph_sync_idxs+1]-tp[ph_sync_idxs]
            if self._cur_pixel<self._pixel_pts:
                   cur_hist = np.histogram(dts, bins = self._hist_bins)[0]
                   self._flim_data_syncs[self._cur_pixel] += len(sync_idxs)
                   self._flim_data[self._cur_pixel] += cur_hist#.astype(np.float)*1e4/np.max([len(sync_idxs),1])
            elif self._cur_pixel>self._pixel_pts:
                logging.warning(self.get_name()+': number of pixels detected by qutau exeeds total number of pixels, discarding remaining pixel data.')

            last_pixel_clk_idx = pixel_clk_idx
            if last_pixel_clk_idx != valid_length:
                #print self._cur_pixel
                self._cur_pixel+=1
        return True

    def save(self):
        scan2d_counts.save(self)
        #print np.sum(self._flim_data)
        #print self._saved_data_checksum
        if self.get_do_flim() and np.sum(self._flim_data)!=self._saved_data_checksum:
            print 'SAVING DATA'
            if self._cur_pixel != self._pixel_pts:
                logging.warning(self.get_name()+': number of pixels detected by qutau {:d} not equal total number of pixels {:d}'.format(self._cur_pixel,self._pixel_pts))
            #print 'total counts', np.sum(self.get_last_2d_qutau_data()), 'max counts',np.max(self.get_last_2d_qutau_data()),' at', np.where(self.get_last_2d_qutau_data() == np.max(self.get_last_2d_qutau_data()))
            f = h5py.File(self._last_filepath,'a')
            f.create_dataset('flim_data', data = self.get_2d_flim_data(self._flim_data))
            f.create_dataset('flim_data_syncs', data = self._flim_data_syncs.reshape(self._xsteps,self._ysteps))
            f.attrs['roi_min_bin'] = self._roi_min_bin
            f.attrs['roi_max_bin'] = self._roi_max_bin
            f.attrs['timebase']    = self.get_timebinsize()
            f.attrs['roi_min_ns']  = self.get_roi_min()
            f.attrs['roi_max_ns']  = self.get_roi_max()
            f.attrs['flim_units']  = 'counts per pulse x 1e4'
            f.close()
            self._saved_data_checksum = np.sum(self._flim_data)


    def get_2d_flim_data(self, data):
        return data.reshape(self._xsteps,self._ysteps,self._hist_pts)

    def _scan_finished(self):
        scan2d_counts._scan_finished(self)
        self._stop_timetagger()

    def remove(self):
        gobject.source_remove(self._timer_id)
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        gobject.source_remove(self._timer_id)
        print 'reloading'
        Instrument.reload(self)

    def _temp_program_awg(self):
        awg = qt.instruments['AWG']
        pts=1#self._pixel_pts
        if awg.get_runmode()=='SEQ' and int(awg.get_sq_length()) == pts:
            pass
        else:
            from measurement.lib.pulsar import pulse, pulselib, element, pulsar
            p_wait = pulse.SquarePulse('katana_trg', length=2e-6, amplitude = 0)
            p_sync = pulse.SquarePulse('katana_trg', length=200e-9, amplitude = 1)
            elts=[]
            s= pulsar.Sequence('test_flim_seq')
            e=element.Element('sync_elt', pulsar=qt.pulsar)
            e.add(p_sync, start = 200e-9)
            e.add(p_wait)
            elts.append(e)
            for i in range(pts):
                s.append(name = 'sync_init'+str(i),
                                wfname = e.name,
                                trigger_wait = 1,
                                repetitions = 1)
            qt.pulsar.program_awg(s,e)
            
        awg.start()
        i=0
        awg_ready = False
        while not awg_ready and i<100:
            if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
                raise Exception('User abort while waiting for AWG')
            try:
                if awg.get_state() == 'Waiting for trigger':
                    qt.msleep(1)
                    awg_ready = True
                    print 'AWG Ready!'
                    break
                else:
                    print 'AWG not in wait for trigger state but in state:', awg.get_state()
            except:
                print 'waiting for awg: usually means awg is still busy and doesnt respond'
                print 'waiting', i, '/ 100'
                awg.clear_visa()
                i=i+1

            qt.msleep(0.5)