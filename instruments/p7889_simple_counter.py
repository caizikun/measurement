from instrument import Instrument
import time
import types
import qt
import gobject
import os
import numpy as np
from lib import config

class p7889_simple_counter(Instrument):
    
    def __init__(self, name, p7889 = 'p7889', physical_adwin=None):
        Instrument.__init__(self, name)
        self.name = name
        
        self._p7889 = qt.instruments[p7889]
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
                minval = 0.1,
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

        self.add_function('start')
        self.add_function('stop')
                
        self.set_is_running(False)
        self.set_integration_time(0.2)
        self.set_adwin_par(43)
        self.set_roi_min(1)
        self.set_roi_max(100)
        self._total_countrate, self._roi_countrate = 0,0
        self._timer_id = -1

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
            self._c0_tot = 0
            self._c0_roi = 0
            self._init_p7889()
            self._p7889.Start()
            self._timer_id = gobject.timeout_add(int(self._integration_time*1e3), self._update_countrates)
        
    def stop(self):
        self._is_running = False
        self._p7889.Stop()
        return gobject.source_remove(self._timer_id)

    def _init_p7889(self):
        self._p7889.set_binwidth(1)
        if self._p7889.get_range_ns()< self.get_roi_max():
            self._p7889.set_range_ns(self.get_roi_max()*2)
        self._p7889.set_ROI_ns(self.get_roi_min(),self.get_roi_max())

    def do_get_countrate(self):
       # print self._roi_countrate
        return  self._roi_countrate

    def _update_countrates(self):
        if not self._is_running or not self._p7889.get_state():
            self.stop()
            return False
        #print 'poo'
        t1 = time.time()
        _c1_tot = self._p7889.get_total_sum()
        _c1_roi = self._p7889.get_RoiSum()
        self._total_countrate = (_c1_tot - self._c0_tot)/(t1- self._t0)
        self._roi_countrate = (_c1_roi - self._c0_roi)/(t1- self._t0)
        self.get_countrate()
        self._t0 = t1
        self._c0_tot = _c1_tot
        self._c0_roi = _c1_roi

        if self._physical_adwin != None:
            self._physical_adwin.Set_Par(self.get_adwin_par(),int(np.round(self._roi_countrate)))
        #self.stop()
        return True
            

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
    
        
        
    