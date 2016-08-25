# Fluorescent lifetime 2d scanner. uses the linescan to obtain data.
# author: Bas Hensen 2016

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
from scan2d_counts import scan2d_counts
import msvcrt
import types
import gobject
import numpy as np
import qt
import hdf5_data as h5
import measurement.lib.measurement2.measurement as m2
import h5py
import logging

class scan2d_flim(scan2d_counts):
    def __init__(self, name, linescan, mos, qutau, qutau_pixel_clk_channel=0, qutau_apd_channel=2, qutau_sync_channel=3, **kw):
        scan2d_counts.__init__(self, name, linescan, mos, **kw)

        self.add_parameter('roi_min',
            unit='ns',
            type = types.FloatType,
            flags = Instrument.FLAG_GETSET)
        self.add_parameter('roi_max',
            unit='ns',
            type = types.FloatType,
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

        self.add_function('get_2d_qutau_data')

        self._qutau = qt.instruments[qutau]
        self._qutau_pixel_clk_channel = qutau_pixel_clk_channel
        self._qutau_apd_channel = qutau_apd_channel
        self._qutau_sync_channel = qutau_sync_channel
        self._timer_id = -1

        self.set_roi_min(100)
        self.set_roi_max(300)
        self.set_retrieve_time(0.05)
        self.set_do_flim(True)

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


    def _start_running(self):
        if self.get_do_flim():
            print 'start'      
            self._pixel_pts = self._xsteps*self._ysteps
            self._temp_program_awg()
            self._roi_min_bin = int(np.round(self.get_roi_min()*1e-9/self._qutau.get_timebase()))
            self._roi_max_bin = int(np.round(self.get_roi_max()*1e-9/self._qutau.get_timebase()))
            self._hist_pts = self._roi_max_bin-self._roi_min_bin
            self._qutau_data = np.zeros((self._pixel_pts,self._hist_pts), dtype=np.float)
            self._qutau_data_raw = np.zeros((self._pixel_pts,self._hist_pts), dtype=np.int)
            self._cur_pixel = 0
            self._qutau.get_last_timestamps()
            self._timer_id = gobject.timeout_add(int(self.get_pixel_time()), self._retrieve_qutau_data)
        scan2d_counts._start_running(self)


    def _temp_program_awg(self):
        awg = qt.instruments['AWG']
        pts=1#self._pixel_pts
        
        if awg.get_runmode()=='SEQ' and int(awg.get_sq_length()) == pts:
            pass
        else:
            from measurement.lib.pulsar import pulse, pulselib, element, pulsar
            p_wait = pulse.SquarePulse('sync0', length=2e-6, amplitude = 0)
            p_sync = pulse.SquarePulse('sync0', length=200e-9, amplitude = 1)
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

    def save(self):
        scan2d_counts.save(self)
        if self.get_do_flim() and self._qutau_data!=self._saved_data:
            if self._cur_pixel != self._pixel_pts:
                logging.warning(self.get_name()+': number of pixels detected by qutau {:d} not equal total number of pixels {:d}'.format(self._cur_pixel,self._pixel_pts))
            #print 'total counts', np.sum(self.get_last_2d_qutau_data()), 'max counts',np.max(self.get_last_2d_qutau_data()),' at', np.where(self.get_last_2d_qutau_data() == np.max(self.get_last_2d_qutau_data()))
            f = h5py.File(self._last_filepath,'a')
            f.create_dataset('flim_data', data = self.get_2d_qutau_data(self._qutau_data))
            f.create_dataset('flim_data_raw', data = self.get_2d_qutau_data(self._qutau_data_raw))
            f.attrs['roi_min_bin'] = self._roi_min_bin
            f.attrs['roi_max_bin'] = self._roi_max_bin
            f.attrs['timebase']    = self._qutau.get_timebase()
            f.attrs['roi_min_ns']  = self.get_roi_min()
            f.attrs['roi_max_ns']  = self.get_roi_max()
            f.attrs['flim_units']  = 'counts per pulse x 1e4'
            f.close()
            self._saved_data = self._qutau_data

    def get_2d_qutau_data(self, data):
        return data.reshape(self._xsteps,self._ysteps,self._hist_pts)

    def _retrieve_qutau_data(self):
        if not self._is_running:
            return False
        t,c,v = self._qutau.get_last_timestamps()
        #print 'valid events:',v
        if v == self._qutau.get_buffer_size():
            logging.warning(self.get_name() + ': QuTau buffer full, decrease retrieve_time or eventrates.')
        tv,cv= t[:v],c[:v]
        pixel_clk_idxs = np.where(cv == self._qutau_pixel_clk_channel)

        last_pixel_clk_idx = 0
        for i,pixel_clk_idx in enumerate(np.append(pixel_clk_idxs,v)): #we also take the data at the end, belonging to the next pixel.
            tp,cp = tv[last_pixel_clk_idx:pixel_clk_idx], cv[last_pixel_clk_idx:pixel_clk_idx]
            #Because we have to be fast here, we count only events where one photon directly followed a sync pulse.
            ph_idxs   = np.where(cp == self._qutau_apd_channel)[0]
            sync_idxs = np.where(cp == self._qutau_sync_channel)[0]
            ph_sync_idxs = np.intersect1d(ph_idxs-1,sync_idxs)
            dts = tp[ph_sync_idxs+1]-tp[ph_sync_idxs]
            if self._cur_pixel<self._pixel_pts:
                   self._qutau_data[self._cur_pixel] += np.histogram(dts, bins = np.arange(self._roi_min_bin, self._roi_max_bin+1))[0].astype(np.float)*1e4/np.max([len(sync_idxs),1])
                   self._qutau_data_raw[self._cur_pixel] += np.histogram(dts, bins = np.arange(self._roi_min_bin, self._roi_max_bin+1))[0]
            elif self._cur_pixel>self._pixel_pts:
                logging.warning(self.get_name()+': number of pixels detected by qutau exeeds total number of pixels, discarding remaining pixel data.')

            last_pixel_clk_idx = pixel_clk_idx
            if last_pixel_clk_idx != v:
                #print self._cur_pixel
                self._cur_pixel+=1

        return True

    def remove(self):
        gobject.source_remove(self._timer_id)
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        gobject.source_remove(self._timer_id)
        print 'reloading'
        Instrument.reload(self)