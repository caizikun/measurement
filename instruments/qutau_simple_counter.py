#Bas Hensen 2016
from instrument import Instrument
import time
import types
import qt
import gobject
import os
import numpy as np
from lib import config
import logging
from analysis.lib.fitting import fit, common

class qutau_simple_counter(Instrument):
    
    def __init__(self, name, qutau = 'qutau', physical_adwin=None, qutau_apd_channel=2, qutau_sync_channel=3):
        Instrument.__init__(self, name)
        self.name = name
        
        self._qutau = qt.instruments[qutau]
        if physical_adwin != None:
            self._physical_adwin = qt.instruments[physical_adwin]
        else:
            self._physical_adwin = None
        self.add_parameter('is_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)
                
        self.add_parameter('integration_time',
                type=types.FloatType,
                unit='s',
                flags=Instrument.FLAG_GETSET,
                minval = 0.01,
                maxval = 10)
        self.add_parameter('adwin_par',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET,
                minval = 1,
                maxval = 80)
        self.add_parameter('roi_min',
            unit='ns',
            type = types.FloatType,
            flags = Instrument.FLAG_GETSET)
        self.add_parameter('roi_max',
            unit='ns',
            type = types.FloatType,
            flags = Instrument.FLAG_GETSET)
        self.add_parameter('countrate',
            type = types.FloatType,
            flags = Instrument.FLAG_GET)
        self.add_parameter('countrate_roi',
            type = types.FloatType,
            flags = Instrument.FLAG_GET)
        self.add_parameter('cpsh',
            type = types.FloatType,
            flags = Instrument.FLAG_GET)

        self.add_function('start')
        self.add_function('stop')
        self.add_function('plot_last_histogram')
        self.add_function('manual_update')
                
        self.set_is_running(False)
        self.set_integration_time(0.2)
        self.set_adwin_par(43)
        self.set_roi_min(1)
        self.set_roi_max(100)
        self._total_countrate, self._roi_countrate, self._cpsh = 0,0,0
        self._timer_id = -1

        self._qutau_apd_channel = qutau_apd_channel
        self._qutau_sync_channel = qutau_sync_channel
        
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
            po = self.get_parameter_options(p)
            if po and po['flags'] & Instrument.FLAG_SET:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self.get_parameter_names():
            value = self.get(param)
            self.ins_cfg[param] = value
            
    
    def do_get_is_running(self):
        return self._is_running

    def do_set_is_running(self, val):
        self._is_running = val
        
    def do_get_integration_time(self):
        return self._integration_time

    def do_set_integration_time(self, val):
        self._integration_time = val
        
    def do_get_adwin_par(self):
        return self._adwin_par

    def do_set_adwin_par(self, val):
        self._adwin_par = val

    def do_get_roi_min(self):
        return self._roi_min

    def do_set_roi_min(self, val):
        self._roi_min = val

    def do_get_roi_max(self):
        return self._roi_max

    def do_set_roi_max(self, val):
        self._roi_max = val

    def start(self):
        if not self._is_running:
            self._is_running = True
            self._t0 = time.time()
            self._qutau.get_last_timestamps()
            self._hist_binsize_ns = 0.1# ns
            self._plot_extra_range = 10 #ns
            self._hist_bins = np.linspace((self.get_roi_min()- self._plot_extra_range)/self._hist_binsize_ns, (self.get_roi_max()+ self._plot_extra_range)/self._hist_binsize_ns,np.round((self.get_roi_max()-self.get_roi_min()+2*self._plot_extra_range)/self._hist_binsize_ns))
            self._hist = np.zeros(len(self._hist_bins)-1, dtype =np.int)
            self._timer_id = gobject.timeout_add(int(self.get_integration_time()*1e3), self._update_countrates)
        
    def stop(self):
        self._is_running = False
        return gobject.source_remove(self._timer_id)

    def do_get_countrate(self):
        return self._total_countrate

    def do_get_cpsh(self):
        return self._cpsh

    def do_get_countrate_roi(self):
        return self._roi_countrate

    def _update_countrates(self, manual=False):
        if not manual and not self._is_running:
            self.stop()
            return False
        #print 'poo'
       
        t1 = time.time()
        t,c,v = self._qutau.get_last_timestamps()
        #print 'valid events:',v
        if v == self._qutau.get_buffer_size():
            logging.warning(self.get_name() + ': QuTau buffer full, decrease integration time or eventrates.')
        self._ts,self._cs= t[:v],c[:v]
        total_counts = np.sum(self._cs == self._qutau_apd_channel)
        #print 'syncrate',float(np.sum(self._cs == self._qutau_sync_channel))/(t1- self._t0)
        
        #Because we have to be fast here, we count only events where one photon directly followed a sync pulse.
        ph_idxs   = np.where(self._cs == self._qutau_apd_channel)[0]
        sync_idxs = np.where(self._cs == self._qutau_sync_channel)[0]
        ph_sync_idxs = np.intersect1d(ph_idxs-1,sync_idxs)
        dts = self._ts[ph_sync_idxs+1]-self._ts[ph_sync_idxs]
        
        self._dts_ns = dts*0.1#1e9*self._qutau.get_timebase()
        self._hist += np.histogram(self._dts_ns,bins = self._hist_bins)[0]#np.min(dts[dts>0]),np.max(dts),pts))

        roi_counts = np.sum((self._dts_ns>self.get_roi_min()) & (self._dts_ns <=self.get_roi_max()))

        self._total_countrate = float(total_counts)/(t1- self._t0)
        self._roi_countrate = float(roi_counts)/(t1- self._t0)
        self._cpsh = 1e4*float(roi_counts)/max(len(sync_idxs),1)
        self.get_countrate()
        self.get_countrate_roi()
        self.get_cpsh()
        self._t0 = t1

        if self._physical_adwin != None:
            self._physical_adwin.Set_Par(self.get_adwin_par(),int(np.round(self._roi_countrate)))
        #self.stop()
        return True
            
    def manual_update(self):
        self._t0 = time.time()
        self._qutau.get_last_timestamps()
        qt.msleep(self.get_integration_time())
        self._update_countrates(manual=True)

    def plot_last_histogram(self):
        y,x = self._hist, self._hist_bins[1:]*self._hist_binsize_ns#np.histogram(self._dts_ns, bins = np.linspace(self.get_roi_min(), self.get_roi_max(),pts))#np.min(dts[dts>0]),np.max(dts),pts))
        plotname = self.get_name()+'_histogram'
        qt.plot(x,y, name=plotname, clear=True)
        f = common.fit_exp_decay_shifted_with_offset
        #A * exp(-(x-x0)/tau) + a
        #['g_a', 'g_A', 'g_tau', 'g_x0']
        args=[1,np.max(y)*0.1,12,x[np.argmax(y)+2.]]
        first_fit_bin =  int(np.round(self._plot_extra_range/self._hist_binsize_ns))
        xf,yf=x[first_fit_bin:],y[first_fit_bin:]
        fitres = fit.fit1d(xf,yf, f,*args, fixed = [0],
                   do_print = False, ret = True, maxfev=100)
        plot_pts=200
        x_p=np.linspace(min(xf),max(xf),plot_pts)
        if fitres['success']:
            y_p = fitres['fitfunc'](x_p)
            print 'fit success'
        else:
            y_p = f(*args)[1](x_p)
            print 'fit failed'
        print fitres['params_dict']
        qt.plot(x_p,y_p,'b', name=plotname, clear=False)


    def remove(self):
        self.save_cfg()
        self.stop()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self.save_cfg()
        self.stop()
        print 'reloading'
        Instrument.reload(self)
    
        
        
    